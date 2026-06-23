# Initial Schema Draft

## Purpose

This document defines the initial raw schema design for the Banking Operations Analytics project.

The schema may evolve during development, but this draft provides the starting structure for Python data generation, PostgreSQL table creation, staging transformations, warehouse modeling, and Power BI reporting.

## Raw Tables

## raw_customers

Stores customer master data.

| Column           | Description                                      |
| ---------------- | ------------------------------------------------ |
| customer_id      | Unique customer identifier                       |
| customer_name    | Customer full name                               |
| gender           | Customer gender                                  |
| date_of_birth    | Customer date of birth                           |
| age_group        | Derived age group                                |
| city             | Customer city                                    |
| state            | Customer state                                   |
| customer_segment | Customer segment such as Mass, Affluent, Premium |
| onboarding_date  | Date customer joined the bank                    |
| kyc_status       | KYC completion status                            |
| risk_band        | Customer risk category                           |

## raw_accounts

Stores account-level information.

| Column          | Description                           |
| --------------- | ------------------------------------- |
| account_id      | Unique account identifier             |
| customer_id     | Customer linked to the account        |
| product_id      | Product linked to the account         |
| branch_id       | Branch where account was opened       |
| account_type    | Type of account                       |
| open_date       | Account opening date                  |
| account_status  | Active, Closed, Dormant, or Suspended |
| current_balance | Current account balance               |

## raw_products

Stores banking product reference data.

| Column           | Description                         |
| ---------------- | ----------------------------------- |
| product_id       | Unique product identifier           |
| product_name     | Product name                        |
| product_category | Product category                    |
| fee_rate         | Fee percentage or rate              |
| is_active        | Indicates whether product is active |

## raw_branches

Stores branch reference data.

| Column      | Description              |
| ----------- | ------------------------ |
| branch_id   | Unique branch identifier |
| branch_name | Branch name              |
| city        | Branch city              |
| state       | Branch state             |
| region      | Business region          |

## raw_channels

Stores transaction channel reference data.

| Column       | Description                                                     |
| ------------ | --------------------------------------------------------------- |
| channel_id   | Unique channel identifier                                       |
| channel_name | Channel name such as Mobile, ATM, Branch, Internet Banking, UPI |

## raw_transactions

Stores transaction activity.

| Column             | Description                           |
| ------------------ | ------------------------------------- |
| transaction_id     | Unique transaction identifier         |
| account_id         | Account linked to transaction         |
| transaction_date   | Date of transaction                   |
| transaction_type   | Type of transaction                   |
| transaction_status | Success, Failed, Reversed, or Pending |
| amount             | Transaction amount                    |
| fee_amount         | Fee charged on transaction            |
| channel_id         | Channel used for transaction          |
| branch_id          | Branch linked to transaction          |
| file_month         | Source file month                     |
| load_date          | Date when data was loaded             |

## raw_complaints

Stores customer complaint records.

| Column             | Description                            |
| ------------------ | -------------------------------------- |
| complaint_id       | Unique complaint identifier            |
| customer_id        | Customer who raised complaint          |
| account_id         | Account linked to complaint            |
| complaint_date     | Complaint creation date                |
| complaint_category | Complaint type or category             |
| complaint_status   | Open, In Progress, Resolved, or Closed |
| resolution_date    | Date complaint was resolved            |
| branch_id          | Branch linked to complaint             |
| channel_id         | Complaint channel                      |

## raw_campaigns

Stores marketing campaign records.

| Column              | Description                                |
| ------------------- | ------------------------------------------ |
| campaign_id         | Unique campaign identifier                 |
| customer_id         | Customer targeted in campaign              |
| campaign_name       | Campaign name                              |
| campaign_channel    | Channel used for campaign                  |
| campaign_start_date | Campaign start date                        |
| campaign_response   | Customer response                          |
| converted_flag      | Indicates whether customer converted       |
| conversion_amount   | Revenue or value generated from conversion |

## raw_sla_tickets

Stores SLA tracking records for operational tickets.

| Column                 | Description                        |
| ---------------------- | ---------------------------------- |
| ticket_id              | Unique ticket identifier           |
| complaint_id           | Complaint linked to the SLA ticket |
| opened_date            | Ticket opened date                 |
| closed_date            | Ticket closed date                 |
| sla_target_days        | SLA target in days                 |
| actual_resolution_days | Actual days taken to resolve       |
| sla_met_flag           | Indicates whether SLA was met      |

## Planned Warehouse Tables

## Dimension Tables

* dim_customer
* dim_account
* dim_product
* dim_branch
* dim_channel
* dim_date

## Fact Tables

* fact_transactions
* fact_complaints
* fact_campaigns
* fact_sla_tickets

## Key Relationships

* raw_customers.customer_id → raw_accounts.customer_id
* raw_accounts.account_id → raw_transactions.account_id
* raw_products.product_id → raw_accounts.product_id
* raw_branches.branch_id → raw_accounts.branch_id
* raw_branches.branch_id → raw_transactions.branch_id
* raw_channels.channel_id → raw_transactions.channel_id
* raw_customers.customer_id → raw_complaints.customer_id
* raw_accounts.account_id → raw_complaints.account_id
* raw_complaints.complaint_id → raw_sla_tickets.complaint_id
* raw_customers.customer_id → raw_campaigns.customer_id

## Notes

This schema is intentionally designed to support:

* Customer analytics
* Transaction analytics
* Product analytics
* Branch analytics
* Channel analytics
* Complaint analytics
* Campaign analytics
* SLA analytics
* Incremental refresh simulation
* Data quality checks
* Power BI reporting
