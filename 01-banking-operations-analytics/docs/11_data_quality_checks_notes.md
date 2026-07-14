# Warehouse Data Quality Checks

## Objective

Create final warehouse-level data quality checks after raw, staging, dimension, and fact tables have been created.

The goal of this step is to validate that the reporting warehouse is reliable before using it for business KPI queries and Power BI reporting.

## SQL File Created

* `sql/05_data_quality_checks/01_warehouse_data_quality_checks.sql`

## Schemas Used

* `warehouse`

## Tables Validated

### Dimension Tables

* `warehouse.dim_customer`
* `warehouse.dim_account`
* `warehouse.dim_product`
* `warehouse.dim_branch`
* `warehouse.dim_channel`
* `warehouse.dim_date`

### Fact Tables

* `warehouse.fact_transactions`
* `warehouse.fact_complaints`
* `warehouse.fact_campaigns`
* `warehouse.fact_sla_tickets`

## Checks Performed

The warehouse data quality script validates:

* Warehouse table row-count sanity
* Fact-to-dimension orphan records
* Date key consistency
* Transaction business rules
* Complaint business rules
* Campaign business rules
* SLA ticket business rules
* Natural key consistency between facts and dimensions

## Key Validation Areas

### 1. Row Count Sanity

The script checks that all important dimension and fact tables have records.

This helps confirm that the warehouse load process created usable reporting tables.

### 2. Fact-to-Dimension Integrity

The script checks whether fact rows successfully connect back to their related dimension rows.

Examples:

* Transactions must connect to customer, account, product, branch, channel, and date dimensions.
* Complaints must connect to customer and account dimensions.
* Campaigns must connect to customer dimensions.
* SLA tickets must connect to customer and account dimensions.

### 3. Date Key Consistency

The script validates that date keys in fact tables correctly match the actual business dates.

Examples:

* `transaction_date_key` must match `transaction_date`
* `complaint_date_key` must match `complaint_date`
* `sent_date_key` must match `sent_date`
* SLA created, due, and resolved date keys must match their respective datetime fields

### 4. Transaction Business Rules

Transaction checks include:

* Amount should not be null or negative
* Fee amount should not be null or negative
* Fee amount should not exceed transaction amount
* Transaction status should be populated
* Transaction type should be populated
* Currency should be populated

### 5. Complaint Business Rules

Complaint checks include:

* Complaint category should be populated
* Complaint priority should be populated
* Complaint status should be populated
* Resolved complaints should have a resolution date
* Resolution date should not be before complaint date
* Resolution days should not be negative
* Resolution days should match the date difference

### 6. Campaign Business Rules

Campaign checks include:

* Campaign name should be populated
* Campaign type should be populated
* Response status should be populated
* Response date should not be before sent date
* Converted campaigns should have `converted_count = 1`
* Non-converted campaigns should have `converted_count = 0`

### 7. SLA Ticket Business Rules

SLA checks include:

* Ticket priority should be populated
* Ticket status should be populated
* Assigned team should be populated
* SLA target hours should be positive
* Due datetime should not be before created datetime
* Resolved datetime should not be before created datetime
* Resolved ticket flag should match resolved datetime
* SLA met flag should match due/resolution timing

### 8. Natural Key Consistency

The script checks that surrogate keys still match the correct natural business IDs.

Examples:

* Transaction `account_key` should match the transaction `account_id`
* Transaction `customer_key` should match the transaction `customer_id`
* Complaint `account_key` should match the complaint `account_id`
* SLA `customer_key` should match the SLA `customer_id`

## Validation Result

The warehouse data quality checks passed successfully.

This confirms that:

* Warehouse tables are populated
* Fact records are connected to dimensions
* Date keys are consistent
* Key business rules are valid
* KPI reporting can proceed safely
* The warehouse is ready for business query development

## Why This Step Matters

This step protects the quality of downstream analytics.

Without warehouse-level validation, Power BI reports may show incorrect KPIs due to missing joins, invalid dates, duplicate records, negative values, or broken business logic.

By validating the warehouse before creating business KPI queries, the project demonstrates an analyst’s ability to think beyond query writing and ensure reporting trustworthiness.

## Interview Explanation

After creating the warehouse fact and dimension tables, I added a final data quality layer to validate the reporting model. These checks confirmed that fact records were connected to dimensions, date keys matched source dates, transaction and SLA business rules were valid, and no important reporting fields were missing. This gave me confidence that the warehouse was ready for KPI queries and Power BI reporting.

## AI-Assisted Development Approach

AI assistance was used to accelerate the drafting of warehouse-level data quality checks.

The checks were reviewed to ensure that:

* They aligned with the warehouse star schema
* They validated real reporting risks
* They covered both technical and business-rule quality
* They supported trust in downstream Power BI dashboards

The analyst remained responsible for reviewing the validation logic, running the checks, interpreting the results, and confirming that the warehouse was ready for business analysis.

## Status

Warehouse data quality checks completed successfully.
