# Claude Code Project Instructions — Banking Operations Analytics

## Project purpose

This repository is a retail-banking analytics and Agentic AI portfolio project. The Jan-Jun 2026 data pipeline is already validated and should be treated as the analytical source of truth for the interview demo.

Two bounded agents live in this project:

1. `v2_practical_agent/` — business investigation agent for KPI definitions, live KPI questions, period comparisons, transaction lookup, and mixed RAG + operational analysis.
2. `data_quality_agent/` — data-quality and validation agent for raw/staging/warehouse reconciliation, duplicate checks, missing-channel checks, failed-fee validation, high-value review, and trusted-warehouse readiness.

The two agents must tell one consistent story. Do not create duplicate or conflicting KPI/DQ rules.

## Shared business story

The governed data flow is:

`raw source -> detect/record DQ exceptions -> clean staging -> trusted warehouse -> Power BI / agent tools`

The trusted warehouse is used for normal KPI analysis. Raw and DQ exception layers remain available for audit and data-quality investigation.

Controlled Jan-Jun 2026 transaction checks currently include:

- raw rows: 188,015
- unique transaction IDs: 188,000
- trusted staging rows: 188,000
- warehouse rows: 188,000
- duplicate transaction rows: 15
- failed transactions with non-zero raw fee: 40
- missing channel IDs: 20
- high-value transactions above 500,000: 309

Do not hard-code these values into business logic. They may appear in evaluation fixtures only as known demo controls.

## Knowledge sources

Use these files as approved human-reviewable knowledge:

- `v2_practical_agent/knowledge/kpi_definitions.md`
- `v2_practical_agent/knowledge/business_rules.md`
- `v2_practical_agent/knowledge/data_dictionary.md`
- `v2_practical_agent/knowledge/investigation_playbook.md`
- `docs/8_staging_layer_notes.md`
- `docs/10_fact_tables_notes.md`

The Data Quality Agent intentionally reuses the shared `business_rules.md` rather than maintaining a second copy of the same DQ rules.

## Engineering boundaries

- Keep database access read-only inside both agents.
- Do not add unrestricted LLM-generated SQL.
- Calculations, reconciliation, validation, authorization checks, and write restrictions remain deterministic.
- Claude may assist with reasoning/synthesis, but it must use supplied evidence and must not invent thresholds or root causes.
- Never expose or commit `.env`, database passwords, API keys, tokens, or other secrets.
- Do not modify the synthetic source-data design, warehouse tables, or established KPI logic unless the task explicitly requires it.
- Do not silently auto-delete, impute, or correct data-quality exceptions. Detection and recommendation are separate from remediation.

## Claude Code workflow expected for changes

For non-trivial changes, use this sequence:

1. Understand the requested business behavior.
2. Trace the relevant files/functions before editing.
3. Explain the proposed change and affected files.
4. Make the smallest bounded change.
5. Run the relevant evaluation suite.
6. Review the diff for functional correctness, security, performance, scalability, and maintainability.
7. Report what changed, what was tested, and any remaining production gap.

Do not treat generated code as correct simply because it runs.

## Commands — Banking Investigation Agent

From `01-banking-operations-analytics/v2_practical_agent`:

```powershell
.\.venv\Scripts\python.exe -m src.evaluation
.\.venv\Scripts\python.exe -m src.agent "Compare February and March Mobile Banking failure rate."
.\.venv\Scripts\python.exe -m uvicorn src.api:app --reload --port 8000
```

Expected evaluation summary: `Passed 4/4 evaluation groups` when PostgreSQL credentials and the Jan-Jun warehouse are available.

## Commands — Data Quality Agent

From `01-banking-operations-analytics/data_quality_agent`:

```powershell
.\.venv\Scripts\python.exe -m src.evaluation
.\.venv\Scripts\python.exe -m src.agent "Validate the current transaction load."
.\.venv\Scripts\python.exe -m uvicorn src.api:app --reload --port 8001
```

## Review checklist

Before accepting a Claude-assisted change, check:

- Functional correctness: does behavior match the business rule and expected data grain?
- Security: are secrets protected and are database/tool capabilities least privilege/read-only?
- Performance: are queries bounded and reasonably efficient for the demo scope?
- Scalability: is the design modular enough to replace local components with production services later?
- Maintainability: are business rules centralized, functions narrow, traces explainable, and tests/evals updated?

## Interview positioning

The correct story is not "Claude does everything." The correct story is:

`Claude Code accelerates engineering work -> LangGraph orchestrates bounded runtime flows -> Markdown provides governed knowledge -> PostgreSQL/Python/SQL provide deterministic evidence -> validation controls correctness -> optional Claude synthesis explains validated evidence.`
