-- Create warehouse fact tables
-- Purpose:Build reporting-ready fact tables from staging tables and warehouse dimensions.

CREATE SCHEMA IF NOT EXISTS warehouse;

DROP TABLE IF EXISTS warehouse.fact_sla_tickets;
DROP TABLE IF EXISTS warehouse.fact_campaigns;
DROP TABLE IF EXISTS warehouse.fact_complaints;
DROP TABLE IF EXISTS warehouse.fact_transactions;


-- ============================================================
-- 1. Transaction Fact
-- Grain: One row per transaction
-- ============================================================

CREATE TABLE warehouse.fact_transactions AS
SELECT
    ROW_NUMBER() OVER (ORDER BY t.transaction_id) AS transaction_key,
    t.transaction_id,

    da.account_key,
    dc.customer_key,
    dp.product_key,
    db.branch_key,
    dch.channel_key,
    dd.date_key AS transaction_date_key,

    t.account_id,
    t.customer_id,
    t.product_id,
    t.branch_id,
    t.channel_id,

    t.transaction_datetime,
    t.transaction_date,
    t.transaction_month,
    t.transaction_type,
    t.transaction_status,
    t.amount,
    t.fee_amount,
    t.currency,
    t.balance_after_transaction,
    t.is_successful_transaction,

    CASE
        WHEN t.transaction_status = 'Success' THEN 1
        ELSE 0
    END AS successful_transaction_count,

    CASE
        WHEN t.transaction_status = 'Failed' THEN 1
        ELSE 0
    END AS failed_transaction_count,

    1 AS transaction_count,
    CURRENT_TIMESTAMP AS warehouse_loaded_at

FROM staging.stg_transactions t
LEFT JOIN warehouse.dim_account da
    ON t.account_id = da.account_id
LEFT JOIN warehouse.dim_customer dc
    ON t.customer_id = dc.customer_id
LEFT JOIN warehouse.dim_product dp
    ON t.product_id = dp.product_id
LEFT JOIN warehouse.dim_branch db
    ON t.branch_id = db.branch_id
LEFT JOIN warehouse.dim_channel dch
    ON t.channel_id = dch.channel_id
LEFT JOIN warehouse.dim_date dd
    ON t.transaction_date = dd.full_date;


-- ============================================================
-- 2. Complaint Fact
-- Grain: One row per complaint
-- ============================================================

CREATE TABLE warehouse.fact_complaints AS
SELECT
    ROW_NUMBER() OVER (ORDER BY c.complaint_id) AS complaint_key,
    c.complaint_id,

    dc.customer_key,
    da.account_key,
    dp.product_key,
    dch.channel_key,
    dd.date_key AS complaint_date_key,

    c.customer_id,
    c.account_id,
    c.product_id,
    c.channel_id,

    c.complaint_date,
    c.complaint_category,
    c.complaint_priority,
    c.complaint_status,
    c.resolution_date,
    c.resolution_days,
    c.is_resolved,

    CASE
        WHEN c.is_resolved = TRUE THEN 1
        ELSE 0
    END AS resolved_complaint_count,

    CASE
        WHEN c.is_resolved = FALSE THEN 1
        ELSE 0
    END AS open_complaint_count,

    1 AS complaint_count,
    CURRENT_TIMESTAMP AS warehouse_loaded_at

FROM staging.stg_complaints c
LEFT JOIN warehouse.dim_customer dc
    ON c.customer_id = dc.customer_id
LEFT JOIN warehouse.dim_account da
    ON c.account_id = da.account_id
LEFT JOIN warehouse.dim_product dp
    ON c.product_id = dp.product_id
LEFT JOIN warehouse.dim_channel dch
    ON c.channel_id = dch.channel_id
LEFT JOIN warehouse.dim_date dd
    ON c.complaint_date = dd.full_date;


-- ============================================================
-- 3. Campaign Fact
-- Grain: One row per campaign/customer offer
-- ============================================================

CREATE TABLE warehouse.fact_campaigns AS
SELECT
    ROW_NUMBER() OVER (ORDER BY camp.campaign_id) AS campaign_key,
    camp.campaign_id,

    dc.customer_key,
    dp.product_key AS offer_product_key,
    dch.channel_key AS campaign_channel_key,
    dd.date_key AS sent_date_key,

    camp.customer_id,
    camp.offer_product_id,
    camp.campaign_channel_id,

    camp.campaign_name,
    camp.campaign_type,
    camp.sent_date,
    camp.response_status,
    camp.response_date,
    camp.converted_flag,
    camp.converted_count,

    CASE
        WHEN camp.response_status IN ('Opened', 'Clicked', 'Converted') THEN 1
        ELSE 0
    END AS engaged_count,

    1 AS campaign_sent_count,
    CURRENT_TIMESTAMP AS warehouse_loaded_at

FROM staging.stg_campaigns camp
LEFT JOIN warehouse.dim_customer dc
    ON camp.customer_id = dc.customer_id
LEFT JOIN warehouse.dim_product dp
    ON camp.offer_product_id = dp.product_id
LEFT JOIN warehouse.dim_channel dch
    ON camp.campaign_channel_id = dch.channel_id
LEFT JOIN warehouse.dim_date dd
    ON camp.sent_date = dd.full_date;


-- ============================================================
-- 4. SLA Ticket Fact
-- Grain: One row per SLA ticket
-- ============================================================

CREATE TABLE warehouse.fact_sla_tickets AS
SELECT
    ROW_NUMBER() OVER (ORDER BY s.ticket_id) AS sla_ticket_key,
    s.ticket_id,
    s.complaint_id,

    dc.customer_key,
    da.account_key,
    created_dt.date_key AS created_date_key,
    due_dt.date_key AS due_date_key,
    resolved_dt.date_key AS resolved_date_key,

    s.customer_id,
    s.account_id,

    s.created_datetime,
    s.due_datetime,
    s.resolved_datetime,
    s.ticket_priority,
    s.sla_target_hours,
    s.ticket_status,
    s.sla_met_flag,
    s.assigned_team,
    s.is_ticket_resolved,

    CASE
        WHEN s.is_ticket_resolved = TRUE THEN 1
        ELSE 0
    END AS resolved_ticket_count,

    CASE
        WHEN s.sla_met_flag = TRUE THEN 1
        ELSE 0
    END AS sla_met_count,

    CASE
        WHEN s.sla_met_flag = FALSE THEN 1
        ELSE 0
    END AS sla_breached_count,

    1 AS ticket_count,
    CURRENT_TIMESTAMP AS warehouse_loaded_at

FROM staging.stg_sla_tickets s
LEFT JOIN warehouse.dim_customer dc
    ON s.customer_id = dc.customer_id
LEFT JOIN warehouse.dim_account da
    ON s.account_id = da.account_id
LEFT JOIN warehouse.dim_date created_dt
    ON s.created_datetime::DATE = created_dt.full_date
LEFT JOIN warehouse.dim_date due_dt
    ON s.due_datetime::DATE = due_dt.full_date
LEFT JOIN warehouse.dim_date resolved_dt
    ON s.resolved_datetime::DATE = resolved_dt.full_date;


-- ============================================================
-- 5. Add primary keys
-- ============================================================

ALTER TABLE warehouse.fact_transactions
ADD CONSTRAINT pk_fact_transactions PRIMARY KEY (transaction_key);

ALTER TABLE warehouse.fact_complaints
ADD CONSTRAINT pk_fact_complaints PRIMARY KEY (complaint_key);

ALTER TABLE warehouse.fact_campaigns
ADD CONSTRAINT pk_fact_campaigns PRIMARY KEY (campaign_key);

ALTER TABLE warehouse.fact_sla_tickets
ADD CONSTRAINT pk_fact_sla_tickets PRIMARY KEY (sla_ticket_key);


-- ============================================================
-- 6. Add unique constraints on source business IDs
-- ============================================================

ALTER TABLE warehouse.fact_transactions
ADD CONSTRAINT uq_fact_transactions_transaction_id UNIQUE (transaction_id);

ALTER TABLE warehouse.fact_complaints
ADD CONSTRAINT uq_fact_complaints_complaint_id UNIQUE (complaint_id);

ALTER TABLE warehouse.fact_campaigns
ADD CONSTRAINT uq_fact_campaigns_campaign_id UNIQUE (campaign_id);

ALTER TABLE warehouse.fact_sla_tickets
ADD CONSTRAINT uq_fact_sla_tickets_ticket_id UNIQUE (ticket_id);