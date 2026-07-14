-- Business KPI Queries
-- Purpose:
-- Use the warehouse star schema to answer business questions
-- for analytics, interviews, and Power BI dashboard planning.

-- ============================================================
-- 1. Executive KPI Summary
-- Business Question:
-- What are the overall banking operations KPIs?
-- ============================================================

SELECT
    COUNT(DISTINCT ft.transaction_id) AS total_transactions,
    ROUND(SUM(ft.amount)::numeric, 2) AS total_transaction_amount,
    ROUND(SUM(ft.fee_amount)::numeric, 2) AS total_fee_amount,
    SUM(ft.successful_transaction_count) AS successful_transactions,
    SUM(ft.failed_transaction_count) AS failed_transactions,
    ROUND(
        100.0 * SUM(ft.successful_transaction_count) / NULLIF(SUM(ft.transaction_count), 0),
        2
    ) AS transaction_success_rate_pct,
    COUNT(DISTINCT ft.customer_id) AS active_transaction_customers
FROM warehouse.fact_transactions ft;


-- ============================================================
-- 2. Transaction Volume and Value by Channel
-- Business Question:
-- Which channels drive the highest transaction activity?
-- ============================================================

SELECT
    dch.channel_name,
    dch.channel_category,
    dch.is_digital,
    COUNT(ft.transaction_id) AS transaction_count,
    ROUND(SUM(ft.amount)::numeric, 2) AS total_transaction_amount,
    ROUND(AVG(ft.amount)::numeric, 2) AS avg_transaction_amount,
    SUM(ft.successful_transaction_count) AS successful_transactions,
    SUM(ft.failed_transaction_count) AS failed_transactions,
    ROUND(
        100.0 * SUM(ft.successful_transaction_count) / NULLIF(SUM(ft.transaction_count), 0),
        2
    ) AS success_rate_pct
FROM warehouse.fact_transactions ft
LEFT JOIN warehouse.dim_channel dch
    ON ft.channel_key = dch.channel_key
GROUP BY
    dch.channel_name,
    dch.channel_category,
    dch.is_digital
ORDER BY
    total_transaction_amount DESC;


-- ============================================================
-- 3. Transaction Performance by Product
-- Business Question:
-- Which banking products generate the most transaction value?
-- ============================================================

SELECT
    dp.product_name,
    dp.product_category,
    dp.product_type,
    COUNT(ft.transaction_id) AS transaction_count,
    ROUND(SUM(ft.amount)::numeric, 2) AS total_transaction_amount,
    ROUND(AVG(ft.amount)::numeric, 2) AS avg_transaction_amount,
    ROUND(SUM(ft.fee_amount)::numeric, 2) AS total_fee_amount,
    ROUND(
        100.0 * SUM(ft.successful_transaction_count) / NULLIF(SUM(ft.transaction_count), 0),
        2
    ) AS success_rate_pct
FROM warehouse.fact_transactions ft
LEFT JOIN warehouse.dim_product dp
    ON ft.product_key = dp.product_key
GROUP BY
    dp.product_name,
    dp.product_category,
    dp.product_type
ORDER BY
    total_transaction_amount DESC;


-- ============================================================
-- 4. Transaction Trend by Date
-- Business Question:
-- How does transaction activity trend over time?
-- ============================================================

SELECT
    dd.full_date,
    dd.day_name,
    dd.is_weekend,
    COUNT(ft.transaction_id) AS transaction_count,
    ROUND(SUM(ft.amount)::numeric, 2) AS total_transaction_amount,
    SUM(ft.successful_transaction_count) AS successful_transactions,
    SUM(ft.failed_transaction_count) AS failed_transactions,
    ROUND(
        100.0 * SUM(ft.successful_transaction_count) / NULLIF(SUM(ft.transaction_count), 0),
        2
    ) AS success_rate_pct
FROM warehouse.fact_transactions ft
LEFT JOIN warehouse.dim_date dd
    ON ft.transaction_date_key = dd.date_key
GROUP BY
    dd.full_date,
    dd.day_name,
    dd.is_weekend
ORDER BY
    dd.full_date;


-- ============================================================
-- 5. Customer Segment Transaction Analysis
-- Business Question:
-- Which customer segments are most active and valuable?
-- ============================================================

SELECT
    dc.customer_segment,
    dc.risk_band,
    COUNT(DISTINCT ft.customer_id) AS active_customers,
    COUNT(ft.transaction_id) AS transaction_count,
    ROUND(SUM(ft.amount)::numeric, 2) AS total_transaction_amount,
    ROUND(AVG(ft.amount)::numeric, 2) AS avg_transaction_amount,
    ROUND(
        COUNT(ft.transaction_id)::numeric / NULLIF(COUNT(DISTINCT ft.customer_id), 0),
        2
    ) AS avg_transactions_per_customer
FROM warehouse.fact_transactions ft
LEFT JOIN warehouse.dim_customer dc
    ON ft.customer_key = dc.customer_key
GROUP BY
    dc.customer_segment,
    dc.risk_band
ORDER BY
    total_transaction_amount DESC;


-- ============================================================
-- 6. Branch Performance
-- Business Question:
-- Which branches drive the most transaction value?
-- ============================================================

SELECT
    db.region,
    db.state,
    db.city,
    db.branch_name,
    COUNT(ft.transaction_id) AS transaction_count,
    ROUND(SUM(ft.amount)::numeric, 2) AS total_transaction_amount,
    ROUND(AVG(ft.amount)::numeric, 2) AS avg_transaction_amount,
    SUM(ft.failed_transaction_count) AS failed_transactions,
    ROUND(
        100.0 * SUM(ft.successful_transaction_count) / NULLIF(SUM(ft.transaction_count), 0),
        2
    ) AS success_rate_pct
FROM warehouse.fact_transactions ft
LEFT JOIN warehouse.dim_branch db
    ON ft.branch_key = db.branch_key
GROUP BY
    db.region,
    db.state,
    db.city,
    db.branch_name
ORDER BY
    total_transaction_amount DESC;


-- ============================================================
-- 7. Complaint Summary
-- Business Question:
-- What is the overall complaint volume and resolution performance?
-- ============================================================

SELECT
    COUNT(fc.complaint_id) AS total_complaints,
    SUM(fc.resolved_complaint_count) AS resolved_complaints,
    SUM(fc.open_complaint_count) AS open_complaints,
    ROUND(
        100.0 * SUM(fc.resolved_complaint_count) / NULLIF(SUM(fc.complaint_count), 0),
        2
    ) AS complaint_resolution_rate_pct,
    ROUND(AVG(fc.resolution_days)::numeric, 2) AS avg_resolution_days
FROM warehouse.fact_complaints fc;


-- ============================================================
-- 8. Complaints by Category and Priority
-- Business Question:
-- What are the major customer pain points?
-- ============================================================

SELECT
    fc.complaint_category,
    fc.complaint_priority,
    COUNT(fc.complaint_id) AS complaint_count,
    SUM(fc.resolved_complaint_count) AS resolved_complaints,
    SUM(fc.open_complaint_count) AS open_complaints,
    ROUND(AVG(fc.resolution_days)::numeric, 2) AS avg_resolution_days,
    ROUND(
        100.0 * SUM(fc.resolved_complaint_count) / NULLIF(SUM(fc.complaint_count), 0),
        2
    ) AS resolution_rate_pct
FROM warehouse.fact_complaints fc
GROUP BY
    fc.complaint_category,
    fc.complaint_priority
ORDER BY
    complaint_count DESC,
    fc.complaint_priority;


-- ============================================================
-- 9. Complaints by Channel
-- Business Question:
-- Which customer touchpoints generate the most complaints?
-- ============================================================

SELECT
    dch.channel_name,
    dch.channel_category,
    dch.is_digital,
    COUNT(fc.complaint_id) AS complaint_count,
    SUM(fc.resolved_complaint_count) AS resolved_complaints,
    SUM(fc.open_complaint_count) AS open_complaints,
    ROUND(AVG(fc.resolution_days)::numeric, 2) AS avg_resolution_days
FROM warehouse.fact_complaints fc
LEFT JOIN warehouse.dim_channel dch
    ON fc.channel_key = dch.channel_key
GROUP BY
    dch.channel_name,
    dch.channel_category,
    dch.is_digital
ORDER BY
    complaint_count DESC;


-- ============================================================
-- 10. SLA Performance Summary
-- Business Question:
-- Are service teams meeting SLA expectations?
-- ============================================================

SELECT
    COUNT(fst.ticket_id) AS total_tickets,
    SUM(fst.resolved_ticket_count) AS resolved_tickets,
    SUM(fst.sla_met_count) AS sla_met_tickets,
    SUM(fst.sla_breached_count) AS sla_breached_tickets,
    ROUND(
        100.0 * SUM(fst.sla_met_count) / NULLIF(SUM(fst.ticket_count), 0),
        2
    ) AS sla_met_rate_pct,
    ROUND(
        100.0 * SUM(fst.sla_breached_count) / NULLIF(SUM(fst.ticket_count), 0),
        2
    ) AS sla_breach_rate_pct
FROM warehouse.fact_sla_tickets fst;


-- ============================================================
-- 11. SLA Performance by Assigned Team
-- Business Question:
-- Which teams have higher SLA breaches?
-- ============================================================

SELECT
    fst.assigned_team,
    fst.ticket_priority,
    COUNT(fst.ticket_id) AS ticket_count,
    SUM(fst.sla_met_count) AS sla_met_tickets,
    SUM(fst.sla_breached_count) AS sla_breached_tickets,
    ROUND(
        100.0 * SUM(fst.sla_met_count) / NULLIF(SUM(fst.ticket_count), 0),
        2
    ) AS sla_met_rate_pct,
    ROUND(
        100.0 * SUM(fst.sla_breached_count) / NULLIF(SUM(fst.ticket_count), 0),
        2
    ) AS sla_breach_rate_pct
FROM warehouse.fact_sla_tickets fst
GROUP BY
    fst.assigned_team,
    fst.ticket_priority
ORDER BY
    sla_breach_rate_pct DESC,
    ticket_count DESC;


-- ============================================================
-- 12. Campaign Performance Summary
-- Business Question:
-- How effective are marketing campaigns?
-- ============================================================

SELECT
    COUNT(fc.campaign_id) AS campaign_offers_sent,
    SUM(fc.engaged_count) AS engaged_customers,
    SUM(fc.converted_count) AS converted_customers,
    ROUND(
        100.0 * SUM(fc.engaged_count) / NULLIF(SUM(fc.campaign_sent_count), 0),
        2
    ) AS engagement_rate_pct,
    ROUND(
        100.0 * SUM(fc.converted_count) / NULLIF(SUM(fc.campaign_sent_count), 0),
        2
    ) AS conversion_rate_pct
FROM warehouse.fact_campaigns fc;


-- ============================================================
-- 13. Campaign Performance by Campaign Type
-- Business Question:
-- Which campaign types convert better?
-- ============================================================

SELECT
    fc.campaign_type,
    fc.campaign_name,
    COUNT(fc.campaign_id) AS campaign_offers_sent,
    SUM(fc.engaged_count) AS engaged_customers,
    SUM(fc.converted_count) AS converted_customers,
    ROUND(
        100.0 * SUM(fc.engaged_count) / NULLIF(SUM(fc.campaign_sent_count), 0),
        2
    ) AS engagement_rate_pct,
    ROUND(
        100.0 * SUM(fc.converted_count) / NULLIF(SUM(fc.campaign_sent_count), 0),
        2
    ) AS conversion_rate_pct
FROM warehouse.fact_campaigns fc
GROUP BY
    fc.campaign_type,
    fc.campaign_name
ORDER BY
    conversion_rate_pct DESC,
    campaign_offers_sent DESC;


-- ============================================================
-- 14. Campaign Conversion by Customer Segment
-- Business Question:
-- Which customer segments respond better to campaigns?
-- ============================================================

SELECT
    dc.customer_segment,
    dc.risk_band,
    COUNT(fc.campaign_id) AS campaign_offers_sent,
    SUM(fc.engaged_count) AS engaged_customers,
    SUM(fc.converted_count) AS converted_customers,
    ROUND(
        100.0 * SUM(fc.converted_count) / NULLIF(SUM(fc.campaign_sent_count), 0),
        2
    ) AS conversion_rate_pct
FROM warehouse.fact_campaigns fc
LEFT JOIN warehouse.dim_customer dc
    ON fc.customer_key = dc.customer_key
GROUP BY
    dc.customer_segment,
    dc.risk_band
ORDER BY
    conversion_rate_pct DESC,
    campaign_offers_sent DESC;


-- ============================================================
-- 15. Product Complaint Rate
-- Business Question:
-- Which products have higher complaint volume compared to transaction activity?
-- ============================================================

WITH product_transactions AS (
    SELECT
        product_key,
        COUNT(transaction_id) AS transaction_count
    FROM warehouse.fact_transactions
    GROUP BY product_key
),

product_complaints AS (
    SELECT
        product_key,
        COUNT(complaint_id) AS complaint_count
    FROM warehouse.fact_complaints
    GROUP BY product_key
)

SELECT
    dp.product_name,
    dp.product_category,
    COALESCE(pt.transaction_count, 0) AS transaction_count,
    COALESCE(pc.complaint_count, 0) AS complaint_count,
    ROUND(
        1000.0 * COALESCE(pc.complaint_count, 0) / NULLIF(pt.transaction_count, 0),
        2
    ) AS complaints_per_1000_transactions
FROM warehouse.dim_product dp
LEFT JOIN product_transactions pt
    ON dp.product_key = pt.product_key
LEFT JOIN product_complaints pc
    ON dp.product_key = pc.product_key
ORDER BY
    complaints_per_1000_transactions DESC NULLS LAST;


-- ============================================================
-- 16. Customer 360 View
-- Business Question:
-- Which customers have high activity, complaints, and campaign engagement?
-- ============================================================

WITH transaction_summary AS (
    SELECT
        customer_key,
        COUNT(transaction_id) AS transaction_count,
        ROUND(SUM(amount)::numeric, 2) AS total_transaction_amount,
        SUM(failed_transaction_count) AS failed_transaction_count
    FROM warehouse.fact_transactions
    GROUP BY customer_key
),

complaint_summary AS (
    SELECT
        customer_key,
        COUNT(complaint_id) AS complaint_count,
        SUM(open_complaint_count) AS open_complaint_count
    FROM warehouse.fact_complaints
    GROUP BY customer_key
),

campaign_summary AS (
    SELECT
        customer_key,
        COUNT(campaign_id) AS campaign_offer_count,
        SUM(converted_count) AS converted_campaign_count
    FROM warehouse.fact_campaigns
    GROUP BY customer_key
)

SELECT
    dc.customer_id,
    dc.customer_name,
    dc.customer_segment,
    dc.risk_band,
    COALESCE(ts.transaction_count, 0) AS transaction_count,
    COALESCE(ts.total_transaction_amount, 0) AS total_transaction_amount,
    COALESCE(ts.failed_transaction_count, 0) AS failed_transaction_count,
    COALESCE(cs.complaint_count, 0) AS complaint_count,
    COALESCE(cs.open_complaint_count, 0) AS open_complaint_count,
    COALESCE(camps.campaign_offer_count, 0) AS campaign_offer_count,
    COALESCE(camps.converted_campaign_count, 0) AS converted_campaign_count
FROM warehouse.dim_customer dc
LEFT JOIN transaction_summary ts
    ON dc.customer_key = ts.customer_key
LEFT JOIN complaint_summary cs
    ON dc.customer_key = cs.customer_key
LEFT JOIN campaign_summary camps
    ON dc.customer_key = camps.customer_key
ORDER BY
    total_transaction_amount DESC
LIMIT 50;


-- ============================================================
-- 17. Power BI Transaction Reporting Base Query
-- Business Question:
-- What is the transaction-level dataset for Power BI?
-- ============================================================

SELECT
    ft.transaction_id,
    ft.transaction_datetime,
    ft.transaction_date,
    ft.transaction_month,
    ft.transaction_type,
    ft.transaction_status,
    ft.amount,
    ft.fee_amount,
    ft.currency,
    ft.successful_transaction_count,
    ft.failed_transaction_count,
    ft.transaction_count,

    dc.customer_segment,
    dc.risk_band,
    dc.city AS customer_city,
    dc.state AS customer_state,

    da.account_status,
    da.current_balance,

    dp.product_name,
    dp.product_category,
    dp.product_type,

    db.branch_name,
    db.region AS branch_region,
    db.state AS branch_state,

    dch.channel_name,
    dch.channel_category,
    dch.is_digital

FROM warehouse.fact_transactions ft
LEFT JOIN warehouse.dim_customer dc
    ON ft.customer_key = dc.customer_key
LEFT JOIN warehouse.dim_account da
    ON ft.account_key = da.account_key
LEFT JOIN warehouse.dim_product dp
    ON ft.product_key = dp.product_key
LEFT JOIN warehouse.dim_branch db
    ON ft.branch_key = db.branch_key
LEFT JOIN warehouse.dim_channel dch
    ON ft.channel_key = dch.channel_key
LIMIT 100;