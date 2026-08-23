from typing import Any, TypedDict


class DQAgentState(TypedDict, total=False):
    """Shared LangGraph state for the bounded data-quality workflow."""

    question: str
    intent: str
    checks_requested: list[str]
    retrieved_rules: list[dict[str, Any]]
    check_results: dict[str, Any]
    evidence_status: str
    validation_status: str
    final_answer: str
    trace: list[str]
