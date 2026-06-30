# Day 4: Account Master Data Generation

## Objective

Generate the account master dataset for the Banking Operations Analytics project.

## Input File

`data/raw/raw_customers.csv`

## Output File

`data/raw/raw_accounts.csv`

## Target Volume

15,000 account records.

## Columns Generated

* account_id
* customer_id
* product_id
* branch_id
* account_open_date
* account_status
* current_balance
* interest_rate
* credit_limit

## Business Logic

Each account is linked to an existing customer using `customer_id`.

The account dataset supports multiple accounts per customer. Product IDs and branch IDs are generated using planned reference IDs that will be created in the reference data generation step.

The account generation logic includes product-specific balance ranges, interest rate ranges, and credit limit logic. This helps make the simulated data more realistic for banking analytics use cases.

## Products Used

* PROD001: Savings Account
* PROD002: Current Account
* PROD003: Salary Account
* PROD004: Fixed Deposit
* PROD005: Credit Card
* PROD006: Personal Loan
* PROD007: Home Loan

## Validation Checks

The validation script checks:

* Row count equals 15,000
* account_id is unique
* account_id has no nulls
* customer_id has no nulls
* all account customer IDs exist in `raw_customers.csv`
* product IDs are valid
* branch IDs are valid
* account status values are valid
* current balance is non-negative
* interest rate is non-negative
* account open date is not before customer onboarding date

## Validation Result

All account validation checks passed successfully.

Total rows generated: 15,000
Unique customers with accounts: 7,750

## AI-Assisted Dataset Generation Approach

This dataset was generated using Python with AI assistance to accelerate the creation of realistic synthetic banking data.

AI was used as a productivity assistant to help draft the initial Python structure, including account generation logic, reusable functions, randomized distributions, product-specific balance ranges, interest rate rules, credit limit logic, and validation checks.

The generated code was reviewed before execution to ensure that:

* Account IDs are unique
* Each account is linked to an existing customer
* Product IDs follow the planned banking product reference structure
* Branch IDs follow the planned branch reference structure
* Account open dates are not earlier than customer onboarding dates
* Numeric fields such as current balance, interest rate, and credit limit are reasonable for the account/product type
* Validation checks are separated from generation logic
* Generated data supports downstream warehouse modeling and Power BI reporting

The dataset was then validated using a separate Python validation script. This helped confirm row count, uniqueness, referential integrity, valid categories, non-negative numeric values, and date consistency.

This approach demonstrates practical AI-assisted analytics development, where AI helps reduce manual coding time while the analyst remains responsible for reviewing logic, validating outputs, and ensuring business rules are correctly applied.

## Status

Account master data generation completed successfully.
