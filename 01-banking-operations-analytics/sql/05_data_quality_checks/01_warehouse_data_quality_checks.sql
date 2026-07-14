-- Warehouse Data Quality Checks
-- Purpose:
-- Run final business-rule and warehouse-level data quality checks
-- after raw, staging, dimension, and fact tables have been created.

-- ============================================================
-- 1. Warehouse table row count sanity checks
-- ============================================================

SELECT
    'dim_customer row count > 0' AS validation_check,
    COUNT(*) AS failed_count,
    CASE WHEN COUNT(*) > 0 THEN 'PASSED' ELSE 'FAILED' END AS validation_status
FROM warehouse.dim_customer

UNION ALL

SELECT
    'dim_account row count > 0',
    COUNT(*),
    CASE WHEN COUNT(*) > 0 THEN 'PASSED' ELSE 'FAILED' END
FROM warehouse.dim_account

UNION ALL

SELECT
    'dim_product row count > 0',
    COUNT(*),
    CASE WHEN COUNT(*) > 0 THEN 'PASSED' ELSE 'FAILED' END
FROM warehouse.dim_product

UNION ALL

SELECT
    'dim_branch row count > 0',
    COUNT(*),
    CASE WHEN COUNT(*) > 0 THEN 'PASSED' ELSE 'FAILED' END
FROM warehouse.dim_branch

UNION ALL

SELECT
    'dim_channel row count > 0',
    COUNT(*),
    CASE WHEN COUNT(*) > 0 THEN 'PASSED' ELSE 'FAILED' END
FROM warehouse.dim_channel

UNION ALL

SELECT
    'dim_date row count > 0',
    COUNT(*),
    CASE WHEN COUNT(*) > 0 THEN 'PASSED' ELSE 'FAILED' END
FROM warehouse.dim_date

UNION ALL

SELECT
    'fact_transactions row count > 0',
    COUNT(*),
    CASE WHEN COUNT(*) > 0 THEN 'PASSED' ELSE 'FAILED' END
FROM warehouse.fact_transactions

UNION ALL

SELECT
    'fact_complaints row count > 0',
    COUNT(*),
    CASE WHEN COUNT(*) > 0 THEN 'PASSED' ELSE 'FAILED' END
FROM warehouse.fact_complaints

UNION ALL

SELECT
    'fact_campaigns row count > 0',
    COUNT(*),
    CASE WHEN COUNT(*) > 0 THEN 'PASSED' ELSE 'FAILED' END
FROM warehouse.fact_campaigns

UNION ALL

SELECT
    'fact_sla_tickets row count > 0',
    COUNT(*),
    CASE WHEN COUNT(*) > 0 THEN 'PASSED' ELSE 'FAILED' END
FROM warehouse.fact_sla_tickets;


-- ============================================================
-- 2. Fact-to-dimension orphan checks
-- ============================================================

SELECT
    'fact_transactions orphan customer_key' AS validation_check,
    COUNT(*) AS failed_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END AS validation_status
FROM warehouse.fact_transactions ft
LEFT JOIN warehouse.dim_customer dc
    ON ft.customer_key = dc.customer_key
WHERE dc.customer_key IS NULL

UNION ALL

SELECT
    'fact_transactions orphan account_key',
    COUNT(*),
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END
FROM warehouse.fact_transactions ft
LEFT JOIN warehouse.dim_account da
    ON ft.account_key = da.account_key
WHERE da.account_key IS NULL

UNION ALL

SELECT
    'fact_transactions orphan product_key',
    COUNT(*),
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END
FROM warehouse.fact_transactions ft
LEFT JOIN warehouse.dim_product dp
    ON ft.product_key = dp.product_key
WHERE dp.product_key IS NULL

UNION ALL

SELECT
    'fact_transactions orphan branch_key',
    COUNT(*),
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END
FROM warehouse.fact_transactions ft
LEFT JOIN warehouse.dim_branch db
    ON ft.branch_key = db.branch_key
WHERE db.branch_key IS NULL

UNION ALL

SELECT
    'fact_transactions orphan channel_key',
    COUNT(*),
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END
FROM warehouse.fact_transactions ft
LEFT JOIN warehouse.dim_channel dch
    ON ft.channel_key = dch.channel_key
WHERE dch.channel_key IS NULL

UNION ALL

SELECT
    'fact_complaints orphan customer_key',
    COUNT(*),
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END
FROM warehouse.fact_complaints fc
LEFT JOIN warehouse.dim_customer dc
    ON fc.customer_key = dc.customer_key
WHERE dc.customer_key IS NULL

UNION ALL

SELECT
    'fact_complaints orphan account_key',
    COUNT(*),
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END
FROM warehouse.fact_complaints fc
LEFT JOIN warehouse.dim_account da
    ON fc.account_key = da.account_key
WHERE da.account_key IS NULL

UNION ALL

SELECT
    'fact_campaigns orphan customer_key',
    COUNT(*),
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END
FROM warehouse.fact_campaigns fc
LEFT JOIN warehouse.dim_customer dc
    ON fc.customer_key = dc.customer_key
WHERE dc.customer_key IS NULL

UNION ALL

SELECT
    'fact_sla_tickets orphan customer_key',
    COUNT(*),
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END
FROM warehouse.fact_sla_tickets fst
LEFT JOIN warehouse.dim_customer dc
    ON fst.customer_key = dc.customer_key
WHERE dc.customer_key IS NULL

UNION ALL

SELECT
    'fact_sla_tickets orphan account_key',
    COUNT(*),
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END
FROM warehouse.fact_sla_tickets fst
LEFT JOIN warehouse.dim_account da
    ON fst.account_key = da.account_key
WHERE da.account_key IS NULL;


-- ============================================================
-- 3. Date key consistency checks
-- ============================================================

SELECT
    'transaction_date_key matches transaction_date' AS validation_check,
    COUNT(*) AS failed_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END AS validation_status
FROM warehouse.fact_transactions ft
LEFT JOIN warehouse.dim_date dd
    ON ft.transaction_date_key = dd.date_key
WHERE dd.full_date IS NULL
   OR dd.full_date <> ft.transaction_date

UNION ALL

SELECT
    'complaint_date_key matches complaint_date',
    COUNT(*),
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END
FROM warehouse.fact_complaints fc
LEFT JOIN warehouse.dim_date dd
    ON fc.complaint_date_key = dd.date_key
WHERE dd.full_date IS NULL
   OR dd.full_date <> fc.complaint_date

UNION ALL

SELECT
    'campaign sent_date_key matches sent_date',
    COUNT(*),
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END
FROM warehouse.fact_campaigns fc
LEFT JOIN warehouse.dim_date dd
    ON fc.sent_date_key = dd.date_key
WHERE dd.full_date IS NULL
   OR dd.full_date <> fc.sent_date

UNION ALL

SELECT
    'sla created_date_key matches created_datetime date',
    COUNT(*),
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END
FROM warehouse.fact_sla_tickets fst
LEFT JOIN warehouse.dim_date dd
    ON fst.created_date_key = dd.date_key
WHERE dd.full_date IS NULL
   OR dd.full_date <> fst.created_datetime::DATE

UNION ALL

SELECT
    'sla due_date_key matches due_datetime date',
    COUNT(*),
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END
FROM warehouse.fact_sla_tickets fst
LEFT JOIN warehouse.dim_date dd
    ON fst.due_date_key = dd.date_key
WHERE dd.full_date IS NULL
   OR dd.full_date <> fst.due_datetime::DATE

UNION ALL

SELECT
    'sla resolved_date_key matches resolved_datetime date when resolved',
    COUNT(*),
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END
FROM warehouse.fact_sla_tickets fst
LEFT JOIN warehouse.dim_date dd
    ON fst.resolved_date_key = dd.date_key
WHERE fst.resolved_datetime IS NOT NULL
  AND (
        dd.full_date IS NULL
        OR dd.full_date <> fst.resolved_datetime::DATE
      );


-- ============================================================
-- 4. Transaction business-rule checks
-- ============================================================

SELECT
    'transaction amount is not null and non-negative' AS validation_check,
    COUNT(*) AS failed_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END AS validation_status
FROM warehouse.fact_transactions
WHERE amount IS NULL
   OR amount < 0

UNION ALL

SELECT
    'transaction fee amount is not null and non-negative',
    COUNT(*),
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END
FROM warehouse.fact_transactions
WHERE fee_amount IS NULL
   OR fee_amount < 0

UNION ALL

SELECT
    'transaction fee is not greater than transaction amount',
    COUNT(*),
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END
FROM warehouse.fact_transactions
WHERE fee_amount > amount

UNION ALL

SELECT
    'transaction status is populated',
    COUNT(*),
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END
FROM warehouse.fact_transactions
WHERE transaction_status IS NULL
   OR TRIM(transaction_status) = ''

UNION ALL

SELECT
    'transaction type is populated',
    COUNT(*),
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END
FROM warehouse.fact_transactions
WHERE transaction_type IS NULL
   OR TRIM(transaction_type) = ''

UNION ALL

SELECT
    'currency is populated',
    COUNT(*),
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END
FROM warehouse.fact_transactions
WHERE currency IS NULL
   OR TRIM(currency) = '';


-- ============================================================
-- 5. Complaint business-rule checks
-- ============================================================

SELECT
    'complaint category is populated' AS validation_check,
    COUNT(*) AS failed_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END AS validation_status
FROM warehouse.fact_complaints
WHERE complaint_category IS NULL
   OR TRIM(complaint_category) = ''

UNION ALL

SELECT
    'complaint priority is populated',
    COUNT(*),
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END
FROM warehouse.fact_complaints
WHERE complaint_priority IS NULL
   OR TRIM(complaint_priority) = ''

UNION ALL

SELECT
    'complaint status is populated',
    COUNT(*),
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END
FROM warehouse.fact_complaints
WHERE complaint_status IS NULL
   OR TRIM(complaint_status) = ''

UNION ALL

SELECT
    'resolved complaints have resolution_date',
    COUNT(*),
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END
FROM warehouse.fact_complaints
WHERE is_resolved = TRUE
  AND resolution_date IS NULL

UNION ALL

SELECT
    'complaint resolution_date is not before complaint_date',
    COUNT(*),
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END
FROM warehouse.fact_complaints
WHERE resolution_date IS NOT NULL
  AND resolution_date < complaint_date

UNION ALL

SELECT
    'complaint resolution_days is non-negative when populated',
    COUNT(*),
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END
FROM warehouse.fact_complaints
WHERE resolution_days IS NOT NULL
  AND resolution_days < 0

UNION ALL

SELECT
    'complaint resolution_days matches date difference when resolved',
    COUNT(*),
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END
FROM warehouse.fact_complaints
WHERE resolution_date IS NOT NULL
  AND resolution_days IS NOT NULL
  AND resolution_days <> (resolution_date - complaint_date);


-- ============================================================
-- 6. Campaign business-rule checks
-- ============================================================

SELECT
    'campaign name is populated' AS validation_check,
    COUNT(*) AS failed_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END AS validation_status
FROM warehouse.fact_campaigns
WHERE campaign_name IS NULL
   OR TRIM(campaign_name) = ''

UNION ALL

SELECT
    'campaign type is populated',
    COUNT(*),
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END
FROM warehouse.fact_campaigns
WHERE campaign_type IS NULL
   OR TRIM(campaign_type) = ''

UNION ALL

SELECT
    'campaign response status is populated',
    COUNT(*),
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END
FROM warehouse.fact_campaigns
WHERE response_status IS NULL
   OR TRIM(response_status) = ''

UNION ALL

SELECT
    'campaign response_date is not before sent_date',
    COUNT(*),
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END
FROM warehouse.fact_campaigns
WHERE response_date IS NOT NULL
  AND response_date < sent_date

UNION ALL

SELECT
    'converted campaigns have converted_count = 1',
    COUNT(*),
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END
FROM warehouse.fact_campaigns
WHERE converted_flag = TRUE
  AND converted_count <> 1

UNION ALL

SELECT
    'non-converted campaigns have converted_count = 0',
    COUNT(*),
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END
FROM warehouse.fact_campaigns
WHERE converted_flag = FALSE
  AND converted_count <> 0;


-- ============================================================
-- 7. SLA ticket business-rule checks
-- ============================================================

SELECT
    'sla ticket priority is populated' AS validation_check,
    COUNT(*) AS failed_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END AS validation_status
FROM warehouse.fact_sla_tickets
WHERE ticket_priority IS NULL
   OR TRIM(ticket_priority) = ''

UNION ALL

SELECT
    'sla ticket status is populated',
    COUNT(*),
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END
FROM warehouse.fact_sla_tickets
WHERE ticket_status IS NULL
   OR TRIM(ticket_status) = ''

UNION ALL

SELECT
    'assigned team is populated',
    COUNT(*),
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END
FROM warehouse.fact_sla_tickets
WHERE assigned_team IS NULL
   OR TRIM(assigned_team) = ''

UNION ALL

SELECT
    'sla target hours is positive',
    COUNT(*),
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END
FROM warehouse.fact_sla_tickets
WHERE sla_target_hours IS NULL
   OR sla_target_hours <= 0

UNION ALL

SELECT
    'sla due_datetime is not before created_datetime',
    COUNT(*),
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END
FROM warehouse.fact_sla_tickets
WHERE due_datetime < created_datetime

UNION ALL

SELECT
    'sla resolved_datetime is not before created_datetime',
    COUNT(*),
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END
FROM warehouse.fact_sla_tickets
WHERE resolved_datetime IS NOT NULL
  AND resolved_datetime < created_datetime

UNION ALL

SELECT
    'resolved ticket flag matches resolved_datetime',
    COUNT(*),
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END
FROM warehouse.fact_sla_tickets
WHERE
    (resolved_datetime IS NOT NULL AND is_ticket_resolved IS DISTINCT FROM TRUE)
    OR
    (resolved_datetime IS NULL AND is_ticket_resolved IS DISTINCT FROM FALSE)

UNION ALL

SELECT
    'sla_met_flag valid when resolved before or on due_datetime',
    COUNT(*),
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END
FROM warehouse.fact_sla_tickets
WHERE resolved_datetime IS NOT NULL
  AND resolved_datetime <= due_datetime
  AND sla_met_flag IS DISTINCT FROM TRUE

UNION ALL

SELECT
    'sla_met_flag valid when resolved after due_datetime',
    COUNT(*),
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END
FROM warehouse.fact_sla_tickets
WHERE resolved_datetime IS NOT NULL
  AND resolved_datetime > due_datetime
  AND sla_met_flag IS DISTINCT FROM FALSE;


-- ============================================================
-- 8. Natural key consistency checks between facts and dimensions
-- ============================================================

SELECT
    'transaction account_key matches account_id' AS validation_check,
    COUNT(*) AS failed_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END AS validation_status
FROM warehouse.fact_transactions ft
LEFT JOIN warehouse.dim_account da
    ON ft.account_key = da.account_key
WHERE ft.account_id <> da.account_id

UNION ALL

SELECT
    'transaction customer_key matches customer_id',
    COUNT(*),
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END
FROM warehouse.fact_transactions ft
LEFT JOIN warehouse.dim_customer dc
    ON ft.customer_key = dc.customer_key
WHERE ft.customer_id <> dc.customer_id

UNION ALL

SELECT
    'transaction product_key matches product_id',
    COUNT(*),
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END
FROM warehouse.fact_transactions ft
LEFT JOIN warehouse.dim_product dp
    ON ft.product_key = dp.product_key
WHERE ft.product_id <> dp.product_id

UNION ALL

SELECT
    'transaction branch_key matches branch_id',
    COUNT(*),
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END
FROM warehouse.fact_transactions ft
LEFT JOIN warehouse.dim_branch db
    ON ft.branch_key = db.branch_key
WHERE ft.branch_id <> db.branch_id

UNION ALL

SELECT
    'transaction channel_key matches channel_id',
    COUNT(*),
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END
FROM warehouse.fact_transactions ft
LEFT JOIN warehouse.dim_channel dch
    ON ft.channel_key = dch.channel_key
WHERE ft.channel_id <> dch.channel_id

UNION ALL

SELECT
    'complaint customer_key matches customer_id',
    COUNT(*),
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END
FROM warehouse.fact_complaints fc
LEFT JOIN warehouse.dim_customer dc
    ON fc.customer_key = dc.customer_key
WHERE fc.customer_id <> dc.customer_id

UNION ALL

SELECT
    'complaint account_key matches account_id',
    COUNT(*),
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END
FROM warehouse.fact_complaints fc
LEFT JOIN warehouse.dim_account da
    ON fc.account_key = da.account_key
WHERE fc.account_id <> da.account_id

UNION ALL

SELECT
    'campaign customer_key matches customer_id',
    COUNT(*),
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END
FROM warehouse.fact_campaigns fc
LEFT JOIN warehouse.dim_customer dc
    ON fc.customer_key = dc.customer_key
WHERE fc.customer_id <> dc.customer_id

UNION ALL

SELECT
    'sla customer_key matches customer_id',
    COUNT(*),
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END
FROM warehouse.fact_sla_tickets fst
LEFT JOIN warehouse.dim_customer dc
    ON fst.customer_key = dc.customer_key
WHERE fst.customer_id <> dc.customer_id

UNION ALL

SELECT
    'sla account_key matches account_id',
    COUNT(*),
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END
FROM warehouse.fact_sla_tickets fst
LEFT JOIN warehouse.dim_account da
    ON fst.account_key = da.account_key
WHERE fst.account_id <> da.account_id;