# Banking Operations Agent V2 — Interview Demo

## Purpose

This is a bounded Agentic AI investigation layer on top of the Jan-Jun 2026 Banking Operations Analytics project.

The business problem is the step after a dashboard identifies an issue: an analyst still has to locate the KPI definition, retrieve the correct operational evidence, compare periods, validate the result, and explain what the evidence supports.

The agent demonstrates that workflow without giving an LLM unrestricted database authority.

## Implemented Architecture

```text
User question
    |
    v
LangGraph bounded router + AgentState
    |
    +----------------------+-----------------------+
    |                      |                       |
Knowledge question     Live-data question      Mixed investigation
    |                      |                       |
Scoped Markdown RAG    Controlled DB tool      RAG + controlled DB tool
    |                      |                       |
    +----------------------+-----------------------+
                           |
                    SQL safety validation
                           |
                  PostgreSQL trusted warehouse
                           |
                    Evidence validation
                           |
             Deterministic / optional Claude synthesis
                           |
              Answer + source + period + trace
```

## What Is Actually Implemented

- LangGraph `StateGraph` workflow with explicit branching.
- Structured `AgentState` for question, intent, knowledge context, tool request, tool result, validation, final answer, and trace.
- Governed Markdown knowledge base:
  - KPI definitions
  - business/data-quality rules
  - data dictionary
  - investigation playbook
- Scoped lexical retrieval with source, section, and retrieval-score metadata.
- Controlled PostgreSQL tools for approved KPI metrics, period comparisons, transaction lookup, and DQ exception summary.
- Deterministic read-only SQL validation before every query.
- Parameterized SQL rather than LLM-generated unrestricted SQL.
- Evidence validation and explicit abstention/error paths.
- Per-run trace events for routing, retrieval, tool execution, validation, and synthesis.
- Golden evaluation script covering routing, RAG retrieval, SQL guardrails, KPI reconciliation, and DQ controls.
- Thin FastAPI interface for an interviewer-friendly `/docs` demo.
- Optional Claude synthesis when `USE_LLM=true`; deterministic synthesis keeps the demo functional without an API key.

## Deliberate Prototype Boundaries

The following are production-design extensions, not claims about the current prototype:

- vector database / embeddings / reranking;
- production authentication and RBAC;
- durable LangGraph checkpoint persistence;
- MCP server;
- human-in-the-loop approval for write actions;
- production tracing platform and centralized monitoring;
- unrestricted autonomous SQL generation.

These are intentionally separated from the working interview prototype so the implemented scope remains explainable and safe.

## Folder Structure

```text
v2_practical_agent/
├── .env.example
├── README.md
├── requirements.txt
├── docs/
│   └── agent_contract.md
├── knowledge/
│   ├── business_rules.md
│   ├── data_dictionary.md
│   ├── investigation_playbook.md
│   └── kpi_definitions.md
└── src/
    ├── __init__.py
    ├── agent.py
    ├── api.py
    ├── db_tools.py
    ├── evaluation.py
    ├── knowledge_loader.py
    ├── retriever.py
    └── state.py
```

## Setup

From `01-banking-operations-analytics`:

```powershell
cd v2_practical_agent
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `.env` and set the local PostgreSQL username/password for `banking_analytics_db`.

The Jan-Jun staging and warehouse build must already be loaded locally.

## Pre-Demo Validation

Run the evaluation suite first:

```powershell
python -m src.evaluation
```

Expected groups:

```text
PASS | routing golden cases
PASS | RAG retrieval golden cases
PASS | read-only SQL guard
PASS | run_id request correlation
PASS | knowledge-route evidence validation
PASS | PostgreSQL reconciliation controls
Passed 6/6 evaluation groups
```

The database reconciliation confirms the established synthetic-data demo signals, including approximately:

- February Mobile Banking transaction failure rate: 19.52%
- March Mobile Banking transaction failure rate: 9.26%
- DQ exceptions: duplicate ID 15, failed-with-fee 40, missing channel 20, high-value 309

## Terminal Demo

### 1. RAG-only question

```powershell
python -m src.agent "What is Transaction Failure Rate?"
```

Expected route: `knowledge_question` -> Markdown RAG -> approved KPI definition.

### 2. Live operational KPI

```powershell
python -m src.agent "What was Mobile Banking failure rate in March 2026?"
```

Expected route: `operational_metric` -> PostgreSQL tool -> validation -> evidence-backed answer.

### 3. Period comparison

```powershell
python -m src.agent "Compare February and March Mobile Banking failure rate."
```

Expected evidence: February around 19.52%, March around 9.26%, with the percentage-point movement calculated by code.

### 4. Mixed RAG + live evidence

```powershell
python -m src.agent "Was March concerning for transaction failures in Mobile Banking?"
```

The workflow retrieves approved KPI/investigation context and compares February with March. Because no approved formal concern threshold is defined, the agent must not invent one.

### 5. Safety control

```powershell
python -m src.agent "DELETE FROM warehouse.fact_transactions"
```

Expected route: guardrail -> request blocked; no database write is executed.

## FastAPI / Swagger Demo

Start the service:

```powershell
python -m uvicorn src.api:app --reload
```

Open:

```text
http://127.0.0.1:8000/docs
```

Use `POST /investigate` with:

```json
{
  "question": "Compare February and March Mobile Banking failure rate."
}
```

The response exposes the final answer plus intent, tool, evidence, validation status, knowledge sources, and execution trace. This makes the agent workflow inspectable rather than presenting only an LLM paragraph.

## Optional Claude Synthesis

The core demo does not require an LLM key. Deterministic code calculates and validates facts, and a deterministic fallback formats the answer.

To demonstrate Claude as the synthesis model, set:

```text
USE_LLM=true
ANTHROPIC_API_KEY=<local secret>
ANTHROPIC_MODEL=<approved Claude model name>
```

Secrets belong only in local `.env`; do not commit them.

The model does not calculate the KPI or connect directly to PostgreSQL. It receives already retrieved knowledge and validated tool evidence and is instructed not to invent thresholds or root causes.

## Interview Positioning

A concise and accurate description is:

> I built a bounded Banking Operations investigation agent on top of my PostgreSQL and Power BI analytics platform. LangGraph manages the workflow and state. Stable KPI definitions and business rules are retrieved from governed Markdown knowledge, while current operational metrics come from controlled read-only PostgreSQL tools. Deterministic code owns calculations, SQL safety, and evidence validation. The final synthesis can be deterministic or use Claude, but the model is not given unrestricted database authority.

For production, I would add semantic/vector retrieval, enterprise authentication/RBAC, durable checkpoints where needed, stronger tracing/evaluation infrastructure, and risk-based HITL for consequential actions.
