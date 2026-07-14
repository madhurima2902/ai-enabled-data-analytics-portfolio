# Warehouse Fact Tables

## Objective

Create warehouse fact tables from the staging layer and connect them to warehouse dimension tables using surrogate keys.

## Database

`banking_analytics_db`

## Schemas Used

* `staging`
* `warehouse`

## SQL Files Created

* `sql/04_warehouse_tables/03_create_fact_tables.sql`
* `sql/04_warehouse_tables/04_validate_fact_tables.sql`

## Fact Tables Created

* warehouse.fact_transactions
* warehouse.fact_complaints
* warehouse.fact_campaigns
* warehouse.fact_sla_tickets

## Why Fact Tables Matter

Fact tables store measurable business events.

Examples:

* A transaction happened
* A complaint was logged
* A campaign offer was sent
* An SLA ticket was created or resolved

Fact tables are the center of the reporting model. Dimension tables provide descriptive context around them.

## Fact Table Grain

The grain defines what one row represents.

* `fact_transactions`: one row per transaction
* `fact_complaints`: one row per complaint
* `fact_campaigns`: one row per customer campaign offer
* `fact_sla_tickets`: one row per SLA ticket

Defining grain is important because it prevents double counting and makes Power BI measures more reliable.

## Key Transformations Applied

The warehouse fact layer adds reporting-ready structure.

Examples include:

* Creating surrogate keys such as transaction_key, complaint_key, campaign_key, and sla_ticket_key
* Connecting fact rows to dimension tables using customer_key, account_key, product_key, branch_key, channel_key, and date_key
* Preserving original source IDs such as transaction_id, complaint_id, campaign_id, and ticket_id
* Creating count helper fields such as transaction_count, complaint_count, campaign_sent_count, and ticket_count
* Creating status-based count fields such as successful_transaction_count, failed_transaction_count, resolved_complaint_count, converted_count, sla_met_count, and sla_breached_count
* Adding warehouse_loaded_at metadata

## Validation Checks

The validation script checks:

* Row count consistency between staging and warehouse fact tables
* Null checks on fact surrogate keys
* Duplicate checks on source business IDs
* Dimension lookup completeness
* Date key lookup completeness
* Derived count field logic

## Validation Result

The fact table validation checks passed successfully.

The validation confirmed that:

* Fact row counts match staging source counts
* Fact surrogate keys are populated
* Source business IDs remain unique
* Fact tables successfully connect to dimension tables
* Date keys are populated correctly
* Derived count fields are logically correct

## Why This Step Matters

This step completes the core warehouse star schema.

The warehouse now has descriptive dimension tables and measurable fact tables. This structure is ready for analytical queries, KPI development, and Power BI semantic modeling.

Instead of connecting Power BI directly to raw source data, the report can use clean fact and dimension tables that support reliable relationships, slicers, filters, and measures.

## AI-Assisted Development Approach

AI assistance was used to accelerate the creation of fact-table SQL and validation logic.

The generated SQL was reviewed to ensure that:

* Fact table grain was clearly defined
* Dimension keys were joined correctly
* Source business IDs were preserved
* Count fields supported KPI creation
* Row counts matched staging source tables
* Validation checks confirmed fact table completeness and join readiness

This approach demonstrates practical AI-assisted analytics development, where AI helps speed up repetitive SQL modeling while the analyst remains responsible for reviewing the model, validating outputs, and ensuring the warehouse supports business reporting.

## Status

Warehouse fact table creation completed successfully.
