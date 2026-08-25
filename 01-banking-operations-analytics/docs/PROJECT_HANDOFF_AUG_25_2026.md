# Banking Operations Analytics V2 — Project Handoff

**Snapshot date:** 2026-08-25  
**Purpose:** Preserve the current project state, important decisions, validated numbers, superseded work, and next steps so the Banking V2 project can be continued without relying on prior chat history.

> This is a point-in-time handoff. For current code behavior, the repository files and latest branch history remain authoritative.

---

## 1. Authoritative Working Branch

Current Banking working branch:

`feature/agent-v2-practical`

Current branch HEAD at this snapshot:

`b827057b01ed17f1a3e97a242d29ab19f381aac0`

Latest commit at this snapshot:

`Evaluate evidence-based derived metric analysis`

Branch position versus `main` at this snapshot:

- 65 commits ahead of `main`
- 16 commits behind `main`
- no open Banking PR to `main`

Important: PR #3 and PR #4 were merged into `feature/agent-v2-practical`, not into `main`.

The older branch `feature/banking-v2-february-march` still exists but should not be treated as the latest source of truth. Its useful work was carried forward into the broader Jan-Jun implementation and agent branch.

---

## 2. Project Evolution — What Happened and Why

The project evolved through the following stages:

1. Banking Operations Analytics V1 was completed with PostgreSQL, SQL transformations, a warehouse model, data-quality checks, and a five-page Power BI dashboard.
2. V2 began with a January baseline and focus-selection exercise.
3. January analysis selected the focus population:
   - Channel: **Mobile Banking**
   - Product: **Savings Account**
   - Customer segment: **Mass**
4. An initial February-March incremental-load design was created.
5. During review, the original synthetic data was judged too clean for a realistic DQ/interview story.
6. The design was expanded to a controlled **January-June 2026** scenario with explicit business signals and known DQ exceptions.
7. For the working interview demo, the implementation intentionally switched from the earlier true incremental-load design to a controlled Jan-Jun full-refresh workflow.
8. A Banking Operations Investigation Agent was then built on top of the trusted warehouse.
9. A companion Banking Data Quality & Validation Agent was added.
10. Both agents were hardened with better traceability, rule grounding, abstention, evaluation, and bounded Claude-assisted development.
11. The Banking Investigation Agent was later expanded with basic aggregates, multi-month KPI comparisons, approved derived metrics, and deterministic evidence-based trend interpretation.

The earlier incremental-load design is retained as an architecture/interview discussion artifact rather than deleted.

---

## 3. January Baseline — Historical Milestone

January baseline work was completed and merged through PR #1.

Key January transaction baseline:

- Total January transactions: **25,000**
- Success: **23,025**
- Failed: **1,483**
- Reversed: **492**
- Overall failure rate: **5.93%**
- Distinct January customers: **1,800**

Mobile Banking January baseline:

- Transactions: **4,210**
- Failed: **244**
- Reversed: **91**

Selected focus population:

**Mobile Banking × Savings Account × Mass**

January focus-group evidence:

- distinct customers: **803**
- transactions: **983**
- failed transactions: **50**
- reversed transactions: **19**
- affected transactions: **69**
- share of Mobile Banking volume: **23.35%**
- share of Mobile Banking failures: **20.49%**
- total transaction amount: **37,805,508.85**
- affected transaction amount: **2,695,401.77**
- complaints: **43**
- complaints per 1,000 transactions: **43.74**
- resolved complaints: **28**
- average resolution days: **6.18**
- SLA tickets: **97**
- SLA breaches: **21**
- SLA breach rate: **21.65%**

Why this group was selected:

- highest transaction volume among Mobile Banking product/segment cells
- highest affected-transaction count
- highest failed-transaction count
- highest complaint count
- highest SLA-ticket volume
- broad enough operational exposure to support a credible investigation story

Important limitation retained from the January analysis:

- complaints are not directly linked to individual transactions
- complaint metrics are aggregate operational association, not proof of transaction-level causality
- DQ defects must never be presented as the cause of business deterioration unless evidence explicitly supports that claim

---

## 4. Earlier February-March Incremental-Load Design

File retained:

`docs/v2_february_march_incremental_load_design.md`

This document records:

- Phase 1 audit of the January pipeline
- Phase 2 February-March incremental-load design
- same-schema monthly input design
- unique ID continuation
- controlled DQ defect design
- raw -> staging -> warehouse architecture
- duplicate/reject reconciliation
- idempotency considerations

Current status of that design:

**Superseded for the interview-demo implementation, but retained as a valid architecture exercise.**

Reason for the scope change:

The project moved to a Jan-Jun controlled full refresh so more time could be spent on agent architecture, retrieval, deterministic validation, DQ reasoning, API exposure, traceability, and interview demonstration.

Do not describe the current working pipeline as a production incremental-load implementation.

---

## 5. Current Jan-Jun 2026 Data Scope

Current validated demo scale:

- customers: **10,000**
- accounts: **15,000**
- products: **7**
- branches: **20**
- channels: **6**
- raw transaction rows: **188,015**
- unique transaction IDs: **188,000**
- clean staging transaction rows: **188,000**
- warehouse transaction rows: **188,000**
- complaints: **7,500**
- campaigns: **16,400**
- SLA tickets: **11,200**
- warehouse transaction date coverage: **2026-01-01 through 2026-06-30**

Monthly transaction counts:

- January: **25,000**
- February: **28,000**
- March: **30,000**
- April: **32,007**
- May: **35,008**
- June: **38,000**

The excess raw rows in April/May contribute to the controlled duplicate scenario; the trusted warehouse reconciles to 188,000 unique transaction IDs.

---

## 6. Designed Monthly Business Signals

The current six-month business story is deliberate and controlled:

### January
Operational baseline.

### February
Mobile Banking transaction-failure incident.

Key failure-rate examples:

- Jan Mobile Banking: **6.39%**
- Feb Mobile Banking: **19.52%**
- Mar Mobile Banking: **9.26%**

Internet Banking comparison:

- Jan: **5.96%**
- Feb: **9.51%**
- Mar: **5.87%**

Interpretation: February deterioration is concentrated more strongly in Mobile Banking, with March showing partial recovery rather than a perfect reset.

### April
Complaint-volume and resolution backlog.

Monthly complaints:

- Jan: 900
- Feb: 1,250
- Mar: 1,050
- Apr: **1,650**
- May: 1,300
- Jun: 1,350

Average resolution days:

- Jan: 5.76
- Feb: 5.43
- Mar: 5.42
- Apr: **8.24**
- May: 5.63
- Jun: 5.60

### May
Digital Banking Support SLA deterioration.

Known demonstration point:

- resolved Digital Banking Support tickets: **271**
- breach rate: **44.65%**

### June
Higher engagement but weaker campaign conversion.

Campaign summary:

- Jan sent 2,200 / engagement 52.77% / conversion 7.41%
- Feb sent 2,400 / engagement 54.79% / conversion 7.75%
- Mar sent 2,600 / engagement 52.81% / conversion 8.96%
- Apr sent 2,800 / engagement 54.04% / conversion 8.11%
- May sent 3,000 / engagement 53.83% / conversion 7.83%
- Jun sent 3,400 / engagement **55.53%** / conversion **5.03%**

---

## 7. Controlled Data-Quality Story

The current raw layer intentionally contains a small number of known exceptions so the project demonstrates detection, handling, and trusted reporting rather than an unrealistically perfect dataset.

Controlled transaction exceptions:

- **15** duplicate transaction rows
- **40** failed transactions with non-zero fees
- **20** missing `channel_id` values
- **309** high-value transactions flagged for review

Handling rules:

### Duplicate transaction IDs

- detected in raw
- captured as exceptions
- removed before trusted warehouse
- warehouse must contain no duplicate `transaction_id`

### Failed transactions with non-zero fee

- detected and captured
- corrected in trusted staging
- no failed transaction with non-zero fee should remain in trusted warehouse

### Missing channel ID

- flagged for review
- channel must not be invented
- known missing values are preserved under controlled reporting treatment

### High-value transactions

- flagged for review
- not automatically deleted or treated as invalid
- plausible records remain in trusted reporting data

Core trusted-data flow:

`raw source -> DQ detection / exception capture -> clean staging -> warehouse -> Power BI / agents`

Current expected warehouse-readiness position:

`READY_WITH_KNOWN_EXCEPTIONS`

---

## 8. Key Data-Layer Files

Important current files on the Banking feature branch include:

- `scripts/generators/generate_jan_jun_2026_data.py`
- `scripts/generators/validate_jan_jun_2026_data.py`
- `scripts/loaders/load_raw_csvs.py`
- `scripts/loaders/build_jan_jun_warehouse.py`
- `sql/03_staging_tables/03_transaction_dq_exceptions_and_cleaning.sql`
- `docs/8_staging_layer_notes.md`
- `README.md`
- `docs/v2_february_march_incremental_load_design.md`

These files represent the implemented Jan-Jun data path and the retained earlier incremental-load design.

---

## 9. Power BI Status

Power BI V1 is complete and remains part of the project platform.

Five dashboard pages:

1. Executive Overview
2. Channel Performance: Digital vs Non-Digital Analysis
3. Complaints & Customer Pain Analysis
4. SLA & Operations Performance Analysis
5. Campaign & Customer Engagement Analysis

The agent work is built on top of the same governed analytics model rather than replacing Power BI.

---

## 10. Banking Operations Investigation Agent V2

Location:

`v2_practical_agent/`

Purpose:

Answer business-investigation questions after trusted data is available.

Current implemented architecture:

`User -> LangGraph route -> governed Markdown RAG and/or controlled PostgreSQL tool -> SQL safety validation -> trusted warehouse -> evidence validation -> deterministic or optional Claude synthesis -> answer + source + period + trace`

Implemented capabilities include:

- LangGraph `StateGraph`
- structured `AgentState`
- governed Markdown knowledge base
- scoped lexical retrieval
- controlled read-only PostgreSQL tools
- parameterized SQL
- KPI retrieval
- period comparison
- multi-month KPI comparison
- transaction lookup
- DQ summary lookup
- basic analyst-style aggregates
- approved derived metrics
- deterministic evidence validation
- explicit abstention/error paths
- request-level `run_id`
- execution trace
- FastAPI / Swagger demo
- optional Claude synthesis over validated evidence

Current production-boundary principle:

The LLM does not receive unrestricted database authority. Calculations, SQL safety, and evidence validation remain deterministic.

---

## 11. Investigation Agent — Multi-Month KPI Upgrade

The router now recognizes campaign conversion wording such as:

- campaign success
- campaign successful
- campaign conversion
- converted

and maps it to:

`campaign_conversion_rate`

Questions with three or more explicitly named months are routed to:

`compare_kpi_periods`

Example supported intent:

`Compare January, March and June campaign success data`

Conceptual route:

- KPI: `campaign_conversion_rate`
- months: `[1, 3, 6]`
- tool: `compare_kpi_periods`

---

## 12. Investigation Agent — Basic Aggregates

Controlled aggregate layer supports:

- COUNT
- SUM
- AVERAGE

Approved entities include:

- transactions
- complaints
- campaigns
- SLA tickets
- customers
- accounts
- products
- branches
- channels

The model/router may request only approved entities and measures. Arbitrary table/column access is not allowed.

Examples of approved measures include:

- transaction amount
- transaction fee amount
- complaint resolution days
- campaign converted count
- campaign engaged count
- campaign sent count
- SLA target hours
- customer age
- account balance
- credit limit
- interest rate

---

## 13. Investigation Agent — Approved Derived Metric

Current approved derived metric:

**Average Transactions per Active Customer**

Definition:

`monthly transaction count / distinct customers with at least one transaction in that month`

Current derived-metric code performs deterministic evidence analysis including:

- first vs last value
- sequential period movement
- overall direction
- metric percentage change
- transaction-volume percentage change
- active-customer-base percentage change
- relative numerator/denominator growth pattern

Important interpretation boundary:

The agent may describe observed movement, but must not label the metric good, bad, acceptable, or concerning unless an approved target/threshold exists.

Latest branch work specifically added and evaluated this evidence-based interpretation behavior.

---

## 14. Banking Data Quality & Validation Agent

Location:

`data_quality_agent/`

Purpose:

Validate whether raw, staging, exception, and warehouse layers are consistent enough for trusted KPI reporting.

Conceptual distinction:

- Data Quality Agent: **Can I trust the data?**
- Banking Investigation Agent: **What does the trusted data tell me?**

Implemented DQ checks include:

1. raw/staging/warehouse reconciliation
2. duplicate transaction validation
3. failed-transaction fee validation
4. missing-channel validation
5. high-value transaction review logic
6. overall warehouse readiness

Possible readiness outcomes:

- `READY`
- `READY_WITH_KNOWN_EXCEPTIONS`
- `NOT_READY`

Current expected result:

`READY_WITH_KNOWN_EXCEPTIONS`

---

## 15. DQ Agent — Rule-Grounding Hardening

The DQ agent does not maintain a second conflicting DQ rule set. It reuses the governed sources used by the broader Banking project.

Important hardening change:

`retrieve rules -> validate rule coverage -> execute deterministic checks only when required approved rules exist`

If a required rule is missing, the workflow should abstain rather than invent a cleaning policy.

Missing-rule outcome:

- `validation_status = ABSTAINED_MISSING_RULE`
- `evidence_status = INSUFFICIENT`

Rule grounding and database evidence remain separate state concepts.

---

## 16. Claude-Assisted Hardening PRs

### PR #3

Title:

`Harden Banking Agent traceability and RAG validation with Claude`

Merged into:

`feature/agent-v2-practical`

Key changes:

- request-level `run_id`
- API run correlation
- knowledge-route evidence validation
- abstention when approved knowledge is unavailable
- evaluation expansion
- factual AI-assisted development notes

Reported validation:

**6/6 evaluation groups passed**

### PR #4

Title:

`Harden Data Quality Agent traceability and rule grounding with Claude`

Merged into:

`feature/agent-v2-practical`

Key changes:

- request-level `run_id`
- approved-rule coverage gate
- missing-rule abstention path
- separation of rule grounding and deterministic evidence
- evaluation expansion

Reported validation:

**8/8 evaluation groups passed**

---

## 17. Shared Agent Design Principle

The project should be described consistently as:

`Claude Code accelerates bounded engineering delivery -> LangGraph orchestrates runtime workflow -> governed Markdown provides stable rules/definitions -> PostgreSQL/SQL/Python provide current evidence and calculations -> deterministic validation controls correctness -> optional Claude synthesis explains already validated evidence`

Stable definitions should live in governed documentation.

Changing operational values should come from PostgreSQL tools.

The LLM should not invent:

- KPI formulas
- business thresholds
- root causes
- cleaning rules
- unsupported facts

---

## 18. Current Prototype Boundaries — Do Not Overclaim

Do not describe the following as already implemented:

- vector database / embeddings / reranking
- enterprise authentication/RBAC
- MCP server
- durable LangGraph checkpoint persistence
- centralized production observability platform
- unrestricted natural-language-to-SQL
- automatic remediation/write-back
- scheduled/event-triggered DQ validation
- enterprise HITL approval workflow
- metadata-driven dynamic rule authoring

These remain production extensions or future architecture discussions.

---

## 19. Current Git / Repository Risk

At this handoff snapshot, `feature/agent-v2-practical` contains the current Banking solution but has diverged substantially from `main`.

Therefore the next major repository step should not be an unreviewed direct merge.

Recommended sequence:

1. review the complete Banking feature branch
2. reconcile/sync with current `main`
3. ensure unrelated `main` changes are preserved
4. run the full Banking Investigation Agent evaluation suite
5. run the full DQ Agent evaluation suite
6. manually test representative terminal/API demo questions
7. inspect the final branch diff
8. open one controlled Banking PR to `main`
9. merge only after validation
10. verify merged Banking files on `main`

Do not separately merge the old `feature/banking-v2-february-march` branch unless a future review proves it contains unique required work not already carried into the current branch.

---

## 20. Representative Demo Questions

### Banking Investigation Agent

- What is Transaction Failure Rate?
- What was Mobile Banking failure rate in March 2026?
- Compare February and March Mobile Banking failure rate.
- Was March concerning for transaction failures in Mobile Banking?
- Compare January, March and June campaign success data.
- What was the average number of transactions per active customer by month?
- Show the trend and explain whether transaction volume or active-customer growth drove it.

### Data Quality Agent

- Validate the current transaction load.
- Are there duplicate transaction IDs?
- Why do raw and warehouse row counts differ?
- Are any channel IDs missing?
- Should high-value transactions be removed?
- Is the warehouse ready for KPI reporting?

### Safety demonstration

- `DELETE FROM warehouse.fact_transactions`

Expected outcome: request is blocked; no database write is executed.

---

## 21. High-Level Interview Narrative

A concise current project description:

> I built a retail-banking analytics platform using Python-generated operational data, PostgreSQL raw/staging/warehouse layers, controlled data-quality exceptions, SQL validation, and Power BI. I then added two bounded LangGraph agents. The Banking Investigation Agent answers business questions using governed Markdown knowledge and controlled read-only PostgreSQL tools. The Data Quality Agent validates whether the data is ready for trusted reporting before those KPIs are used. Deterministic code owns calculations, SQL safety, DQ reconciliation, and evidence validation. Claude is optional for explanation/synthesis after evidence has been validated, rather than being given unrestricted authority over the database.

Production extensions can be discussed separately without claiming they are already implemented.

---

## 22. Important Historical Decisions to Preserve

These decisions came from earlier project work and should not be casually reversed:

- analysis must follow trusted data preparation/validation; do not analyze an unvalidated load
- the earlier incremental-load design remains valuable, but the current demo implementation is Jan-Jun full refresh
- controlled DQ exceptions are intentional and must remain explainable
- do not silently invent missing channel IDs
- do not automatically delete high-value transactions
- do not present DQ exceptions as the cause of business incidents without evidence
- aggregate complaint/SLA association does not prove direct transaction causality
- use approved business IDs/joins consistently where appropriate
- stable KPI definitions belong in governed documentation
- live metric values belong in deterministic tools/database evidence
- the agent should abstain when required knowledge or evidence is missing
- write operations remain outside the current prototype authority

---

## 23. Suggested Resume Point for a New Chat/Work Session

Use this as the starting context:

> Current working branch is `feature/agent-v2-practical`. Banking Operations Analytics V2 now covers Jan-Jun 2026 with controlled business signals and DQ exceptions, a validated trusted PostgreSQL warehouse, completed Power BI V1, a bounded Banking Operations Investigation Agent, and a bounded Banking Data Quality & Validation Agent. The Investigation Agent supports governed Markdown RAG, controlled PostgreSQL KPI tools, multi-month comparisons, approved aggregates, an approved derived metric with evidence-based trend analysis, run-level tracing, abstention, evaluation, FastAPI, and optional Claude synthesis. The DQ Agent validates raw/staging/warehouse reconciliation, duplicates, failed-with-fee issues, missing channels, high-value review items, and overall readiness, with approved-rule coverage and rule-gap abstention. The branch is ahead of and behind `main`, so the next major engineering checkpoint is branch reconciliation, full evaluation, final diff review, and then one controlled Banking PR to `main`.

---

## 24. Key Files to Read First in a Future Session

Recommended reading order:

1. `README.md`
2. `docs/PROJECT_HANDOFF_AUG_25_2026.md`
3. `docs/8_staging_layer_notes.md`
4. `docs/v2_february_march_incremental_load_design.md`
5. `v2_practical_agent/README.md`
6. `v2_practical_agent/docs/agent_contract.md`
7. `v2_practical_agent/knowledge/kpi_definitions.md`
8. `v2_practical_agent/knowledge/business_rules.md`
9. `v2_practical_agent/src/agent.py`
10. `v2_practical_agent/src/aggregate_tools.py`
11. `v2_practical_agent/src/derived_metrics.py`
12. `v2_practical_agent/src/evaluation.py`
13. `data_quality_agent/README.md`
14. `data_quality_agent/docs/agent_contract.md`
15. `data_quality_agent/src/agent.py`
16. `data_quality_agent/src/dq_tools.py`
17. `data_quality_agent/src/evaluation.py`

---

## 25. Final Status at Handoff

Completed:

- Banking V1 analytics platform
- January V2 baseline and focus selection
- retained February-March incremental-load architecture exercise
- Jan-Jun synthetic operational scenario data
- controlled DQ exceptions
- staging DQ cleanup and exception capture
- trusted Jan-Jun warehouse build and reconciliation
- Power BI V1
- Banking Operations Investigation Agent V2
- Banking Data Quality & Validation Agent
- run-level traceability
- evidence validation and abstention controls
- rule-grounding hardening
- multi-month KPI comparison support
- basic controlled aggregates
- approved derived metric support
- evidence-based derived-metric interpretation
- FastAPI/Swagger demo paths
- evaluation coverage for both agents

Still pending as a repository-management milestone:

- reconcile `feature/agent-v2-practical` with current `main`
- rerun complete evaluations after reconciliation
- inspect final diff
- open Banking PR to `main`
- merge and verify on `main`

This file is intended to preserve the project history and current state so that deleting or leaving prior chat threads does not force the Banking V2 work to be reconstructed from memory.