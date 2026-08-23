# Banking Operations Analytics

This project simulates a retail banking analytics environment using Python-generated operational data, PostgreSQL, SQL transformations, data quality checks, warehouse modeling, Power BI reporting, and bounded Agentic AI workflows.

## Business Objective

The goal is to analyze customer activity, transaction performance, product usage, complaint trends, campaign effectiveness, operational risk, and trusted-data readiness for a retail banking business.

## Core Components

- Python-generated banking source data
- PostgreSQL raw, staging, and warehouse layers
- SQL data quality checks and exception handling
- Fact and dimension warehouse modeling
- Business KPI queries
- Power BI dashboard
- Business KPI documentation
- Jan-Jun 2026 operational scenario data for agent and interview demonstrations
- Banking Operations Agent V2 for business investigation
- Banking Data Quality & Validation Agent for trusted-data readiness
- Project-level `CLAUDE.md` so both agents can be reviewed and evolved consistently through Claude Code

## Current V2 Data Scope

The current demo dataset covers January through June 2026.

- Raw transaction rows: 188,015
- Unique transactions: 188,000
- Complaints: 7,500
- Campaign interactions: 16,400
- SLA tickets: 11,200
- Customers: 10,000
- Accounts: 15,000

The additional 15 raw transaction rows are intentional duplicates used for data-quality testing.

## Designed Analytical Signals

The six-month dataset contains controlled business patterns for investigation:

- January: operational baseline
- February: Mobile Banking transaction failure incident
- March: partial recovery
- April: complaint-volume and resolution backlog
- May: Digital Banking Support SLA deterioration
- June: stronger campaign engagement with weaker conversion

## Data Quality and Trusted Reporting Flow

The project intentionally keeps a small number of raw-layer exceptions so data-quality handling can be demonstrated rather than hidden.

Current controlled transaction exceptions include:

- 15 duplicate transaction rows
- 40 failed transactions with non-zero fees
- 20 missing `channel_id` values
- 309 high-value transactions flagged for review

The implemented flow is:

`raw source data -> DQ detection / exception capture -> cleaned staging -> warehouse -> Power BI / agent tools`

Raw exceptions remain available for audit and agent investigation. Duplicate transactions are removed before the trusted warehouse, failed-with-fee values are corrected in the trusted staging layer, missing channel IDs are not invented, and legitimate high-value transactions remain in reporting data.

Final transaction reconciliation:

- Raw rows: 188,015
- Unique transaction IDs: 188,000
- Clean staging rows: 188,000
- Warehouse rows: 188,000
- Warehouse date coverage: 2026-01-01 through 2026-06-30

## Data Areas

- Customers
- Accounts
- Products
- Branches
- Channels
- Transactions
- Complaints
- Campaigns
- SLA Tickets

## Current Status

Power BI dashboard V1 is complete.

The Jan-Jun 2026 V2 data layer, controlled DQ scenarios, staging cleanup, DQ exception capture, and warehouse refresh have been completed and validated successfully.

Two bounded agent workflows are now implemented on top of the same governed data model and rules.

## Agent 1 — Banking Operations Agent V2

Location: `v2_practical_agent/`

Purpose: answer business-investigation questions after trusted data is available.

Implemented capabilities include:

- LangGraph state and conditional routing
- scoped Markdown RAG for KPI/business context
- controlled parameterized PostgreSQL tools
- KPI retrieval and period comparison
- transaction lookup and DQ summary
- deterministic read-only SQL validation
- evidence validation and abstention
- execution trace
- golden evaluation suite
- FastAPI/Swagger demo
- optional Claude synthesis over validated evidence

Example questions:

- What is Transaction Failure Rate?
- What was Mobile Banking failure rate in March 2026?
- Compare February and March Mobile Banking failure rate.
- Was March concerning for transaction failures in Mobile Banking?

Flow:

`User -> LangGraph route -> RAG and/or PostgreSQL tool -> validation -> evidence-backed synthesis -> answer + source + period + trace`

See `v2_practical_agent/README.md`.

## Agent 2 — Banking Data Quality & Validation Agent

Location: `data_quality_agent/`

Purpose: validate whether the raw/staging/warehouse pipeline is ready for trusted KPI reporting.

Implemented capabilities include:

- LangGraph routing to approved DQ checks
- shared governed DQ rules reused from the Banking Investigation Agent knowledge base
- raw/staging/warehouse row reconciliation
- duplicate transaction validation
- failed-transaction fee validation
- missing-channel validation
- high-value transaction review logic
- overall warehouse-readiness assessment
- deterministic read-only SQL guard
- PASS / REVIEW / FAIL evidence handling
- evaluation suite
- FastAPI/Swagger demo on a separate port
- optional Claude synthesis over validated DQ evidence

Example questions:

- Validate the current transaction load.
- Are there duplicate transaction IDs?
- Why do raw and warehouse row counts differ?
- Are any channel IDs missing?
- Should high-value transactions be removed?
- Is the warehouse ready for KPI reporting?

Flow:

`User -> LangGraph route -> shared DQ rule -> deterministic PostgreSQL checks -> PASS/REVIEW/FAIL -> evidence-backed readiness answer`

See `data_quality_agent/README.md`.

## Shared rule and Claude Code consistency

Both agents deliberately use one consistent business story:

- stable rules live in approved Markdown/documentation;
- changing values come from PostgreSQL tools;
- calculations and validation remain deterministic;
- agents do not receive unrestricted write authority;
- Claude may explain validated evidence but should not invent thresholds, root causes, or cleaning rules.

The project-level `CLAUDE.md` defines how Claude Code should understand, modify, test, and review both agents. It also tells Claude Code to reuse the same KPI/DQ sources instead of creating conflicting copies.

The intended engineering story is:

`Claude Code accelerates repository understanding and bounded delivery -> LangGraph orchestrates runtime workflows -> Markdown provides governed knowledge -> PostgreSQL/SQL/Python provide evidence -> deterministic validation controls correctness -> optional Claude synthesis explains the evidence.`

Production extensions such as vector embeddings, enterprise RBAC, durable checkpointing, MCP, centralized observability, scheduled DQ runs, and write-action HITL are documented as future design rather than represented as completed prototype features.

## Earlier Incremental-Load Design

A February-March incremental-load design exercise was completed before the scope changed to a six-month agent demo. That design is retained in `docs/v2_february_march_incremental_load_design.md` as an architecture exercise. For the interview-demo implementation, a controlled Jan-Jun full refresh was chosen to keep the data layer simple and spend more time on agent architecture, retrieval, data-quality validation, API tools, and observability.

## Power BI Dashboard

The Power BI dashboard provides a five-page business-facing view of banking operations performance.

### Dashboard Pages

1. Executive Overview
2. Channel Performance: Digital vs Non-Digital Analysis
3. Complaints & Customer Pain Analysis
4. SLA & Operations Performance Analysis
5. Campaign & Customer Engagement Analysis

### Executive Overview

![Executive Overview](assets/screenshots/powerbi/01_executive_overview.png)

### Channel Performance

![Channel Performance](assets/screenshots/powerbi/02_channel_performance.png)

### Complaints Analysis

![Complaints Analysis](assets/screenshots/powerbi/03_complaints_analysis.png)

### SLA Performance

![SLA Performance](assets/screenshots/powerbi/04_sla_performance.png)

### Campaign Performance

![Campaign Performance](assets/screenshots/powerbi/05_campaign_performance.png)

For detailed dashboard logic, KPIs, model assumptions, and interview explanation, see:

[Power BI Dashboard Notes](docs/15_powerbi_dashboard_notes.md)
