-- Validate warehouse fact tables
-- Purpose: Confirm warehouse fact tables are complete, unique, and join-ready.

-- ============================================================
-- 1. Row count comparison: staging vs warehouse facts
-- ============================================================

SELECT
    'fact_transactions' AS fact_name,
    (SELECT COUNT(*) FROM staging.stg_transactions) AS staging_rows,
    (SELECT COUNT(*) FROM warehouse.fact_transactions) AS warehouse_rows,
    CASE
        WHEN (SELECT COUNT(*) FROM staging.stg_transactions) = (SELECT COUNT(*) FROM warehouse.fact_transactions)
        THEN 'PASSED'
        ELSE 'FAILED'
    END AS validation_status

UNION ALL

SELECT
    'fact_complaints' AS fact_name,
    (SELECT COUNT(*) FROM staging.stg_complaints) AS staging_rows,
    (SELECT COUNT(*) FROM warehouse.fact_complaints) AS warehouse_rows,
    CASE
        WHEN (SELECT COUNT(*) FROM staging.stg_complaints) = (SELECT COUNT(*) FROM warehouse.fact_complaints)
        THEN 'PASSED'
        ELSE 'FAILED'
    END AS validation_status

UNION ALL

SELECT
    'fact_campaigns' AS fact_name,
    (SELECT COUNT(*) FROM staging.stg_campaigns) AS staging_rows,
    (SELECT COUNT(*) FROM warehouse.fact_campaigns) AS warehouse_rows,
    CASE
        WHEN (SELECT COUNT(*) FROM staging.stg_campaigns) = (SELECT COUNT(*) FROM warehouse.fact_campaigns)
        THEN 'PASSED'
        ELSE 'FAILED'
    END AS validation_status

UNION ALL

SELECT
    'fact_sla_tickets' AS fact_name,
    (SELECT COUNT(*) FROM staging.stg_sla_tickets) AS staging_rows,
    (SELECT COUNT(*) FROM warehouse.fact_sla_tickets) AS warehouse_rows,
    CASE
        WHEN (SELECT COUNT(*) FROM staging.stg_sla_tickets) = (SELECT COUNT(*) FROM warehouse.fact_sla_tickets)
        THEN 'PASSED'
        ELSE 'FAILED'
    END AS validation_status;


-- ============================================================
-- 2. Fact surrogate key null checks
-- ============================================================

SELECT
    'warehouse.fact_transactions' AS table_name,
    'transaction_key' AS checked_column,
    COUNT(*) AS null_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END AS validation_status
FROM warehouse.fact_transactions
WHERE transaction_key IS NULL

UNION ALL

SELECT
    'warehouse.fact_complaints' AS table_name,
    'complaint_key' AS checked_column,
    COUNT(*) AS null_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END AS validation_status
FROM warehouse.fact_complaints
WHERE complaint_key IS NULL

UNION ALL

SELECT
    'warehouse.fact_campaigns' AS table_name,
    'campaign_key' AS checked_column,
    COUNT(*) AS null_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END AS validation_status
FROM warehouse.fact_campaigns
WHERE campaign_key IS NULL

UNION ALL

SELECT
    'warehouse.fact_sla_tickets' AS table_name,
    'sla_ticket_key' AS checked_column,
    COUNT(*) AS null_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END AS validation_status
FROM warehouse.fact_sla_tickets
WHERE sla_ticket_key IS NULL;


-- ============================================================
-- 3. Source business ID duplicate checks
-- ============================================================

SELECT
    'warehouse.fact_transactions' AS table_name,
    'transaction_id' AS natural_key,
    COUNT(*) AS duplicate_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END AS validation_status
FROM (
    SELECT transaction_id
    FROM warehouse.fact_transactions
    GROUP BY transaction_id
    HAVING COUNT(*) > 1
) dup

UNION ALL

SELECT
    'warehouse.fact_complaints' AS table_name,
    'complaint_id' AS natural_key,
    COUNT(*) AS duplicate_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END AS validation_status
FROM (
    SELECT complaint_id
    FROM warehouse.fact_complaints
    GROUP BY complaint_id
    HAVING COUNT(*) > 1
) dup

UNION ALL

SELECT
    'warehouse.fact_campaigns' AS table_name,
    'campaign_id' AS natural_key,
    COUNT(*) AS duplicate_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END AS validation_status
FROM (
    SELECT campaign_id
    FROM warehouse.fact_campaigns
    GROUP BY campaign_id
    HAVING COUNT(*) > 1
) dup

UNION ALL

SELECT
    'warehouse.fact_sla_tickets' AS table_name,
    'ticket_id' AS natural_key,
    COUNT(*) AS duplicate_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END AS validation_status
FROM (
    SELECT ticket_id
    FROM warehouse.fact_sla_tickets
    GROUP BY ticket_id
    HAVING COUNT(*) > 1
) dup;


-- ============================================================
-- 4. Transaction fact dimension lookup checks
-- ============================================================

SELECT
    'fact_transactions.account_key populated' AS validation_check,
    COUNT(*) AS failed_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END AS validation_status
FROM warehouse.fact_transactions
WHERE account_key IS NULL

UNION ALL

SELECT
    'fact_transactions.customer_key populated' AS validation_check,
    COUNT(*) AS failed_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END AS validation_status
FROM warehouse.fact_transactions
WHERE customer_key IS NULL

UNION ALL

SELECT
    'fact_transactions.product_key populated' AS validation_check,
    COUNT(*) AS failed_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END AS validation_status
FROM warehouse.fact_transactions
WHERE product_key IS NULL

UNION ALL

SELECT
    'fact_transactions.branch_key populated' AS validation_check,
    COUNT(*) AS failed_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END AS validation_status
FROM warehouse.fact_transactions
WHERE branch_key IS NULL

UNION ALL

SELECT
    'fact_transactions.channel_key populated' AS validation_check,
    COUNT(*) AS failed_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END AS validation_status
FROM warehouse.fact_transactions
WHERE channel_key IS NULL

UNION ALL

SELECT
    'fact_transactions.transaction_date_key populated' AS validation_check,
    COUNT(*) AS failed_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END AS validation_status
FROM warehouse.fact_transactions
WHERE transaction_date_key IS NULL;


-- ============================================================
-- 5. Complaint, campaign, and SLA dimension lookup checks
-- ============================================================

SELECT
    'fact_complaints.customer_key populated' AS validation_check,
    COUNT(*) AS failed_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END AS validation_status
FROM warehouse.fact_complaints
WHERE customer_key IS NULL

UNION ALL

SELECT
    'fact_complaints.account_key populated' AS validation_check,
    COUNT(*) AS failed_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END AS validation_status
FROM warehouse.fact_complaints
WHERE account_key IS NULL

UNION ALL

SELECT
    'fact_complaints.product_key populated' AS validation_check,
    COUNT(*) AS failed_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END AS validation_status
FROM warehouse.fact_complaints
WHERE product_key IS NULL

UNION ALL

SELECT
    'fact_complaints.channel_key populated' AS validation_check,
    COUNT(*) AS failed_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END AS validation_status
FROM warehouse.fact_complaints
WHERE channel_key IS NULL

UNION ALL

SELECT
    'fact_campaigns.customer_key populated' AS validation_check,
    COUNT(*) AS failed_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END AS validation_status
FROM warehouse.fact_campaigns
WHERE customer_key IS NULL

UNION ALL

SELECT
    'fact_campaigns.offer_product_key populated' AS validation_check,
    COUNT(*) AS failed_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END AS validation_status
FROM warehouse.fact_campaigns
WHERE offer_product_key IS NULL

UNION ALL

SELECT
    'fact_campaigns.campaign_channel_key populated' AS validation_check,
    COUNT(*) AS failed_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END AS validation_status
FROM warehouse.fact_campaigns
WHERE campaign_channel_key IS NULL

UNION ALL

SELECT
    'fact_sla_tickets.customer_key populated' AS validation_check,
    COUNT(*) AS failed_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END AS validation_status
FROM warehouse.fact_sla_tickets
WHERE customer_key IS NULL

UNION ALL

SELECT
    'fact_sla_tickets.account_key populated' AS validation_check,
    COUNT(*) AS failed_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END AS validation_status
FROM warehouse.fact_sla_tickets
WHERE account_key IS NULL

UNION ALL

SELECT
    'fact_sla_tickets.created_date_key populated' AS validation_check,
    COUNT(*) AS failed_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END AS validation_status
FROM warehouse.fact_sla_tickets
WHERE created_date_key IS NULL

UNION ALL

SELECT
    'fact_sla_tickets.due_date_key populated' AS validation_check,
    COUNT(*) AS failed_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END AS validation_status
FROM warehouse.fact_sla_tickets
WHERE due_date_key IS NULL

UNION ALL

SELECT
    'fact_sla_tickets.resolved_date_key valid when resolved_datetime exists' AS validation_check,
    COUNT(*) AS failed_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END AS validation_status
FROM warehouse.fact_sla_tickets
WHERE resolved_datetime IS NOT NULL
  AND resolved_date_key IS NULL;


-- ============================================================
-- 6. Derived count field validation
-- ============================================================

SELECT
    'transaction_count always equals 1' AS validation_check,
    COUNT(*) AS failed_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END AS validation_status
FROM warehouse.fact_transactions
WHERE transaction_count <> 1

UNION ALL

SELECT
    'successful_transaction_count logic valid' AS validation_check,
    COUNT(*) AS failed_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END AS validation_status
FROM warehouse.fact_transactions
WHERE
    (transaction_status = 'Success' AND successful_transaction_count <> 1)
    OR
    (transaction_status <> 'Success' AND successful_transaction_count <> 0)

UNION ALL

SELECT
    'failed_transaction_count logic valid' AS validation_check,
    COUNT(*) AS failed_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END AS validation_status
FROM warehouse.fact_transactions
WHERE
    (transaction_status = 'Failed' AND failed_transaction_count <> 1)
    OR
    (transaction_status <> 'Failed' AND failed_transaction_count <> 0)

UNION ALL

SELECT
    'complaint_count always equals 1' AS validation_check,
    COUNT(*) AS failed_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END AS validation_status
FROM warehouse.fact_complaints
WHERE complaint_count <> 1

UNION ALL

SELECT
    'resolved_complaint_count logic valid' AS validation_check,
    COUNT(*) AS failed_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END AS validation_status
FROM warehouse.fact_complaints
WHERE
    (is_resolved = TRUE AND resolved_complaint_count <> 1)
    OR
    (is_resolved = FALSE AND resolved_complaint_count <> 0)

UNION ALL

SELECT
    'campaign_sent_count always equals 1' AS validation_check,
    COUNT(*) AS failed_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END AS validation_status
FROM warehouse.fact_campaigns
WHERE campaign_sent_count <> 1

UNION ALL

SELECT
    'converted_count logic valid' AS validation_check,
    COUNT(*) AS failed_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END AS validation_status
FROM warehouse.fact_campaigns
WHERE
    (converted_flag = TRUE AND converted_count <> 1)
    OR
    (converted_flag = FALSE AND converted_count <> 0)

UNION ALL

SELECT
    'ticket_count always equals 1' AS validation_check,
    COUNT(*) AS failed_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END AS validation_status
FROM warehouse.fact_sla_tickets
WHERE ticket_count <> 1

UNION ALL

SELECT
    'sla_met_count logic valid' AS validation_check,
    COUNT(*) AS failed_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END AS validation_status
FROM warehouse.fact_sla_tickets
WHERE
    (sla_met_flag = TRUE AND sla_met_count <> 1)
    OR
    (sla_met_flag IS DISTINCT FROM TRUE AND sla_met_count <> 0)

UNION ALL

SELECT
    'sla_breached_count logic valid' AS validation_check,
    COUNT(*) AS failed_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END AS validation_status
FROM warehouse.fact_sla_tickets
WHERE
    (sla_met_flag = FALSE AND sla_breached_count <> 1)
    OR
    (sla_met_flag IS DISTINCT FROM FALSE AND sla_breached_count <> 0);