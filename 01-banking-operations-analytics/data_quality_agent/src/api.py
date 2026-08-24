from typing import Any

from fastapi import FastAPI
from pydantic import BaseModel, Field

try:
    from .agent import run_agent
except ImportError:
    from agent import run_agent


app = FastAPI(
    title="Banking Data Quality & Validation Agent",
    description=(
        "Interview-demo API for a bounded LangGraph data-quality agent using shared governed rules, "
        "deterministic read-only PostgreSQL checks, evidence validation, and optional Claude synthesis."
    ),
    version="1.0.0-demo",
)


class ValidationRequest(BaseModel):
    question: str = Field(min_length=3, max_length=500)


class ValidationResponse(BaseModel):
    question: str
    run_id: str | None = None
    intent: str
    answer: str
    validation_status: str | None = None
    evidence_status: str | None = None
    checks_requested: list[str] = []
    rule_sources: list[dict[str, Any]] = []
    check_results: dict[str, Any] = {}
    trace: list[str] = []


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "banking-data-quality-agent"}


@app.post("/validate", response_model=ValidationResponse)
def validate(request: ValidationRequest) -> ValidationResponse:
    state = run_agent(request.question)

    rule_sources = [
        {
            "source": item.get("source"),
            "section": item.get("section"),
            "check": item.get("check"),
        }
        for item in state.get("retrieved_rules", [])
    ]

    return ValidationResponse(
        question=request.question,
        run_id=state.get("run_id"),
        intent=state.get("intent", "unknown"),
        answer=state.get("final_answer", "No answer returned."),
        validation_status=state.get("validation_status"),
        evidence_status=state.get("evidence_status"),
        checks_requested=state.get("checks_requested", []),
        rule_sources=rule_sources,
        check_results=state.get("check_results", {}),
        trace=state.get("trace", []),
    )
