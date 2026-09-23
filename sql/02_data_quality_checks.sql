-- Data-quality and reconciliation checks
-- Goal: prove the reporting layer is trustworthy before using it for KPIs.

-- 1. Duplicate transaction IDs in staging
SELECT
    transaction_id,
    COUNT(*) AS row_count
FROM staging.stg_transactions
GROUP BY transaction_id
HAVING COUNT(*) > 1;


-- 2. Transactions with no matching account
SELECT
    t.transaction_id,
    t.account_id
FROM staging.stg_transactions t
LEFT JOIN staging.stg_accounts a
    ON t.account_id = a.account_id
WHERE a.account_id IS NULL;


-- 3. Transactions with no matching customer
SELECT
    t.transaction_id,
    t.customer_id
FROM staging.stg_transactions t
LEFT JOIN staging.stg_customers c
    ON t.customer_id = c.customer_id
WHERE c.customer_id IS NULL;


-- 4. Missing channel references
SELECT
    COUNT(*) AS missing_channel_rows
FROM staging.stg_transactions
WHERE channel_id IS NULL;


-- 5. Failed transactions with a non-zero fee
SELECT
    transaction_id,
    transaction_status,
    fee_amount
FROM staging.stg_transactions
WHERE transaction_status = 'Failed'
  AND fee_amount > 0;


-- 6. Reconcile trusted staging rows to warehouse rows
SELECT
    (SELECT COUNT(*) FROM staging.stg_transactions) AS staging_rows,
    (SELECT COUNT(*) FROM warehouse.fact_transactions) AS warehouse_rows,
    (
        SELECT COUNT(*) FROM staging.stg_transactions
    ) - (
        SELECT COUNT(*) FROM warehouse.fact_transactions
    ) AS difference;


-- 7. Check warehouse transaction grain
SELECT
    transaction_id,
    COUNT(*) AS row_count
FROM warehouse.fact_transactions
GROUP BY transaction_id
HAVING COUNT(*) > 1;


-- 8. Check for unresolved foreign-key lookups in the reporting fact
SELECT
    COUNT(*) FILTER (WHERE account_key IS NULL) AS missing_account_key,
    COUNT(*) FILTER (WHERE customer_key IS NULL) AS missing_customer_key,
    COUNT(*) FILTER (WHERE channel_key IS NULL) AS missing_channel_key
FROM warehouse.fact_transactions;
