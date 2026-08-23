import argparse
import calendar
import json
import os
import re
import uuid
from typing import Any

from langgraph.graph import END, START, StateGraph

try:
    from anthropic import Anthropic
except Exception:  # Optional; deterministic synthesis works without an API key.
    Anthropic = None

try:
    from .db_tools import (
        KPI_LABELS,
        compare_kpi,
        get_dq_summary,
        get_kpi_metric,
        get_transaction_details,
        validate_readonly_sql,
    )
    from .retriever import detect_knowledge_scope, retrieve_chunks
    from .state import AgentState
except ImportError:  # Allows: python src/agent.py "question"
    from db_tools import (
        KPI_LABELS,
        compare_kpi,
        get_dq_summary,
        get_kpi_metric,
        get_transaction_details,
        validate_readonly_sql,
    )
    from retriever import detect_knowledge_scope, retrieve_chunks
    from state import AgentState


MONTHS = {name.lower(): number for number, name in enumerate(calendar.month_name) if name}
MONTHS.update({name.lower(): number for number, name in enumerate(calendar.month_abbr) if name})

CHANNELS = {
    "mobile": "Mobile Banking",
    "mobile banking": "Mobile Banking",
    "internet": "Internet Banking",
    "internet banking": "Internet Banking",
    "atm": "ATM",
    "branch": "Branch",
    "pos": "POS",
    "call center": "Call Center",
}

UNSAFE_TERMS = [
    "delete ", "update ", "insert ", "drop ", "truncate ", "alter ",
    "create table", "grant ", "revoke ",
]


def _trace(state: AgentState, message: str) -> list[str]:
    return list(state.get("trace", [])) + [message]


def parse_months(question: str) -> list[int]:
    q = question.lower()
    found: list[tuple[int, int]] = []

    for name, number in MONTHS.items():
        match = re.search(rf"\b{re.escape(name)}\b", q)
        if match:
            found.append((match.start(), number))

    # Keep month order from the question and remove duplicates caused by full/abbr names.
    ordered: list[int] = []
    for _, number in sorted(found):
        if number not in ordered:
            ordered.append(number)
    return ordered


def detect_year(question: str) -> int:
    match = re.search(r"\b(20\d{2})\b", question)
    return int(match.group(1)) if match else 2026


def detect_channel(question: str) -> str | None:
    q = question.lower()
    # Longer phrases first.
    for phrase in sorted(CHANNELS, key=len, reverse=True):
        if phrase in q:
            return CHANNELS[phrase]
    return None


def detect_kpi(question: str) -> str | None:
    q = question.lower()

    if "complaints per" in q or "complaint burden" in q:
        return "complaints_per_1000_transactions"
    if "complaint resolution" in q or ("complaint" in q and "resolution rate" in q):
        return "complaint_resolution_rate"
    if "sla" in q and any(term in q for term in ["breach", "breached", "performance"]):
        return "sla_breach_rate"
    if "campaign" in q and any(term in q for term in ["conversion", "converted"]):
        return "campaign_conversion_rate"
    if "success rate" in q or "transaction success" in q:
        return "transaction_success_rate"
    if "failure rate" in q or "transaction failure" in q or "transaction failures" in q:
        return "transaction_failure_rate"

    return None


def classify_question(question: str) -> dict[str, Any]:
    """Deterministic bounded router for the interview demo."""

    q = question.lower().strip()
    months = parse_months(question)
    year = detect_year(question)
    channel = detect_channel(question)
    kpi = detect_kpi(question)
    scopes = detect_knowledge_scope(question)

    if any(term in q for term in UNSAFE_TERMS):
        return {
            "intent": "unsafe_request",
            "knowledge_scope": [],
            "tool_name": "none",
            "tool_args": {},
        }

    transaction_match = re.search(r"\btx[a-z0-9_-]*\d+[a-z0-9_-]*\b", q, re.IGNORECASE)
    if transaction_match or "transaction_id" in q or "transaction id" in q:
        transaction_id = transaction_match.group(0).upper() if transaction_match else ""
        return {
            "intent": "transaction_lookup",
            "knowledge_scope": [],
            "tool_name": "get_transaction_details",
            "tool_args": {"transaction_id": transaction_id},
        }

    if any(term in q for term in [
        "duplicate", "missing channel", "failed transaction with fee", "high-value",
        "high value", "data quality", "dq exception", "dq summary",
    ]):
        return {
            "intent": "dq_investigation",
            "knowledge_scope": ["business_rules.md"],
            "tool_name": "get_dq_summary",
            "tool_args": {},
        }

    if kpi and any(term in q for term in ["concerning", "why", "investigate", "root cause", "interpret"]):
        if not months:
            return {
                "intent": "unknown",
                "knowledge_scope": scopes,
                "tool_name": "none",
                "tool_args": {},
            }
        current_month = months[-1]
        prior_month = current_month - 1 if current_month > 1 else 12
        prior_year = year if current_month > 1 else year - 1
        if prior_year != year:
            # The current portfolio data is Jan-Jun 2026; do not silently cross outside it.
            return {
                "intent": "unknown",
                "knowledge_scope": scopes,
                "tool_name": "none",
                "tool_args": {},
            }
        return {
            "intent": "mixed_analysis",
            "knowledge_scope": ["kpi_definitions.md", "investigation_playbook.md"],
            "tool_name": "compare_kpi",
            "tool_args": {
                "kpi": kpi,
                "month_a": prior_month,
                "month_b": current_month,
                "channel": channel,
                "year": year,
            },
        }

    if kpi and (
        len(months) >= 2
        or any(term in q for term in ["compare", "versus", " vs ", "change", "improve", "deteriorate"])
    ):
        if len(months) >= 2:
            month_a, month_b = months[0], months[1]
        elif len(months) == 1:
            month_b = months[0]
            month_a = month_b - 1
        else:
            return {
                "intent": "unknown",
                "knowledge_scope": [],
                "tool_name": "none",
                "tool_args": {},
            }
        return {
            "intent": "comparison",
            "knowledge_scope": [],
            "tool_name": "compare_kpi",
            "tool_args": {
                "kpi": kpi,
                "month_a": month_a,
                "month_b": month_b,
                "channel": channel,
                "year": year,
            },
        }

    if kpi and months:
        return {
            "intent": "operational_metric",
            "knowledge_scope": [],
            "tool_name": "get_kpi_metric",
            "tool_args": {
                "kpi": kpi,
                "month": months[-1],
                "channel": channel,
                "year": year,
            },
        }

    if scopes or any(term in q for term in ["what is", "definition", "define", "mean", "formula"]):
        return {
            "intent": "knowledge_question",
            "knowledge_scope": scopes or ["kpi_definitions.md"],
            "tool_name": "none",
            "tool_args": {},
        }

    return {
        "intent": "unknown",
        "knowledge_scope": scopes,
        "tool_name": "none",
        "tool_args": {},
    }


def classify_node(state: AgentState) -> AgentState:
    decision = classify_question(state["question"])
    return {
        **decision,
        "trace": _trace(
            state,
            f"[ROUTE] intent={decision['intent']} tool={decision['tool_name']}",
        ),
    }


def retrieve_node(state: AgentState) -> AgentState:
    scopes = state.get("knowledge_scope") or None
    results = retrieve_chunks(state["question"], top_k=3, scopes=scopes)

    if results:
        source_text = ", ".join(
            f"{result['source']}#{result['section']}" for result in results
        )
        message = f"[RAG] retrieved={source_text}"
    else:
        message = "[RAG] no relevant approved chunk retrieved"

    return {
        "retrieved_context": results,
        "trace": _trace(state, message),
    }


def tool_node(state: AgentState) -> AgentState:
    name = state.get("tool_name", "none")
    args = state.get("tool_args", {})

    try:
        if name == "get_kpi_metric":
            result = get_kpi_metric(**args)
        elif name == "compare_kpi":
            result = compare_kpi(**args)
        elif name == "get_transaction_details":
            if not args.get("transaction_id"):
                raise ValueError("A transaction ID is required for transaction lookup.")
            result = get_transaction_details(**args)
        elif name == "get_dq_summary":
            result = get_dq_summary()
        else:
            result = {"error": f"Unsupported or missing tool: {name}"}
    except Exception as exc:
        result = {"error": str(exc), "tool": name}

    status = "ERROR" if result.get("error") else "SUCCESS"
    return {
        "tool_result": result,
        "trace": _trace(state, f"[TOOL] {name} status={status}"),
    }


def validation_node(state: AgentState) -> AgentState:
    result = state.get("tool_result", {})

    if state.get("intent") == "knowledge_question":
        context = state.get("retrieved_context", [])
        if context:
            evidence_status = "SUFFICIENT"
            validation_status = "PASSED"
        else:
            evidence_status = "INSUFFICIENT"
            validation_status = "ABSTAINED: no approved chunk retrieved"
    elif result.get("error"):
        evidence_status = "INSUFFICIENT"
        validation_status = f"FAILED: {result['error']}"
    elif state.get("tool_name") == "get_kpi_metric":
        denominator = result.get("metric_denominator")
        if denominator in (None, 0):
            evidence_status = "INSUFFICIENT"
            validation_status = "FAILED: KPI denominator is empty or zero"
        else:
            evidence_status = "SUFFICIENT"
            validation_status = "PASSED"
    elif state.get("tool_name") == "compare_kpi":
        first = result.get("first_period", {})
        second = result.get("second_period", {})
        if first.get("metric_value") is None or second.get("metric_value") is None:
            evidence_status = "INSUFFICIENT"
            validation_status = "FAILED: one comparison period has no KPI value"
        else:
            evidence_status = "SUFFICIENT"
            validation_status = "PASSED"
    elif state.get("tool_name") == "get_transaction_details":
        evidence_status = "SUFFICIENT" if result.get("found") else "INSUFFICIENT"
        validation_status = "PASSED" if result.get("found") else "FAILED: transaction not found"
    else:
        evidence_status = "SUFFICIENT"
        validation_status = "PASSED"

    return {
        "evidence_status": evidence_status,
        "validation_status": validation_status,
        "trace": _trace(
            state,
            f"[VALIDATION] {validation_status} evidence={evidence_status}",
        ),
    }


def safety_stop_node(state: AgentState) -> AgentState:
    sample = state["question"]
    valid, reason = validate_readonly_sql(sample)
    if valid:
        reason = "The request asks for a data-changing action, which is outside the agent contract."

    answer = (
        "Request rejected. This Banking Operations Agent is read-only and cannot execute "
        f"data-changing SQL or operational updates. Control result: {reason}"
    )
    return {
        "evidence_status": "NOT_APPLICABLE",
        "validation_status": "BLOCKED",
        "final_answer": answer,
        "trace": _trace(state, "[GUARDRAIL] unsafe/write request blocked"),
    }


def fallback_node(state: AgentState) -> AgentState:
    return {
        "evidence_status": "INSUFFICIENT",
        "validation_status": "ABSTAINED",
        "final_answer": (
            "I do not have enough approved routing information to answer this request safely. "
            "Please ask for an approved KPI definition, a Jan-Jun 2026 KPI period/comparison, "
            "a transaction lookup, or a supported data-quality investigation."
        ),
        "trace": _trace(state, "[ABSTAIN] unsupported or underspecified request"),
    }


def _format_knowledge_answer(state: AgentState) -> str:
    context = state.get("retrieved_context", [])
    if not context:
        return (
            "I could not find an approved definition or rule for this question. "
            "I will not invent one."
        )

    best = context[0]
    return (
        f"Approved knowledge source: {best['source']} -> {best['section']}\n\n"
        f"{best['content']}"
    )


def _format_metric_answer(result: dict[str, Any]) -> str:
    value = result.get("metric_value")
    numerator = result.get("metric_numerator")
    denominator = result.get("metric_denominator")
    return (
        f"{result['kpi_label']} for {result['channel']} was {value}% for "
        f"{result['period_start']} to {result['period_end_exclusive']} (end exclusive). "
        f"Evidence: numerator={numerator}, denominator={denominator}. "
        f"Source: {result['source']}. SQL validation: {result['sql_validation']}."
    )


def _format_comparison_answer(result: dict[str, Any], mixed: bool = False) -> str:
    first = result["first_period"]
    second = result["second_period"]
    delta = result.get("delta_percentage_points")

    direction = "increased" if (delta or 0) > 0 else "decreased" if (delta or 0) < 0 else "did not change"
    base = (
        f"{result['kpi_label']} for {result['channel']} {direction} from "
        f"{first['metric_value']}% ({first['period_start']}) to "
        f"{second['metric_value']}% ({second['period_start']}), a change of "
        f"{delta} percentage points. Source: {result['source']}."
    )

    if mixed:
        base += (
            " The approved knowledge does not define a formal 'concerning' threshold, "
            "so I would not invent one. The evidence supports describing the period-over-period "
            "movement; a specific root cause requires additional evidence."
        )

    return base


def deterministic_synthesis(state: AgentState) -> str:
    intent = state.get("intent")

    if intent == "knowledge_question":
        return _format_knowledge_answer(state)

    if state.get("evidence_status") == "INSUFFICIENT":
        error = state.get("tool_result", {}).get("error")
        return (
            "I cannot produce an evidence-backed answer because the required evidence is unavailable. "
            f"Details: {error or state.get('validation_status', 'insufficient evidence')}"
        )

    result = state.get("tool_result", {})

    if intent == "operational_metric":
        return _format_metric_answer(result)
    if intent == "comparison":
        return _format_comparison_answer(result)
    if intent == "mixed_analysis":
        return _format_comparison_answer(result, mixed=True)
    if intent == "transaction_lookup":
        record = result.get("record")
        if not record:
            return f"Transaction {result.get('transaction_id')} was not found in the trusted warehouse."
        return (
            f"Transaction {record['transaction_id']} has status {record['transaction_status']}, "
            f"amount {record['amount']} {record['currency']}, fee {record['fee_amount']}, "
            f"channel {record.get('channel_name')}, at {record['transaction_datetime']}. "
            "Source: PostgreSQL trusted warehouse."
        )
    if intent == "dq_investigation":
        rows = result.get("exceptions", [])
        summary = ", ".join(
            f"{row['exception_type']}={row['exception_count']}" for row in rows
        )
        return (
            f"Current transaction DQ exceptions: {summary}. "
            "Normal KPI analysis uses the trusted warehouse; exception records remain available "
            "for audit and investigation. Source: staging.stg_transaction_dq_exceptions."
        )

    return "The workflow completed, but no supported synthesis route was selected."


def optional_claude_synthesis(state: AgentState, deterministic_answer: str) -> str | None:
    """Optional Claude synthesis. The demo remains functional with USE_LLM=false."""

    if os.getenv("USE_LLM", "false").lower() != "true":
        return None
    if Anthropic is None or not os.getenv("ANTHROPIC_API_KEY"):
        return None

    model = os.getenv("ANTHROPIC_MODEL")
    if not model:
        return None

    client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    context = state.get("retrieved_context", [])
    evidence = state.get("tool_result", {})

    prompt = f"""
User question:
{state['question']}

Approved retrieved context:
{json.dumps(context, default=str)}

Deterministic tool evidence:
{json.dumps(evidence, default=str)}

Validated deterministic draft:
{deterministic_answer}

Write a concise banking-operations answer using only the supplied context and evidence.
Do not invent thresholds or root causes. Include source and period where available.
If evidence is insufficient, say so explicitly.
""".strip()

    response = client.messages.create(
        model=model,
        max_tokens=600,
        temperature=0,
        system=(
            "You are a bounded banking operations analytics assistant. "
            "Calculations and facts come from approved context and deterministic tools."
        ),
        messages=[{"role": "user", "content": prompt}],
    )

    if not response.content:
        return None
    return getattr(response.content[0], "text", None)


def synthesis_node(state: AgentState) -> AgentState:
    deterministic_answer = deterministic_synthesis(state)

    try:
        llm_answer = optional_claude_synthesis(state, deterministic_answer)
    except Exception as exc:
        llm_answer = None
        trace = _trace(state, f"[LLM] Claude synthesis failed; deterministic fallback used: {exc}")
    else:
        mode = "Claude" if llm_answer else "deterministic"
        trace = _trace(state, f"[SYNTHESIS] mode={mode}")

    return {
        "final_answer": llm_answer or deterministic_answer,
        "trace": trace,
    }


def route_after_classify(state: AgentState) -> str:
    intent = state.get("intent")
    if intent == "unsafe_request":
        return "safety_stop"
    if intent == "unknown":
        return "fallback"
    if intent in {"knowledge_question", "mixed_analysis", "dq_investigation"}:
        return "retrieve"
    return "tool"


def route_after_retrieve(state: AgentState) -> str:
    if state.get("intent") == "knowledge_question":
        return "validate"
    return "tool"


def build_graph():
    builder = StateGraph(AgentState)

    builder.add_node("classify", classify_node)
    builder.add_node("retrieve", retrieve_node)
    builder.add_node("tool", tool_node)
    builder.add_node("validate", validation_node)
    builder.add_node("synthesize", synthesis_node)
    builder.add_node("safety_stop", safety_stop_node)
    builder.add_node("fallback", fallback_node)

    builder.add_edge(START, "classify")
    builder.add_conditional_edges(
        "classify",
        route_after_classify,
        {
            "retrieve": "retrieve",
            "tool": "tool",
            "safety_stop": "safety_stop",
            "fallback": "fallback",
        },
    )
    builder.add_conditional_edges(
        "retrieve",
        route_after_retrieve,
        {"validate": "validate", "tool": "tool"},
    )
    builder.add_edge("tool", "validate")
    builder.add_edge("validate", "synthesize")
    builder.add_edge("synthesize", END)
    builder.add_edge("safety_stop", END)
    builder.add_edge("fallback", END)

    return builder.compile()


GRAPH = build_graph()


def run_agent(question: str) -> AgentState:
    run_id = str(uuid.uuid4())
    initial: AgentState = {
        "run_id": run_id,
        "question": question,
        "trace": [f"[START] request received run_id={run_id}"],
    }
    return GRAPH.invoke(initial)


def main() -> None:
    parser = argparse.ArgumentParser(description="Banking Operations Agent V2")
    parser.add_argument("question", nargs="+", help="Natural-language banking operations question")
    parser.add_argument("--show-state", action="store_true", help="Print final structured state")
    args = parser.parse_args()

    question = " ".join(args.question)
    result = run_agent(question)

    print(f"\n=== RUN ID ===\n{result.get('run_id')}")

    print("\n=== TRACE ===")
    for event in result.get("trace", []):
        print(event)

    print("\n=== ANSWER ===")
    print(result.get("final_answer", "No answer returned."))

    if args.show_state:
        print("\n=== STATE ===")
        print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
