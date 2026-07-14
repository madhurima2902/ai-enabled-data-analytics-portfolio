# Customer Master Data Generation

## Objective

Generate the customer master dataset for the Banking Operations Analytics project.

## Output File

`data/raw/raw_customers.csv`

## Target Volume

10,000 customer records.

## Columns Generated

- customer_id
- customer_name
- gender
- date_of_birth
- age_group
- city
- state
- customer_segment
- onboarding_date
- kyc_status
- risk_band

## Business Logic

The customer data represents a synthetic Indian retail banking customer base across major cities.

Customer segmentation uses three categories:

- Mass
- Affluent
- Premium

KYC status uses three categories:

- Complete
- Pending
- Failed

Risk band uses three categories:

- Low
- Medium
- High

## Validation Checks

The validation script checks:

- Row count equals 10,000
- customer_id is unique
- customer_id has no nulls
- customer_name has no nulls
- gender values are valid
- customer_segment values are valid
- kyc_status values are valid
- risk_band values are valid

## Validation Result

All validation checks passed successfully.

## Status

Customer master data generation completed successfully.