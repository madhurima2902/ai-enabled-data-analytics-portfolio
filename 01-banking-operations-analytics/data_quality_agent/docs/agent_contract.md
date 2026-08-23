# Banking Data Quality & Validation Agent — Agent Contract

## Primary user

Banking data analysts, BI developers, data-quality analysts, and engineering reviewers validating the Jan-Jun 2026 Banking Operations data pipeline.

## Business problem

Data-quality validation is repetitive and often requires several checks across raw, staging, exception, and warehouse layers. The agent coordinates approved checks and explains the evidence without allowing an LLM to modify source data or invent cleaning rules.

## Goal

Given a natural-language validation question, determine which approved data-quality checks are required, execute deterministic read-only SQL checks, compare results with approved business rules, and return a concise evidence-backed readiness assessment.

## Supported questions

- Validate the current transaction load.
- Are there duplicate transaction IDs?
- Are failed transactions carrying fees?
- Are channel IDs missing?
- How are high-value transactions handled?
- Why do raw and warehouse row counts differ?
- Is the trusted warehouse ready for KPI reporting?

## Approved knowledge

The agent reuses the shared Banking Agent knowledge rather than creating duplicate rules:

- `../v2_practical_agent/knowledge/business_rules.md`
- `../v2_practical_agent/knowledge/data_dictionary.md`
- `../docs/8_staging_layer_notes.md`
- `../docs/10_fact_tables_notes.md`

## Allowed actions

- Read approved Markdown rules.
- Run predefined read-only PostgreSQL validation queries.
- Compare counts across raw, staging, DQ exception, and warehouse layers.
- Classify check outcomes as PASS, REVIEW, or FAIL using deterministic conditions.
- Explain what a result means and recommend the next investigation step.
- Abstain when a requested rule is not approved or the required evidence is unavailable.

## Prohibited actions

- DELETE, UPDATE, INSERT, DROP, ALTER, TRUNCATE, CREATE, GRANT, REVOKE, COPY, CALL, or EXECUTE database statements.
- Automatically delete duplicates or high-value records.
- Invent or impute missing channel values.
- Change source-system data.
- Invent thresholds or business rules.
- Expose credentials or sensitive values.

## Deterministic cleaning/validation principle

The agent may decide which approved validation check to run and how to explain the outcome. SQL/Python determines the actual counts, reconciliation, and pass/fail conditions.

Cleaning/remediation is separate from detection:

- duplicates: capture for audit; trusted layer retains one row per transaction ID;
- failed-with-fee: capture raw exception; trusted layer fee is corrected to zero by the established pipeline rule;
- missing channel: flag and preserve missing value; do not invent a channel;
- high-value transaction: flag for review and retain unless separate evidence proves it invalid.

## Expected output

Each answer should contain, where applicable:

- requested validation scope;
- check result(s);
- actual evidence/counts;
- source layer/table;
- PASS/REVIEW/FAIL status;
- explanation of the approved rule;
- next step or remediation recommendation;
- trace showing the workflow path.

## Success criteria

The agent is considered correct when:

1. routing selects the expected validation check(s);
2. business rules come from the shared approved knowledge;
3. SQL remains read-only;
4. evidence reconciles to the trusted Jan-Jun source tables;
5. the warehouse-readiness conclusion follows deterministic check results;
6. unsupported requests are blocked or explicitly abstained from.

## Prototype boundary

This is an interview/portfolio prototype. Production extensions could include a metadata-driven rules engine, scheduler/event trigger, persistent run history, enterprise RBAC, alerting, human approval for remediation, and centralized observability. Those are design extensions, not current implementation claims.
