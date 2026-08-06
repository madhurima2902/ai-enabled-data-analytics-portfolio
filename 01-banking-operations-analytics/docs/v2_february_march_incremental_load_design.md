# Banking Operations Analytics V2 — February–March Incremental Load Design

## 1. Purpose

This document records the Phase 1 audit of the existing January pipeline and the Phase 2 design for adding February and March 2026 data through a true incremental-load workflow.

The business focus remains:

**Mobile Banking × Savings Account × Mass segment**

The implementation sequence is:

1. Generate monthly input files using the January schemas.
2. Introduce a controlled February deterioration and March partial recovery.
3. Introduce a small, documented set of realistic data-quality defects.
4. Load incoming files through raw, staging and warehouse layers without rebuilding January.
5. Reconcile accepted, rejected and duplicate records.
6. Analyze January–March performance only after the load is validated.

---

## 2. Phase 1 Audit — Existing January Pipeline

### 2.1 Repository structure

The project already separates work into:

- `scripts/generators`
- `scripts/loaders`
- `sql/01_raw_layer`
- `sql/02_raw_data_quality`
- `sql/03_staging_tables`
- `sql/04_warehouse_tables`
- `sql/05_data_quality_checks`
- `sql/06_business_queries`
- `sql/07_incremental_load`

This structure will be preserved.

### 2.2 January transaction generation

The current `generate_transactions_jan.py` script:

- generates 25,000 January 2026 transactions;
- writes `data/raw/raw_transactions_jan.csv`;
- uses fixed random seed `45`;
- selects an existing account and derives customer, product and branch from that account;
- assigns a random channel;
- generates transaction IDs in the form `TXN202601########`;
- uses status probabilities of approximately 92% Success, 6% Failed and 2% Reversed;
- forces failed and reversed transactions to have zero fees;
- keeps balance-after-transaction non-negative.

### 2.3 Existing operational-data generation

The current `generate_operational_data.py` script is not month-specific:

- complaints are generated across January and February 2026;
- campaigns are generated across January and February 2026;
- SLA tickets are derived from complaints and can spill into March because ticket creation and resolution occur after the complaint date;
- output files are single combined files:
  - `raw_complaints.csv`
  - `raw_campaigns.csv`
  - `raw_sla_tickets.csv`;
- IDs currently restart from 1 within each dataset.

This explains why complaint and campaign tables already contain February rows and why SLA tickets contain some March rows even though transaction generation is January-only.

### 2.4 Existing validation approach

The current `validate_transactions_jan.py` script is strict and fail-fast. It requires:

- exactly 25,000 rows;
- unique, non-null transaction IDs;
- valid account and channel references;
- valid transaction types and statuses;
- January-only dates;
- positive amounts;
- non-negative fees and balances;
- zero fees for failed transactions;
- customer, product and branch consistency with the selected account.

This design produces an almost completely clean transaction file. It validates source generation, but it does not model a realistic incoming operational feed where some records fail validation.

### 2.5 Existing raw loader

The current `load_raw_csvs.py` script:

- uses PostgreSQL `COPY`;
- truncates every raw table before loading;
- loads one fixed file per table;
- includes only `raw_transactions_jan.csv` for transactions;
- does not log file name, batch ID, load timestamp or source month;
- is not incremental;
- is not idempotent in the analytical sense because rerunning rebuilds raw tables instead of detecting previously processed files.

### 2.6 Main audit conclusion

The project has a sound layered folder structure, but the current ingestion process is a full-refresh prototype rather than a true incremental pipeline.

The V2 implementation must therefore preserve the existing schemas while changing the monthly ingestion pattern from:

`truncate → reload all`

into:

`receive monthly batch → validate → accept/reject → append only new valid records → reconcile`.

---

## 3. Phase 2 Design Principles

### 3.1 Uniform monthly schema

February and March files must use the same columns and data types as the existing January source files.

No analytical field should be added directly to source CSVs merely to make analysis easier.

### 3.2 Monthly file pattern

The preferred monthly source files are:

- `raw_transactions_feb.csv`
- `raw_transactions_mar.csv`
- `raw_complaints_feb.csv`
- `raw_complaints_mar.csv`
- `raw_campaigns_feb.csv`
- `raw_campaigns_mar.csv`
- `raw_sla_tickets_feb.csv`
- `raw_sla_tickets_mar.csv`

Reference and master data such as customers, accounts, products, branches and channels will be reused unless a later requirement introduces controlled master-data changes.

### 3.3 ID strategy

Business IDs must remain unique across months.

Planned patterns:

- January transactions: `TXN202601########`
- February transactions: `TXN202602########`
- March transactions: `TXN202603########`

Complaint, campaign and SLA IDs will also include a month component or use non-overlapping ranges so that monthly files cannot collide.

### 3.4 Reproducibility

Each monthly generator will use an explicit random seed.

The same seed and parameters must reproduce the same file, which supports testing, debugging and portfolio demonstration.

---

## 4. Monthly Business Scenario

### 4.1 January

January remains the baseline and will not be regenerated or modified.

### 4.2 February deterioration

February will show a controlled deterioration concentrated in:

**Mobile Banking × Savings Account × Mass segment**

The deterioration will affect:

- transaction failure rate;
- transaction reversal rate;
- affected transaction count and value;
- complaint volume;
- complaints per 1,000 transactions;
- complaint-resolution rate;
- average resolution days;
- SLA-ticket volume;
- SLA-breach rate.

The scenario will be large enough to be analytically visible but not so extreme that it appears artificial.

### 4.3 March partial recovery

March will show improvement after an operational intervention, but not a perfect return to zero defects or zero failures.

Expected pattern:

- lower failure and reversal rates than February;
- lower complaint intensity;
- improved complaint resolution;
- reduced SLA breaches;
- some residual risk remaining.

### 4.4 Control groups

Other product and segment combinations will remain broadly stable with normal random variation.

This allows comparison between the focus population and controls without claiming direct causality from synthetic data.

---

## 5. Data-Quality Design

### 5.1 Rationale

Real operational feeds are rarely perfectly clean. V2 will therefore introduce a small, controlled set of defects in incoming February and March batches.

The intended defect rate will be approximately 1%–3% of incoming records, depending on the table.

### 5.2 Planned transaction defects

Possible injected defects include:

- duplicate transaction IDs;
- null customer or account IDs;
- account/customer mismatches;
- invalid product or channel IDs;
- invalid transaction status values;
- dates outside the source month;
- non-positive or null amounts;
- failed transactions with non-zero fees;
- leading/trailing whitespace in categorical values.

### 5.3 Planned complaint and SLA defects

Possible injected defects include:

- duplicate complaint IDs;
- orphan complaint customer/account references;
- invalid complaint status or priority values;
- resolution date before complaint date;
- SLA tickets with invalid complaint IDs;
- due time before created time;
- resolved tickets without resolved timestamps;
- inconsistent SLA flags.

### 5.4 Separation of business and data-quality effects

The February operational deterioration and the injected data-quality defects are separate design elements.

The project will not claim that invalid rows caused the business deterioration.

Business analysis will use accepted warehouse records. Data-quality reporting will separately explain rejected and corrected records.

---

## 6. Incremental-Load Design

### 6.1 Batch metadata

Each incoming load should be identifiable through metadata such as:

- batch ID;
- source file name;
- source month;
- load timestamp;
- file row count;
- accepted row count;
- rejected row count;
- duplicate row count;
- load status.

### 6.2 Processing flow

The target flow is:

`monthly CSV → raw landing/batch table → validation → accepted staging rows + rejected rows → warehouse append → reconciliation`.

### 6.3 Raw-layer behavior

The incremental loader must not truncate the historical raw tables for monthly loads.

It should either:

- append incoming rows with batch metadata; or
- load each incoming file into a dedicated landing table and then persist the batch outcome.

### 6.4 Staging behavior

Staging will:

- standardize whitespace and case where appropriate;
- cast dates and numeric fields;
- apply business-rule checks;
- deduplicate within the incoming batch;
- compare business IDs against warehouse history;
- separate accepted and rejected rows.

### 6.5 Warehouse behavior

Warehouse inserts will include only valid, new business records.

Existing January rows will remain unchanged.

### 6.6 Idempotency and rerun protection

Reprocessing the same file or rerunning the same batch must not duplicate warehouse records.

Protection will be based on a combination of:

- processed-file or batch tracking;
- business-key checks;
- `NOT EXISTS`, conflict handling or equivalent insert logic;
- reconciliation after every run.

---

## 7. Validation and Reconciliation Rules

### 7.1 File-level validation

- expected columns are present;
- no unexpected schema changes;
- source month matches the file name;
- row count is captured;
- file is not already processed.

### 7.2 Record-level validation

- required fields are present;
- IDs and foreign keys are valid;
- dates are logically valid;
- amounts and fees satisfy business rules;
- status and category values are valid;
- complaint and SLA relationships are valid.

### 7.3 Load-level reconciliation

For each table and batch:

`source rows = accepted rows + rejected rows + duplicate rows`

Warehouse growth must equal accepted new rows only.

### 7.4 Historical protection

After February and March loads:

- January transaction count must remain 25,000;
- January IDs and values must remain unchanged;
- monthly date coverage must reconcile;
- no business ID may occur in more than one accepted warehouse row.

### 7.5 Business validation

After technical validation:

- February deterioration must be visible in the selected focus group;
- controls must remain broadly stable;
- March must show partial recovery;
- complaint and SLA trends must support the operational narrative;
- rate calculations must use correct denominators and output grain.

---

## 8. Planned Implementation Files

The likely next implementation files are:

- `scripts/generators/generate_monthly_transactions.py`
- `scripts/generators/generate_monthly_operational_data.py`
- `scripts/generators/validate_monthly_inputs.py`
- `scripts/loaders/load_incremental_batch.py`
- `sql/07_incremental_load/01_create_batch_control_and_reject_tables.sql`
- `sql/07_incremental_load/02_load_february_march_incremental.sql`
- `sql/07_incremental_load/03_validate_incremental_load.sql`
- `sql/07_incremental_load/04_january_march_trend_analysis.sql`

Exact names may be adjusted after inspecting the existing raw, staging and warehouse table definitions.

---

## 9. Phase 1 and 2 Completion Status

Completed:

- audited the January transaction generator;
- audited the operational-data generator;
- audited January transaction validation;
- audited the current raw CSV loader;
- confirmed the existing SQL layer structure;
- identified that current raw loading is full refresh, not incremental;
- identified why the current source data is almost completely clean;
- defined monthly schema, ID, scenario, data-quality, incremental-load and reconciliation rules.

Not yet implemented:

- February and March generators;
- defect injection code;
- incremental loader;
- reject/quarantine tables;
- database execution and row-count validation;
- January–March analysis.

These items belong to Phase 3 onward.
