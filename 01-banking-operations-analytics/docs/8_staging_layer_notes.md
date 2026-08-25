# Staging Layer Creation

## Objective

Create staging tables from the PostgreSQL raw layer and apply cleaning, standardization, data-quality handling, and derived fields before warehouse modeling.

## Database

`banking_analytics_db`

## Schemas Used

- `raw`
- `staging`

## SQL Files Used

- `sql/03_staging_tables/01_create_staging_tables.sql`
- `sql/03_staging_tables/02_validate_staging_tables.sql`
- `sql/03_staging_tables/03_transaction_dq_exceptions_and_cleaning.sql`

## Staging Tables Created

- `staging.stg_customers`
- `staging.stg_accounts`
- `staging.stg_products`
- `staging.stg_branches`
- `staging.stg_channels`
- `staging.stg_complaints`
- `staging.stg_campaigns`
- `staging.stg_sla_tickets`
- `staging.stg_transactions`
- `staging.stg_transaction_dq_exceptions`

## Jan-Jun 2026 Transaction Reconciliation

The current V2 dataset covers January through June 2026.

- Raw transaction rows: 188,015
- Unique transaction IDs: 188,000
- Clean staging transaction rows: 188,000
- Warehouse transaction rows: 188,000

The 15-row difference between raw and staging is intentional. Duplicate source rows remain visible in the raw layer and are captured as DQ exceptions, but they are removed before the trusted reporting layer.

## Transformations Applied

The staging layer applies basic standardization to raw data, including:

- trimming extra spaces from text fields;
- standardizing ID fields to uppercase;
- converting empty strings to nulls;
- adding `staging_loaded_at` timestamps;
- creating transaction date and month fields;
- creating successful-transaction flags;
- creating complaint and ticket resolution flags;
- creating campaign conversion helper fields.

## Transaction DQ Handling

The Jan-Jun V2 refresh intentionally contains a small number of raw transaction exceptions so that data-quality behavior can be demonstrated.

The staging process handles these as follows:

### Duplicate transaction IDs

Duplicate rows are detected from the raw layer and recorded in `staging.stg_transaction_dq_exceptions` with exception type `DUPLICATE_TRANSACTION_ID`.

Only one trusted row per `transaction_id` is retained in `staging.stg_transactions`, allowing the warehouse to enforce transaction-ID uniqueness.

### Failed transactions with fees

Raw failed transactions with non-zero fees are captured with exception type `FAILED_TRANSACTION_WITH_FEE`.

The trusted staging value is corrected to a zero fee because the project business rule states that failed transactions should not carry a charged fee. The original raw value remains available for audit.

### Missing channel IDs

Missing transaction channel IDs are captured with exception type `MISSING_CHANNEL_ID`.

The staging process does not invent or impute a channel value. The missing value is preserved so the downstream process can distinguish unknown source data from known channels.

### High-value transactions

Transactions above the defined high-value threshold are captured with exception type `HIGH_VALUE_TRANSACTION` for review.

These records are not automatically removed or corrected because a large amount is an analytical outlier, not automatically a data error.

## Current DQ Exception Counts

For the validated Jan-Jun 2026 dataset:

- `DUPLICATE_TRANSACTION_ID`: 15
- `FAILED_TRANSACTION_WITH_FEE`: 40
- `MISSING_CHANNEL_ID`: 20
- `HIGH_VALUE_TRANSACTION`: 309

After staging cleanup, failed-with-fee records remaining in the warehouse: 0.

## Validation Checks

Validation covers:

- raw and staging row reconciliation;
- null checks on important business keys;
- duplicate checks on business IDs;
- transaction date/month consistency;
- derived status-flag logic;
- unique transaction count reconciliation;
- warehouse transaction count reconciliation;
- Jan-Jun date coverage;
- confirmation that failed-with-fee exceptions do not remain in the trusted warehouse.

## Why This Step Matters

The raw layer represents what arrived from the source and therefore keeps the intentional exceptions.

The staging layer is the controlled working layer where data is standardized, exceptions are recorded, and only justified corrections are applied before reporting. This prevents silent data loss while also preventing known bad records from distorting trusted KPIs.

The resulting pattern is:

`raw -> detect / record DQ exceptions -> clean staging -> warehouse -> Power BI / agent tools`

This also gives the agent two distinct sources to use later:

- trusted warehouse tables for operational KPIs and analysis;
- the DQ exception table for investigation and audit questions.

## AI-Assisted Development Approach

AI assistance was used to accelerate SQL and Python development for the staging and refresh workflow. The transformation and validation behavior was reviewed against the intended business rules and verified through reconciliation output after execution.

The analyst remains responsible for understanding why each exception is flagged, deciding whether it should be corrected or preserved, and validating that the trusted reporting layer reconciles correctly.

## Status

Jan-Jun 2026 staging cleanup, transaction DQ exception capture, and warehouse reconciliation completed successfully.
