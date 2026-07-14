# January Transaction Data Generation

## Objective

Generate the clean January transaction dataset for the Banking Operations Analytics project.

## Output File

`data/raw/raw_transactions_jan.csv`

## Target Volume

25,000 transaction records.

## Input Files Used

- `data/raw/raw_accounts.csv`
- `data/raw/raw_channels.csv`

## Columns Generated

- transaction_id
- account_id
- customer_id
- product_id
- branch_id
- channel_id
- transaction_datetime
- transaction_type
- transaction_status
- amount
- fee_amount
- currency
- balance_after_transaction

## Business Logic

The January transaction dataset represents retail banking transaction activity across customer accounts, products, branches, and service channels.

Each transaction is linked to an existing account. Customer, product, and branch values are inherited from the account dataset to maintain clean referential consistency.

The dataset includes multiple transaction types such as deposits, withdrawals, transfers, bill payments, card payments, UPI payments, ATM withdrawals, fee debits, interest credits, and loan EMI payments.

Transaction statuses include successful, failed, and reversed transactions.

For this clean dataset version, failed transactions do not have fees charged. Controlled real-world data quality issues will be introduced later in a separate step.

## Validation Checks

The validation script checks:

- Row count equals 25,000
- transaction_id is unique
- transaction_id has no nulls
- account_id has no nulls
- customer_id has no nulls
- all transaction accounts exist in account master data
- all transaction channels exist in channel reference data
- transaction types are valid
- transaction statuses are valid
- all transactions are in January 2026
- amount is positive
- fee amount is non-negative
- balance after transaction is non-negative
- failed transactions have zero fee
- transaction customer matches account customer
- transaction product matches account product
- transaction branch matches account branch

## AI-Assisted Dataset Generation Approach

This transaction dataset was generated using Python with AI assistance to accelerate the creation of realistic synthetic banking transaction data.

AI was used as a productivity assistant to help draft the Python structure for transaction generation, including transaction type distributions, randomized transaction amounts, transaction status logic, fee calculation rules, and validation checks.

The generated code was reviewed before execution to ensure that:

- Transactions link to valid accounts
- Customer, product, and branch values align with the account dataset
- Channel values come from the channel reference dataset
- Transaction dates fall within January 2026
- Amount and fee fields follow reasonable business rules
- Failed transactions do not have fees in the clean dataset version
- Validation logic is separated from generation logic

The dataset was then validated using a separate Python validation script. This helped confirm row count, uniqueness, referential integrity, valid transaction values, date consistency, and business rule consistency.

This approach demonstrates practical AI-assisted analytics development, where AI helps reduce manual coding time while the analyst remains responsible for reviewing business rules, validating outputs, and ensuring the generated data is fit for downstream SQL, warehouse modeling, and Power BI reporting.

## Status

January transaction data generation completed successfully.