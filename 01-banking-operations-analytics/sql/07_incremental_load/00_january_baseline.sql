-- ============================================================
-- 1. Transaction date coverage and Complaint date coverage and row count
-- ============================================================

SELECT 
    'fact_transactions' AS table_name,
    MIN(transaction_date) AS min_date,
    MAX(transaction_date) AS max_date,
    COUNT (*) AS row_count
FROM warehouse.fact_transactions

UNION ALL

SELECT
    'fact_complaints' AS table_name,
    MIN(complaint_date) AS min_date,
    MAX(complaint_date) AS max_date,
    COUNT (*) AS row_count
FROM warehouse.fact_complaints;

-- ============================================================
-- 2. Complaint row count by month
-- ============================================================
SELECT
    DATE_TRUNC('month',complaint_date)::DATE AS complaint_month,
    COUNT(*) AS complaint_count
FROM warehouse.fact_complaints
GROUP BY 1
ORDER BY 1;

-- ============================================================
-- 3. Campaign row count by month
-- ============================================================

SELECT
    DATE_TRUNC('month',sent_date)::DATE AS campaign_month,
    COUNT(*) AS campaign_count
FROM warehouse.fact_campaigns
GROUP BY 1
ORDER BY 1;

-- ============================================================
-- 4. SLA ticket row count by month
-- ============================================================
SELECT
    DATE_TRUNC('month', created_datetime)::DATE AS sla_month,
    COUNT(*) AS sla_ticket_count
FROM warehouse.fact_sla_tickets
GROUP BY 1
ORDER BY 1;

-- ============================================================
-- 5. Matched SLA ticket creation month by complaint month
-- ============================================================

SELECT
    DATE_TRUNC('month', fc.complaint_date)::DATE AS complaint_month,
    DATE_TRUNC('month', fst.created_datetime)::DATE AS sla_creation_month,
    COUNT(DISTINCT fst.ticket_id) AS sla_ticket_count
FROM warehouse.fact_complaints fc
JOIN warehouse.fact_sla_tickets fst
    ON fc.complaint_id = fst.complaint_id
GROUP BY 1, 2
ORDER BY 1, 2;

-- ============================================================
-- 6. Complaint-to-SLA relationship by complaint month
-- ============================================================

SELECT 
    DATE_TRUNC('month', fc.complaint_date)::DATE AS complaint_month,
    COUNT(distinct fc.complaint_id) AS total_complaint_count,
    COUNT(DISTINCT CASE WHEN fst.complaint_id IS NULL THEN fc.complaint_id END) AS complaint_without_ticket_count,
    COUNT(DISTINCT CASE WHEN fst.complaint_id IS NOT NULL THEN fc.complaint_id END) AS complaint_with_ticket_count,
    COUNT(DISTINCT fst.ticket_id) AS total_ticket_count
FROM warehouse.fact_complaints fc
LEFT JOIN warehouse.fact_sla_tickets fst
    ON fc.complaint_id = fst.complaint_id
GROUP BY 1
ORDER BY 1;

-- ============================================================
-- 7. January transaction KPI baseline
-- ============================================================
SELECT 
    DATE_TRUNC('month', transaction_date)::DATE AS reporting_month,
    COUNT (DISTINCT customer_id) AS distinct_customer_count,
    COUNT (DISTINCT transaction_id) AS total_transaction_count,
    COUNT (DISTINCT CASE WHEN transaction_status = 'Success' THEN transaction_id END) AS successful_transaction_count,
    COUNT (DISTINCT CASE WHEN transaction_status = 'Failed' THEN transaction_id END) AS failed_transaction_count,
    COUNT (DISTINCT CASE WHEN transaction_status = 'Reversed' THEN transaction_id END) AS reversed_transaction_count,
    ROUND(100.0 * COUNT (DISTINCT CASE WHEN transaction_status = 'Success' THEN transaction_id END) / NULLIF(COUNT (DISTINCT transaction_id), 0), 2) AS transaction_success_rate_pct,
    ROUND(100.0 * COUNT (DISTINCT CASE WHEN transaction_status = 'Failed' THEN transaction_id END) / NULLIF(COUNT (DISTINCT transaction_id), 0), 2) AS transaction_failure_rate_pct,
    ROUND(100.0 * COUNT (DISTINCT CASE WHEN transaction_status = 'Reversed' THEN transaction_id END) / NULLIF(COUNT (DISTINCT transaction_id), 0), 2) AS transaction_reversal_rate_pct,
    SUM(amount) AS total_transaction_amount,
    SUM(fee_amount) AS total_fee_amount
FROM warehouse.fact_transactions
WHERE transaction_date >= '2026-01-01' AND transaction_date < '2026-02-01'
GROUP BY 1;

-- ============================================================
-- 7A. Validate transaction status categories
-- ============================================================

SELECT 
    transaction_status,
    COUNT(*) AS status_count
FROM warehouse.fact_transactions
WHERE transaction_date >= '2026-01-01' AND transaction_date < '2026-02-01'
GROUP BY 1
ORDER BY 1;

-- ============================================================
-- 8. January transaction performance by channel
-- ============================================================

SELECT
    dc.channel_name,
    dc.channel_category,
    dc.is_digital,
    COUNT(DISTINCT ft.transaction_id) AS total_transaction_count,
    COUNT(DISTINCT CASE WHEN ft.transaction_status = 'Success' THEN ft.transaction_id END) AS successful_transaction_count,
    COUNT(DISTINCT CASE WHEN ft.transaction_status = 'Failed' THEN ft.transaction_id END) AS failed_transaction_count,
    COUNT(DISTINCT CASE WHEN ft.transaction_status = 'Reversed' THEN ft.transaction_id END) AS reversed_transaction_count,
    ROUND(100.0 * COUNT(DISTINCT CASE WHEN ft.transaction_status = 'Success' THEN ft.transaction_id END) / NULLIF(COUNT(DISTINCT ft.transaction_id), 0), 2) AS transaction_success_rate_pct,
    ROUND(100.0 * COUNT(DISTINCT CASE WHEN ft.transaction_status = 'Failed' THEN ft.transaction_id END) / NULLIF(COUNT(DISTINCT ft.transaction_id), 0), 2) AS transaction_failure_rate_pct,
    ROUND(100.0 * COUNT(DISTINCT CASE WHEN ft.transaction_status = 'Reversed' THEN ft.transaction_id END) / NULLIF(COUNT(DISTINCT ft.transaction_id), 0), 2) AS transaction_reversal_rate_pct,
    SUM(ft.amount) AS total_transaction_amount,
    SUM(ft.fee_amount) AS total_fee_amount
FROM warehouse.fact_transactions ft
JOIN warehouse.dim_channel dc
    ON ft.channel_id = dc.channel_id
WHERE ft.transaction_date >= '2026-01-01' AND ft.transaction_date < '2026-02-01'
GROUP BY 1, 2, 3
ORDER BY 
    transaction_failure_rate_pct DESC, 
    transaction_reversal_rate_pct DESC, 
    total_transaction_count DESC;
-- ============================================================
-- 9. January digital vs non-digital transaction performance
-- ============================================================

SELECT
    dc.is_digital,
    COUNT(DISTINCT ft.transaction_id) AS total_transaction_count,
    CASE 
        WHEN dc.is_digital 
        THEN 'Digital' 
        ELSE 'Non-Digital' 
    END AS channel_type,
    ROUND(100.0 * COUNT(DISTINCT ft.transaction_id) / NULLIF(SUM(COUNT(DISTINCT ft.transaction_id)) OVER (),0 ),2) AS transaction_share_pct,
    COUNT(DISTINCT CASE WHEN ft.transaction_status = 'Success' THEN ft.transaction_id END) AS successful_transaction_count,
    COUNT(DISTINCT CASE WHEN ft.transaction_status = 'Failed' THEN ft.transaction_id END) AS failed_transaction_count,
    COUNT(DISTINCT CASE WHEN ft.transaction_status = 'Reversed' THEN ft.transaction_id END) AS reversed_transaction_count,
    ROUND(100.0 * COUNT(DISTINCT CASE WHEN ft.transaction_status = 'Success' THEN ft.transaction_id END) / NULLIF(COUNT(DISTINCT ft.transaction_id), 0), 2) AS transaction_success_rate_pct,
    ROUND(100.0 * COUNT(DISTINCT CASE WHEN ft.transaction_status = 'Failed' THEN ft.transaction_id END) / NULLIF(COUNT(DISTINCT ft.transaction_id), 0), 2) AS transaction_failure_rate_pct,
    ROUND(100.0 * COUNT(DISTINCT CASE WHEN ft.transaction_status = 'Reversed' THEN ft.transaction_id END) / NULLIF(COUNT(DISTINCT ft.transaction_id), 0), 2) AS transaction_reversal_rate_pct,
    SUM(ft.amount) AS total_transaction_amount,
    AVG(ft.amount) AS average_transaction_amount,
    SUM(ft.fee_amount) AS total_fee_amount
FROM warehouse.fact_transactions ft
JOIN warehouse.dim_channel dc
    ON ft.channel_id = dc.channel_id
WHERE ft.transaction_date >= '2026-01-01' AND ft.transaction_date < '2026-02-01'
GROUP BY 1
ORDER BY 
    transaction_failure_rate_pct DESC, 
    transaction_reversal_rate_pct DESC, 
    total_transaction_count DESC;

-- ============================================================
-- 10. January transaction performance by channel and product
-- ============================================================

WITH channel_product_transactions AS (
    SELECT
        dc.channel_name,
        dc.channel_category,
        dc.is_digital,
        dp.product_name,
        COUNT(DISTINCT ft.transaction_id) AS total_transaction_count,
        COUNT(DISTINCT CASE WHEN ft.transaction_status = 'Success' THEN ft.transaction_id END) AS successful_transaction_count,
        COUNT(DISTINCT CASE WHEN ft.transaction_status = 'Failed' THEN ft.transaction_id END) AS failed_transaction_count,
        COUNT(DISTINCT CASE WHEN ft.transaction_status = 'Reversed' THEN ft.transaction_id END) AS reversed_transaction_count,
        ROUND(100.0 * COUNT(DISTINCT CASE WHEN ft.transaction_status = 'Success' THEN ft.transaction_id END) / NULLIF(COUNT(DISTINCT ft.transaction_id), 0), 2) AS transaction_success_rate_pct,
        ROUND(100.0 * COUNT(DISTINCT CASE WHEN ft.transaction_status = 'Failed' THEN ft.transaction_id END) / NULLIF(COUNT(DISTINCT ft.transaction_id), 0), 2) AS transaction_failure_rate_pct,
        ROUND(100.0 * COUNT(DISTINCT CASE WHEN ft.transaction_status = 'Reversed' THEN ft.transaction_id END) / NULLIF(COUNT(DISTINCT ft.transaction_id), 0), 2) AS transaction_reversal_rate_pct,
        SUM(ft.amount) AS total_transaction_amount,
        SUM(CASE WHEN ft.transaction_status = 'Failed' THEN ft.amount ELSE 0 END) AS failed_transaction_amount,
        SUM(CASE WHEN ft.transaction_status = 'Reversed' THEN ft.amount ELSE 0 END) AS reversed_transaction_amount
    FROM warehouse.fact_transactions ft
    JOIN warehouse.dim_channel dc
        ON ft.channel_id = dc.channel_id
    JOIN warehouse.dim_product dp
        ON ft.product_id = dp.product_id
    WHERE ft.transaction_date >= '2026-01-01' AND ft.transaction_date < '2026-02-01'
    GROUP BY 1, 2, 3, 4),
ranked as (
    SELECT *,
        ROW_NUMBER() OVER (ORDER BY transaction_failure_rate_pct DESC, transaction_reversal_rate_pct DESC, total_transaction_count DESC) AS operational_risk_rank
    FROM channel_product_transactions
)
SELECT *
FROM ranked
ORDER BY operational_risk_rank;

-- ============================================================
-- 11. January digital transaction performance by customer segment
-- ============================================================

WITH customer_channel_transactions AS (
        SELECT
            dcust.customer_segment,
            COUNT(DISTINCT ft.customer_id) AS distinct_customer_count,
            COUNT(DISTINCT ft.transaction_id) AS total_transaction_count,
            COUNT(DISTINCT CASE WHEN ft.transaction_status = 'Success' THEN ft.transaction_id END) AS successful_transaction_count,
            COUNT(DISTINCT CASE WHEN ft.transaction_status = 'Failed' THEN ft.transaction_id END) AS failed_transaction_count,
            COUNT(DISTINCT CASE WHEN ft.transaction_status = 'Reversed' THEN ft.transaction_id  END) AS reversed_transaction_count,
            ROUND(100.0 * COUNT(DISTINCT CASE WHEN ft.transaction_status = 'Failed' THEN ft.transaction_id END) / NULLIF(COUNT(DISTINCT ft.transaction_id), 0), 2) AS transaction_failure_rate_pct,
            ROUND(100.0 * COUNT(DISTINCT CASE WHEN ft.transaction_status = 'Reversed' THEN ft.transaction_id END) / NULLIF(COUNT(DISTINCT ft.transaction_id), 0), 2) AS transaction_reversal_rate_pct,
            SUM(ft.amount) AS total_transaction_amount,
            AVG(ft.amount) AS average_transaction_amount,
            SUM(CASE WHEN ft.transaction_status = 'Failed' THEN ft.amount ELSE 0 END) AS failed_transaction_amount,
            SUM(CASE WHEN ft.transaction_status = 'Reversed' THEN ft.amount ELSE 0 END) AS reversed_transaction_amount
        FROM warehouse.fact_transactions ft
        JOIN warehouse.dim_channel dc
            ON ft.channel_id = dc.channel_id
        JOIN warehouse.dim_customer dcust
            ON ft.customer_id = dcust.customer_id
        WHERE ft.transaction_date >= '2026-01-01' AND ft.transaction_date < '2026-02-01'
            AND dc.is_digital = True
        GROUP BY 1
),
ranked AS (
    SELECT *,
        ROW_NUMBER() OVER (ORDER BY transaction_failure_rate_pct DESC, transaction_reversal_rate_pct DESC, total_transaction_count DESC) AS operational_risk_rank
    FROM customer_channel_transactions
)
SELECT *
FROM ranked
ORDER BY operational_risk_rank;

-- ============================================================
-- 12. January Mobile Banking vs Internet Banking performance
-- ============================================================

SELECT
    dc.channel_name,
    COUNT(DISTINCT ft.customer_id) AS distinct_customer_count,
    COUNT(DISTINCT ft.transaction_id) AS total_transaction_count,
    COUNT(DISTINCT CASE WHEN ft.transaction_status = 'Success' THEN ft.transaction_id END) AS successful_transaction_count,
    COUNT(DISTINCT CASE WHEN ft.transaction_status = 'Failed' THEN ft.transaction_id END) AS failed_transaction_count,
    COUNT(DISTINCT CASE WHEN ft.transaction_status = 'Reversed' THEN ft.transaction_id END) AS reversed_transaction_count,
    ROUND(100.0 * COUNT(DISTINCT CASE WHEN ft.transaction_status = 'Failed' THEN ft.transaction_id END) / NULLIF(COUNT(DISTINCT ft.transaction_id), 0), 2) AS transaction_failure_rate_pct,
    ROUND(100.0 * COUNT(DISTINCT CASE WHEN ft.transaction_status = 'Reversed' THEN ft.transaction_id END) / NULLIF(COUNT(DISTINCT ft.transaction_id), 0), 2) AS transaction_reversal_rate_pct,
    SUM(ft.amount) AS total_transaction_amount,
    AVG(ft.amount) AS average_transaction_amount,
    SUM(CASE WHEN ft.transaction_status = 'Failed' THEN ft.amount ELSE 0 END) AS failed_transaction_amount,
    SUM(CASE WHEN ft.transaction_status = 'Reversed' THEN ft.amount ELSE 0 END) AS reversed_transaction_amount
FROM warehouse.fact_transactions ft
JOIN warehouse.dim_channel dc
    ON ft.channel_id = dc.channel_id
WHERE ft.transaction_date >= '2026-01-01' AND ft.transaction_date < '2026-02-01'
    AND dc.channel_name IN ('Mobile Banking', 'Internet Banking')
GROUP BY 1
ORDER BY
    failed_transaction_count DESC,
    reversed_transaction_count DESC;

-- ============================================================
-- 13. January Mobile Banking performance by product
-- ============================================================

SELECT
    dp.product_name,
    COUNT(DISTINCT ft.transaction_id) AS total_transaction_count,
    ROUND(100.0 * COUNT(DISTINCT ft.transaction_id) / NULLIF(SUM(COUNT(DISTINCT ft.transaction_id)) OVER(), 0), 2) AS share_of_mobile_banking_volume,
    COUNT(DISTINCT CASE WHEN ft.transaction_status = 'Failed' THEN ft.transaction_id END) AS failed_transaction_count,
    COUNT(DISTINCT CASE WHEN ft.transaction_status = 'Reversed' THEN ft.transaction_id END) AS reversed_transaction_count,
    ROUND(100.0 * COUNT(DISTINCT CASE WHEN ft.transaction_status = 'Failed' THEN ft.transaction_id END) / NULLIF(COUNT(DISTINCT ft.transaction_id), 0), 2) AS transaction_failure_rate_pct,
    ROUND(100.0 * COUNT(DISTINCT CASE WHEN ft.transaction_status = 'Reversed' THEN ft.transaction_id END) / NULLIF(COUNT(DISTINCT ft.transaction_id), 0), 2) AS transaction_reversal_rate_pct,
    SUM(ft.amount) AS total_transaction_amount,
    ROUND(AVG(ft.amount),2) AS average_transaction_amount,
    SUM(CASE WHEN ft.transaction_status = 'Failed' THEN ft.amount ELSE 0 END) AS failed_transaction_amount,
    ROUND(
    100.0 *
    COUNT(DISTINCT CASE 
		WHEN ft.transaction_status = 'Failed'
        THEN ft.transaction_id
    END)
    /
    NULLIF(
        SUM(
            COUNT(DISTINCT CASE
                WHEN ft.transaction_status = 'Failed'
                THEN ft.transaction_id
            END)
        ) OVER (),
        0
    ),
    2
) AS share_of_mobile_banking_failures_pct,
    SUM(CASE WHEN ft.transaction_status = 'Reversed' THEN ft.amount ELSE 0 END) AS reversed_transaction_amount
FROM warehouse.fact_transactions ft
JOIN warehouse.dim_channel dc
    ON ft.channel_id = dc.channel_id
JOIN warehouse.dim_product dp
    ON ft.product_id = dp.product_id
WHERE ft.transaction_date >= '2026-01-01' AND ft.transaction_date < '2026-02-01'
    AND dc.channel_name = 'Mobile Banking'
GROUP BY 1
ORDER BY 
    failed_transaction_count DESC,
    reversed_transaction_count DESC,
    total_transaction_amount DESC, 
    total_transaction_count DESC,
    transaction_failure_rate_pct DESC, 
    transaction_reversal_rate_pct DESC;

-- ============================================================
-- 14. January Mobile Banking performance by customer segment
-- ============================================================

SELECT
    cust.customer_segment,
    COUNT(DISTINCT ft.customer_id) AS distinct_customer_count,
    COUNT(DISTINCT ft.transaction_id) AS total_transaction_count,
    ROUND(100.0 * COUNT(DISTINCT ft.transaction_id) / NULLIF(SUM(COUNT(DISTINCT ft.transaction_id)) OVER(), 0), 2) AS share_of_mobile_banking_volume,
    COUNT(DISTINCT CASE WHEN ft.transaction_status = 'Failed' THEN ft.transaction_id END) AS failed_transaction_count,
    COUNT(DISTINCT CASE WHEN ft.transaction_status = 'Reversed' THEN ft.transaction_id END) AS reversed_transaction_count,
    ROUND(100.0 * COUNT(DISTINCT CASE WHEN ft.transaction_status = 'Failed' THEN ft.transaction_id END) / NULLIF(COUNT(DISTINCT ft.transaction_id), 0), 2) AS transaction_failure_rate_pct,
    ROUND(100.0 * COUNT(DISTINCT CASE WHEN ft.transaction_status = 'Reversed' THEN ft.transaction_id END) / NULLIF(COUNT(DISTINCT ft.transaction_id), 0), 2) AS transaction_reversal_rate_pct,
    SUM(ft.amount) AS total_transaction_amount,
    SUM(CASE WHEN ft.transaction_status = 'Failed' THEN ft.amount ELSE 0 END) AS failed_transaction_amount,
    SUM(CASE WHEN ft.transaction_status = 'Reversed' THEN ft.amount ELSE 0 END) AS reversed_transaction_amount,
    ROUND(
        100.0 *
        COUNT(DISTINCT CASE 
            WHEN ft.transaction_status = 'Failed'
            THEN ft.transaction_id
        END)
        /
        NULLIF(
            SUM(
                COUNT(DISTINCT CASE
                    WHEN ft.transaction_status = 'Failed'
                    THEN ft.transaction_id
                END)
            ) OVER (),
            0
        ),
        2
    ) AS share_of_mobile_banking_failures_pct
FROM warehouse.fact_transactions ft
JOIN warehouse.dim_channel dc
    ON ft.channel_id = dc.channel_id
JOIN warehouse.dim_customer cust
    ON ft.customer_id = cust.customer_id
WHERE ft.transaction_date >= '2026-01-01' AND ft.transaction_date < '2026-02-01'
    AND dc.channel_name = 'Mobile Banking'
GROUP BY 1
ORDER BY 
    failed_transaction_count DESC,
    reversed_transaction_count DESC,
    total_transaction_amount DESC, 
    total_transaction_count DESC,
    transaction_failure_rate_pct DESC, 
    transaction_reversal_rate_pct DESC;

-- ============================================================
-- 15. January Mobile Banking exposure by product and customer segment
-- ============================================================

SELECT
    dp.product_name,
    cust.customer_segment,
    COUNT(DISTINCT ft.customer_id) AS distinct_customer_count,
    COUNT(DISTINCT ft.transaction_id) AS total_transaction_count,
    COUNT(DISTINCT CASE WHEN ft.transaction_status = 'Failed' THEN ft.transaction_id END) AS failed_transaction_count,
    COUNT(DISTINCT CASE WHEN ft.transaction_status = 'Reversed' THEN ft.transaction_id END) AS reversed_transaction_count,
    ROUND(100.0 * COUNT(DISTINCT CASE WHEN ft.transaction_status = 'Failed' THEN ft.transaction_id END) / NULLIF(COUNT(DISTINCT ft.transaction_id), 0), 2) AS transaction_failure_rate_pct,
    ROUND(100.0 * COUNT(DISTINCT CASE WHEN ft.transaction_status = 'Reversed' THEN ft.transaction_id END) / NULLIF(COUNT(DISTINCT ft.transaction_id), 0), 2) AS transaction_reversal_rate_pct,
    SUM(ft.amount) AS total_transaction_amount,
    SUM(CASE WHEN ft.transaction_status = 'Failed' THEN ft.amount ELSE 0 END) AS failed_transaction_amount,
    SUM(CASE WHEN ft.transaction_status = 'Reversed' THEN ft.amount ELSE 0 END) AS reversed_transaction_amount,
    ROUND(
        100.0 *
        COUNT(DISTINCT CASE
        WHEN ft.transaction_status = 'Failed'
        THEN ft.transaction_id
    END)
    /
    NULLIF(
        SUM(
            COUNT(DISTINCT CASE
                WHEN ft.transaction_status = 'Failed'
                THEN ft.transaction_id
            END)
        ) OVER (),
        0
    ),
    2
) AS share_of_mobile_banking_failures_pct
FROM warehouse.fact_transactions ft
JOIN warehouse.dim_channel dc
    ON ft.channel_id = dc.channel_id
JOIN warehouse.dim_product dp
    ON ft.product_id = dp.product_id
JOIN warehouse.dim_customer cust
    ON ft.customer_id = cust.customer_id
WHERE ft.transaction_date >= '2026-01-01' AND ft.transaction_date < '2026-02-01'
    AND dc.channel_name = 'Mobile Banking'
GROUP BY 1, 2
ORDER BY 
    failed_transaction_count DESC,
    reversed_transaction_count DESC,
    total_transaction_amount DESC, 
    total_transaction_count DESC,
    transaction_failure_rate_pct DESC, 
    transaction_reversal_rate_pct DESC;


-- ============================================================
-- 16A. Validate complaint categories, statuses and priorities
-- ============================================================

SELECT 
    complaint_category,
    COUNT(*) AS category_count
FROM warehouse.fact_complaints
WHERE complaint_date >= '2026-01-01' AND complaint_date < '2026-02-01'
GROUP BY 1;

SELECT 
    complaint_status,
    COUNT(*) AS status_count
FROM warehouse.fact_complaints
WHERE complaint_date >= '2026-01-01' AND complaint_date < '2026-02-01'
GROUP BY 1;

SELECT 
    complaint_priority,
    COUNT(*) AS priority_count
FROM warehouse.fact_complaints
WHERE complaint_date >= '2026-01-01' AND complaint_date < '2026-02-01'
GROUP BY 1;

SELECT
    is_resolved,
    COUNT(*) AS complaint_count
FROM warehouse.fact_complaints
WHERE complaint_date >= '2026-01-01' AND complaint_date < '2026-02-01'
GROUP BY 1;

-- ============================================================
-- 16. January complaint KPI baseline
-- ============================================================

WITH complaint_summary AS (
    SELECT
        DATE_TRUNC('month', fc.complaint_date)::DATE AS reporting_month,
        COUNT(DISTINCT fc.complaint_id) AS total_complaint_count,
        COUNT(DISTINCT CASE
            WHEN fc.is_resolved = TRUE
            THEN fc.complaint_id
        END) AS resolved_complaint_count,
        COUNT(DISTINCT CASE
            WHEN fc.is_resolved = FALSE
            THEN fc.complaint_id
        END) AS unresolved_complaint_count,
        ROUND(
            100.0 *
            COUNT(DISTINCT CASE
                WHEN fc.is_resolved = TRUE
                THEN fc.complaint_id
            END)
            /
            NULLIF(COUNT(DISTINCT fc.complaint_id), 0),
            2
        ) AS complaint_resolution_rate_pct,
        ROUND(
            AVG(
                CASE
                    WHEN fc.is_resolved = TRUE
                    THEN fc.resolution_days
                END
            ),
            2
        ) AS average_resolution_days,
        COUNT(DISTINCT CASE
            WHEN fc.complaint_priority = 'High'
            THEN fc.complaint_id
        END) AS high_priority_complaint_count
    FROM warehouse.fact_complaints fc
    WHERE fc.complaint_date >= '2026-01-01'
      AND fc.complaint_date < '2026-02-01'
    GROUP BY 1
),

sla_relationship_summary AS (
    SELECT
        DATE_TRUNC('month', fc.complaint_date)::DATE AS reporting_month,
        COUNT(DISTINCT CASE
            WHEN fst.ticket_id IS NOT NULL
            THEN fc.complaint_id
        END) AS complaint_with_sla_ticket_count,
        COUNT(DISTINCT CASE
            WHEN fst.ticket_id IS NULL
            THEN fc.complaint_id
        END) AS complaint_without_sla_ticket_count,
        COUNT(DISTINCT fst.ticket_id) AS total_sla_ticket_count
    FROM warehouse.fact_complaints fc
    LEFT JOIN warehouse.fact_sla_tickets fst
        ON fc.complaint_id = fst.complaint_id
    WHERE fc.complaint_date >= '2026-01-01'
      AND fc.complaint_date < '2026-02-01'
    GROUP BY 1
)

SELECT
    cs.reporting_month,
    cs.total_complaint_count,
    cs.resolved_complaint_count,
    cs.unresolved_complaint_count,
    cs.complaint_resolution_rate_pct,
    cs.average_resolution_days,
    cs.high_priority_complaint_count,
    COALESCE(srs.complaint_with_sla_ticket_count, 0)
        AS complaint_with_sla_ticket_count,
    COALESCE(srs.complaint_without_sla_ticket_count, 0)
        AS complaint_without_sla_ticket_count,
    COALESCE(srs.total_sla_ticket_count, 0)
        AS total_sla_ticket_count
FROM complaint_summary cs
LEFT JOIN sla_relationship_summary srs
    ON cs.reporting_month = srs.reporting_month;


-- ============================================================
-- 17. January complaint performance by channel
-- ============================================================

WITH complaint_by_channel AS (
    SELECT
        fc.channel_id,
        dc.channel_name,
        COUNT(DISTINCT fc.complaint_id) AS total_complaint_count,
        COUNT(DISTINCT CASE
            WHEN fc.is_resolved = TRUE
            THEN fc.complaint_id
        END) AS resolved_complaint_count,
        COUNT(DISTINCT CASE
            WHEN fc.is_resolved = FALSE
            THEN fc.complaint_id
        END) AS unresolved_complaint_count,
        ROUND(
            100.0 *
            COUNT(DISTINCT CASE
                WHEN fc.is_resolved = TRUE
                THEN fc.complaint_id
            END)
            /
            NULLIF(COUNT(DISTINCT fc.complaint_id), 0),
            2
        ) AS complaint_resolution_rate_pct,
        ROUND(
            AVG(
                CASE
                    WHEN fc.is_resolved = TRUE
                    THEN fc.resolution_days
                END
            ),
            2
        ) AS average_resolution_days,
        COUNT(DISTINCT CASE
            WHEN fc.complaint_priority = 'High'
            THEN fc.complaint_id
        END) AS high_priority_complaint_count
    FROM warehouse.fact_complaints fc
    JOIN warehouse.dim_channel dc
        ON fc.channel_id = dc.channel_id
    WHERE fc.complaint_date >= '2026-01-01'
      AND fc.complaint_date < '2026-02-01'
    GROUP BY 1, 2
),

sla_by_channel AS (
    SELECT
        fc.channel_id,
        COUNT(DISTINCT CASE
            WHEN fst.ticket_id IS NOT NULL
            THEN fc.complaint_id
        END) AS complaint_with_sla_ticket_count,
        COUNT(DISTINCT fst.ticket_id) AS total_sla_ticket_count
    FROM warehouse.fact_complaints fc
    LEFT JOIN warehouse.fact_sla_tickets fst
        ON fc.complaint_id = fst.complaint_id
    WHERE fc.complaint_date >= '2026-01-01'
      AND fc.complaint_date < '2026-02-01'
    GROUP BY 1
)

SELECT
    cbc.channel_name,
    cbc.total_complaint_count,
    cbc.resolved_complaint_count,
    cbc.unresolved_complaint_count,
    cbc.complaint_resolution_rate_pct,
    cbc.average_resolution_days,
    cbc.high_priority_complaint_count,
    COALESCE(sbc.complaint_with_sla_ticket_count, 0)
        AS complaint_with_sla_ticket_count,
    COALESCE(sbc.total_sla_ticket_count, 0)
        AS total_sla_ticket_count
FROM complaint_by_channel cbc
LEFT JOIN sla_by_channel sbc
    ON cbc.channel_id = sbc.channel_id
ORDER BY
    cbc.total_complaint_count DESC,
    cbc.complaint_resolution_rate_pct ASC;

-- ============================================================
-- 18. January complaints per 1,000 transactions by channel
-- ============================================================

WITH transaction_by_channel AS (
    SELECT
        ft.channel_id,
        dc.channel_name,
        COUNT(DISTINCT ft.transaction_id) AS total_transaction_count
    FROM warehouse.fact_transactions ft
    JOIN warehouse.dim_channel dc
        ON ft.channel_id = dc.channel_id
    WHERE ft.transaction_date >= '2026-01-01'
      AND ft.transaction_date < '2026-02-01'
    GROUP BY 1, 2
),

complaint_by_channel AS (
    SELECT
        fc.channel_id,
        COUNT(DISTINCT fc.complaint_id) AS total_complaint_count
    FROM warehouse.fact_complaints fc
    WHERE fc.complaint_date >= '2026-01-01'
      AND fc.complaint_date < '2026-02-01'
    GROUP BY 1
)

SELECT
    tbc.channel_name,
    tbc.total_transaction_count,
    COALESCE(cbc.total_complaint_count, 0) AS total_complaint_count,
    ROUND(
        1000.0 *
        COALESCE(cbc.total_complaint_count, 0)
        /
        NULLIF(tbc.total_transaction_count, 0),
        2
    ) AS complaints_per_1000_transactions
FROM transaction_by_channel tbc
LEFT JOIN complaint_by_channel cbc
    ON tbc.channel_id = cbc.channel_id
ORDER BY complaints_per_1000_transactions DESC;

-- ============================================================
-- 19. SLA performance for January complaint cohort
-- ============================================================

SELECT
    fst.assigned_team,
    fst.ticket_priority,
    COUNT(DISTINCT fst.ticket_id) AS total_sla_ticket_count,
    COUNT(DISTINCT CASE
        WHEN fst.is_ticket_resolved = TRUE
        THEN fst.ticket_id
    END) AS resolved_sla_ticket_count,
    COUNT(DISTINCT CASE
        WHEN fst.sla_met_count = 1
        THEN fst.ticket_id
    END) AS sla_met_ticket_count,
    COUNT(DISTINCT CASE
        WHEN fst.sla_breached_count = 1
        THEN fst.ticket_id
    END) AS sla_breached_ticket_count,
    ROUND(
        100.0 *
        COUNT(DISTINCT CASE
            WHEN fst.sla_breached_count = 1
            THEN fst.ticket_id
        END)
        /
        NULLIF(COUNT(DISTINCT fst.ticket_id), 0),
        2
    ) AS sla_breach_rate_pct,
    COUNT(DISTINCT fc.complaint_id)
        AS distinct_complaint_count,
    ROUND(
        1.0 * COUNT(DISTINCT fst.ticket_id)
        /
        NULLIF(COUNT(DISTINCT fc.complaint_id), 0),
        2
    ) AS tickets_per_complaint
FROM warehouse.fact_complaints fc
JOIN warehouse.fact_sla_tickets fst
    ON fc.complaint_id = fst.complaint_id
WHERE fc.complaint_date >= '2026-01-01'
  AND fc.complaint_date < '2026-02-01'
GROUP BY 1, 2
ORDER BY
    sla_breach_rate_pct DESC,
    total_sla_ticket_count DESC;

-- ============================================================
-- 20. January Mobile Banking complaint and SLA impact
--     by product and customer segment
-- ============================================================

WITH complaint_by_product_segment AS (
    SELECT
        fc.product_id,
        dp.product_name,
        cust.customer_segment,
        COUNT(DISTINCT fc.customer_id) AS distinct_customer_count,
        COUNT(DISTINCT fc.complaint_id) AS total_complaint_count,
        COUNT(DISTINCT CASE
            WHEN fc.is_resolved = TRUE
            THEN fc.complaint_id
        END) AS resolved_complaint_count,
        ROUND(
            100.0 *
            COUNT(DISTINCT CASE
                WHEN fc.is_resolved = TRUE
                THEN fc.complaint_id
            END)
            /
            NULLIF(COUNT(DISTINCT fc.complaint_id), 0),
            2
        ) AS complaint_resolution_rate_pct,
        ROUND(
            AVG(
                CASE
                    WHEN fc.is_resolved = TRUE
                    THEN fc.resolution_days
                END
            ),
            2
        ) AS average_resolution_days
    FROM warehouse.fact_complaints fc
    JOIN warehouse.dim_channel dc
        ON fc.channel_id = dc.channel_id
    JOIN warehouse.dim_product dp
        ON fc.product_id = dp.product_id
    JOIN warehouse.dim_customer cust
        ON fc.customer_id = cust.customer_id
    WHERE fc.complaint_date >= '2026-01-01'
      AND fc.complaint_date < '2026-02-01'
      AND dc.channel_name = 'Mobile Banking'
    GROUP BY 1, 2, 3
),

sla_by_product_segment AS (
    SELECT
        fc.product_id,
        cust.customer_segment,
        COUNT(DISTINCT fst.ticket_id) AS total_sla_ticket_count,
        COUNT(DISTINCT CASE
            WHEN fst.sla_breached_count = 1
            THEN fst.ticket_id
        END) AS sla_breached_ticket_count,
        ROUND(
            100.0 *
            COUNT(DISTINCT CASE
                WHEN fst.sla_breached_count = 1
                THEN fst.ticket_id
            END)
            /
            NULLIF(COUNT(DISTINCT fst.ticket_id), 0),
            2
        ) AS sla_breach_rate_pct
    FROM warehouse.fact_complaints fc
    JOIN warehouse.dim_channel dc
        ON fc.channel_id = dc.channel_id
    JOIN warehouse.dim_customer cust
        ON fc.customer_id = cust.customer_id
    JOIN warehouse.fact_sla_tickets fst
        ON fc.complaint_id = fst.complaint_id
    WHERE fc.complaint_date >= '2026-01-01'
      AND fc.complaint_date < '2026-02-01'
      AND dc.channel_name = 'Mobile Banking'
    GROUP BY 1, 2
)

SELECT
    cbps.product_name,
    cbps.customer_segment,
    cbps.distinct_customer_count,
    cbps.total_complaint_count,
    cbps.resolved_complaint_count,
    cbps.complaint_resolution_rate_pct,
    cbps.average_resolution_days,
    COALESCE(sbps.total_sla_ticket_count, 0)
        AS total_sla_ticket_count,
    COALESCE(sbps.sla_breached_ticket_count, 0)
        AS sla_breached_ticket_count,
    COALESCE(sbps.sla_breach_rate_pct, 0)
        AS sla_breach_rate_pct
FROM complaint_by_product_segment cbps
LEFT JOIN sla_by_product_segment sbps
    ON cbps.product_id = sbps.product_id
   AND cbps.customer_segment = sbps.customer_segment
ORDER BY
    cbps.total_complaint_count DESC,
    sla_breach_rate_pct DESC;

-- ============================================================
-- 21. January Mobile Banking focus selection scorecard
-- ============================================================

WITH transaction_summary AS (
    SELECT
        ft.product_id,
        dp.product_name,
        cust.customer_segment,
        COUNT(DISTINCT ft.customer_id) AS distinct_customer_count,
        COUNT(DISTINCT ft.transaction_id) AS total_transaction_count,
        COUNT(DISTINCT CASE
            WHEN ft.transaction_status = 'Failed'
            THEN ft.transaction_id
        END) AS failed_transaction_count,
        COUNT(DISTINCT CASE
            WHEN ft.transaction_status = 'Reversed'
            THEN ft.transaction_id
        END) AS reversed_transaction_count,
        SUM(ft.amount) AS total_transaction_amount,
        SUM(CASE
            WHEN ft.transaction_status = 'Failed'
            THEN ft.amount
            ELSE 0
        END) AS failed_transaction_amount,
        SUM(CASE
            WHEN ft.transaction_status = 'Reversed'
            THEN ft.amount
            ELSE 0
        END) AS reversed_transaction_amount
    FROM warehouse.fact_transactions ft
    JOIN warehouse.dim_channel dc
        ON ft.channel_id = dc.channel_id
    JOIN warehouse.dim_product dp
        ON ft.product_id = dp.product_id
    JOIN warehouse.dim_customer cust
        ON ft.customer_id = cust.customer_id
    WHERE ft.transaction_date >= '2026-01-01'
      AND ft.transaction_date < '2026-02-01'
      AND dc.channel_name = 'Mobile Banking'
    GROUP BY 1, 2, 3
),

complaint_summary AS (
    SELECT
        fc.product_id,
        cust.customer_segment,
        COUNT(DISTINCT fc.complaint_id) AS total_complaint_count,
        COUNT(DISTINCT CASE
            WHEN fc.is_resolved = TRUE
            THEN fc.complaint_id
        END) AS resolved_complaint_count,
        ROUND(
            AVG(
                CASE
                    WHEN fc.is_resolved = TRUE
                    THEN fc.resolution_days
                END
            ),
            2
        ) AS average_resolution_days,
        ROUND(
            100.0 *
            COUNT(DISTINCT CASE
                WHEN fc.is_resolved = TRUE
                THEN fc.complaint_id
            END)
            /
            NULLIF(COUNT(DISTINCT fc.complaint_id), 0),
        2
        ) AS complaint_resolution_rate_pct
    FROM warehouse.fact_complaints fc
    JOIN warehouse.dim_channel dc
        ON fc.channel_id = dc.channel_id
    JOIN warehouse.dim_customer cust
        ON fc.customer_id = cust.customer_id
    WHERE fc.complaint_date >= '2026-01-01'
      AND fc.complaint_date < '2026-02-01'
      AND dc.channel_name = 'Mobile Banking'
    GROUP BY 1, 2
),

sla_summary AS (
    SELECT
        fc.product_id,
        cust.customer_segment,
        COUNT(DISTINCT fst.ticket_id) AS total_sla_ticket_count,
        COUNT(DISTINCT CASE
            WHEN fst.sla_breached_count = 1
            THEN fst.ticket_id
        END) AS sla_breached_ticket_count,
        ROUND(
            100.0 *
            COUNT(DISTINCT CASE
                WHEN fst.sla_breached_count = 1
                THEN fst.ticket_id
            END)
            /
            NULLIF(COUNT(DISTINCT fst.ticket_id), 0),
            2
        ) AS sla_breach_rate_pct
    FROM warehouse.fact_complaints fc
    JOIN warehouse.dim_channel dc
        ON fc.channel_id = dc.channel_id
    JOIN warehouse.dim_customer cust
        ON fc.customer_id = cust.customer_id
    JOIN warehouse.fact_sla_tickets fst
        ON fc.complaint_id = fst.complaint_id
    WHERE fc.complaint_date >= '2026-01-01'
      AND fc.complaint_date < '2026-02-01'
      AND dc.channel_name = 'Mobile Banking'
    GROUP BY 1, 2
),

focus_scorecard AS (
    SELECT
        ts.product_id,
        ts.product_name,
        ts.customer_segment,
        ts.distinct_customer_count,
        ts.total_transaction_count,
        ts.failed_transaction_count,
        ts.reversed_transaction_count,
        ts.failed_transaction_count
            + ts.reversed_transaction_count
            AS affected_transaction_count,
        ts.total_transaction_amount,
        ts.failed_transaction_amount,
        ts.reversed_transaction_amount,
        ts.failed_transaction_amount
            + ts.reversed_transaction_amount
            AS affected_transaction_amount,
        COALESCE(cs.total_complaint_count, 0)
            AS total_complaint_count,
        COALESCE(cs.resolved_complaint_count, 0)
            AS resolved_complaint_count,
        cs.average_resolution_days,
        COALESCE(ss.total_sla_ticket_count, 0)
            AS total_sla_ticket_count,
        COALESCE(ss.sla_breached_ticket_count, 0)
            AS sla_breached_ticket_count,
        COALESCE(cs.complaint_resolution_rate_pct, 0)
            AS complaint_resolution_rate_pct,
        COALESCE(ss.sla_breach_rate_pct, 0)
            AS sla_breach_rate_pct
    FROM transaction_summary ts
    LEFT JOIN complaint_summary cs
        ON ts.product_id = cs.product_id
       AND ts.customer_segment = cs.customer_segment
    LEFT JOIN sla_summary ss
        ON ts.product_id = ss.product_id
       AND ts.customer_segment = ss.customer_segment
)

SELECT
    product_name,
    customer_segment,
    distinct_customer_count,
    total_transaction_count,
    ROUND(
        100.0 * total_transaction_count
        /
        NULLIF(SUM(total_transaction_count) OVER (), 0),
        2
    ) AS share_of_mobile_banking_volume_pct,
    failed_transaction_count,
    reversed_transaction_count,
    affected_transaction_count,
    ROUND(
        100.0 * failed_transaction_count
        /
        NULLIF(SUM(failed_transaction_count) OVER (), 0),
        2
    ) AS share_of_mobile_banking_failures_pct,
    total_transaction_amount,
    failed_transaction_amount,
    reversed_transaction_amount,
    affected_transaction_amount,
    total_complaint_count,
    ROUND(
        1000.0 * total_complaint_count
        /
        NULLIF(total_transaction_count, 0),
        2
    ) AS complaints_per_1000_transactions,
    resolved_complaint_count,
    complaint_resolution_rate_pct,
    average_resolution_days,
    total_sla_ticket_count,
    sla_breached_ticket_count,
    sla_breach_rate_pct
FROM focus_scorecard
ORDER BY
    affected_transaction_count DESC,
    affected_transaction_amount DESC,
    total_complaint_count DESC,
    total_transaction_count DESC;