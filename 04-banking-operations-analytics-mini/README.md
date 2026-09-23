# Retail Banking Operations Analytics — Data Management & Reporting Mini

This is a **learning project** focused on the data management and reporting side of retail banking operations. It is a deliberately smaller version of the broader banking project so the core workflow—profiling, validation, modeling, analysis, and reporting—can be reviewed clearly without unrelated AI/agent components.

## What I wanted to learn

I wanted to go beyond importing a clean CSV directly into Power BI and understand more of what happens before reporting:

- how source data is profiled and checked
- how raw data is loaded into PostgreSQL
- how SQL is used for validation, reconciliation, and transformations
- how fact and dimension tables support reporting
- how operational KPIs are defined and investigated in Power BI

## Tools

- **Python / Pandas** — source-data profiling and basic validation
- **PostgreSQL** — relational database
- **SQL** — data-quality checks, warehouse transformations, and KPI queries
- **Power BI** — operational reporting and visualization
- **Git / GitHub** — version control

## Project scope

The mini version focuses on five related data areas:

- Customers
- Accounts
- Transactions
- Complaints
- SLA / service tickets

The data is synthetic and was created for learning and portfolio use.

## Data flow

```text
Synthetic CSV files
        ↓
Python / Pandas
profiling + basic checks
        ↓
PostgreSQL raw / staging data
        ↓
SQL validation + transformation
        ↓
Reporting model
facts + dimensions
        ↓
Power BI
operational KPIs
```

## Reporting model

### Fact tables

- **fact_transactions** — one row per transaction
- **fact_complaints** — one row per complaint
- **fact_sla_tickets** — one row per service ticket

### Dimensions

- **dim_customer**
- **dim_account**
- **dim_branch**
- **dim_channel**
- **dim_date**

Being explicit about **grain** was important because an incorrect join can duplicate event rows and distort KPIs.

## Data-quality checks demonstrated

The project includes examples of:

- duplicate transaction IDs
- missing values
- orphan account/customer references
- row-count reconciliation
- failed transactions with unexpected fees
- missing channel references
- reporting-model integrity checks

I treat exceptions as something to **investigate first**, rather than automatically deleting or filling them.

## Example business questions

The reporting layer is designed to answer questions such as:

- What is the transaction success / failure rate?
- Which channels have higher failure rates?
- Which complaint categories are most common?
- What is the complaint resolution rate?
- Which support teams have higher SLA breach rates?
- Where should an operations team investigate process issues?

## Power BI examples

### Executive overview

![Executive Overview](assets/01_executive_overview.png)

### Channel performance

![Channel Performance](assets/02_channel_performance.png)

### Complaints

![Complaints Analysis](assets/03_complaints_analysis.png)

### SLA performance

![SLA Performance](assets/04_sla_performance.png)

## Repository structure

```text
.
├── README.md
├── requirements.txt
├── python/
│   └── profile_source_data.py
├── sql/
│   ├── 01_reporting_model.sql
│   ├── 02_data_quality_checks.sql
│   └── 03_business_queries.sql
├── docs/
│   └── DATA_MODEL.md
└── assets/
    ├── 01_executive_overview.png
    ├── 02_channel_performance.png
    ├── 03_complaints_analysis.png
    └── 04_sla_performance.png
```

## What this project does not claim

This is not presented as a production banking system. I built it in a controlled learning environment where I know the data and schema. The next experience I want is working in an existing client environment where schemas, refresh dependencies, change controls, failures, and downstream users already exist.
