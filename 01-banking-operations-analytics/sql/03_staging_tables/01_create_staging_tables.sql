--Create staging tables from raw layer
-- Purpose:
-- Standardize raw data before warehouse fact/dimension modeling.

CREATE SCHEMA IF NOT EXISTS staging;

DROP TABLE IF EXISTS staging.stg_transactions;
DROP TABLE IF EXISTS staging.stg_sla_tickets;
DROP TABLE IF EXISTS staging.stg_campaigns;
DROP TABLE IF EXISTS staging.stg_complaints;
DROP TABLE IF EXISTS staging.stg_accounts;
DROP TABLE IF EXISTS staging.stg_customers;
DROP TABLE IF EXISTS staging.stg_products;
DROP TABLE IF EXISTS staging.stg_branches;
DROP TABLE IF EXISTS staging.stg_channels;


-- ============================================================
-- 1. Customers
-- ============================================================

CREATE TABLE staging.stg_customers AS
SELECT
    UPPER(NULLIF(TRIM(customer_id), '')) AS customer_id,
    NULLIF(TRIM(customer_name), '') AS customer_name,
    NULLIF(TRIM(gender), '') AS gender,
    date_of_birth,
    NULLIF(TRIM(age_group), '') AS age_group,
    NULLIF(TRIM(city), '') AS city,
    NULLIF(TRIM(state), '') AS state,
    NULLIF(TRIM(customer_segment), '') AS customer_segment,
    onboarding_date,
    NULLIF(TRIM(kyc_status), '') AS kyc_status,
    NULLIF(TRIM(risk_band), '') AS risk_band,
    CURRENT_TIMESTAMP AS staging_loaded_at
FROM raw.customers;


-- ============================================================
-- 2. Accounts
-- ============================================================

CREATE TABLE staging.stg_accounts AS
SELECT
    UPPER(NULLIF(TRIM(account_id), '')) AS account_id,
    UPPER(NULLIF(TRIM(customer_id), '')) AS customer_id,
    UPPER(NULLIF(TRIM(product_id), '')) AS product_id,
    UPPER(NULLIF(TRIM(branch_id), '')) AS branch_id,
    account_open_date,
    NULLIF(TRIM(account_status), '') AS account_status,
    current_balance,
    interest_rate,
    credit_limit,
    CURRENT_TIMESTAMP AS staging_loaded_at
FROM raw.accounts;


-- ============================================================
-- 3. Products
-- ============================================================

CREATE TABLE staging.stg_products AS
SELECT
    UPPER(NULLIF(TRIM(product_id), '')) AS product_id,
    NULLIF(TRIM(product_name), '') AS product_name,
    NULLIF(TRIM(product_category), '') AS product_category,
    NULLIF(TRIM(product_type), '') AS product_type,
    is_active,
    CURRENT_TIMESTAMP AS staging_loaded_at
FROM raw.products;


-- ============================================================
-- 4. Branches
-- ============================================================

CREATE TABLE staging.stg_branches AS
SELECT
    UPPER(NULLIF(TRIM(branch_id), '')) AS branch_id,
    NULLIF(TRIM(branch_name), '') AS branch_name,
    NULLIF(TRIM(city), '') AS city,
    NULLIF(TRIM(state), '') AS state,
    NULLIF(TRIM(region), '') AS region,
    NULLIF(TRIM(branch_type), '') AS branch_type,
    CURRENT_TIMESTAMP AS staging_loaded_at
FROM raw.branches;


-- ============================================================
-- 5. Channels
-- ============================================================

CREATE TABLE staging.stg_channels AS
SELECT
    UPPER(NULLIF(TRIM(channel_id), '')) AS channel_id,
    NULLIF(TRIM(channel_name), '') AS channel_name,
    NULLIF(TRIM(channel_category), '') AS channel_category,
    is_digital,
    CURRENT_TIMESTAMP AS staging_loaded_at
FROM raw.channels;


-- ============================================================
-- 6. Complaints
-- ============================================================

CREATE TABLE staging.stg_complaints AS
SELECT
    UPPER(NULLIF(TRIM(complaint_id), '')) AS complaint_id,
    UPPER(NULLIF(TRIM(customer_id), '')) AS customer_id,
    UPPER(NULLIF(TRIM(account_id), '')) AS account_id,
    UPPER(NULLIF(TRIM(product_id), '')) AS product_id,
    UPPER(NULLIF(TRIM(channel_id), '')) AS channel_id,
    complaint_date,
    NULLIF(TRIM(complaint_category), '') AS complaint_category,
    NULLIF(TRIM(complaint_priority), '') AS complaint_priority,
    NULLIF(TRIM(complaint_status), '') AS complaint_status,
    resolution_date,
    resolution_days,
    CASE
        WHEN NULLIF(TRIM(complaint_status), '') IN ('Resolved', 'Closed') THEN TRUE
        ELSE FALSE
    END AS is_resolved,
    CURRENT_TIMESTAMP AS staging_loaded_at
FROM raw.complaints;


-- ============================================================
-- 7. Campaigns
-- ============================================================

CREATE TABLE staging.stg_campaigns AS
SELECT
    UPPER(NULLIF(TRIM(campaign_id), '')) AS campaign_id,
    UPPER(NULLIF(TRIM(customer_id), '')) AS customer_id,
    NULLIF(TRIM(campaign_name), '') AS campaign_name,
    NULLIF(TRIM(campaign_type), '') AS campaign_type,
    UPPER(NULLIF(TRIM(offer_product_id), '')) AS offer_product_id,
    UPPER(NULLIF(TRIM(campaign_channel_id), '')) AS campaign_channel_id,
    sent_date,
    NULLIF(TRIM(response_status), '') AS response_status,
    response_date,
    converted_flag,
    CASE
        WHEN converted_flag = TRUE THEN 1
        ELSE 0
    END AS converted_count,
    CURRENT_TIMESTAMP AS staging_loaded_at
FROM raw.campaigns;


-- ============================================================
-- 8. SLA Tickets
-- ============================================================

CREATE TABLE staging.stg_sla_tickets AS
SELECT
    UPPER(NULLIF(TRIM(ticket_id), '')) AS ticket_id,
    UPPER(NULLIF(TRIM(complaint_id), '')) AS complaint_id,
    UPPER(NULLIF(TRIM(customer_id), '')) AS customer_id,
    UPPER(NULLIF(TRIM(account_id), '')) AS account_id,
    created_datetime,
    due_datetime,
    resolved_datetime,
    NULLIF(TRIM(ticket_priority), '') AS ticket_priority,
    sla_target_hours,
    NULLIF(TRIM(ticket_status), '') AS ticket_status,
    sla_met_flag,
    NULLIF(TRIM(assigned_team), '') AS assigned_team,
    CASE
        WHEN resolved_datetime IS NOT NULL THEN TRUE
        ELSE FALSE
    END AS is_ticket_resolved,
    CURRENT_TIMESTAMP AS staging_loaded_at
FROM raw.sla_tickets;


-- ============================================================
-- 9. Transactions
-- ============================================================

CREATE TABLE staging.stg_transactions AS
SELECT
    UPPER(NULLIF(TRIM(transaction_id), '')) AS transaction_id,
    UPPER(NULLIF(TRIM(account_id), '')) AS account_id,
    UPPER(NULLIF(TRIM(customer_id), '')) AS customer_id,
    UPPER(NULLIF(TRIM(product_id), '')) AS product_id,
    UPPER(NULLIF(TRIM(branch_id), '')) AS branch_id,
    UPPER(NULLIF(TRIM(channel_id), '')) AS channel_id,
    transaction_datetime,
    transaction_datetime::DATE AS transaction_date,
    DATE_TRUNC('month', transaction_datetime)::DATE AS transaction_month,
    NULLIF(TRIM(transaction_type), '') AS transaction_type,
    NULLIF(TRIM(transaction_status), '') AS transaction_status,
    amount,
    fee_amount,
    UPPER(NULLIF(TRIM(currency), '')) AS currency,
    balance_after_transaction,
    CASE
        WHEN NULLIF(TRIM(transaction_status), '') = 'Success' THEN TRUE
        ELSE FALSE
    END AS is_successful_transaction,
    CURRENT_TIMESTAMP AS staging_loaded_at
FROM raw.transactions;