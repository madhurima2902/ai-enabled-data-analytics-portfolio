# Architecture

## Overview

This project follows a layered analytics architecture that simulates how operational banking data moves from source files into a reporting-ready warehouse model.

The architecture is designed to show practical data analyst capabilities across data generation, ingestion, cleaning, validation, modeling, reporting, and stakeholder communication.

## Architecture Flow

Python Source Data Generator
→ Monthly CSV Files
→ PostgreSQL Raw Layer
→ PostgreSQL Staging Layer
→ Data Quality Checks
→ PostgreSQL Warehouse Layer
→ Power BI Semantic Model
→ Power BI Dashboards
→ Business Insights and Stakeholder Reporting

## 1. Source Data Layer

The source system is simulated using Python-generated CSV files.

The purpose of this layer is to create realistic banking operational data without depending on public datasets.

Source files include:

* raw_customers.csv
* raw_accounts.csv
* raw_products.csv
* raw_branches.csv
* raw_channels.csv
* raw_transactions_jan.csv
* raw_transactions_feb.csv
* raw_transactions_mar_refresh.csv
* raw_complaints.csv
* raw_campaigns.csv
* raw_sla_tickets.csv

## 2. Raw Layer

The raw layer stores source data in PostgreSQL with minimal transformation.

Purpose:

* Preserve the original source structure
* Support auditability
* Allow comparison between raw and cleaned data
* Capture source-level data quality issues
* Simulate a landing zone used in real analytics environments

Example raw tables:

* raw_customers
* raw_accounts
* raw_products
* raw_branches
* raw_channels
* raw_transactions
* raw_complaints
* raw_campaigns
* raw_sla_tickets

## 3. Staging Layer

The staging layer standardizes, cleans, and validates raw data before loading it into the warehouse.

Staging activities include:

* Standardizing transaction statuses
* Standardizing branch names
* Standardizing channel values
* Handling null transaction types
* Flagging duplicate transaction IDs
* Validating customer-account relationships
* Validating product references
* Validating branch references
* Creating business-rule flags
* Preparing clean data for reporting

Example staging tables:

* stg_customers
* stg_accounts
* stg_products
* stg_branches
* stg_channels
* stg_transactions
* stg_complaints
* stg_campaigns
* stg_sla_tickets

## 4. Data Quality Layer

The data quality layer contains SQL checks used to identify and document source data problems.

Planned checks include:

* Duplicate transaction detection
* Missing customer reference detection
* Missing account reference detection
* Null transaction type validation
* Invalid transaction amount validation
* Failed transaction fee validation
* Invalid branch validation
* Invalid channel validation
* SLA breach validation
* Campaign conversion validation

Data quality issues are intentionally injected into monthly files to create realistic interview discussion points.

## 5. Warehouse Layer

The warehouse layer contains reporting-ready fact and dimension tables.

This layer is designed for Power BI reporting and business KPI calculation.

Dimension tables:

* dim_customer
* dim_account
* dim_product
* dim_branch
* dim_channel
* dim_date

Fact tables:

* fact_transactions
* fact_complaints
* fact_campaigns
* fact_sla_tickets

## 6. Incremental Refresh Simulation

The project simulates monthly data refresh using transaction files.

Planned refresh flow:

1. Load January transaction file
2. Load February transaction file
3. Generate March refresh file
4. Include late-arriving February transactions in March file
5. Load March refresh data
6. Validate duplicate and late-arriving records
7. Update warehouse reporting tables

This demonstrates how reporting systems handle new monthly data and delayed operational records.

## 7. Reporting Layer

Power BI connects to PostgreSQL warehouse tables.

Dashboard pages:

1. Executive Overview
2. Customer Analytics
3. Product & Channel Analytics
4. Operational Risk & Complaints
5. Campaign Effectiveness

## 8. Business KPI Layer

Planned KPIs include:

* Total Transaction Amount
* Total Fee Revenue
* Active Customers
* Transaction Count
* Successful Transaction Count
* Failed Transaction Count
* Success Rate
* Failed Transaction Rate
* Revenue per Customer
* Month-over-Month Revenue Growth
* Complaint Count
* Complaint Rate
* SLA Breach Rate
* Campaign Conversion Rate

## 9. AI-Assisted Analytics Layer

AI tools may be used to support:

* SQL query drafting
* SQL debugging
* Documentation drafting
* KPI explanation
* Business insight summarization
* Dashboard narrative creation
* Stakeholder ticket creation

AI is used as a productivity assistant, not as a replacement for understanding the data model, SQL logic, or business context.

## Final Architecture Goal

The final project should clearly demonstrate the ability to move from messy operational source data to reliable business reporting through a structured analytics pipeline.
