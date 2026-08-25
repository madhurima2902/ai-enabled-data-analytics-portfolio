# AI-Assisted Development Notes

## 1. Purpose

Claude Cowork was used as an AI development partner for Banking Operations Agent V2. Claude assisted with reviewing the existing implementation and making bounded, scoped code changes under human direction and review.

## 2. Scope Reviewed

Before making any change, Claude inspected:

- `README.md`
- `docs/agent_contract.md`
- `src/agent.py`
- `src/state.py`
- `src/retriever.py`
- `src/db_tools.py`
- `src/api.py`
- `src/evaluation.py`
- the approved knowledge files (`knowledge/*.md`)

## 3. Changes Made

- Added request-level `run_id` correlation using Python's standard `uuid` module, so a single request can be traced through the LangGraph workflow, the trace log, and the FastAPI response.
- Added explicit validation for knowledge-only RAG routes. Previously, `validation_status` and `evidence_status` were left unset for RAG-only questions; the workflow now routes these questions through the existing validation node.
- Added explicit abstention behavior when approved knowledge evidence is unavailable: if no approved knowledge chunk is retrieved, the agent reports `evidence_status = INSUFFICIENT` and returns an abstention message rather than an invented answer.
- Extended the evaluation suite from 4 groups to 6 groups, adding coverage for `run_id` correlation and knowledge-route validation.

## 4. Human Validation

- Changes were reviewed through `git diff` before acceptance.
- The evaluation suite was executed against the real local PostgreSQL warehouse.
- All 6 evaluation groups passed.
- Supported and unsupported RAG questions were manually tested to confirm correct validation and abstention behavior.

## 5. Boundaries

- Claude did not change KPI formulas.
- Claude did not modify warehouse data or schema.
- Claude did not receive database credentials.
- Database access remains read-only.
- Claude did not commit or merge the changes.

## 6. Production Extensions Not Currently Implemented

The following remain design extensions rather than implemented capabilities:

- vector/hybrid RAG
- production authentication/RBAC
- durable LangGraph checkpoints
- MCP
- production human-in-the-loop (HITL) approval
- enterprise observability platform

## Note on Scope of Claude's Role

Claude's role was limited to code review, bounded implementation of developer-specified changes, and documentation support. Claude did not independently design, approve, or validate the underlying banking business logic, KPI definitions, or data-quality rules; those remain the responsibility of the project owner and the approved knowledge sources.
