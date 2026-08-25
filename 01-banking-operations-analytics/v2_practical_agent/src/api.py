from typing import Any

from fastapi import FastAPI
from pydantic import BaseModel, Field

try:
    from .agent import run_agent
except ImportError:  # Allows running from the src folder during local debugging.
    from agent import run_agent


app = FastAPI(
    title="Banking Operations Agent V2",
    description=(
        "Interview-demo API for a bounded LangGraph analytics agent using governed "
        "Markdown retrieval, controlled PostgreSQL tools, validation, and evidence-backed synthesis."
    ),
    version="2.0.0-demo",
)


class InvestigationRequest(BaseModel):
    question: str = Field(min_length=3, max_length=500)


class InvestigationResponse(BaseModel):
    run_id: str | None = None
    question: str
    intent: str
    answer: str
    validation_status: str | None = None
    evidence_status: str | None = None
    knowledge_sources: list[dict[str, Any]] = Field(default_factory=list)
    tool_name: str | None = None
    tool_result: dict[str, Any] = Field(default_factory=dict)
    trace: list[str] = Field(default_factory=list)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "banking-operations-agent-v2"}


@app.post("/investigate", response_model=InvestigationResponse)
def investigate(request: InvestigationRequest) -> InvestigationResponse:
    state = run_agent(request.question)

    knowledge_sources = [
        {
            "source": item.get("source"),
            "section": item.get("section"),
            "score": item.get("score"),
        }
        for item in state.get("retrieved_context", [])
    ]

    return InvestigationResponse(
        run_id=state.get("run_id"),
        question=request.question,
        intent=state.get("intent", "unknown"),
        answer=state.get("final_answer", "No answer returned."),
        validation_status=state.get("validation_status"),
        evidence_status=state.get("evidence_status"),
        knowledge_sources=knowledge_sources,
        tool_name=state.get("tool_name"),
        tool_result=state.get("tool_result", {}),
        trace=state.get("trace", []),
    )
