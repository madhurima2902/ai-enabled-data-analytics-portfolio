-- Raw data profile checks
-- Purpose: Profile raw tables after CSV loading and before staging transformations.

-- ============================================================
-- 1. Row count validation
-- ============================================================

SELECT
    'raw.customers' AS table_name,
    COUNT(*) AS actual_rows,
    10000 AS expected_rows,
    CASE WHEN COUNT(*) = 10000 THEN 'PASSED' ELSE 'FAILED' END AS validation_status
FROM raw.customers

UNION ALL

SELECT
    'raw.accounts' AS table_name,
    COUNT(*) AS actual_rows,
    15000 AS expected_rows,
    CASE WHEN COUNT(*) = 15000 THEN 'PASSED' ELSE 'FAILED' END AS validation_status
FROM raw.accounts

UNION ALL

SELECT
    'raw.products' AS table_name,
    COUNT(*) AS actual_rows,
    7 AS expected_rows,
    CASE WHEN COUNT(*) = 7 THEN 'PASSED' ELSE 'FAILED' END AS validation_status
FROM raw.products

UNION ALL

SELECT
    'raw.branches' AS table_name,
    COUNT(*) AS actual_rows,
    20 AS expected_rows,
    CASE WHEN COUNT(*) = 20 THEN 'PASSED' ELSE 'FAILED' END AS validation_status
FROM raw.branches

UNION ALL

SELECT
    'raw.channels' AS table_name,
    COUNT(*) AS actual_rows,
    6 AS expected_rows,
    CASE WHEN COUNT(*) = 6 THEN 'PASSED' ELSE 'FAILED' END AS validation_status
FROM raw.channels

UNION ALL

SELECT
    'raw.complaints' AS table_name,
    COUNT(*) AS actual_rows,
    2000 AS expected_rows,
    CASE WHEN COUNT(*) = 2000 THEN 'PASSED' ELSE 'FAILED' END AS validation_status
FROM raw.complaints

UNION ALL

SELECT
    'raw.campaigns' AS table_name,
    COUNT(*) AS actual_rows,
    5000 AS expected_rows,
    CASE WHEN COUNT(*) = 5000 THEN 'PASSED' ELSE 'FAILED' END AS validation_status
FROM raw.campaigns

UNION ALL

SELECT
    'raw.sla_tickets' AS table_name,
    COUNT(*) AS actual_rows,
    4000 AS expected_rows,
    CASE WHEN COUNT(*) = 4000 THEN 'PASSED' ELSE 'FAILED' END AS validation_status
FROM raw.sla_tickets

UNION ALL

SELECT
    'raw.transactions' AS table_name,
    COUNT(*) AS actual_rows,
    25000 AS expected_rows,
    CASE WHEN COUNT(*) = 25000 THEN 'PASSED' ELSE 'FAILED' END AS validation_status
FROM raw.transactions;


-- ============================================================
-- 2. Duplicate primary/business ID checks
-- ============================================================

SELECT
    'raw.customers' AS table_name,
    'customer_id' AS checked_column,
    COUNT(*) AS duplicate_id_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END AS validation_status
FROM (
    SELECT customer_id
    FROM raw.customers
    GROUP BY customer_id
    HAVING COUNT(*) > 1
) dup

UNION ALL

SELECT
    'raw.accounts' AS table_name,
    'account_id' AS checked_column,
    COUNT(*) AS duplicate_id_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END AS validation_status
FROM (
    SELECT account_id
    FROM raw.accounts
    GROUP BY account_id
    HAVING COUNT(*) > 1
) dup

UNION ALL

SELECT
    'raw.products' AS table_name,
    'product_id' AS checked_column,
    COUNT(*) AS duplicate_id_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END AS validation_status
FROM (
    SELECT product_id
    FROM raw.products
    GROUP BY product_id
    HAVING COUNT(*) > 1
) dup

UNION ALL

SELECT
    'raw.branches' AS table_name,
    'branch_id' AS checked_column,
    COUNT(*) AS duplicate_id_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END AS validation_status
FROM (
    SELECT branch_id
    FROM raw.branches
    GROUP BY branch_id
    HAVING COUNT(*) > 1
) dup

UNION ALL

SELECT
    'raw.channels' AS table_name,
    'channel_id' AS checked_column,
    COUNT(*) AS duplicate_id_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END AS validation_status
FROM (
    SELECT channel_id
    FROM raw.channels
    GROUP BY channel_id
    HAVING COUNT(*) > 1
) dup

UNION ALL

SELECT
    'raw.complaints' AS table_name,
    'complaint_id' AS checked_column,
    COUNT(*) AS duplicate_id_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END AS validation_status
FROM (
    SELECT complaint_id
    FROM raw.complaints
    GROUP BY complaint_id
    HAVING COUNT(*) > 1
) dup

UNION ALL

SELECT
    'raw.campaigns' AS table_name,
    'campaign_id' AS checked_column,
    COUNT(*) AS duplicate_id_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END AS validation_status
FROM (
    SELECT campaign_id
    FROM raw.campaigns
    GROUP BY campaign_id
    HAVING COUNT(*) > 1
) dup

UNION ALL

SELECT
    'raw.sla_tickets' AS table_name,
    'ticket_id' AS checked_column,
    COUNT(*) AS duplicate_id_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END AS validation_status
FROM (
    SELECT ticket_id
    FROM raw.sla_tickets
    GROUP BY ticket_id
    HAVING COUNT(*) > 1
) dup

UNION ALL

SELECT
    'raw.transactions' AS table_name,
    'transaction_id' AS checked_column,
    COUNT(*) AS duplicate_id_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END AS validation_status
FROM (
    SELECT transaction_id
    FROM raw.transactions
    GROUP BY transaction_id
    HAVING COUNT(*) > 1
) dup;


-- ============================================================
-- 3. Null key checks
-- ============================================================

SELECT
    'raw.customers' AS table_name,
    'customer_id' AS checked_column,
    COUNT(*) AS null_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END AS validation_status
FROM raw.customers
WHERE customer_id IS NULL

UNION ALL

SELECT
    'raw.accounts' AS table_name,
    'account_id' AS checked_column,
    COUNT(*) AS null_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END AS validation_status
FROM raw.accounts
WHERE account_id IS NULL

UNION ALL

SELECT
    'raw.accounts' AS table_name,
    'customer_id' AS checked_column,
    COUNT(*) AS null_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END AS validation_status
FROM raw.accounts
WHERE customer_id IS NULL

UNION ALL

SELECT
    'raw.transactions' AS table_name,
    'transaction_id' AS checked_column,
    COUNT(*) AS null_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END AS validation_status
FROM raw.transactions
WHERE transaction_id IS NULL

UNION ALL

SELECT
    'raw.transactions' AS table_name,
    'account_id' AS checked_column,
    COUNT(*) AS null_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END AS validation_status
FROM raw.transactions
WHERE account_id IS NULL

UNION ALL

SELECT
    'raw.complaints' AS table_name,
    'complaint_id' AS checked_column,
    COUNT(*) AS null_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END AS validation_status
FROM raw.complaints
WHERE complaint_id IS NULL

UNION ALL

SELECT
    'raw.campaigns' AS table_name,
    'campaign_id' AS checked_column,
    COUNT(*) AS null_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END AS validation_status
FROM raw.campaigns
WHERE campaign_id IS NULL

UNION ALL

SELECT
    'raw.sla_tickets' AS table_name,
    'ticket_id' AS checked_column,
    COUNT(*) AS null_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END AS validation_status
FROM raw.sla_tickets
WHERE ticket_id IS NULL;


-- ============================================================
-- 4. Date range profiling
-- ============================================================

SELECT
    'raw.customers' AS table_name,
    'onboarding_date' AS date_column,
    MIN(onboarding_date) AS min_date,
    MAX(onboarding_date) AS max_date
FROM raw.customers

UNION ALL

SELECT
    'raw.accounts' AS table_name,
    'account_open_date' AS date_column,
    MIN(account_open_date) AS min_date,
    MAX(account_open_date) AS max_date
FROM raw.accounts

UNION ALL

SELECT
    'raw.complaints' AS table_name,
    'complaint_date' AS date_column,
    MIN(complaint_date) AS min_date,
    MAX(complaint_date) AS max_date
FROM raw.complaints

UNION ALL

SELECT
    'raw.campaigns' AS table_name,
    'sent_date' AS date_column,
    MIN(sent_date) AS min_date,
    MAX(sent_date) AS max_date
FROM raw.campaigns

UNION ALL

SELECT
    'raw.transactions' AS table_name,
    'transaction_datetime' AS date_column,
    MIN(transaction_datetime)::DATE AS min_date,
    MAX(transaction_datetime)::DATE AS max_date
FROM raw.transactions;


-- ============================================================
-- 5. Status/category distributions
-- ============================================================

SELECT
    'customer_segment' AS category_type,
    customer_segment AS category_value,
    COUNT(*) AS record_count
FROM raw.customers
GROUP BY customer_segment
ORDER BY record_count DESC;


SELECT
    'kyc_status' AS category_type,
    kyc_status AS category_value,
    COUNT(*) AS record_count
FROM raw.customers
GROUP BY kyc_status
ORDER BY record_count DESC;


SELECT
    'account_status' AS category_type,
    account_status AS category_value,
    COUNT(*) AS record_count
FROM raw.accounts
GROUP BY account_status
ORDER BY record_count DESC;


SELECT
    'complaint_status' AS category_type,
    complaint_status AS category_value,
    COUNT(*) AS record_count
FROM raw.complaints
GROUP BY complaint_status
ORDER BY record_count DESC;


SELECT
    'campaign_response_status' AS category_type,
    response_status AS category_value,
    COUNT(*) AS record_count
FROM raw.campaigns
GROUP BY response_status
ORDER BY record_count DESC;


SELECT
    'ticket_status' AS category_type,
    ticket_status AS category_value,
    COUNT(*) AS record_count
FROM raw.sla_tickets
GROUP BY ticket_status
ORDER BY record_count DESC;


SELECT
    'transaction_status' AS category_type,
    transaction_status AS category_value,
    COUNT(*) AS record_count
FROM raw.transactions
GROUP BY transaction_status
ORDER BY record_count DESC;


SELECT
    'transaction_type' AS category_type,
    transaction_type AS category_value,
    COUNT(*) AS record_count
FROM raw.transactions
GROUP BY transaction_type
ORDER BY record_count DESC;


-- ============================================================
-- 6. Numeric range profiling
-- ============================================================

SELECT
    'raw.accounts' AS table_name,
    'current_balance' AS numeric_column,
    MIN(current_balance) AS min_value,
    MAX(current_balance) AS max_value,
    AVG(current_balance) AS avg_value
FROM raw.accounts

UNION ALL

SELECT
    'raw.accounts' AS table_name,
    'interest_rate' AS numeric_column,
    MIN(interest_rate) AS min_value,
    MAX(interest_rate) AS max_value,
    AVG(interest_rate) AS avg_value
FROM raw.accounts

UNION ALL

SELECT
    'raw.accounts' AS table_name,
    'credit_limit' AS numeric_column,
    MIN(credit_limit) AS min_value,
    MAX(credit_limit) AS max_value,
    AVG(credit_limit) AS avg_value
FROM raw.accounts

UNION ALL

SELECT
    'raw.transactions' AS table_name,
    'amount' AS numeric_column,
    MIN(amount) AS min_value,
    MAX(amount) AS max_value,
    AVG(amount) AS avg_value
FROM raw.transactions

UNION ALL

SELECT
    'raw.transactions' AS table_name,
    'fee_amount' AS numeric_column,
    MIN(fee_amount) AS min_value,
    MAX(fee_amount) AS max_value,
    AVG(fee_amount) AS avg_value
FROM raw.transactions

UNION ALL

SELECT
    'raw.transactions' AS table_name,
    'balance_after_transaction' AS numeric_column,
    MIN(balance_after_transaction) AS min_value,
    MAX(balance_after_transaction) AS max_value,
    AVG(balance_after_transaction) AS avg_value
FROM raw.transactions;