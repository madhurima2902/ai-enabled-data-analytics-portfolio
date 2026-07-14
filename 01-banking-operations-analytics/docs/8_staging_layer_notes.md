# Staging Layer Creation

## Objective

Create staging tables from the PostgreSQL raw layer and apply basic cleaning, standardization, and derived fields before warehouse modeling.

## Database

`banking_analytics_db`

## Schemas Used

* `raw`
* `staging`

## SQL Files Created

* `sql/03_staging_tables/01_create_staging_tables.sql`
* `sql/03_staging_tables/02_validate_staging_tables.sql`

## Staging Tables Created

* staging.stg_customers
* staging.stg_accounts
* staging.stg_products
* staging.stg_branches
* staging.stg_channels
* staging.stg_complaints
* staging.stg_campaigns
* staging.stg_sla_tickets
* staging.stg_transactions

## Transformations Applied

The staging layer applies basic standardization to raw data.

Examples include:

* Trimming extra spaces from text fields
* Standardizing ID fields to uppercase
* Converting empty strings to nulls
* Adding `staging_loaded_at` timestamp
* Creating derived transaction fields:

  * transaction_date
  * transaction_month
  * is_successful_transaction
* Creating derived complaint and ticket fields:

  * is_resolved
  * is_ticket_resolved
* Creating campaign conversion helper field:

  * converted_count

## Validation Checks

The staging validation script checks:

* Raw-to-staging row count consistency
* Null checks on important key fields
* Duplicate checks on business IDs
* Derived transaction date and month consistency
* Successful transaction flag logic
* Complaint resolved flag logic
* Campaign converted count logic

## Validation Result

The staging table validation checks passed successfully.

The validation confirmed that:

* Row counts were preserved from raw to staging
* Important business keys were not null
* Business IDs remained unique
* Derived transaction date and month fields were accurate
* Derived status flags were logically correct
* Staging tables are ready for warehouse fact and dimension modeling

## Why This Step Matters

The staging layer acts as the cleaned working layer between raw source data and the reporting warehouse.

Raw data should remain close to source format, while staging prepares the data for reliable joins, fact tables, dimension tables, and Power BI reporting.

This step helps ensure that downstream reporting is based on standardized and validated data rather than directly on raw source files.

## AI-Assisted Development Approach

AI assistance was used to accelerate the creation of staging transformation and validation SQL patterns.

The generated SQL was reviewed to ensure that:

* Staging tables matched the raw table structures
* Text standardization did not change the business meaning of the data
* Derived fields were logically correct
* Row counts were preserved from raw to staging
* Validation checks confirmed staging quality before warehouse modeling
* The staging design supported future fact and dimension table creation

This approach demonstrates practical AI-assisted analytics development, where AI helps speed up repetitive SQL development while the analyst remains responsible for reviewing transformation logic, validating outputs, and understanding the business purpose of the staging layer.

## Status

Staging layer creation completed successfully.
