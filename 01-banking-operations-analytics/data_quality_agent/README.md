# Banking Data Quality & Validation Agent — Interview Demo

## Purpose

This is a bounded companion agent to `v2_practical_agent/`.

The Banking Investigation Agent answers business questions after trusted data is available. This Data Quality Agent focuses on the step before that: validating whether raw, staging, exception, and warehouse layers are consistent enough for trusted KPI reporting.

The two agents intentionally share the same data-quality story and the same approved Markdown rules.

## Shared architecture story

```text
Raw data
   |
   v
Data Quality Agent
   |
   +--> classify requested validation
   +--> retrieve shared approved DQ rule
   +--> run deterministic SQL/Python check
   +--> compare evidence across raw/staging/warehouse
   +--> PASS / REVIEW / FAIL
   +--> optional Claude synthesis
   |
   v
Trusted warehouse
   |
   +--> Power BI
   +--> Banking Investigation Agent V2
```

The key principle is:

> The agent decides which approved validation check is relevant and how to explain the evidence. SQL/Python determines what the data actually says.

## Why this is agentic

This is not an LLM cleaning a dataframe by itself. The workflow:

1. interprets the user's validation goal;
2. routes to one or more approved checks;
3. retrieves the governing DQ rule from the shared Markdown knowledge;
4. executes deterministic read-only validation tools;
5. evaluates the evidence;
6. synthesizes a readiness or investigation response;
7. blocks unsupported data-changing requests.

LangGraph makes that workflow and state explicit.

## Shared source of truth

This agent does **not** maintain a second copy of the Banking DQ rules. It reuses:

- `../v2_practical_agent/knowledge/business_rules.md`
- `../docs/8_staging_layer_notes.md`

This prevents the two agents from giving different explanations for duplicates, failed transaction fees, missing channels, or high-value transactions.

Project-level Claude Code instructions are in `../CLAUDE.md`.

## Implemented checks

### 1. Row reconciliation

Compares:

- raw transaction rows;
- unique raw transaction IDs;
- trusted staging rows;
- warehouse rows.

The expected control is that trusted staging and warehouse reconcile to unique transaction IDs while raw retains source duplicates for audit.

### 2. Duplicate transaction validation

Confirms:

- source duplicate rows are detected;
- duplicate exceptions are captured;
- trusted warehouse contains no duplicate `transaction_id` values.

### 3. Failed-transaction fee validation

Confirms:

- failed transactions with non-zero raw fees are captured as exceptions;
- no failed transaction remains with a non-zero fee in the trusted warehouse.

### 4. Missing-channel validation

Confirms:

- missing `channel_id` values are flagged;
- the pipeline does not invent a channel;
- missing channel values remain visible for controlled reporting treatment.

This produces `REVIEW`, not automatic `FAIL`, when the known exception is controlled correctly.

### 5. High-value transaction validation

Confirms:

- high-value records are flagged;
- the same plausible transactions remain in trusted data;
- the agent does not treat an outlier as an error without additional evidence.

This also produces `REVIEW` when controls are working correctly.

### 6. Warehouse readiness

Runs all five checks and returns:

- `READY` — all checks pass with no review items;
- `READY_WITH_KNOWN_EXCEPTIONS` — no blocking failure, but approved review items remain;
- `NOT_READY` — at least one blocking validation failure exists.

For the current Jan-Jun demo, the expected status is `READY_WITH_KNOWN_EXCEPTIONS` because missing-channel and high-value records are intentionally preserved for review rather than silently corrected or deleted.

## Safety boundary

The agent may detect, validate, explain, and recommend. It may not modify data.

It blocks database-changing requests such as DELETE, UPDATE, INSERT, DROP, ALTER, and TRUNCATE. All database queries used by the agent are predefined and pass a deterministic read-only SQL validator.

## Hardening controls

### Run correlation

Every `run_agent()` execution is stamped with a `run_id` (`uuid.uuid4()`), consistent with the Banking Investigation Agent. It is created at the start of the run, carried in `DQAgentState`, recorded as the first trace line, and returned by `POST /validate`. This makes one agent execution traceable end-to-end across the trace log, the API response, and (once both agents run side by side) cross-agent log correlation.

### Approved-rule coverage gate

Retrieving a rule and finding no matching rule are different outcomes, but before this control they looked the same to the workflow: `retrieve_rules` silently skips any check whose file or section can't be found, so a missing rule and a found rule both just flowed into the same `execute_checks` step. A new `rule_coverage` node runs right after retrieval and explicitly confirms that every requested check has a corresponding entry in `retrieved_rules`.

- If every requested check is covered, the workflow proceeds to the deterministic PostgreSQL checks as before.
- If any requested check has no approved rule behind it, the graph routes to a `rule_gap` node instead of `execute_checks`. It marks `validation_status = "ABSTAINED_MISSING_RULE"`, `evidence_status = "INSUFFICIENT"`, never invents cleaning guidance, and never even computes a PostgreSQL result for that run — deterministic check results and rule-grounding status stay two separate, never-conflated pieces of state.

## Folder structure

```text
data_quality_agent/
├── .env.example
├── README.md
├── requirements.txt
├── docs/
│   └── agent_contract.md
└── src/
    ├── __init__.py
    ├── agent.py
    ├── api.py
    ├── dq_tools.py
    ├── evaluation.py
    ├── knowledge.py
    └── state.py
```

## Setup

From `01-banking-operations-analytics`:

```powershell
cd data_quality_agent
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Add the same local `banking_analytics_db` PostgreSQL credentials used by `v2_practical_agent`.

Keep `USE_LLM=false` for the deterministic base demo. Claude synthesis can be enabled later with a valid Anthropic API key/model.

## Evaluation

Run:

```powershell
.\.venv\Scripts\python.exe -m src.evaluation
```

Expected groups:

```text
PASS | routing golden cases
PASS | shared-rule knowledge consistency
PASS | read-only SQL guard
PASS | PostgreSQL DQ reconciliation controls
PASS | end-to-end warehouse readiness flow
PASS | run_id request correlation
PASS | approved-rule coverage (success case)
PASS | approved-rule coverage (missing rule case)

Passed 8/8 evaluation groups
```

The PostgreSQL checks reconcile against the established Jan-Jun demo controls:

- raw rows: 188,015
- unique transaction IDs: 188,000
- staging rows: 188,000
- warehouse rows: 188,000
- duplicate transaction rows: 15
- failed-with-fee raw exceptions: 40
- missing channel IDs: 20
- high-value transactions: 309

## Terminal demo

### Full load validation

```powershell
.\.venv\Scripts\python.exe -m src.agent "Validate the current transaction load."
```

Expected route:

```text
full_validation
-> shared DQ rules
-> all deterministic checks
-> evidence validation
-> READY_WITH_KNOWN_EXCEPTIONS
```

### Duplicate check

```powershell
.\.venv\Scripts\python.exe -m src.agent "Are there duplicate transaction IDs?"
```

### Reconciliation explanation

```powershell
.\.venv\Scripts\python.exe -m src.agent "Why do raw and warehouse row counts differ?"
```

### Missing channel check

```powershell
.\.venv\Scripts\python.exe -m src.agent "Are any channel IDs missing?"
```

### High-value rule

```powershell
.\.venv\Scripts\python.exe -m src.agent "Should high-value transactions be removed?"
```

### Safety control

```powershell
.\.venv\Scripts\python.exe -m src.agent "DELETE FROM warehouse.fact_transactions"
```

## FastAPI / Swagger demo

Start this agent on port 8001 so it can run beside the Banking Investigation Agent on port 8000:

```powershell
.\.venv\Scripts\python.exe -m uvicorn src.api:app --reload --port 8001
```

Open:

```text
http://127.0.0.1:8001/docs
```

Use `POST /validate` with:

```json
{
  "question": "Validate the current transaction load."
}
```

The response exposes a `run_id`, intent, requested checks, shared rule sources, check evidence, validation status, trace, and final answer.

## Optional Claude synthesis

The base workflow remains deterministic and works without an external model.

To validate the Claude runtime path later:

```text
USE_LLM=true
ANTHROPIC_API_KEY=<local secret>
ANTHROPIC_MODEL=<approved Claude model>
```

Claude does not perform the underlying reconciliation and does not receive write authority. It explains already validated evidence and approved rules.

## Claude Code positioning

Both Banking agents are prepared to be worked on through Claude Code using the project-level `../CLAUDE.md` instructions.

A credible engineering workflow is:

```text
Ask Claude Code to map the relevant flow
-> inspect proposed change
-> approve bounded edit
-> run evaluation
-> review git diff
-> assess correctness/security/performance/scalability/maintainability
-> accept or revise
```

This is distinct from Claude runtime synthesis. Claude Code is the engineering delivery tool; the optional Anthropic API call is a runtime model integration.

## Interview-ready description

> I built a second bounded LangGraph agent focused on data quality and trusted-data readiness. Instead of letting an LLM clean data directly, the agent routes the validation goal to approved checks, reuses the same governed business rules as my Banking Investigation Agent, and executes deterministic read-only PostgreSQL reconciliation. It distinguishes blocking failures from controlled review items and can explain whether the warehouse is ready for KPI reporting. The important design principle is that the agent decides what to validate and how to interpret the evidence, while SQL/Python determines the actual data result. Both agents are structured for Claude Code-assisted engineering using a shared project instruction file so their rules and delivery workflow stay consistent.

## Prototype boundaries

Not currently claimed as implemented:

- automatic remediation/write-back;
- scheduled/event-triggered validation;
- enterprise RBAC;
- persistent DQ run history;
- metadata-driven dynamic rule authoring;
- centralized observability platform;
- production HITL remediation approvals.

Those are production extensions rather than interview-demo requirements.
