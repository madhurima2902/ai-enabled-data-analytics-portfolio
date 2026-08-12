-- Commercial Auto Insurance Analytics
-- PostgreSQL setup and CSV import script
--
-- Portfolio note:
-- The table structure and analytical workflow reflect the original work pattern,
-- but the data loaded by this script is fully synthetic and contains no client data.
--
-- Expected generated files under ../data/
--   quotes.csv
--   policies.csv
--   vehicles.csv
--   premiums.csv
--   claims.csv
--
-- Recommended execution order:
--   1. Run scripts/generate_synthetic_data.py
--   2. Create a PostgreSQL database, e.g. commercial_auto_analytics
--   3. Connect to that database in psql or pgAdmin
--   4. Run this file
--   5. Run 01_data_profiling.sql
--   6. Run 02_reconciliation_checks.sql
--   7. Run 03_kpi_analysis.sql

BEGIN;

DROP TABLE IF EXISTS claims;
DROP TABLE IF EXISTS premiums;
DROP TABLE IF EXISTS vehicles;
DROP TABLE IF EXISTS policies;
DROP TABLE IF EXISTS quotes;

CREATE TABLE quotes (
    quote_id          VARCHAR(20),
    quote_date        DATE,
    state             VARCHAR(2),
    channel           VARCHAR(20),
    segment           VARCHAR(40),
    quoted_premium    NUMERIC(12,2),
    quote_status      VARCHAR(20)
);

CREATE TABLE policies (
    policy_id         VARCHAR(20),
    quote_id          VARCHAR(20),
    effective_date    DATE,
    expiration_date   DATE,
    written_premium   NUMERIC(12,2),
    policy_status     VARCHAR(20)
);

CREATE TABLE vehicles (
    vehicle_id        VARCHAR(20),
    policy_id         VARCHAR(20),
    make              VARCHAR(30),
    vehicle_type      VARCHAR(30),
    model_year        INTEGER
);

CREATE TABLE premiums (
    premium_id        VARCHAR(20),
    policy_id         VARCHAR(20),
    written_premium   NUMERIC(12,2),
    earned_premium    NUMERIC(12,2),
    billing_plan      VARCHAR(20)
);

CREATE TABLE claims (
    claim_id          VARCHAR(20),
    policy_id         VARCHAR(20),
    claim_date        DATE,
    claim_status      VARCHAR(20),
    paid_loss         NUMERIC(14,2),
    case_reserve      NUMERIC(14,2),
    claim_type        VARCHAR(30)
);

COMMIT;

-- ============================================================================
-- CSV LOAD
-- ============================================================================
-- Option A: psql \copy commands
-- Replace the relative paths if your working directory differs.
--
-- \copy quotes    FROM '../data/quotes.csv'    WITH (FORMAT csv, HEADER true);
-- \copy policies  FROM '../data/policies.csv'  WITH (FORMAT csv, HEADER true);
-- \copy vehicles  FROM '../data/vehicles.csv'  WITH (FORMAT csv, HEADER true);
-- \copy premiums  FROM '../data/premiums.csv'  WITH (FORMAT csv, HEADER true);
-- \copy claims    FROM '../data/claims.csv'    WITH (FORMAT csv, HEADER true);
--
-- Option B: pgAdmin Import/Export Data
-- Import each CSV into its matching table using:
--   Format: CSV
--   Header: Yes
--   Delimiter: comma
--   Encoding: UTF-8
--
-- IMPORTANT:
-- Foreign-key constraints are intentionally NOT created before loading.
-- The project contains deliberately seeded orphan/missing-key exceptions, and
-- strict FK constraints would reject the very records the reconciliation work
-- is intended to detect.

-- ============================================================================
-- POST-LOAD INDEXES
-- ============================================================================
-- Run these after importing the CSV files.

CREATE INDEX IF NOT EXISTS idx_quotes_quote_id
    ON quotes (quote_id);

CREATE INDEX IF NOT EXISTS idx_quotes_quote_date
    ON quotes (quote_date);

CREATE INDEX IF NOT EXISTS idx_quotes_status
    ON quotes (quote_status);

CREATE INDEX IF NOT EXISTS idx_policies_policy_id
    ON policies (policy_id);

CREATE INDEX IF NOT EXISTS idx_policies_quote_id
    ON policies (quote_id);

CREATE INDEX IF NOT EXISTS idx_policies_dates
    ON policies (effective_date, expiration_date);

CREATE INDEX IF NOT EXISTS idx_vehicles_vehicle_id
    ON vehicles (vehicle_id);

CREATE INDEX IF NOT EXISTS idx_vehicles_policy_id
    ON vehicles (policy_id);

CREATE INDEX IF NOT EXISTS idx_premiums_premium_id
    ON premiums (premium_id);

CREATE INDEX IF NOT EXISTS idx_premiums_policy_id
    ON premiums (policy_id);

CREATE INDEX IF NOT EXISTS idx_claims_claim_id
    ON claims (claim_id);

CREATE INDEX IF NOT EXISTS idx_claims_policy_id
    ON claims (policy_id);

CREATE INDEX IF NOT EXISTS idx_claims_claim_date
    ON claims (claim_date);

ANALYZE quotes;
ANALYZE policies;
ANALYZE vehicles;
ANALYZE premiums;
ANALYZE claims;

-- ============================================================================
-- POST-LOAD SANITY CHECKS
-- ============================================================================
-- Expected target volumes:
-- quotes   ~80,000
-- policies ~32,000
-- vehicles ~40,000
-- premiums ~32,000
-- claims   ~6,500

SELECT 'quotes' AS table_name, COUNT(*) AS row_count FROM quotes
UNION ALL
SELECT 'policies', COUNT(*) FROM policies
UNION ALL
SELECT 'vehicles', COUNT(*) FROM vehicles
UNION ALL
SELECT 'premiums', COUNT(*) FROM premiums
UNION ALL
SELECT 'claims', COUNT(*) FROM claims
ORDER BY table_name;

-- Expected quote-date coverage: 2024-01-01 through 2025-12-31
SELECT
    MIN(quote_date) AS min_quote_date,
    MAX(quote_date) AS max_quote_date,
    COUNT(DISTINCT DATE_TRUNC('month', quote_date)) AS months_present
FROM quotes;

-- Expected months_present = 24.
