# SQL Model Walkthrough

## Purpose

This document explains the SQL model used in the Banking Operations Analytics project.

The goal is to make the project easy to understand during interviews, portfolio reviews, and future Power BI development.

## High-Level Flow

The SQL workflow follows this structure:

```text
Raw source data
        ↓
Raw PostgreSQL tables
        ↓
Raw data quality checks
        ↓
Staging tables
        ↓
Warehouse dimensions and facts
        ↓
Warehouse data quality checks
        ↓
Business KPI queries
        ↓
Power BI reporting
```

## Database

The project uses PostgreSQL.

Database name:

```text
banking_analytics_db
```

## Schemas Used

The project uses separate schemas to organize the analytics workflow.

```text
raw
staging
warehouse
dq
analytics
```

The main schemas used in the current SQL model are:

* `raw`
* `staging`
* `warehouse`

## Raw Layer

The raw layer stores the loaded source data.

Raw tables are designed to stay close to the original file structure. This helps preserve source data before cleaning or transformation.

Raw tables include:

* `raw.customers`
* `raw.accounts`
* `raw.products`
* `raw.branches`
* `raw.channels`
* `raw.transactions`
* `raw.complaints`
* `raw.campaigns`
* `raw.sla_tickets`

## Why the Raw Layer Exists

The raw layer is important because it provides traceability.

If a downstream KPI looks incorrect, the analyst can compare the warehouse table back to staging and raw data.

This supports debugging, validation, and auditability.

## Raw Data Quality Checks

Raw data quality checks validate whether the loaded data is usable.

Examples of raw checks include:

* Are row counts correct?
* Are important IDs missing?
* Are business IDs duplicated?
* Are dates within expected ranges?
* Are categories and statuses valid?
* Do foreign keys connect to reference tables?
* Do transaction customer/product/branch fields match the account table?

These checks help catch issues before transformation.

## Staging Layer

The staging layer prepares raw data for warehouse modeling.

Staging tables include:

* `staging.stg_customers`
* `staging.stg_accounts`
* `staging.stg_products`
* `staging.stg_branches`
* `staging.stg_channels`
* `staging.stg_transactions`
* `staging.stg_complaints`
* `staging.stg_campaigns`
* `staging.stg_sla_tickets`

## Staging Transformations

Staging transformations include:

* Trimming text fields
* Standardizing ID fields
* Converting empty strings to nulls
* Creating transaction date fields
* Creating transaction month fields
* Creating resolved/open flags
* Creating conversion helper fields
* Adding staging load timestamps

## Why the Staging Layer Exists

The staging layer separates cleaning logic from warehouse modeling.

This makes the project easier to debug and explain.

Raw data remains close to source format, while staging contains standardized and cleaned data.

## Warehouse Layer

The warehouse layer contains reporting-ready fact and dimension tables.

This layer is designed for business analysis and Power BI reporting.

The warehouse uses a star-schema style model.

## Dimension Tables

Dimension tables provide descriptive business context.

Dimension tables include:

* `warehouse.dim_customer`
* `warehouse.dim_account`
* `warehouse.dim_product`
* `warehouse.dim_branch`
* `warehouse.dim_channel`
* `warehouse.dim_date`

## Customer Dimension

`warehouse.dim_customer` describes the customer.

Example fields:

* `customer_key`
* `customer_id`
* `customer_name`
* `gender`
* `customer_age`
* `age_group`
* `city`
* `state`
* `customer_segment`
* `kyc_status`
* `risk_band`

This dimension supports customer segmentation, risk analysis, and customer behavior analysis.

## Account Dimension

`warehouse.dim_account` describes the account.

Example fields:

* `account_key`
* `account_id`
* `customer_key`
* `product_key`
* `branch_key`
* `account_open_date`
* `account_status`
* `current_balance`
* `interest_rate`
* `credit_limit`

This dimension connects accounts to customers, products, and branches.

## Product Dimension

`warehouse.dim_product` describes banking products.

Example fields:

* `product_key`
* `product_id`
* `product_name`
* `product_category`
* `product_type`
* `is_active`

This dimension supports product-level transaction and complaint analysis.

## Branch Dimension

`warehouse.dim_branch` describes branches and locations.

Example fields:

* `branch_key`
* `branch_id`
* `branch_name`
* `city`
* `state`
* `region`
* `branch_type`

This dimension supports branch and regional performance analysis.

## Channel Dimension

`warehouse.dim_channel` describes customer touchpoints.

Example fields:

* `channel_key`
* `channel_id`
* `channel_name`
* `channel_category`
* `is_digital`

This dimension supports analysis of digital versus non-digital channels.

## Date Dimension

`warehouse.dim_date` supports time-based reporting.

Example fields:

* `date_key`
* `full_date`
* `day_of_month`
* `month_number`
* `month_name`
* `quarter_number`
* `year_number`
* `day_name`
* `is_weekend`

This table supports trends, time slicers, and date-based Power BI visuals.

## Fact Tables

Fact tables store measurable business events.

Fact tables include:

* `warehouse.fact_transactions`
* `warehouse.fact_complaints`
* `warehouse.fact_campaigns`
* `warehouse.fact_sla_tickets`

## Transaction Fact

`warehouse.fact_transactions` captures one row per transaction.

Grain:

```text
One row per transaction
```

Example measures and fields:

* `transaction_count`
* `successful_transaction_count`
* `failed_transaction_count`
* `amount`
* `fee_amount`
* `transaction_status`
* `transaction_type`

Connected dimensions:

* Customer
* Account
* Product
* Branch
* Channel
* Date

Business questions supported:

* What is the transaction success rate?
* Which channels drive the most transaction value?
* Which products generate the highest activity?
* Which branches have high failed transaction counts?

## Complaint Fact

`warehouse.fact_complaints` captures one row per complaint.

Grain:

```text
One row per complaint
```

Example measures and fields:

* `complaint_count`
* `resolved_complaint_count`
* `open_complaint_count`
* `resolution_days`
* `complaint_category`
* `complaint_priority`
* `complaint_status`

Connected dimensions:

* Customer
* Account
* Product
* Channel
* Date

Business questions supported:

* What are the main customer pain points?
* Which complaint categories are most common?
* How quickly are complaints resolved?
* Which channels generate more complaints?

## Campaign Fact

`warehouse.fact_campaigns` captures one row per customer campaign offer.

Grain:

```text
One row per customer campaign offer
```

Example measures and fields:

* `campaign_sent_count`
* `engaged_count`
* `converted_count`
* `converted_flag`
* `campaign_type`
* `response_status`

Connected dimensions:

* Customer
* Product
* Channel
* Date

Business questions supported:

* Which campaigns have higher conversion rates?
* Which customer segments respond better?
* Which channels perform better for campaigns?

## SLA Ticket Fact

`warehouse.fact_sla_tickets` captures one row per SLA ticket.

Grain:

```text
One row per SLA ticket
```

Example measures and fields:

* `ticket_count`
* `resolved_ticket_count`
* `sla_met_count`
* `sla_breached_count`
* `sla_target_hours`
* `ticket_priority`
* `assigned_team`

Connected dimensions:

* Customer
* Account
* Date

Business questions supported:

* Are service teams meeting SLA targets?
* Which teams have higher breach rates?
* Which priorities drive more SLA failures?

## Data Quality Layer

After creating fact and dimension tables, warehouse data quality checks validate the reporting model.

The checks cover:

* Row count sanity
* Orphaned fact records
* Date key consistency
* Transaction business rules
* Complaint business rules
* Campaign business rules
* SLA ticket business rules
* Natural key consistency

This confirms the warehouse is trustworthy before building KPI queries.

## Business Query Layer

Business KPI queries use the warehouse model to answer stakeholder questions.

The query file covers:

* Executive KPI summary
* Transaction performance
* Channel performance
* Product performance
* Customer segment analysis
* Branch performance
* Complaint analysis
* SLA analysis
* Campaign performance
* Customer 360 view
* Power BI base query

## Star Schema Explanation

The model is structured like a star schema.

Fact tables sit at the center and store measurable events.

Dimension tables surround the facts and provide descriptive context.

Example:

```text
dim_customer
dim_account
dim_product
dim_branch
dim_channel
dim_date
        ↓
fact_transactions
```

This structure is useful for Power BI because it supports:

* Clean relationships
* Simple filters
* Reliable DAX measures
* Better performance
* Easier stakeholder explanation

## Interview Walkthrough

A clear interview explanation would be:

I started by generating realistic banking data using Python. Then I loaded the data into PostgreSQL raw tables. After that, I created raw data quality checks to validate counts, duplicates, nulls, dates, and relationships. Once the raw layer was validated, I built staging tables to standardize the data and create useful derived fields. Then I created warehouse dimension and fact tables using a star-schema approach. I defined the grain of each fact table clearly to avoid double counting. After building the warehouse, I added final data quality checks to validate joins, dates, and business rules. Finally, I wrote KPI queries to answer business questions around transactions, complaints, SLA performance, campaigns, branches, products, and customers.

## How This Supports Power BI

The SQL model supports Power BI because the warehouse already contains:

* Fact tables
* Dimension tables
* Surrogate keys
* Date dimension
* KPI helper columns
* Clean business fields
* Validated joins

Power BI can connect to these warehouse tables to build:

* KPI cards
* Trend charts
* Channel analysis
* Product analysis
* Customer segment visuals
* Complaint dashboards
* SLA dashboards
* Campaign performance dashboards

## AI-Assisted Development Positioning

AI was used as a productivity assistant during the project.

AI helped draft SQL patterns, validation logic, documentation, and business question framing.

The analyst reviewed the logic, ran the SQL, validated outputs, and confirmed that the project supported business reporting requirements.

This is a practical example of AI-assisted analytics development with human review and control.

## Current Status

The SQL foundation of the project is complete.

Completed:

* Raw layer
* Raw data quality
* Staging layer
* Dimension tables
* Fact tables
* Warehouse data quality checks
* Business KPI queries
* SQL model documentation

Next:

* Power BI semantic model
* Power BI dashboard pages
* DAX measures
* Incremental refresh planning
* Final README polish
