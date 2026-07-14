# Business KPI Queries

## Objective

Create SQL business KPI queries using the warehouse fact and dimension tables.

The goal of this step is to prove that the warehouse model can answer real business questions and support Power BI dashboard development.

## SQL File Created

* `sql/06_business_queries/01_business_kpi_queries.sql`

## Schema Used

* `warehouse`

## Business Areas Covered

The KPI query script covers:

* Executive banking operations summary
* Transaction performance
* Channel performance
* Product performance
* Customer segment analysis
* Branch performance
* Complaint analysis
* SLA performance
* Campaign performance
* Product complaint rate
* Customer 360 view
* Power BI reporting base query

## Key Business Questions Answered

The SQL queries answer questions such as:

* What is the total transaction volume and value?
* What is the transaction success rate?
* Which channels drive the most transactions?
* Which products generate the most transaction value?
* Which customer segments are most active?
* Which branches drive the most transaction value?
* What are the major customer complaint categories?
* Which channels generate the most complaints?
* Are SLA tickets being resolved within target?
* Which teams have higher SLA breaches?
* Which campaigns have better engagement and conversion?
* Which customer segments respond better to campaigns?
* Which products have higher complaint volume compared with transaction activity?
* Which customers have high activity, complaints, and campaign engagement?

## Why This Step Matters

This step connects the technical data model to business value.

Creating fact and dimension tables is not enough by itself. The model must also answer meaningful business questions.

These KPI queries demonstrate that the warehouse is ready for:

* Business analysis
* Interview discussion
* Power BI semantic modeling
* Dashboard layout planning
* KPI measure design
* Executive insight generation

## Star Schema Usage

The queries use the warehouse star schema.

Fact tables provide measurable events:

* Transactions
* Complaints
* Campaign offers
* SLA tickets

Dimension tables provide descriptive context:

* Customers
* Accounts
* Products
* Branches
* Channels
* Dates

Examples:

* `fact_transactions` joins to customer, product, branch, channel, account, and date dimensions
* `fact_complaints` joins to customer, account, product, channel, and date dimensions
* `fact_campaigns` joins to customer, product, channel, and date dimensions
* `fact_sla_tickets` joins to customer, account, and date dimensions

This structure supports clean filtering, grouping, and aggregation for Power BI reporting.

## Power BI Readiness

The business queries help identify the visuals and KPIs that can be built in Power BI.

Possible dashboard sections include:

* Executive KPI cards
* Transaction trend
* Channel performance
* Product performance
* Branch performance
* Complaint categories
* SLA breach analysis
* Campaign conversion analysis
* Customer segment performance
* Product complaint rate
* Customer 360 view

The final query in the script provides a transaction-level reporting dataset that can be used as a reference for building Power BI visuals.

## Important KPI Logic

Examples of KPI logic include:

* Transaction success rate = successful transactions divided by total transactions
* Complaint resolution rate = resolved complaints divided by total complaints
* SLA breach rate = breached SLA tickets divided by total tickets
* Campaign conversion rate = converted customers divided by campaign offers sent
* Complaints per 1,000 transactions = complaints divided by transactions, multiplied by 1,000

These calculations are designed to align with the fact table grain and avoid double counting.

## Interview Explanation

After validating the warehouse, I created business KPI queries to show how the model can answer operational questions. I focused on transaction performance, customer segments, branch activity, complaints, SLA performance, and campaign conversion. These queries helped translate the warehouse model into business insights and also served as a planning layer for Power BI dashboard design.

## AI-Assisted Development Approach

AI assistance was used to accelerate the creation of business KPI query patterns.

The generated SQL was reviewed to ensure that:

* Queries used the warehouse model instead of raw tables
* Business questions were clearly documented
* Aggregations matched the fact table grain
* KPI calculations used correct numerator and denominator logic
* Joins used dimension surrogate keys
* Results could support Power BI dashboard planning

The analyst remained responsible for reviewing the business logic, validating the output, and connecting the results to decision-making.

## Status

Business KPI queries completed successfully.
