# Banking Operations Agent — Agent Contract

## Primary User

Banking operations analysts and managers who consume operational KPI reports and Power BI dashboards.

## Business Goal

Allow users to ask natural-language questions about approved Banking Operations KPIs, investigate Jan-Jun 2026 operational patterns, inspect selected transaction/DQ evidence, and receive an answer grounded in approved knowledge and trusted PostgreSQL data.

## Supported Question Types

- KPI definition and formula questions.
- KPI performance for a specified Jan-Jun 2026 period.
- Period-over-period KPI comparison.
- Mixed interpretation questions that combine approved KPI context with live warehouse evidence.
- Individual transaction lookup by transaction ID.
- Transaction data-quality exception summary and rule explanation.

## Allowed Actions

The agent may:

- retrieve approved Markdown knowledge;
- classify a supported investigation route;
- call approved read-only PostgreSQL tools;
- calculate approved KPIs using deterministic SQL/Python;
- compare periods and summarize evidence;
- return source, period, validation status, and execution trace;
- optionally use Claude to synthesize already validated evidence.

## Restricted Actions

The agent must not:

- create, update, or delete operational records;
- execute database writes or destructive SQL;
- expose database credentials or other secrets;
- invent KPI definitions, thresholds, or unsupported root causes;
- bypass application/database authorization controls;
- treat an analytical outlier as an error without supporting evidence.

## Expected Response

A supported response should contain, where applicable:

- concise finding or definition;
- supporting numerator/denominator or tool evidence;
- selected period and channel/segment;
- approved knowledge or PostgreSQL source;
- validation/evidence status;
- explicit abstention when evidence is insufficient.

## Correctness and Validation

Correctness is evaluated at multiple layers:

1. expected route/intent;
2. expected knowledge source/section for RAG questions;
3. approved tool selection and parameters;
4. deterministic SQL read-only validation;
5. KPI reconciliation against the trusted PostgreSQL warehouse and known Jan-Jun demo controls;
6. final-answer faithfulness to retrieved context and tool evidence.

The included evaluation suite uses golden routing/retrieval cases and database reconciliation controls.

## Human Approval Boundary

The current demo is intentionally read-only, so normal analytical requests do not require human approval. In a production extension, any consequential financial or record-changing action would require stronger authorization and risk-based human approval before execution.

## Prototype Boundary

This is an interview/portfolio prototype, not a production banking system. Vector search, enterprise RBAC, durable checkpoints, MCP, production observability platforms, and write-action HITL are design extensions rather than claims about the current implementation.
