# Project Scope

## Project Name

Banking Operations Analytics

## Project Objective

Build an end-to-end retail banking analytics project that simulates a realistic operational data environment using Python-generated source data, PostgreSQL, SQL transformations, data quality checks, incremental loading, and Power BI dashboards.

The project is designed to demonstrate practical data analyst skills for banking, fintech, GCC, business intelligence, and operations analytics roles.

## Business Context

A retail bank wants to improve visibility into customer activity, transaction behavior, product usage, complaints, campaign effectiveness, and operational risk.

The analytics team is responsible for creating a reliable reporting layer that allows business stakeholders to track KPIs, identify risks, and make data-driven decisions.

## Business Problems Addressed

This project will answer questions such as:

* How are transaction volumes and revenue changing month over month?
* Which customer segments generate the highest transaction value?
* Which products and channels are performing best?
* Which branches have high failed transaction rates?
* Which complaint categories are increasing?
* Are complaints being resolved within SLA?
* Which campaigns are converting customers?
* How does incremental monthly data refresh affect reporting?

## Stakeholders

* Executive Leadership
* CFO / Finance Team
* Operations Team
* Marketing Team
* Customer Experience Team
* Branch Performance Team

## Tools and Technologies

* Python
* Pandas
* NumPy
* Faker
* PostgreSQL
* pgAdmin4
* SQL
* Power BI
* DAX
* GitHub

## Data Sources

The primary data source is synthetic banking data generated using Python.

Planned source files:

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

## Data Volume

Planned Version 1 volume:

* Customers: 10,000
* Accounts: 15,000
* January Transactions: 25,000
* February Transactions: 30,000
* March Refresh Transactions: 35,000
* Complaints: approximately 2,000
* Campaign records: approximately 5,000
* SLA tickets: approximately 4,000

## Project Scope

### In Scope

* Python-based synthetic banking data generation
* Monthly CSV source file simulation
* PostgreSQL database creation
* Raw data layer
* Staging data layer
* Warehouse data layer
* Data quality checks
* Incremental refresh simulation
* Late-arriving transaction handling
* Business SQL analysis
* Window function examples
* Power BI dashboard
* KPI definitions
* Stakeholder-focused documentation
* Interview-ready project explanation

### Out of Scope for Version 1

* Real-time data streaming
* Cloud deployment
* Full orchestration using Airflow or similar tools
* Advanced machine learning models
* Production-grade security implementation
* External RBI, Data.gov, or FRED integration
* Fabric implementation

These can be added later as enhancements after Version 1 is complete.

## Planned Dashboard Pages

1. Executive Overview
2. Customer Analytics
3. Product & Channel Analytics
4. Operational Risk & Complaints
5. Campaign Effectiveness

## Key Skills Demonstrated

* SQL joins
* Aggregations
* CTEs
* Window functions
* Data quality checks
* Referential integrity validation
* Incremental loading logic
* Fact and dimension modeling
* KPI calculation
* Power BI dashboarding
* Business storytelling
* AI-assisted documentation and analysis

## Version 1 Success Criteria

The project will be considered complete when it includes:

* Python-generated banking source data
* PostgreSQL raw tables
* PostgreSQL staging tables
* PostgreSQL warehouse tables
* Data quality validation queries
* Incremental refresh simulation
* SQL business analysis queries
* Power BI dashboard with 5 pages
* Data dictionary
* KPI definitions
* Architecture documentation
* GitHub repository cleanup
* 2-minute and 5-minute interview explanation
