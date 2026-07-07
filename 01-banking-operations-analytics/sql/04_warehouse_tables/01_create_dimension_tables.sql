-- Create warehouse dimension tables
-- Purpose: Build reporting-ready dimension tables from staging tables.

CREATE SCHEMA IF NOT EXISTS warehouse;

DROP TABLE IF EXISTS warehouse.dim_date;
DROP TABLE IF EXISTS warehouse.dim_account;
DROP TABLE IF EXISTS warehouse.dim_customer;
DROP TABLE IF EXISTS warehouse.dim_product;
DROP TABLE IF EXISTS warehouse.dim_branch;
DROP TABLE IF EXISTS warehouse.dim_channel;


-- ============================================================
-- 1. Customer Dimension
-- ============================================================

CREATE TABLE warehouse.dim_customer AS
SELECT
    ROW_NUMBER() OVER (ORDER BY customer_id) AS customer_key,
    customer_id,
    customer_name,
    gender,
    date_of_birth,
    EXTRACT(YEAR FROM AGE(DATE '2026-06-24', date_of_birth))::INT AS customer_age,
    age_group,
    city,
    state,
    customer_segment,
    onboarding_date,
    kyc_status,
    risk_band,
    staging_loaded_at,
    CURRENT_TIMESTAMP AS warehouse_loaded_at
FROM staging.stg_customers;


-- ============================================================
-- 2. Product Dimension
-- ============================================================

CREATE TABLE warehouse.dim_product AS
SELECT
    ROW_NUMBER() OVER (ORDER BY product_id) AS product_key,
    product_id,
    product_name,
    product_category,
    product_type,
    is_active,
    staging_loaded_at,
    CURRENT_TIMESTAMP AS warehouse_loaded_at
FROM staging.stg_products;


-- ============================================================
-- 3. Branch Dimension
-- ============================================================

CREATE TABLE warehouse.dim_branch AS
SELECT
    ROW_NUMBER() OVER (ORDER BY branch_id) AS branch_key,
    branch_id,
    branch_name,
    city,
    state,
    region,
    branch_type,
    staging_loaded_at,
    CURRENT_TIMESTAMP AS warehouse_loaded_at
FROM staging.stg_branches;


-- ============================================================
-- 4. Channel Dimension
-- ============================================================

CREATE TABLE warehouse.dim_channel AS
SELECT
    ROW_NUMBER() OVER (ORDER BY channel_id) AS channel_key,
    channel_id,
    channel_name,
    channel_category,
    is_digital,
    staging_loaded_at,
    CURRENT_TIMESTAMP AS warehouse_loaded_at
FROM staging.stg_channels;


-- ============================================================
-- 5. Account Dimension
-- ============================================================

CREATE TABLE warehouse.dim_account AS
SELECT
    ROW_NUMBER() OVER (ORDER BY a.account_id) AS account_key,
    a.account_id,
    a.customer_id,
    c.customer_key,
    a.product_id,
    p.product_key,
    a.branch_id,
    b.branch_key,
    a.account_open_date,
    a.account_status,
    a.current_balance,
    a.interest_rate,
    a.credit_limit,
    a.staging_loaded_at,
    CURRENT_TIMESTAMP AS warehouse_loaded_at
FROM staging.stg_accounts a
LEFT JOIN warehouse.dim_customer c
    ON a.customer_id = c.customer_id
LEFT JOIN warehouse.dim_product p
    ON a.product_id = p.product_id
LEFT JOIN warehouse.dim_branch b
    ON a.branch_id = b.branch_id;


-- ============================================================
-- 6. Date Dimension
-- ============================================================

CREATE TABLE warehouse.dim_date AS
SELECT
    TO_CHAR(calendar_date, 'YYYYMMDD')::INT AS date_key,
    calendar_date::DATE AS full_date,
    EXTRACT(DAY FROM calendar_date)::INT AS day_of_month,
    EXTRACT(MONTH FROM calendar_date)::INT AS month_number,
    TO_CHAR(calendar_date, 'Month') AS month_name,
    EXTRACT(QUARTER FROM calendar_date)::INT AS quarter_number,
    EXTRACT(YEAR FROM calendar_date)::INT AS year_number,
    EXTRACT(DOW FROM calendar_date)::INT AS day_of_week_number,
    TO_CHAR(calendar_date, 'Day') AS day_name,
    CASE
        WHEN EXTRACT(DOW FROM calendar_date) IN (0, 6) THEN TRUE
        ELSE FALSE
    END AS is_weekend,
    CURRENT_TIMESTAMP AS warehouse_loaded_at
FROM GENERATE_SERIES(
    DATE '2018-01-01',
    DATE '2026-12-31',
    INTERVAL '1 day'
) AS calendar_date;


-- ============================================================
-- 7. Add primary keys
-- ============================================================

ALTER TABLE warehouse.dim_customer
ADD CONSTRAINT pk_dim_customer PRIMARY KEY (customer_key);

ALTER TABLE warehouse.dim_product
ADD CONSTRAINT pk_dim_product PRIMARY KEY (product_key);

ALTER TABLE warehouse.dim_branch
ADD CONSTRAINT pk_dim_branch PRIMARY KEY (branch_key);

ALTER TABLE warehouse.dim_channel
ADD CONSTRAINT pk_dim_channel PRIMARY KEY (channel_key);

ALTER TABLE warehouse.dim_account
ADD CONSTRAINT pk_dim_account PRIMARY KEY (account_key);

ALTER TABLE warehouse.dim_date
ADD CONSTRAINT pk_dim_date PRIMARY KEY (date_key);


-- ============================================================
-- 8. Add unique constraints on natural business IDs
-- ============================================================

ALTER TABLE warehouse.dim_customer
ADD CONSTRAINT uq_dim_customer_customer_id UNIQUE (customer_id);

ALTER TABLE warehouse.dim_product
ADD CONSTRAINT uq_dim_product_product_id UNIQUE (product_id);

ALTER TABLE warehouse.dim_branch
ADD CONSTRAINT uq_dim_branch_branch_id UNIQUE (branch_id);

ALTER TABLE warehouse.dim_channel
ADD CONSTRAINT uq_dim_channel_channel_id UNIQUE (channel_id);

ALTER TABLE warehouse.dim_account
ADD CONSTRAINT uq_dim_account_account_id UNIQUE (account_id);