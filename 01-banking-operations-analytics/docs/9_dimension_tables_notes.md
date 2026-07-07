# Week 2 Day 4: Warehouse Dimension Tables

## Objective

Create warehouse dimension tables from the staging layer for reporting and Power BI semantic modeling.

## Database

`banking_analytics_db`

## Schemas Used

- `staging`
- `warehouse`

## SQL Files Created

- `sql/04_warehouse_tables/01_create_dimension_tables.sql`
- `sql/04_warehouse_tables/02_validate_dimension_tables.sql`

## Dimension Tables Created

- warehouse.dim_customer
- warehouse.dim_account
- warehouse.dim_product
- warehouse.dim_branch
- warehouse.dim_channel
- warehouse.dim_date

## Why Dimension Tables Matter

Dimension tables provide descriptive business context for facts.

Examples:

- Customer dimension explains who the customer is
- Account dimension explains what account the activity belongs to
- Product dimension explains the banking product
- Branch dimension explains the branch/location
- Channel dimension explains how the customer interacted
- Date dimension supports time-based reporting in Power BI

## Transformations Applied

The warehouse dimension layer adds reporting-ready structure.

Examples include:

- Creating surrogate keys such as customer_key, account_key, product_key, branch_key, and channel_key
- Preserving natural business IDs such as customer_id and account_id
- Calculating customer_age from date_of_birth
- Linking account dimension to customer, product, and branch dimensions
- Creating a reusable date dimension from 2018-01-01 through 2026-12-31
- Adding warehouse_loaded_at metadata

## Validation Checks

The validation script checks:

- Row count consistency between staging and warehouse dimensions
- Null checks on dimension surrogate keys
- Duplicate checks on natural business keys
- Account dimension lookup completeness for customer_key, product_key, and branch_key
- Date dimension coverage and completeness

## Validation Result

The dimension table validation checks passed successfully.

The validation confirmed that:

- Dimension row counts match staging source counts
- Dimension keys are populated
- Natural business keys remain unique
- Account dimension relationships are populated
- Date dimension covers the required reporting period

## Why This Step Matters

This step converts cleaned staging data into a Power BI-friendly dimensional model.

Instead of reporting directly from raw or staging tables, Power BI can use dimension tables with fact tables to support clean relationships, slicers, filters, and KPI analysis.

This is the foundation of the star schema used in the final reporting layer.

## AI-Assisted Development Approach

AI assistance was used to accelerate the creation of dimension-table SQL and validation logic.

The generated SQL was reviewed to ensure that:

- Dimension tables matched the intended data model
- Surrogate keys were created consistently
- Natural business IDs were preserved
- Account relationships to customer, product, and branch were populated
- Date dimension fields supported Power BI reporting
- Validation checks confirmed dimension completeness and uniqueness

This approach demonstrates practical AI-assisted analytics development, where AI helps speed up repetitive SQL design while the analyst remains responsible for reviewing the model, validating outputs, and ensuring the warehouse structure supports business reporting.

## Status

Warehouse dimension table creation completed successfully.