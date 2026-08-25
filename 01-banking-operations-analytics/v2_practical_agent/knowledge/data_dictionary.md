# Banking Operations Data Dictionary

## Purpose

This document describes the approved warehouse tables, their grain, important fields, and relationships used by the Banking Operations Agent.

The agent may use this knowledge to understand where operational data comes from and how tables relate to each other.

## Approved Sources

- `sql/04_warehouse_tables/01_create_dimension_tables.sql`
- `sql/04_warehouse_tables/03_create_fact_tables.sql`
- `docs/9_dimension_tables_notes.md`
- `docs/10_fact_tables_notes.md`

## warehouse.fact_transactions

### Purpose

Stores trusted transaction-level banking activity used for transaction KPIs and operational analysis.

### Grain

One row represents one transaction.

### Primary Key

`transaction_key`

### Business Identifier

`transaction_id`

`transaction_id` is unique in the trusted warehouse layer.

### Important Fields

- `transaction_id` — source transaction identifier
- `transaction_datetime` — date and time of the transaction
- `transaction_date` — transaction calendar date
- `transaction_month` — transaction reporting month
- `transaction_type` — type of banking transaction
- `transaction_status` — transaction outcome such as Success or Failed
- `amount` — transaction amount
- `fee_amount` — transaction fee
- `currency` — transaction currency
- `successful_transaction_count` — helper field equal to 1 for a successful transaction
- `failed_transaction_count` — helper field equal to 1 for a failed transaction
- `transaction_count` — helper field equal to 1 for each transaction

### Important Relationships

- `account_key` → `warehouse.dim_account.account_key`
- `customer_key` → `warehouse.dim_customer.customer_key`
- `product_key` → `warehouse.dim_product.product_key`
- `branch_key` → `warehouse.dim_branch.branch_key`
- `channel_key` → `warehouse.dim_channel.channel_key`
- `transaction_date_key` → `warehouse.dim_date.date_key`

### Agent Usage

Use this table as the trusted source for transaction-level questions and transaction KPI calculations.

Examples:

- transaction count
- transaction success rate
- transaction failure rate
- transaction value
- transaction lookup by transaction_id
- transaction trend by time period

## warehouse.dim_channel

### Purpose

Provides descriptive information about the channel through which banking activity occurred.

### Grain

One row represents one channel.

### Primary Key

`channel_key`

### Business Identifier

`channel_id`

### Important Fields

- `channel_id` — source channel identifier
- `channel_name` — business name of the channel
- `channel_category` — channel grouping/category
- `is_digital` — identifies whether the channel is considered digital

### Important Relationships

`warehouse.fact_transactions.channel_key`
→ `warehouse.dim_channel.channel_key`

### Agent Usage

Use this table when transaction or complaint analysis requires channel-level context.

Examples:

- compare failure rate across channels
- identify digital versus non-digital activity
- identify which channel generated the most transactions