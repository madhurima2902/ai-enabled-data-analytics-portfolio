-- Validate warehouse dimension tables
-- Purpose: Confirm warehouse dimension tables are complete, unique, and join-ready.

-- ============================================================
-- 1. Row count comparison: staging vs warehouse dimensions
-- ============================================================

SELECT
    'dim_customer' AS dimension_name,
    (SELECT COUNT(*) FROM staging.stg_customers) AS staging_rows,
    (SELECT COUNT(*) FROM warehouse.dim_customer) AS warehouse_rows,
    CASE
        WHEN (SELECT COUNT(*) FROM staging.stg_customers) = (SELECT COUNT(*) FROM warehouse.dim_customer)
        THEN 'PASSED'
        ELSE 'FAILED'
    END AS validation_status

UNION ALL

SELECT
    'dim_account' AS dimension_name,
    (SELECT COUNT(*) FROM staging.stg_accounts) AS staging_rows,
    (SELECT COUNT(*) FROM warehouse.dim_account) AS warehouse_rows,
    CASE
        WHEN (SELECT COUNT(*) FROM staging.stg_accounts) = (SELECT COUNT(*) FROM warehouse.dim_account)
        THEN 'PASSED'
        ELSE 'FAILED'
    END AS validation_status

UNION ALL

SELECT
    'dim_product' AS dimension_name,
    (SELECT COUNT(*) FROM staging.stg_products) AS staging_rows,
    (SELECT COUNT(*) FROM warehouse.dim_product) AS warehouse_rows,
    CASE
        WHEN (SELECT COUNT(*) FROM staging.stg_products) = (SELECT COUNT(*) FROM warehouse.dim_product)
        THEN 'PASSED'
        ELSE 'FAILED'
    END AS validation_status

UNION ALL

SELECT
    'dim_branch' AS dimension_name,
    (SELECT COUNT(*) FROM staging.stg_branches) AS staging_rows,
    (SELECT COUNT(*) FROM warehouse.dim_branch) AS warehouse_rows,
    CASE
        WHEN (SELECT COUNT(*) FROM staging.stg_branches) = (SELECT COUNT(*) FROM warehouse.dim_branch)
        THEN 'PASSED'
        ELSE 'FAILED'
    END AS validation_status

UNION ALL

SELECT
    'dim_channel' AS dimension_name,
    (SELECT COUNT(*) FROM staging.stg_channels) AS staging_rows,
    (SELECT COUNT(*) FROM warehouse.dim_channel) AS warehouse_rows,
    CASE
        WHEN (SELECT COUNT(*) FROM staging.stg_channels) = (SELECT COUNT(*) FROM warehouse.dim_channel)
        THEN 'PASSED'
        ELSE 'FAILED'
    END AS validation_status;


-- ============================================================
-- 2. Dimension key null checks
-- ============================================================

SELECT
    'warehouse.dim_customer' AS table_name,
    'customer_key' AS checked_column,
    COUNT(*) AS null_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END AS validation_status
FROM warehouse.dim_customer
WHERE customer_key IS NULL

UNION ALL

SELECT
    'warehouse.dim_account' AS table_name,
    'account_key' AS checked_column,
    COUNT(*) AS null_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END AS validation_status
FROM warehouse.dim_account
WHERE account_key IS NULL

UNION ALL

SELECT
    'warehouse.dim_product' AS table_name,
    'product_key' AS checked_column,
    COUNT(*) AS null_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END AS validation_status
FROM warehouse.dim_product
WHERE product_key IS NULL

UNION ALL

SELECT
    'warehouse.dim_branch' AS table_name,
    'branch_key' AS checked_column,
    COUNT(*) AS null_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END AS validation_status
FROM warehouse.dim_branch
WHERE branch_key IS NULL

UNION ALL

SELECT
    'warehouse.dim_channel' AS table_name,
    'channel_key' AS checked_column,
    COUNT(*) AS null_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END AS validation_status
FROM warehouse.dim_channel
WHERE channel_key IS NULL

UNION ALL

SELECT
    'warehouse.dim_date' AS table_name,
    'date_key' AS checked_column,
    COUNT(*) AS null_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END AS validation_status
FROM warehouse.dim_date
WHERE date_key IS NULL;


-- ============================================================
-- 3. Natural key duplicate checks
-- ============================================================

SELECT
    'warehouse.dim_customer' AS table_name,
    'customer_id' AS natural_key,
    COUNT(*) AS duplicate_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END AS validation_status
FROM (
    SELECT customer_id
    FROM warehouse.dim_customer
    GROUP BY customer_id
    HAVING COUNT(*) > 1
) dup

UNION ALL

SELECT
    'warehouse.dim_account' AS table_name,
    'account_id' AS natural_key,
    COUNT(*) AS duplicate_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END AS validation_status
FROM (
    SELECT account_id
    FROM warehouse.dim_account
    GROUP BY account_id
    HAVING COUNT(*) > 1
) dup

UNION ALL

SELECT
    'warehouse.dim_product' AS table_name,
    'product_id' AS natural_key,
    COUNT(*) AS duplicate_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END AS validation_status
FROM (
    SELECT product_id
    FROM warehouse.dim_product
    GROUP BY product_id
    HAVING COUNT(*) > 1
) dup

UNION ALL

SELECT
    'warehouse.dim_branch' AS table_name,
    'branch_id' AS natural_key,
    COUNT(*) AS duplicate_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END AS validation_status
FROM (
    SELECT branch_id
    FROM warehouse.dim_branch
    GROUP BY branch_id
    HAVING COUNT(*) > 1
) dup

UNION ALL

SELECT
    'warehouse.dim_channel' AS table_name,
    'channel_id' AS natural_key,
    COUNT(*) AS duplicate_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END AS validation_status
FROM (
    SELECT channel_id
    FROM warehouse.dim_channel
    GROUP BY channel_id
    HAVING COUNT(*) > 1
) dup;


-- ============================================================
-- 4. Account dimension foreign key lookup checks
-- ============================================================

SELECT
    'dim_account.customer_key is populated' AS validation_check,
    COUNT(*) AS failed_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END AS validation_status
FROM warehouse.dim_account
WHERE customer_key IS NULL

UNION ALL

SELECT
    'dim_account.product_key is populated' AS validation_check,
    COUNT(*) AS failed_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END AS validation_status
FROM warehouse.dim_account
WHERE product_key IS NULL

UNION ALL

SELECT
    'dim_account.branch_key is populated' AS validation_check,
    COUNT(*) AS failed_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END AS validation_status
FROM warehouse.dim_account
WHERE branch_key IS NULL;


-- ============================================================
-- 5. Date dimension validation
-- ============================================================

SELECT
    'date dimension row count greater than zero' AS validation_check,
    COUNT(*) AS actual_count,
    CASE WHEN COUNT(*) > 0 THEN 'PASSED' ELSE 'FAILED' END AS validation_status
FROM warehouse.dim_date

UNION ALL

SELECT
    'date dimension starts at 2018-01-01' AS validation_check,
    COUNT(*) AS actual_count,
    CASE WHEN MIN(full_date) = DATE '2018-01-01' THEN 'PASSED' ELSE 'FAILED' END AS validation_status
FROM warehouse.dim_date

UNION ALL

SELECT
    'date dimension ends at 2026-12-31' AS validation_check,
    COUNT(*) AS actual_count,
    CASE WHEN MAX(full_date) = DATE '2026-12-31' THEN 'PASSED' ELSE 'FAILED' END AS validation_status
FROM warehouse.dim_date;