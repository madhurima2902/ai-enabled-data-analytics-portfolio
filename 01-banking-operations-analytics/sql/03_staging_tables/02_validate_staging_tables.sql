-- Validate staging tables
-- Purpose: Confirm staging tables were created correctly from raw tables.

-- ============================================================
-- 1. Row count comparison: raw vs staging
-- ============================================================

SELECT
    'customers' AS dataset_name,
    (SELECT COUNT(*) FROM raw.customers) AS raw_rows,
    (SELECT COUNT(*) FROM staging.stg_customers) AS staging_rows,
    CASE
        WHEN (SELECT COUNT(*) FROM raw.customers) = (SELECT COUNT(*) FROM staging.stg_customers)
        THEN 'PASSED'
        ELSE 'FAILED'
    END AS validation_status

UNION ALL

SELECT
    'accounts' AS dataset_name,
    (SELECT COUNT(*) FROM raw.accounts) AS raw_rows,
    (SELECT COUNT(*) FROM staging.stg_accounts) AS staging_rows,
    CASE
        WHEN (SELECT COUNT(*) FROM raw.accounts) = (SELECT COUNT(*) FROM staging.stg_accounts)
        THEN 'PASSED'
        ELSE 'FAILED'
    END AS validation_status

UNION ALL

SELECT
    'products' AS dataset_name,
    (SELECT COUNT(*) FROM raw.products) AS raw_rows,
    (SELECT COUNT(*) FROM staging.stg_products) AS staging_rows,
    CASE
        WHEN (SELECT COUNT(*) FROM raw.products) = (SELECT COUNT(*) FROM staging.stg_products)
        THEN 'PASSED'
        ELSE 'FAILED'
    END AS validation_status

UNION ALL

SELECT
    'branches' AS dataset_name,
    (SELECT COUNT(*) FROM raw.branches) AS raw_rows,
    (SELECT COUNT(*) FROM staging.stg_branches) AS staging_rows,
    CASE
        WHEN (SELECT COUNT(*) FROM raw.branches) = (SELECT COUNT(*) FROM staging.stg_branches)
        THEN 'PASSED'
        ELSE 'FAILED'
    END AS validation_status

UNION ALL

SELECT
    'channels' AS dataset_name,
    (SELECT COUNT(*) FROM raw.channels) AS raw_rows,
    (SELECT COUNT(*) FROM staging.stg_channels) AS staging_rows,
    CASE
        WHEN (SELECT COUNT(*) FROM raw.channels) = (SELECT COUNT(*) FROM staging.stg_channels)
        THEN 'PASSED'
        ELSE 'FAILED'
    END AS validation_status

UNION ALL

SELECT
    'complaints' AS dataset_name,
    (SELECT COUNT(*) FROM raw.complaints) AS raw_rows,
    (SELECT COUNT(*) FROM staging.stg_complaints) AS staging_rows,
    CASE
        WHEN (SELECT COUNT(*) FROM raw.complaints) = (SELECT COUNT(*) FROM staging.stg_complaints)
        THEN 'PASSED'
        ELSE 'FAILED'
    END AS validation_status

UNION ALL

SELECT
    'campaigns' AS dataset_name,
    (SELECT COUNT(*) FROM raw.campaigns) AS raw_rows,
    (SELECT COUNT(*) FROM staging.stg_campaigns) AS staging_rows,
    CASE
        WHEN (SELECT COUNT(*) FROM raw.campaigns) = (SELECT COUNT(*) FROM staging.stg_campaigns)
        THEN 'PASSED'
        ELSE 'FAILED'
    END AS validation_status

UNION ALL

SELECT
    'sla_tickets' AS dataset_name,
    (SELECT COUNT(*) FROM raw.sla_tickets) AS raw_rows,
    (SELECT COUNT(*) FROM staging.stg_sla_tickets) AS staging_rows,
    CASE
        WHEN (SELECT COUNT(*) FROM raw.sla_tickets) = (SELECT COUNT(*) FROM staging.stg_sla_tickets)
        THEN 'PASSED'
        ELSE 'FAILED'
    END AS validation_status

UNION ALL

SELECT
    'transactions' AS dataset_name,
    (SELECT COUNT(*) FROM raw.transactions) AS raw_rows,
    (SELECT COUNT(*) FROM staging.stg_transactions) AS staging_rows,
    CASE
        WHEN (SELECT COUNT(*) FROM raw.transactions) = (SELECT COUNT(*) FROM staging.stg_transactions)
        THEN 'PASSED'
        ELSE 'FAILED'
    END AS validation_status;


-- ============================================================
-- 2. Staging key null checks
-- ============================================================

SELECT
    'staging.stg_customers' AS table_name,
    'customer_id' AS checked_column,
    COUNT(*) AS null_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END AS validation_status
FROM staging.stg_customers
WHERE customer_id IS NULL

UNION ALL

SELECT
    'staging.stg_accounts' AS table_name,
    'account_id' AS checked_column,
    COUNT(*) AS null_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END AS validation_status
FROM staging.stg_accounts
WHERE account_id IS NULL

UNION ALL

SELECT
    'staging.stg_transactions' AS table_name,
    'transaction_id' AS checked_column,
    COUNT(*) AS null_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END AS validation_status
FROM staging.stg_transactions
WHERE transaction_id IS NULL

UNION ALL

SELECT
    'staging.stg_complaints' AS table_name,
    'complaint_id' AS checked_column,
    COUNT(*) AS null_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END AS validation_status
FROM staging.stg_complaints
WHERE complaint_id IS NULL

UNION ALL

SELECT
    'staging.stg_campaigns' AS table_name,
    'campaign_id' AS checked_column,
    COUNT(*) AS null_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END AS validation_status
FROM staging.stg_campaigns
WHERE campaign_id IS NULL

UNION ALL

SELECT
    'staging.stg_sla_tickets' AS table_name,
    'ticket_id' AS checked_column,
    COUNT(*) AS null_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END AS validation_status
FROM staging.stg_sla_tickets
WHERE ticket_id IS NULL;


-- ============================================================
-- 3. Staging duplicate ID checks
-- ============================================================

SELECT
    'staging.stg_customers' AS table_name,
    'customer_id' AS checked_column,
    COUNT(*) AS duplicate_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END AS validation_status
FROM (
    SELECT customer_id
    FROM staging.stg_customers
    GROUP BY customer_id
    HAVING COUNT(*) > 1
) dup

UNION ALL

SELECT
    'staging.stg_accounts' AS table_name,
    'account_id' AS checked_column,
    COUNT(*) AS duplicate_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END AS validation_status
FROM (
    SELECT account_id
    FROM staging.stg_accounts
    GROUP BY account_id
    HAVING COUNT(*) > 1
) dup

UNION ALL

SELECT
    'staging.stg_transactions' AS table_name,
    'transaction_id' AS checked_column,
    COUNT(*) AS duplicate_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END AS validation_status
FROM (
    SELECT transaction_id
    FROM staging.stg_transactions
    GROUP BY transaction_id
    HAVING COUNT(*) > 1
) dup

UNION ALL

SELECT
    'staging.stg_complaints' AS table_name,
    'complaint_id' AS checked_column,
    COUNT(*) AS duplicate_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END AS validation_status
FROM (
    SELECT complaint_id
    FROM staging.stg_complaints
    GROUP BY complaint_id
    HAVING COUNT(*) > 1
) dup

UNION ALL

SELECT
    'staging.stg_campaigns' AS table_name,
    'campaign_id' AS checked_column,
    COUNT(*) AS duplicate_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END AS validation_status
FROM (
    SELECT campaign_id
    FROM staging.stg_campaigns
    GROUP BY campaign_id
    HAVING COUNT(*) > 1
) dup

UNION ALL

SELECT
    'staging.stg_sla_tickets' AS table_name,
    'ticket_id' AS checked_column,
    COUNT(*) AS duplicate_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END AS validation_status
FROM (
    SELECT ticket_id
    FROM staging.stg_sla_tickets
    GROUP BY ticket_id
    HAVING COUNT(*) > 1
) dup;


-- ============================================================
-- 4. Derived field validation
-- ============================================================

SELECT
    'transaction_date_matches_transaction_datetime' AS validation_check,
    COUNT(*) AS failed_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END AS validation_status
FROM staging.stg_transactions
WHERE transaction_date <> transaction_datetime::DATE

UNION ALL

SELECT
    'transaction_month_matches_transaction_datetime' AS validation_check,
    COUNT(*) AS failed_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END AS validation_status
FROM staging.stg_transactions
WHERE transaction_month <> DATE_TRUNC('month', transaction_datetime)::DATE

UNION ALL

SELECT
    'successful_transaction_flag_is_valid' AS validation_check,
    COUNT(*) AS failed_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END AS validation_status
FROM staging.stg_transactions
WHERE
    (transaction_status = 'Success' AND is_successful_transaction <> TRUE)
    OR
    (transaction_status <> 'Success' AND is_successful_transaction <> FALSE)

UNION ALL

SELECT
    'complaint_resolved_flag_is_valid' AS validation_check,
    COUNT(*) AS failed_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END AS validation_status
FROM staging.stg_complaints
WHERE
    (complaint_status IN ('Resolved', 'Closed') AND is_resolved <> TRUE)
    OR
    (complaint_status NOT IN ('Resolved', 'Closed') AND is_resolved <> FALSE)

UNION ALL

SELECT
    'campaign_converted_count_is_valid' AS validation_check,
    COUNT(*) AS failed_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END AS validation_status
FROM staging.stg_campaigns
WHERE
    (converted_flag = TRUE AND converted_count <> 1)
    OR
    (converted_flag = FALSE AND converted_count <> 0);