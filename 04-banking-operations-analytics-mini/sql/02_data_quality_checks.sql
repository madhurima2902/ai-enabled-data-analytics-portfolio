/*
PROJECT WALKTHROUGH — DATA QUALITY AND RECONCILIATION

How I explain this file:
Before I trust a dashboard, I want evidence that the reporting data is complete, internally consistent, and connected correctly.

These checks answer business-friendly questions:
1. Are any transaction IDs duplicated?
2. Does every transaction point to a valid account and customer?
3. Are important references such as channel missing?
4. Do failed transactions follow the expected fee rule?
5. Do staging and warehouse row counts reconcile?
6. Does the final fact table still preserve one row per transaction?
7. Did any dimension lookups fail?

I do not automatically delete an exception just because a query finds it.
I first investigate whether the issue comes from the source, the load,
a mapping problem, or a legitimate business exception.
*/

-- ============================================================
-- 1. DUPLICATE TRANSACTION IDs
-- Business question:
-- Is the identifier that should represent one transaction appearing
-- more than once in the validated staging data?
-- HAVING is used because I am filtering after GROUP BY.
-- ============================================================
SELECT
    transaction_id,
    COUNT(*) AS row_count
FROM staging.stg_transactions
GROUP BY transaction_id
HAVING COUNT(*) > 1;


-- ============================================================
-- 2. TRANSACTIONS WITH NO MATCHING ACCOUNT
-- Business question:
-- Does any transaction reference an account that does not exist?
-- LEFT JOIN keeps all transactions; NULL on the account side identifies
-- the transactions for which no account match was found.
-- ============================================================
SELECT
    t.transaction_id,
    t.account_id
FROM staging.stg_transactions t
LEFT JOIN staging.stg_accounts a
    ON t.account_id = a.account_id
WHERE a.account_id IS NULL;


-- ============================================================
-- 3. TRANSACTIONS WITH NO MATCHING CUSTOMER
-- This performs the same referential check at the customer level.
-- ============================================================
SELECT
    t.transaction_id,
    t.customer_id
FROM staging.stg_transactions t
LEFT JOIN staging.stg_customers c
    ON t.customer_id = c.customer_id
WHERE c.customer_id IS NULL;


-- ============================================================
-- 4. MISSING CHANNEL REFERENCES
-- Business question:
-- Can every transaction be assigned to the channel used for reporting?
-- A missing channel may affect channel-level KPIs even if the
-- transaction itself is otherwise valid.
-- ============================================================
SELECT
    COUNT(*) AS missing_channel_rows
FROM staging.stg_transactions
WHERE channel_id IS NULL;


-- ============================================================
-- 5. FAILED TRANSACTIONS WITH A NON-ZERO FEE
-- Business rule being tested:
-- In this project, a failed transaction should not retain a fee.
-- Any returned row becomes a data-quality exception for investigation.
-- ============================================================
SELECT
    transaction_id,
    transaction_status,
    fee_amount
FROM staging.stg_transactions
WHERE transaction_status = 'Failed'
  AND fee_amount > 0;


-- ============================================================
-- 6. STAGING-TO-WAREHOUSE RECONCILIATION
-- How I explain it:
-- If validated records enter the transformation layer, I want to know
-- how many reach the reporting layer. A non-zero difference must be
-- explainable before I trust the downstream KPI.
-- ============================================================
SELECT
    (SELECT COUNT(*) FROM staging.stg_transactions) AS staging_rows,
    (SELECT COUNT(*) FROM warehouse.fact_transactions) AS warehouse_rows,
    (
        SELECT COUNT(*) FROM staging.stg_transactions
    ) - (
        SELECT COUNT(*) FROM warehouse.fact_transactions
    ) AS difference;


-- ============================================================
-- 7. CHECK THE WAREHOUSE TRANSACTION GRAIN
-- Expected grain: one row per transaction_id.
-- If this query returns rows, the reporting fact contains duplicates
-- and transaction KPIs may be inflated.
-- ============================================================
SELECT
    transaction_id,
    COUNT(*) AS row_count
FROM warehouse.fact_transactions
GROUP BY transaction_id
HAVING COUNT(*) > 1;


-- ============================================================
-- 8. UNRESOLVED DIMENSION LOOKUPS
-- Business question:
-- Did any transaction reach the reporting layer without the dimension
-- keys needed for account/customer/channel analysis?
-- FILTER lets me count each type of unresolved relationship separately.
-- ============================================================
SELECT
    COUNT(*) FILTER (WHERE account_key IS NULL) AS missing_account_key,
    COUNT(*) FILTER (WHERE customer_key IS NULL) AS missing_customer_key,
    COUNT(*) FILTER (WHERE channel_key IS NULL) AS missing_channel_key
FROM warehouse.fact_transactions;
