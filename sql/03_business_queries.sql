-- Business-facing SQL examples

-- 1. Executive transaction KPIs
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


-- 2. Transaction performance by channel
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


-- 3. Complaint summary
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


-- 4. Complaint pain points
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


-- 5. SLA performance by support team
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
