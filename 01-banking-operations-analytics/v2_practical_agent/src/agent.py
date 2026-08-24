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
    from .aggregate_tools import get_basic_aggregate
    from .derived_metrics import get_derived_metric
    from .db_tools import (
        compare_kpi,
        compare_kpi_periods,
        get_dq_summary,
        get_kpi_metric,
        get_transaction_details,
        validate_readonly_sql,
    )
    from .retriever import detect_knowledge_scope, retrieve_chunks
    from .state import AgentState
except ImportError:
    from aggregate_tools import get_basic_aggregate
    from derived_metrics import get_derived_metric
    from db_tools import (
        compare_kpi,
        compare_kpi_periods,
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
    "mobile banking": "Mobile Banking",
    "internet banking": "Internet Banking",
    "call center": "Call Center",
    "mobile": "Mobile Banking",
    "internet": "Internet Banking",
    "atm": "ATM",
    "branch": "Branch",
    "pos": "POS",
}

UNSAFE_TERMS = [
    "delete ", "update ", "insert ", "drop ", "truncate ", "alter ",
    "create table", "grant ", "revoke ",
]

ENTITY_TERMS = {
    "transactions": ["transaction", "transactions"],
    "complaints": ["complaint", "complaints"],
    "campaigns": ["campaign", "campaigns"],
    "sla_tickets": ["sla ticket", "sla tickets", "ticket", "tickets"],
    "customers": ["customer", "customers"],
    "accounts": ["account", "accounts"],
    "products": ["product", "products"],
    "branches": ["branch", "branches"],
    "channels": ["channel", "channels"],
}

AGGREGATE_CUES = [
    "how many", "number of", "count", "entries", "entry", "records", "record", "rows", "row",
    "average", "avg", "sum", "total",
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
    if "campaign" in q and any(term in q for term in ["conversion", "converted", "success", "successful"]):
        return "campaign_conversion_rate"
    if "success rate" in q or "transaction success" in q:
        return "transaction_success_rate"
    if "failure rate" in q or "transaction failure" in q or "transaction failures" in q:
        return "transaction_failure_rate"
    return None


def detect_entity(question: str) -> str | None:
    q = question.lower()
    for entity, terms in ENTITY_TERMS.items():
        if any(re.search(rf"\b{re.escape(term)}\b", q) for term in terms):
            return entity
    return None


def detect_derived_metric_request(question: str) -> dict[str, Any] | None:
    """Recognize only explicitly approved derived-metric wording."""

    q = question.lower().strip()
    has_transaction = bool(re.search(r"\btransactions?\b", q))
    has_average = "average" in q or "avg" in q
    has_customer_denominator = any(
        phrase in q
        for phrase in [
            "per user", "per users", "per customer", "per customers",
            "per active user", "per active customer",
        ]
    )

    if not (has_transaction and has_average and has_customer_denominator):
        return None

    # Approved definition: monthly transaction count / distinct customers with at
    # least one transaction in that month. In this banking prototype, "user" is an
    # accepted business-language synonym for customer for this specific metric.
    return {
        "metric": "average_transactions_per_active_customer",
        "months": sorted(set(parse_months(question))),
        "year": detect_year(question),
    }


def detect_aggregate_metric(entity: str, question: str) -> str | None:
    q = question.lower()
    if entity == "transactions":
        if "fee" in q:
            return "fee_amount"
        if "amount" in q or "value" in q:
            return "amount"
    elif entity == "complaints":
        if "resolution" in q and any(term in q for term in ["day", "days", "time"]):
            return "resolution_days"
    elif entity == "campaigns":
        if "converted" in q or "conversion count" in q:
            return "converted_count"
        if "engaged" in q or "engagement count" in q:
            return "engaged_count"
        if "sent" in q:
            return "campaign_sent_count"
    elif entity == "sla_tickets":
        if "target" in q and "hour" in q:
            return "sla_target_hours"
    elif entity == "customers" and "age" in q:
        return "customer_age"
    elif entity == "accounts":
        if "credit limit" in q:
            return "credit_limit"
        if "interest" in q:
            return "interest_rate"
        if "balance" in q:
            return "current_balance"
    return None


def detect_basic_aggregate_request(question: str) -> dict[str, Any] | None:
    q = question.lower().strip()
    if not any(cue in q for cue in AGGREGATE_CUES):
        return None

    entity = detect_entity(question)
    if not entity:
        return {"supported": False, "reason": "No approved aggregate entity matched the request."}

    metric = detect_aggregate_metric(entity, question)
    if any(term in q for term in ["average", "avg"]):
        operation = "average"
    elif "sum" in q or ("total" in q and metric):
        operation = "sum"
    else:
        operation = "count"

    if operation in {"sum", "average"} and not metric:
        return {"supported": False, "reason": f"{operation} requires an approved numeric measure for {entity}."}

    months = sorted(set(parse_months(question)))
    group_by_month = any(term in q for term in ["each month", "per month", "monthly", "by month"])
    if len(months) >= 2:
        group_by_month = True

    return {
        "supported": True,
        "operation": operation,
        "entity": entity,
        "metric": metric,
        "months": months,
        "year": detect_year(question),
        "group_by_month": group_by_month,
    }


def classify_question(question: str) -> dict[str, Any]:
    q = question.lower().strip()
    months = parse_months(question)
    year = detect_year(question)
    channel = detect_channel(question)
    kpi = detect_kpi(question)
    scopes = detect_knowledge_scope(question)

    if any(term in q for term in UNSAFE_TERMS):
        return {"intent": "unsafe_request", "knowledge_scope": [], "tool_name": "none", "tool_args": {}}

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

    derived = detect_derived_metric_request(question)
    if derived is not None:
        return {
            "intent": "derived_metric",
            "knowledge_scope": [],
            "tool_name": "get_derived_metric",
            "tool_args": derived,
        }

    aggregate = detect_basic_aggregate_request(question)
    if aggregate is not None:
        if not aggregate.get("supported"):
            return {"intent": "unknown", "knowledge_scope": [], "tool_name": "none", "tool_args": {}}
        return {
            "intent": "basic_aggregate",
            "knowledge_scope": [],
            "tool_name": "get_basic_aggregate",
            "tool_args": {
                "operation": aggregate["operation"],
                "entity": aggregate["entity"],
                "metric": aggregate["metric"],
                "months": aggregate["months"],
                "year": aggregate["year"],
                "group_by_month": aggregate["group_by_month"],
            },
        }

    if kpi and any(term in q for term in ["concerning", "why", "investigate", "root cause", "interpret"]):
        if not months:
            return {"intent": "unknown", "knowledge_scope": scopes, "tool_name": "none", "tool_args": {}}
        if len(months) >= 2:
            return {
                "intent": "mixed_analysis",
                "knowledge_scope": ["kpi_definitions.md", "investigation_playbook.md"],
                "tool_name": "compare_kpi_periods",
                "tool_args": {
                    "kpi": kpi,
                    "months": sorted(set(months)),
                    "channel": channel,
                    "year": year,
                },
            }
        current_month = months[0]
        prior_month = current_month - 1 if current_month > 1 else 12
        prior_year = year if current_month > 1 else year - 1
        if prior_year != year:
            return {"intent": "unknown", "knowledge_scope": scopes, "tool_name": "none", "tool_args": {}}
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

    if kpi and (len(months) >= 2 or any(term in q for term in ["compare", "versus", " vs ", "change", "improve", "deteriorate"])):
        if len(months) >= 3:
            return {
                "intent": "comparison",
                "knowledge_scope": [],
                "tool_name": "compare_kpi_periods",
                "tool_args": {
                    "kpi": kpi,
                    "months": sorted(set(months)),
                    "channel": channel,
                    "year": year,
                },
            }
        if len(months) >= 2:
            month_a, month_b = sorted(months[:2])
        elif len(months) == 1:
            month_b = months[0]
            month_a = month_b - 1
        else:
            return {"intent": "unknown", "knowledge_scope": [], "tool_name": "none", "tool_args": {}}
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
            "tool_args": {"kpi": kpi, "month": months[-1], "channel": channel, "year": year},
        }

    if scopes or any(term in q for term in ["what is", "what does", "definition", "define", "mean", "formula"]):
        return {
            "intent": "knowledge_question",
            "knowledge_scope": scopes or ["kpi_definitions.md"],
            "tool_name": "none",
            "tool_args": {},
        }

    return {"intent": "unknown", "knowledge_scope": scopes, "tool_name": "none", "tool_args": {}}


def classify_node(state: AgentState) -> AgentState:
    decision = classify_question(state["question"])
    return {
        **decision,
        "trace": _trace(state, f"[ROUTE] intent={decision['intent']} tool={decision['tool_name']}"),
    }


def retrieve_node(state: AgentState) -> AgentState:
    results = retrieve_chunks(state["question"], top_k=3, scopes=state.get("knowledge_scope") or None)
    if results:
        source_text = ", ".join(f"{r['source']}#{r['section']}" for r in results)
        message = f"[RAG] retrieved={source_text}"
    else:
        message = "[RAG] no relevant approved chunk retrieved"
    return {"retrieved_context": results, "trace": _trace(state, message)}


def tool_node(state: AgentState) -> AgentState:
    name = state.get("tool_name", "none")
    args = state.get("tool_args", {})
    try:
        if name == "get_kpi_metric":
            result = get_kpi_metric(**args)
        elif name == "compare_kpi":
            result = compare_kpi(**args)
        elif name == "compare_kpi_periods":
            result = compare_kpi_periods(**args)
        elif name == "get_basic_aggregate":
            result = get_basic_aggregate(**args)
        elif name == "get_derived_metric":
            result = get_derived_metric(**args)
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
    return {"tool_result": result, "trace": _trace(state, f"[TOOL] {name} status={status}")}


def validation_node(state: AgentState) -> AgentState:
    result = state.get("tool_result", {})
    name = state.get("tool_name")

    if state.get("intent") == "knowledge_question":
        valid = bool(state.get("retrieved_context", []))
        evidence_status = "SUFFICIENT" if valid else "INSUFFICIENT"
        validation_status = "PASSED" if valid else "ABSTAINED: no approved chunk retrieved"
    elif result.get("error"):
        evidence_status = "INSUFFICIENT"
        validation_status = f"FAILED: {result['error']}"
    elif name == "get_kpi_metric":
        valid = result.get("metric_denominator") not in (None, 0)
        evidence_status = "SUFFICIENT" if valid else "INSUFFICIENT"
        validation_status = "PASSED" if valid else "FAILED: KPI denominator is empty or zero"
    elif name == "compare_kpi":
        valid = result.get("first_period", {}).get("metric_value") is not None and result.get("second_period", {}).get("metric_value") is not None
        evidence_status = "SUFFICIENT" if valid else "INSUFFICIENT"
        validation_status = "PASSED" if valid else "FAILED: one comparison period has no KPI value"
    elif name == "compare_kpi_periods":
        periods = result.get("periods", [])
        valid = len(periods) >= 2 and all(p.get("metric_value") is not None for p in periods)
        evidence_status = "SUFFICIENT" if valid else "INSUFFICIENT"
        validation_status = "PASSED" if valid else "FAILED: one or more requested comparison periods have no KPI value"
    elif name == "get_basic_aggregate":
        if result.get("grouping") == "month":
            rows = result.get("rows", [])
            valid = bool(rows) and all(r.get("value") is not None for r in rows)
        else:
            valid = result.get("value") is not None
        evidence_status = "SUFFICIENT" if valid else "INSUFFICIENT"
        validation_status = "PASSED" if valid else "FAILED: aggregate query returned no usable value"
    elif name == "get_derived_metric":
        rows = result.get("rows", [])
        valid = bool(rows) and all(
            row.get("metric_value") is not None
            and row.get("metric_numerator") is not None
            and row.get("metric_denominator") not in (None, 0)
            for row in rows
        )
        evidence_status = "SUFFICIENT" if valid else "INSUFFICIENT"
        validation_status = "PASSED" if valid else "FAILED: derived metric numerator or denominator is unavailable"
    elif name == "get_transaction_details":
        valid = bool(result.get("found"))
        evidence_status = "SUFFICIENT" if valid else "INSUFFICIENT"
        validation_status = "PASSED" if valid else "FAILED: transaction not found"
    else:
        evidence_status = "SUFFICIENT"
        validation_status = "PASSED"

    return {
        "evidence_status": evidence_status,
        "validation_status": validation_status,
        "trace": _trace(state, f"[VALIDATION] {validation_status} evidence={evidence_status}"),
    }


def safety_stop_node(state: AgentState) -> AgentState:
    valid, reason = validate_readonly_sql(state["question"])
    if valid:
        reason = "The request asks for a data-changing action, which is outside the agent contract."
    return {
        "evidence_status": "NOT_APPLICABLE",
        "validation_status": "BLOCKED",
        "final_answer": (
            "Request rejected. This Banking Operations Agent is read-only and cannot execute "
            f"data-changing SQL or operational updates. Control result: {reason}"
        ),
        "trace": _trace(state, "[GUARDRAIL] unsafe/write request blocked"),
    }


def fallback_node(state: AgentState) -> AgentState:
    return {
        "evidence_status": "INSUFFICIENT",
        "validation_status": "ABSTAINED",
        "final_answer": (
            "I do not have enough approved routing information to answer this request safely. "
            "Please ask for an approved KPI definition, a Jan-Jun 2026 KPI period/comparison, "
            "a basic count/sum/average or approved derived metric, a transaction lookup, or a supported "
            "data-quality investigation."
        ),
        "trace": _trace(state, "[ABSTAIN] unsupported or underspecified request"),
    }


def _format_knowledge_answer(state: AgentState) -> str:
    context = state.get("retrieved_context", [])
    if not context:
        return "I could not find an approved definition or rule for this question. I will not invent one."
    best = context[0]
    return f"Approved knowledge source: {best['source']} -> {best['section']}\n\n{best['content']}"


def _format_metric_answer(result: dict[str, Any]) -> str:
    return (
        f"{result['kpi_label']} for {result['channel']} was {result.get('metric_value')}% for "
        f"{result['period_start']} to {result['period_end_exclusive']} (end exclusive). "
        f"Evidence: numerator={result.get('metric_numerator')}, denominator={result.get('metric_denominator')}. "
        f"Source: {result['source']}. SQL validation: {result['sql_validation']}."
    )


def _format_comparison_answer(result: dict[str, Any], mixed: bool = False) -> str:
    first = result["first_period"]
    second = result["second_period"]
    delta = result.get("delta_percentage_points")
    direction = "increased" if (delta or 0) > 0 else "decreased" if (delta or 0) < 0 else "did not change"
    base = (
        f"{result['kpi_label']} for {result['channel']} {direction} from "
        f"{first['metric_value']}% ({first['period_start']}) to {second['metric_value']}% "
        f"({second['period_start']}), a change of {delta} percentage points. Source: {result['source']}."
    )
    if mixed:
        base += (
            " The approved knowledge does not define a formal 'concerning' threshold, so I would not invent one. "
            "The evidence supports describing the period-over-period movement; a specific root cause requires additional evidence."
        )
    return base


def _format_multi_period_answer(result: dict[str, Any], mixed: bool = False) -> str:
    period_text = ", ".join(
        f"{p.get('metric_value')}% ({p.get('period_start')})" for p in result.get("periods", [])
    )
    base = f"{result['kpi_label']} for {result['channel']} across the requested periods was {period_text}."
    changes = result.get("changes", [])
    if changes:
        parts = []
        for change in changes:
            delta = change.get("delta_percentage_points")
            delta_text = "unavailable" if delta is None else f"{float(delta):+.2f}"
            parts.append(f"{change.get('from_period')} to {change.get('to_period')}: {delta_text} percentage points")
        base += " Sequential changes: " + "; ".join(parts) + "."
    base += f" Source: {result['source']}."
    if mixed:
        base += (
            " The approved knowledge does not define a formal 'concerning' threshold, so I would not invent one. "
            "The evidence supports describing the multi-period movement; a specific root cause requires additional evidence."
        )
    return base


def _format_basic_aggregate_answer(result: dict[str, Any]) -> str:
    operation = result.get("operation", "aggregate")
    entity_label = result.get("entity_label", result.get("entity", "Entity"))
    metric_label = result.get("metric_label", "value")
    if result.get("grouping") == "month":
        parts = [
            f"{int(row['year']):04d}-{int(row['month']):02d}: {row['value']}"
            for row in result.get("rows", [])
        ]
        return (
            f"{entity_label} {metric_label} ({operation}) by month: " + "; ".join(parts)
            + f". Source: {result['source']}. SQL validation: {result['sql_validation']}."
        )
    return (
        f"{entity_label} {metric_label} ({operation}) = {result.get('value')}. "
        f"Source: {result['source']}. SQL validation: {result['sql_validation']}."
    )


def _format_derived_metric_answer(result: dict[str, Any]) -> str:
    parts = [
        (
            f"{int(row['year']):04d}-{int(row['month']):02d}: {row['metric_value']} "
            f"(transactions={row['metric_numerator']}, active_customers={row['metric_denominator']})"
        )
        for row in result.get("rows", [])
    ]
    return (
        f"{result['metric_label']} by month: " + "; ".join(parts)
        + ". Approved definition: monthly transaction count divided by distinct customers with at least one "
        + f"transaction in that month. Source: {result['source']}. SQL validation: {result['sql_validation']}."
    )


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
    if intent == "basic_aggregate":
        return _format_basic_aggregate_answer(result)
    if intent == "derived_metric":
        return _format_derived_metric_answer(result)
    if intent == "comparison":
        return _format_multi_period_answer(result) if result.get("tool") == "compare_kpi_periods" else _format_comparison_answer(result)
    if intent == "mixed_analysis":
        return _format_multi_period_answer(result, True) if result.get("tool") == "compare_kpi_periods" else _format_comparison_answer(result, True)
    if intent == "transaction_lookup":
        record = result.get("record")
        if not record:
            return f"Transaction {result.get('transaction_id')} was not found in the trusted warehouse."
        return (
            f"Transaction {record['transaction_id']} has status {record['transaction_status']}, amount {record['amount']} "
            f"{record['currency']}, fee {record['fee_amount']}, channel {record.get('channel_name')}, "
            f"at {record['transaction_datetime']}. Source: PostgreSQL trusted warehouse."
        )
    if intent == "dq_investigation":
        summary = ", ".join(
            f"{row['exception_type']}={row['exception_count']}" for row in result.get("exceptions", [])
        )
        return (
            f"Current transaction DQ exceptions: {summary}. Normal KPI analysis uses the trusted warehouse; "
            "exception records remain available for audit and investigation. Source: staging.stg_transaction_dq_exceptions."
        )
    return "The workflow completed, but no supported synthesis route was selected."


def optional_claude_synthesis(state: AgentState, deterministic_answer: str) -> str | None:
    if os.getenv("USE_LLM", "false").lower() != "true":
        return None
    if Anthropic is None or not os.getenv("ANTHROPIC_API_KEY"):
        return None
    model = os.getenv("ANTHROPIC_MODEL")
    if not model:
        return None

    client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    prompt = f"""
User question:
{state['question']}

Approved retrieved context:
{json.dumps(state.get('retrieved_context', []), default=str)}

Deterministic tool evidence:
{json.dumps(state.get('tool_result', {}), default=str)}

Validated deterministic draft:
{deterministic_answer}

Write a concise banking-operations answer using only the supplied context and evidence.
Do not invent thresholds, metric definitions, denominators, or root causes. Include source and period where available.
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
        trace = _trace(state, f"[SYNTHESIS] mode={'Claude' if llm_answer else 'deterministic'}")
    return {"final_answer": llm_answer or deterministic_answer, "trace": trace}


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
    return "validate" if state.get("intent") == "knowledge_question" else "tool"


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
        {"retrieve": "retrieve", "tool": "tool", "safety_stop": "safety_stop", "fallback": "fallback"},
    )
    builder.add_conditional_edges("retrieve", route_after_retrieve, {"validate": "validate", "tool": "tool"})
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

    result = run_agent(" ".join(args.question))
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
