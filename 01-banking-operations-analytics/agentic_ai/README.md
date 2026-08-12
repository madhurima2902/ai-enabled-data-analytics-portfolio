# Banking Operations Investigation Agent

## Purpose

This is a prototype agentic analytics assistant built on top of the Banking Operations Analytics project.

The goal is to let a user ask natural-language operational questions and receive an evidence-backed investigation using:

- PostgreSQL warehouse data
- SQL-based KPI analysis
- Local RAG over banking project knowledge documents
- LangGraph workflow orchestration
- Optional LLM-based response synthesis

This prototype is designed for portfolio and interview demonstration, not production banking use.

---

## What the Agent Can Investigate

Example questions:

- Why are digital channels creating more customer pain?
- Which channel has the highest complaint burden?
- Which team is driving SLA breaches?
- Which complaint category should operations prioritize?
- Which campaign type has weak conversion?

---

## Agent Workflow

```text
User question
→ classify operational intent
→ retrieve relevant KPI/SLA/complaint context from knowledge base
→ generate safe read-only SQL
→ validate SQL safety
→ execute SQL against PostgreSQL warehouse
→ summarize evidence, root cause, and recommended action
```

The workflow is implemented using LangGraph `StateGraph`.

---

## Folder Structure

```text
agentic_ai/
├── README.md
├── requirements.txt
├── .env.example
├── knowledge_base/
│   └── banking_operations_knowledge_base.md
├── sample_outputs/
│   └── sample_investigations.md
└── src/
    └── banking_ops_agent.py
```

---

## Setup

From the project root:

```bash
cd 01-banking-operations-analytics/agentic_ai
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Create a local `.env` file by copying `.env.example`.

Do not commit `.env` because it contains local database credentials and optional API keys.

---

## Environment Variables

```text
DB_HOST=localhost
DB_PORT=5432
DB_NAME=banking_analytics_db
DB_USER=your_postgres_user
DB_PASSWORD=your_postgres_password
OPENAI_API_KEY=optional_for_llm_summary
```

The agent can run without `OPENAI_API_KEY`; in that case, it produces a deterministic rule-based summary.

---

## Run

```bash
python src/banking_ops_agent.py "Why are digital channels creating more customer pain?"
```

Other examples:

```bash
python src/banking_ops_agent.py "Which team has the highest SLA breach rate?"
python src/banking_ops_agent.py "Which complaint categories should operations prioritize?"
python src/banking_ops_agent.py "Which campaign type has weak conversion?"
```

---

## Safety Design

The SQL guard allows only read-only analytical statements that start with `SELECT` or `WITH`.

It blocks common write or destructive operations such as:

- INSERT
- UPDATE
- DELETE
- DROP
- ALTER
- TRUNCATE
- CREATE
- GRANT
- REVOKE
- COPY

This keeps the assistant focused on analysis rather than database modification.

---

## Current Limitations

- Prototype only; not a production-grade banking system.
- Uses local markdown RAG instead of a persistent vector database.
- Uses template-based SQL for the first version to keep queries safe and explainable.
- Requires the PostgreSQL warehouse tables from the Banking Operations Analytics project to be available locally.
- Future version can add month-over-month analysis after February and March incremental loads are added.

---

## Portfolio Positioning

This prototype extends the banking analytics project from dashboard reporting into AI-assisted investigation.

It demonstrates how an analytics assistant can combine business context, KPI definitions, read-only SQL, operational data, and recommendation generation to support root-cause analysis.
