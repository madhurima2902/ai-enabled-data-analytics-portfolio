-- Commercial Auto Insurance Analytics
-- Basic profiling checks (PostgreSQL-compatible)

-- 1. Row counts / portfolio scale
SELECT 'quotes' AS table_name, COUNT(*) AS row_count FROM quotes
UNION ALL SELECT 'policies', COUNT(*) FROM policies
UNION ALL SELECT 'vehicles', COUNT(*) FROM vehicles
UNION ALL SELECT 'premiums', COUNT(*) FROM premiums
UNION ALL SELECT 'claims', COUNT(*) FROM claims;

-- Expected synthetic volumes:
-- quotes 80,000 | policies 32,000 | vehicles 40,000 | premiums 32,000 | claims 6,500

-- 2. Date coverage
SELECT MIN(quote_date) AS first_quote_date,
       MAX(quote_date) AS last_quote_date
FROM quotes;

-- 3. Null profiling on important relationship keys
SELECT
    COUNT(*) AS policy_rows,
    COUNT(*) FILTER (WHERE quote_id IS NULL) AS missing_quote_id
FROM policies;

SELECT
    COUNT(*) AS vehicle_rows,
    COUNT(*) FILTER (WHERE policy_id IS NULL) AS missing_policy_id
FROM vehicles;

SELECT
    COUNT(*) AS claim_rows,
    COUNT(*) FILTER (WHERE policy_id IS NULL) AS missing_policy_id
FROM claims;

-- 4. Duplicate-key profiling
SELECT quote_id, COUNT(*) AS row_count
FROM quotes
GROUP BY quote_id
HAVING COUNT(*) > 1
ORDER BY row_count DESC, quote_id;

-- 5. Basic numeric profiling
SELECT
    MIN(quoted_premium) AS min_quoted_premium,
    AVG(quoted_premium) AS avg_quoted_premium,
    MAX(quoted_premium) AS max_quoted_premium
FROM quotes;

SELECT
    MIN(written_premium) AS min_written_premium,
    AVG(written_premium) AS avg_written_premium,
    MAX(written_premium) AS max_written_premium
FROM premiums;

SELECT
    MIN(paid_loss) AS min_paid_loss,
    AVG(paid_loss) AS avg_paid_loss,
    MAX(paid_loss) AS max_paid_loss
FROM claims;

-- 6. Distribution checks useful during investigation
SELECT quote_status, COUNT(*) AS quote_count
FROM quotes
GROUP BY quote_status
ORDER BY quote_count DESC;

SELECT state, COUNT(*) AS quote_count
FROM quotes
GROUP BY state
ORDER BY quote_count DESC;

SELECT claim_type, COUNT(*) AS claim_count
FROM claims
GROUP BY claim_type
ORDER BY claim_count DESC;
