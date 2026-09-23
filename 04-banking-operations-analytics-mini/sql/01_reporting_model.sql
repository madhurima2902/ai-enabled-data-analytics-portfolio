/*
PROJECT WALKTHROUGH — REPORTING MODEL

How I explain this file:
This file creates the reporting-oriented data model that sits between the cleaned staging data and Power BI.

I separate business events from descriptive attributes. Transactions, complaints, and SLA tickets are the event or fact tables. Customer, account, branch, channel, and date are dimensions used to analyze those events.

The most important concept is grain:
- fact_transactions = one row per transaction
- fact_complaints = one row per complaint
- fact_sla_tickets = one row per service ticket

I generate reporting keys for the dimensions and keep the original business IDs for traceability.

Why this matters:
If a dimension key is not unique or a join multiplies fact rows, the dashboard can produce believable but incorrect KPIs. The model therefore works together with the validation checks in 02_data_quality_checks.sql.
*/

CREATE SCHEMA IF NOT EXISTS warehouse;

-- ============================================================
-- DIMENSIONS
-- These tables describe the people, accounts, locations,
-- channels, and dates associated with business events.
-- ============================================================

DROP TABLE IF EXISTS warehouse.dim_account;
DROP TABLE IF EXISTS warehouse.dim_customer;
DROP TABLE IF EXISTS warehouse.dim_branch;
DROP TABLE IF EXISTS warehouse.dim_channel;
DROP TABLE IF EXISTS warehouse.dim_date;

-- Customer dimension:
-- One row per customer. ROW_NUMBER creates a reporting key while
-- customer_id remains available as the original business identifier.
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


-- Branch dimension:
-- One row per branch, including geographic and branch-type attributes.
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


-- Channel dimension:
-- One row per transaction/service channel. The is_digital flag
-- supports digital versus non-digital reporting.
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


-- Account dimension:
-- One row per account. LEFT JOINs retain the account even if a
-- related customer or branch lookup fails, making unresolved keys visible.
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


-- Date dimension:
-- Provides reusable calendar attributes for trend and period analysis.
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
-- These tables store the business events that are measured.
-- ============================================================

DROP TABLE IF EXISTS warehouse.fact_sla_tickets;
DROP TABLE IF EXISTS warehouse.fact_complaints;
DROP TABLE IF EXISTS warehouse.fact_transactions;

-- Transaction fact
-- Grain: one row per transaction.
-- The dimension keys make it possible to analyze transactions by
-- customer, account, branch, channel, and date.
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


-- Complaint fact
-- Grain: one row per complaint.
-- This supports complaint volume, resolution rate, and resolution-time analysis.
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


-- SLA ticket fact
-- Grain: one row per service ticket.
-- The 0/1 flags make SLA-met and SLA-breached counts easy to aggregate.
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
