from typing import Any, TypedDict


class AgentState(TypedDict, total=False):
    """Shared state passed between LangGraph nodes.

    The state is intentionally explicit so routing, retrieval, tool use,
    validation, and synthesis can be inspected independently during a demo.
    """

    run_id: str
    question: str
    intent: str
    knowledge_scope: list[str]
    retrieved_context: list[dict[str, Any]]
    tool_name: str
    tool_args: dict[str, Any]
    tool_result: dict[str, Any]
    evidence_status: str
    validation_status: str
    final_answer: str
    trace: list[str]
