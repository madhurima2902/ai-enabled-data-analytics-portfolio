import argparse
import json
import os
from typing import Any

from langgraph.graph import END, START, StateGraph

try:
    from anthropic import Anthropic
except Exception:  # Optional; deterministic synthesis works without an API key.
    Anthropic = None

try:
    from .dq_tools import run_checks, validate_readonly_sql, validate_warehouse_readiness
    from .knowledge import retrieve_rules
    from .state import DQAgentState
except ImportError:  # Allows: python src/agent.py "question"
    from dq_tools import run_checks, validate_readonly_sql, validate_warehouse_readiness
    from knowledge import retrieve_rules
    from state import DQAgentState


ALL_CHECKS = [
    "row_reconciliation",
    "duplicate_transactions",
    "failed_transaction_fees",
    "missing_channels",
    "high_value_transactions",
]

UNSAFE_TERMS = [
    "delete ", "update ", "insert ", "drop ", "truncate ", "alter ",
    "create table", "grant ", "revoke ",
]


def _trace(state: DQAgentState, message: str) -> list[str]:
    return list(state.get("trace", [])) + [message]


def classify_question(question: str) -> dict[str, Any]:
    """Bounded deterministic router for approved data-quality checks."""

    q = question.lower().strip()

    if any(term in q for term in UNSAFE_TERMS):
        return {"intent": "unsafe_request", "checks_requested": []}

    if any(term in q for term in [
        "validate the current transaction load",
        "validate current transaction load",
        "validate the transaction load",
        "data quality issues",
        "dq issues",
        "full validation",
        "run all checks",
    ]):
        return {"intent": "full_validation", "checks_requested": ALL_CHECKS}

    if any(term in q for term in [
        "warehouse ready", "ready for kpi", "ready for reporting", "warehouse readiness",
    ]):
        return {"intent": "warehouse_readiness", "checks_requested": ALL_CHECKS}

    if "duplicate" in q:
        return {"intent": "duplicate_check", "checks_requested": ["duplicate_transactions"]}

    if ("failed" in q and "fee" in q) or "failed-fee" in q or "failed fee" in q:
        return {"intent": "failed_fee_check", "checks_requested": ["failed_transaction_fees"]}

    if "missing channel" in q or ("channel" in q and "missing" in q):
        return {"intent": "missing_channel_check", "checks_requested": ["missing_channels"]}

    if "high-value" in q or "high value" in q or "500000" in q or "500,000" in q:
        return {"intent": "high_value_check", "checks_requested": ["high_value_transactions"]}

    if any(term in q for term in [
        "raw and warehouse", "raw vs warehouse", "row count", "reconcile", "reconciliation",
        "why do raw", "raw rows", "warehouse rows",
    ]):
        return {"intent": "reconciliation_check", "checks_requested": ["row_reconciliation"]}

    return {"intent": "unknown", "checks_requested": []}


def classify_node(state: DQAgentState) -> DQAgentState:
    decision = classify_question(state["question"])
    return {
        **decision,
        "trace": _trace(
            state,
            f"[ROUTE] intent={decision['intent']} checks={','.join(decision['checks_requested']) or 'none'}",
        ),
    }


def retrieve_rules_node(state: DQAgentState) -> DQAgentState:
    rules = retrieve_rules(state.get("checks_requested", []))
    sources = ", ".join(
        f"{item['source']}#{item['section']}" for item in rules
    ) or "none"
    return {
        "retrieved_rules": rules,
        "trace": _trace(state, f"[KNOWLEDGE] retrieved={sources}"),
    }


def execute_checks_node(state: DQAgentState) -> DQAgentState:
    try:
        if state.get("intent") in {"full_validation", "warehouse_readiness"}:
            result = validate_warehouse_readiness()
        else:
            result = {
                "check": "selected_checks",
                "results": run_checks(state.get("checks_requested", [])),
                "source": "PostgreSQL raw/staging/warehouse validation controls",
                "sql_validation": "PASSED",
            }
        message = "[TOOLS] deterministic DQ checks status=SUCCESS"
    except Exception as exc:
        result = {"error": str(exc)}
        message = f"[TOOLS] deterministic DQ checks status=ERROR type={type(exc).__name__}"

    return {
        "check_results": result,
        "trace": _trace(state, message),
    }


def validation_node(state: DQAgentState) -> DQAgentState:
    payload = state.get("check_results", {})

    if payload.get("error"):
        validation_status = "FAILED"
        evidence_status = "INSUFFICIENT"
    else:
        if payload.get("check") == "warehouse_readiness":
            statuses = [
                item["status"] for item in payload.get("results", {}).values()
            ]
        else:
            statuses = [
                item["status"] for item in payload.get("results", {}).values()
            ]

        if "FAIL" in statuses:
            validation_status = "FAILED"
            evidence_status = "SUFFICIENT"
        elif "REVIEW" in statuses:
            validation_status = "PASSED_WITH_REVIEW"
            evidence_status = "SUFFICIENT"
        else:
            validation_status = "PASSED"
            evidence_status = "SUFFICIENT"

    return {
        "validation_status": validation_status,
        "evidence_status": evidence_status,
        "trace": _trace(
            state,
            f"[VALIDATION] status={validation_status} evidence={evidence_status}",
        ),
    }


def safety_stop_node(state: DQAgentState) -> DQAgentState:
    valid, reason = validate_readonly_sql(state["question"])
    if valid:
        reason = "The request asks for a data-changing action outside the agent contract."

    return {
        "validation_status": "BLOCKED",
        "evidence_status": "NOT_APPLICABLE",
        "final_answer": (
            "Request rejected. The Data Quality & Validation Agent is read-only and may detect, "
            f"validate, and recommend actions but may not modify data. Control result: {reason}"
        ),
        "trace": _trace(state, "[GUARDRAIL] unsafe/write request blocked"),
    }


def fallback_node(state: DQAgentState) -> DQAgentState:
    return {
        "validation_status": "ABSTAINED",
        "evidence_status": "INSUFFICIENT",
        "final_answer": (
            "I do not have an approved data-quality route for this request. Ask about transaction-load "
            "validation, row reconciliation, duplicates, failed transaction fees, missing channels, "
            "high-value transactions, or warehouse readiness."
        ),
        "trace": _trace(state, "[ABSTAIN] unsupported or underspecified DQ request"),
    }


def _summary_lines(payload: dict[str, Any]) -> list[str]:
    results = payload.get("results", {})
    lines: list[str] = []

    for name, result in results.items():
        evidence = result.get("evidence", {})
        evidence_text = ", ".join(f"{key}={value}" for key, value in evidence.items())
        lines.append(f"- {name}: {result.get('status')} | {evidence_text}")

    return lines


def deterministic_synthesis(state: DQAgentState) -> str:
    if state.get("evidence_status") == "INSUFFICIENT":
        error = state.get("check_results", {}).get("error")
        return (
            "I cannot produce an evidence-backed validation result because the required evidence is unavailable. "
            f"Details: {error or 'unsupported or insufficient evidence'}"
        )

    payload = state.get("check_results", {})
    lines = _summary_lines(payload)
    rules = state.get("retrieved_rules", [])
    sources = sorted({rule["source"] for rule in rules})

    if payload.get("check") == "warehouse_readiness":
        readiness = payload.get("status")
        headline = f"Trusted warehouse readiness: {readiness}."
    else:
        headline = f"Data-quality validation status: {state.get('validation_status')}."

    answer_parts = [headline]
    if lines:
        answer_parts.append("Evidence:\n" + "\n".join(lines))

    review_items = payload.get("review_items", [])
    if review_items:
        answer_parts.append(
            "Review items are controlled exceptions, not automatic data errors: "
            + ", ".join(review_items)
            + "."
        )

    if sources:
        answer_parts.append("Approved rule sources: " + ", ".join(sources) + ".")

    answer_parts.append(
        "The agent does not auto-delete, impute, or update records; remediation remains a separate controlled step."
    )
    return "\n\n".join(answer_parts)


def optional_claude_synthesis(state: DQAgentState, deterministic_answer: str) -> str | None:
    """Optional Claude synthesis over already validated deterministic evidence."""

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

Approved DQ rule context:
{json.dumps(state.get('retrieved_rules', []), default=str)}

Deterministic DQ evidence:
{json.dumps(state.get('check_results', {}), default=str)}

Validated deterministic draft:
{deterministic_answer}

Write a concise data-quality validation answer using only the supplied rules and evidence.
Do not invent cleaning rules, thresholds, or root causes.
Do not recommend deleting or imputing records unless the approved rule explicitly supports it.
Preserve the distinction between a REVIEW flag and a FAIL condition.
""".strip()

    response = client.messages.create(
        model=model,
        max_tokens=700,
        temperature=0,
        system=(
            "You are a bounded banking data-quality assistant. Deterministic SQL/Python provides "
            "the facts; you explain validated evidence and approved rules."
        ),
        messages=[{"role": "user", "content": prompt}],
    )

    if not response.content:
        return None
    return getattr(response.content[0], "text", None)


def synthesis_node(state: DQAgentState) -> DQAgentState:
    deterministic_answer = deterministic_synthesis(state)

    try:
        llm_answer = optional_claude_synthesis(state, deterministic_answer)
    except Exception as exc:
        llm_answer = None
        trace = _trace(state, f"[LLM] Claude synthesis failed; deterministic fallback used: {type(exc).__name__}")
    else:
        mode = "Claude" if llm_answer else "deterministic"
        trace = _trace(state, f"[SYNTHESIS] mode={mode}")

    return {
        "final_answer": llm_answer or deterministic_answer,
        "trace": trace,
    }


def route_after_classify(state: DQAgentState) -> str:
    if state.get("intent") == "unsafe_request":
        return "safety_stop"
    if state.get("intent") == "unknown":
        return "fallback"
    return "retrieve_rules"


def build_graph():
    builder = StateGraph(DQAgentState)

    builder.add_node("classify", classify_node)
    builder.add_node("retrieve_rules", retrieve_rules_node)
    builder.add_node("execute_checks", execute_checks_node)
    builder.add_node("validate", validation_node)
    builder.add_node("synthesize", synthesis_node)
    builder.add_node("safety_stop", safety_stop_node)
    builder.add_node("fallback", fallback_node)

    builder.add_edge(START, "classify")
    builder.add_conditional_edges(
        "classify",
        route_after_classify,
        {
            "retrieve_rules": "retrieve_rules",
            "safety_stop": "safety_stop",
            "fallback": "fallback",
        },
    )
    builder.add_edge("retrieve_rules", "execute_checks")
    builder.add_edge("execute_checks", "validate")
    builder.add_edge("validate", "synthesize")
    builder.add_edge("synthesize", END)
    builder.add_edge("safety_stop", END)
    builder.add_edge("fallback", END)

    return builder.compile()


GRAPH = build_graph()


def run_agent(question: str) -> DQAgentState:
    initial: DQAgentState = {
        "question": question,
        "trace": ["[START] DQ validation request received"],
    }
    return GRAPH.invoke(initial)


def main() -> None:
    parser = argparse.ArgumentParser(description="Banking Data Quality & Validation Agent")
    parser.add_argument("question", nargs="+", help="Natural-language DQ validation question")
    parser.add_argument("--show-state", action="store_true", help="Print final structured state")
    args = parser.parse_args()

    question = " ".join(args.question)
    result = run_agent(question)

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
