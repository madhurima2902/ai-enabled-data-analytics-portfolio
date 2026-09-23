/*
PROJECT WALKTHROUGH — BUSINESS KPI QUERIES

How I explain this file:
After the data-quality checks and reporting model are in place, I use SQL
to answer operational questions.

The purpose of these queries is not simply to demonstrate SQL syntax.
Each query supports a business decision or a deeper investigation.

The sequence moves from:
overall health
→ where a problem is concentrated
→ customer impact
→ internal service/process performance.

If a KPI looks unusual, I would break it down further by time period,
channel, branch, transaction type, complaint category, or support team.
*/

-- ============================================================
-- 1. EXECUTIVE TRANSACTION KPIs
-- Business question:
-- What is the overall volume, value, success count, failure count,
-- and transaction success rate?
--
-- NULLIF prevents division by zero if no transactions are present.
-- ============================================================
SELECT
    COUNT(DISTINCT transaction_id) AS total_transactions,
    ROUND(SUM(amount)::numeric, 2) AS total_transaction_amount,
    SUM(successful_transaction_count) AS successful_transactions,
    SUM(failed_transaction_count) AS failed_transactions,
    ROUND(
        100.0 * SUM(successful_transaction_count)
        / NULLIF(SUM(transaction_count), 0),
        2
    ) AS transaction_success_rate_pct
FROM warehouse.fact_transactions;


-- ============================================================
-- 2. TRANSACTION PERFORMANCE BY CHANNEL
-- Business question:
-- Is an overall failure-rate problem concentrated in one channel?
--
-- I group by channel and calculate failed transactions as a percentage
-- of total transactions. The result gives operations a more focused
-- starting point than the bank-wide average alone.
-- ============================================================
SELECT
    c.channel_name,
    c.is_digital,
    COUNT(t.transaction_id) AS transaction_count,
    SUM(t.failed_transaction_count) AS failed_transactions,
    ROUND(
        100.0 * SUM(t.failed_transaction_count)
        / NULLIF(SUM(t.transaction_count), 0),
        2
    ) AS failure_rate_pct,
    ROUND(SUM(t.amount)::numeric, 2) AS total_transaction_amount
FROM warehouse.fact_transactions t
LEFT JOIN warehouse.dim_channel c
    ON t.channel_key = c.channel_key
GROUP BY
    c.channel_name,
    c.is_digital
ORDER BY failure_rate_pct DESC;


-- ============================================================
-- 3. COMPLAINT SUMMARY
-- Business question:
-- How many complaints were received, what percentage were resolved,
-- and how long did resolution take on average?
--
-- This gives a customer-impact view alongside transaction performance.
-- ============================================================
SELECT
    COUNT(complaint_id) AS total_complaints,
    SUM(resolved_complaint_count) AS resolved_complaints,
    ROUND(
        100.0 * SUM(resolved_complaint_count)
        / NULLIF(SUM(complaint_count), 0),
        2
    ) AS resolution_rate_pct,
    ROUND(AVG(resolution_days)::numeric, 2) AS avg_resolution_days
FROM warehouse.fact_complaints;


-- ============================================================
-- 4. COMPLAINT PAIN POINTS
-- Business question:
-- Which complaint categories and priorities are creating the most
-- customer pain, and which groups take longer to resolve?
--
-- This helps move from total complaint count to a more actionable view.
-- ============================================================
SELECT
    complaint_category,
    complaint_priority,
    COUNT(complaint_id) AS complaint_count,
    ROUND(AVG(resolution_days)::numeric, 2) AS avg_resolution_days
FROM warehouse.fact_complaints
GROUP BY
    complaint_category,
    complaint_priority
ORDER BY complaint_count DESC;


-- ============================================================
-- 5. SLA PERFORMANCE BY SUPPORT TEAM
-- Business question:
-- Which teams and priority levels have the highest SLA breach rates?
--
-- I would use this result as the starting point for a process
-- investigation: capacity, prioritization, handoffs, queue management,
-- or opportunities for automation.
-- ============================================================
SELECT
    assigned_team,
    ticket_priority,
    COUNT(ticket_id) AS ticket_count,
    SUM(sla_met_count) AS sla_met_tickets,
    SUM(sla_breached_count) AS sla_breached_tickets,
    ROUND(
        100.0 * SUM(sla_breached_count)
        / NULLIF(SUM(ticket_count), 0),
        2
    ) AS sla_breach_rate_pct
FROM warehouse.fact_sla_tickets
GROUP BY
    assigned_team,
    ticket_priority
ORDER BY
    sla_breach_rate_pct DESC,
    ticket_count DESC;
