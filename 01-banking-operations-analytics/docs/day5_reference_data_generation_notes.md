# Reference Data Generation

## Objective

Generate reference/master data files for products, branches, and channels for the Banking Operations Analytics project.

## Output Files

* `data/raw/raw_products.csv`
* `data/raw/raw_branches.csv`
* `data/raw/raw_channels.csv`

## Products

The products file contains seven banking products:

* Savings Account
* Current Account
* Salary Account
* Fixed Deposit
* Credit Card
* Personal Loan
* Home Loan

## Branches

The branches file contains 20 synthetic Indian retail banking branches across major cities.

Branch attributes include:

* branch_id
* branch_name
* city
* state
* region
* branch_type

## Channels

The channels file contains six banking transaction/service channels:

* Mobile Banking
* Internet Banking
* ATM
* Branch
* POS
* Call Center

## Business Logic

The reference data provides controlled lookup values for downstream account, transaction, complaint, campaign, and SLA datasets.

Product IDs and branch IDs are intentionally aligned with the account generation logic so that account records can be validated against product and branch reference data.

The channel reference data will be used in later transaction generation and reporting to support analysis by digital, physical, assisted, and merchant channels.

## Validation Checks

The validation script checks:

* Product row count equals 7
* Branch row count equals 20
* Channel row count equals 6
* Product IDs are unique
* Branch IDs are unique
* Channel IDs are unique
* Product IDs have no nulls
* Branch IDs have no nulls
* Channel IDs have no nulls
* Product names have no nulls
* Branch names have no nulls
* Channel names have no nulls
* Account product IDs exist in the product reference file
* Account branch IDs exist in the branch reference file

## Validation Result

All reference data validation checks passed successfully.

Reference data generated:

* Products: 7
* Branches: 20
* Channels: 6

## AI-Assisted Dataset Generation Approach

This reference data was generated using Python with AI assistance to accelerate the creation of structured synthetic banking master data.

AI was used as a productivity assistant to help draft the initial Python structure for creating product, branch, and channel reference datasets, along with validation checks for row counts, uniqueness, null handling, and referential consistency with the account dataset.

The generated code was reviewed before execution to ensure that:

* Product IDs match the account generation logic
* Branch IDs match the account generation logic
* Channel values are realistic for retail banking operations
* Reference data supports downstream warehouse modeling
* Validation logic is separated from generation logic
* Account product and branch references are checked against the generated master data

The dataset was then validated using a separate Python validation script. This helped confirm that reference data was complete, unique, non-null, and aligned with the previously generated account dataset.

This approach demonstrates practical AI-assisted analytics development, where AI helps reduce manual setup time while the analyst remains responsible for reviewing business logic, validating outputs, and ensuring the generated data supports downstream analytics use cases.

## Status

Reference data generation completed successfully.
