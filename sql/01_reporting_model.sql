-- Mini reporting model
-- Assumes cleaned staging tables already exist.
-- Scope intentionally limited to transactions, complaints, and SLA reporting.

CREATE SCHEMA IF NOT EXISTS warehouse;

-- ============================================================
-- DIMENSIONS
-- ============================================================

DROP TABLE IF EXISTS warehouse.dim_account;
DROP TABLE IF EXISTS warehouse.dim_customer;
DROP TABLE IF EXISTS warehouse.dim_branch;
DROP TABLE IF EXISTS warehouse.dim_channel;
DROP TABLE IF EXISTS warehouse.dim_date;

CREATE TABLE warehouse.dim_customer AS
SELECT
    ROW_NUMBER() OVER (ORDER BY customer_id) AS customer_key,
    customer_id,
    customer_name,
    city,
    state,
    customer_segment,
    kyc_status,
    risk_band
FROM staging.stg_customers;

ALTER TABLE warehouse.dim_customer
ADD CONSTRAINT pk_dim_customer PRIMARY KEY (customer_key);

ALTER TABLE warehouse.dim_customer
ADD CONSTRAINT uq_dim_customer_id UNIQUE (customer_id);


CREATE TABLE warehouse.dim_branch AS
SELECT
    ROW_NUMBER() OVER (ORDER BY branch_id) AS branch_key,
    branch_id,
    branch_name,
    city,
    state,
    region,
    branch_type
FROM staging.stg_branches;

ALTER TABLE warehouse.dim_branch
ADD CONSTRAINT pk_dim_branch PRIMARY KEY (branch_key);

ALTER TABLE warehouse.dim_branch
ADD CONSTRAINT uq_dim_branch_id UNIQUE (branch_id);


CREATE TABLE warehouse.dim_channel AS
SELECT
    ROW_NUMBER() OVER (ORDER BY channel_id) AS channel_key,
    channel_id,
    channel_name,
    channel_category,
    is_digital
FROM staging.stg_channels;

ALTER TABLE warehouse.dim_channel
ADD CONSTRAINT pk_dim_channel PRIMARY KEY (channel_key);

ALTER TABLE warehouse.dim_channel
ADD CONSTRAINT uq_dim_channel_id UNIQUE (channel_id);


CREATE TABLE warehouse.dim_account AS
SELECT
    ROW_NUMBER() OVER (ORDER BY a.account_id) AS account_key,
    a.account_id,
    a.customer_id,
    c.customer_key,
    a.branch_id,
    b.branch_key,
    a.account_open_date,
    a.account_status,
    a.current_balance
FROM staging.stg_accounts a
LEFT JOIN warehouse.dim_customer c
    ON a.customer_id = c.customer_id
LEFT JOIN warehouse.dim_branch b
    ON a.branch_id = b.branch_id;

ALTER TABLE warehouse.dim_account
ADD CONSTRAINT pk_dim_account PRIMARY KEY (account_key);

ALTER TABLE warehouse.dim_account
ADD CONSTRAINT uq_dim_account_id UNIQUE (account_id);


CREATE TABLE warehouse.dim_date AS
SELECT
    TO_CHAR(calendar_date, 'YYYYMMDD')::INT AS date_key,
    calendar_date::DATE AS full_date,
    EXTRACT(MONTH FROM calendar_date)::INT AS month_number,
    TO_CHAR(calendar_date, 'Mon') AS month_name,
    EXTRACT(QUARTER FROM calendar_date)::INT AS quarter_number,
    EXTRACT(YEAR FROM calendar_date)::INT AS year_number,
    CASE
        WHEN EXTRACT(DOW FROM calendar_date) IN (0, 6) THEN TRUE
        ELSE FALSE
    END AS is_weekend
FROM GENERATE_SERIES(
    DATE '2026-01-01',
    DATE '2026-12-31',
    INTERVAL '1 day'
) AS calendar_date;

ALTER TABLE warehouse.dim_date
ADD CONSTRAINT pk_dim_date PRIMARY KEY (date_key);


-- ============================================================
-- FACTS
-- ============================================================

DROP TABLE IF EXISTS warehouse.fact_sla_tickets;
DROP TABLE IF EXISTS warehouse.fact_complaints;
DROP TABLE IF EXISTS warehouse.fact_transactions;

-- Grain: one row per transaction
CREATE TABLE warehouse.fact_transactions AS
SELECT
    ROW_NUMBER() OVER (ORDER BY t.transaction_id) AS transaction_key,
    t.transaction_id,
    da.account_key,
    dc.customer_key,
    db.branch_key,
    dch.channel_key,
    dd.date_key AS transaction_date_key,
    t.account_id,
    t.customer_id,
    t.branch_id,
    t.channel_id,
    t.transaction_datetime,
    t.transaction_status,
    t.transaction_type,
    t.amount,
    t.fee_amount,
    CASE WHEN t.transaction_status = 'Success' THEN 1 ELSE 0 END
        AS successful_transaction_count,
    CASE WHEN t.transaction_status = 'Failed' THEN 1 ELSE 0 END
        AS failed_transaction_count,
    1 AS transaction_count
FROM staging.stg_transactions t
LEFT JOIN warehouse.dim_account da
    ON t.account_id = da.account_id
LEFT JOIN warehouse.dim_customer dc
    ON t.customer_id = dc.customer_id
LEFT JOIN warehouse.dim_branch db
    ON t.branch_id = db.branch_id
LEFT JOIN warehouse.dim_channel dch
    ON t.channel_id = dch.channel_id
LEFT JOIN warehouse.dim_date dd
    ON t.transaction_datetime::DATE = dd.full_date;


-- Grain: one row per complaint
CREATE TABLE warehouse.fact_complaints AS
SELECT
    ROW_NUMBER() OVER (ORDER BY c.complaint_id) AS complaint_key,
    c.complaint_id,
    dc.customer_key,
    da.account_key,
    dch.channel_key,
    dd.date_key AS complaint_date_key,
    c.customer_id,
    c.account_id,
    c.channel_id,
    c.complaint_date,
    c.complaint_category,
    c.complaint_priority,
    c.complaint_status,
    c.resolution_date,
    c.resolution_days,
    CASE WHEN c.is_resolved = TRUE THEN 1 ELSE 0 END
        AS resolved_complaint_count,
    1 AS complaint_count
FROM staging.stg_complaints c
LEFT JOIN warehouse.dim_customer dc
    ON c.customer_id = dc.customer_id
LEFT JOIN warehouse.dim_account da
    ON c.account_id = da.account_id
LEFT JOIN warehouse.dim_channel dch
    ON c.channel_id = dch.channel_id
LEFT JOIN warehouse.dim_date dd
    ON c.complaint_date = dd.full_date;


-- Grain: one row per SLA/service ticket
CREATE TABLE warehouse.fact_sla_tickets AS
SELECT
    ROW_NUMBER() OVER (ORDER BY s.ticket_id) AS sla_ticket_key,
    s.ticket_id,
    s.complaint_id,
    dc.customer_key,
    dd.date_key AS created_date_key,
    s.customer_id,
    s.created_datetime,
    s.due_datetime,
    s.resolved_datetime,
    s.assigned_team,
    s.ticket_priority,
    s.ticket_status,
    CASE WHEN s.sla_met_flag = TRUE THEN 1 ELSE 0 END AS sla_met_count,
    CASE WHEN s.sla_met_flag = FALSE THEN 1 ELSE 0 END AS sla_breached_count,
    1 AS ticket_count
FROM staging.stg_sla_tickets s
LEFT JOIN warehouse.dim_customer dc
    ON s.customer_id = dc.customer_id
LEFT JOIN warehouse.dim_date dd
    ON s.created_datetime::DATE = dd.full_date;
