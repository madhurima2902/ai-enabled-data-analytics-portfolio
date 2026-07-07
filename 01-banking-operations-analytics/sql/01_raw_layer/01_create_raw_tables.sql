-- Database: banking_analytics_db
-- Schema: raw

CREATE SCHEMA IF NOT EXISTS raw;

DROP TABLE IF EXISTS raw.transactions;
DROP TABLE IF EXISTS raw.sla_tickets;
DROP TABLE IF EXISTS raw.campaigns;
DROP TABLE IF EXISTS raw.complaints;
DROP TABLE IF EXISTS raw.accounts;
DROP TABLE IF EXISTS raw.customers;
DROP TABLE IF EXISTS raw.products;
DROP TABLE IF EXISTS raw.branches;
DROP TABLE IF EXISTS raw.channels;

CREATE TABLE raw.customers (
    customer_id TEXT,
    customer_name TEXT,
    gender TEXT,
    date_of_birth DATE,
    age_group TEXT,
    city TEXT,
    state TEXT,
    customer_segment TEXT,
    onboarding_date DATE,
    kyc_status TEXT,
    risk_band TEXT
);

CREATE TABLE raw.accounts (
    account_id TEXT,
    customer_id TEXT,
    product_id TEXT,
    branch_id TEXT,
    account_open_date DATE,
    account_status TEXT,
    current_balance NUMERIC(18,2),
    interest_rate NUMERIC(5,2),
    credit_limit NUMERIC(18,2)
);

CREATE TABLE raw.products (
    product_id TEXT,
    product_name TEXT,
    product_category TEXT,
    product_type TEXT,
    is_active BOOLEAN
);

CREATE TABLE raw.branches (
    branch_id TEXT,
    branch_name TEXT,
    city TEXT,
    state TEXT,
    region TEXT,
    branch_type TEXT
);

CREATE TABLE raw.channels (
    channel_id TEXT,
    channel_name TEXT,
    channel_category TEXT,
    is_digital BOOLEAN
);

CREATE TABLE raw.complaints (
    complaint_id TEXT,
    customer_id TEXT,
    account_id TEXT,
    product_id TEXT,
    channel_id TEXT,
    complaint_date DATE,
    complaint_category TEXT,
    complaint_priority TEXT,
    complaint_status TEXT,
    resolution_date DATE,
    resolution_days NUMERIC(6,1)
);

CREATE TABLE raw.campaigns (
    campaign_id TEXT,
    customer_id TEXT,
    campaign_name TEXT,
    campaign_type TEXT,
    offer_product_id TEXT,
    campaign_channel_id TEXT,
    sent_date DATE,
    response_status TEXT,
    response_date DATE,
    converted_flag BOOLEAN
);

CREATE TABLE raw.sla_tickets (
    ticket_id TEXT,
    complaint_id TEXT,
    customer_id TEXT,
    account_id TEXT,
    created_datetime TIMESTAMP,
    due_datetime TIMESTAMP,
    resolved_datetime TIMESTAMP,
    ticket_priority TEXT,
    sla_target_hours INTEGER,
    ticket_status TEXT,
    sla_met_flag BOOLEAN,
    assigned_team TEXT
);

CREATE TABLE raw.transactions (
    transaction_id TEXT,
    account_id TEXT,
    customer_id TEXT,
    product_id TEXT,
    branch_id TEXT,
    channel_id TEXT,
    transaction_datetime TIMESTAMP,
    transaction_type TEXT,
    transaction_status TEXT,
    amount NUMERIC(18,2),
    fee_amount NUMERIC(18,2),
    currency TEXT,
    balance_after_transaction NUMERIC(18,2)
);