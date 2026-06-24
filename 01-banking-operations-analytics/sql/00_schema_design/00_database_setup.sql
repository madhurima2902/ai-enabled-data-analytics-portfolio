-- Banking Operations Analytics
-- Database and schema setup
-- Database name: banking_analytics_db

CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS warehouse;
CREATE SCHEMA IF NOT EXISTS dq;
CREATE SCHEMA IF NOT EXISTS analytics;

-- Validation query
SELECT schema_name
FROM information_schema.schemata
WHERE schema_name IN ('raw', 'staging', 'warehouse', 'dq', 'analytics')
ORDER BY schema_name;
