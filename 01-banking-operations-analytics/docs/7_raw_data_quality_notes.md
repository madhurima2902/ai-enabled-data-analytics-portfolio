# Raw Data Quality Profiling

## Objective

Profile and validate the PostgreSQL raw layer after loading clean source CSV files into the `raw` schema.

The goal of this step was to confirm that the raw data was complete, usable, and properly related before moving into staging transformations.

## Database

`banking_analytics_db`

## Schema

`raw`

## SQL Files Created

* `sql/02_data_quality/01_raw_profile_checks.sql`
* `sql/02_data_quality/02_raw_relationship_checks.sql`

## Raw Tables Profiled

* raw.customers
* raw.accounts
* raw.products
* raw.branches
* raw.channels
* raw.complaints
* raw.campaigns
* raw.sla_tickets
* raw.transactions

## Profile Checks Performed

The raw profile checks validated:

* Row counts
* Duplicate business IDs
* Null key fields
* Date ranges
* Status and category distributions
* Numeric value ranges

These checks help confirm whether the raw data is complete and structurally usable before applying staging transformations.

## Relationship Checks Performed

The relationship checks validated whether records across raw tables can be joined correctly.

Checks included:

* Accounts link to valid customers
* Accounts link to valid products
* Accounts link to valid branches
* Complaints link to valid customers, accounts, products, and channels
* Campaigns link to valid customers, products, and channels
* SLA tickets link to valid complaints, customers, and accounts
* Transactions link to valid accounts, customers, products, branches, and channels

## Cross-Field Consistency Checks

Additional checks validated whether related fields were consistent across linked records.

Examples:

* Transaction customer matches the customer linked to the account
* Transaction product matches the product linked to the account
* Transaction branch matches the branch linked to the account
* Complaint customer matches the customer linked to the account
* Complaint product matches the product linked to the account

## Validation Result

The raw data quality checks completed successfully.

The clean raw datasets passed the baseline validation checks for:

* Completeness
* Uniqueness
* Null key checks
* Valid date ranges
* Valid category distributions
* Referential consistency
* Cross-field consistency

## Why This Step Matters

This step acts as a quality checkpoint between raw data loading and staging transformations.

In a real analytics environment, dashboards should not be built directly on unverified raw data. Profiling the raw layer helps identify issues early, before they affect Power BI reports, KPIs, business users, or downstream warehouse tables.

## AI-Assisted Development Approach

AI assistance was used to accelerate the creation of reusable SQL profiling and relationship-check patterns.

The generated SQL was reviewed to ensure that:

* The checks matched the raw table structures
* Key business IDs were checked for duplicates and nulls
* Row count expectations matched the generated datasets
* Relationship checks matched the intended data model
* Cross-field consistency checks supported downstream reporting accuracy
* The SQL remained readable and reusable for future data-quality testing

This approach demonstrates practical AI-assisted analytics development, where AI helps speed up repetitive SQL development while the analyst remains responsible for reviewing the logic, validating the output, and understanding the business purpose of each check.

## Status

Raw data quality profiling completed successfully.
