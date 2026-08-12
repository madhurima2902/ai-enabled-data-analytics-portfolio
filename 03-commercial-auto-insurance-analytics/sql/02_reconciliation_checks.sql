-- Commercial Auto Insurance Analytics
-- Data-quality and cross-table reconciliation checks
-- PostgreSQL-compatible. Each query returns the records requiring investigation.

-- DQ01: Duplicate quote IDs
-- Expected exception rows: 180
WITH ranked_quotes AS (
    SELECT q.*,
           ROW_NUMBER() OVER (PARTITION BY quote_id ORDER BY quote_date, ctid) AS duplicate_rank
    FROM quotes q
)
SELECT *
FROM ranked_quotes
WHERE duplicate_rank > 1;

-- DQ02: Policies missing their quote key
-- Expected: 140
SELECT *
FROM policies
WHERE quote_id IS NULL;

-- DQ03: Vehicles referencing a policy that does not exist
-- Expected: 190
SELECT v.*
FROM vehicles v
LEFT JOIN policies p ON v.policy_id = p.policy_id
WHERE p.policy_id IS NULL;

-- DQ04: Positive premium record does not reconcile to policy written premium
-- Non-positive premiums are handled separately in DQ08 to prevent double counting.
-- Expected: 175
SELECT
    pr.premium_id,
    pr.policy_id,
    p.written_premium AS policy_written_premium,
    pr.written_premium AS premium_written_premium,
    ROUND((pr.written_premium - p.written_premium)::numeric, 2) AS variance
FROM premiums pr
JOIN policies p ON pr.policy_id = p.policy_id
WHERE pr.written_premium > 0
  AND ABS(pr.written_premium - p.written_premium) > 0.01;

-- DQ05: Claims referencing a policy that does not exist
-- Expected: 135
SELECT c.*
FROM claims c
LEFT JOIN policies p ON c.policy_id = p.policy_id
WHERE p.policy_id IS NULL;

-- DQ06: Policy expiration occurs before effective date
-- Expected: 120
SELECT *
FROM policies
WHERE expiration_date < effective_date;

-- DQ07: Claim date falls outside a valid policy term
-- Invalid policy terms from DQ06 are excluded to avoid overlapping exceptions.
-- Expected: 110
SELECT
    c.claim_id,
    c.policy_id,
    c.claim_date,
    p.effective_date,
    p.expiration_date
FROM claims c
JOIN policies p ON c.policy_id = p.policy_id
WHERE p.expiration_date >= p.effective_date
  AND (c.claim_date < p.effective_date OR c.claim_date > p.expiration_date);

-- DQ08: Non-positive written premium
-- Expected: 80
SELECT *
FROM premiums
WHERE written_premium <= 0;

-- DQ09: Vehicle model year outside the accepted business-rule range
-- Portfolio rule for this synthetic recreation: 1980 through 2026.
-- Expected: 70
SELECT *
FROM vehicles
WHERE model_year < 1980 OR model_year > 2026;

-- Final reconciliation summary.
-- Expected total: 1,200 exception instances.
WITH
q_rank AS (
    SELECT quote_id,
           ROW_NUMBER() OVER (PARTITION BY quote_id ORDER BY quote_date, ctid) AS rn
    FROM quotes
),
dq01 AS (SELECT COUNT(*) AS n FROM q_rank WHERE rn > 1),
dq02 AS (SELECT COUNT(*) AS n FROM policies WHERE quote_id IS NULL),
dq03 AS (
    SELECT COUNT(*) AS n FROM vehicles v
    LEFT JOIN policies p ON v.policy_id = p.policy_id
    WHERE p.policy_id IS NULL
),
dq04 AS (
    SELECT COUNT(*) AS n FROM premiums pr
    JOIN policies p ON pr.policy_id = p.policy_id
    WHERE pr.written_premium > 0
      AND ABS(pr.written_premium - p.written_premium) > 0.01
),
dq05 AS (
    SELECT COUNT(*) AS n FROM claims c
    LEFT JOIN policies p ON c.policy_id = p.policy_id
    WHERE p.policy_id IS NULL
),
dq06 AS (SELECT COUNT(*) AS n FROM policies WHERE expiration_date < effective_date),
dq07 AS (
    SELECT COUNT(*) AS n FROM claims c
    JOIN policies p ON c.policy_id = p.policy_id
    WHERE p.expiration_date >= p.effective_date
      AND (c.claim_date < p.effective_date OR c.claim_date > p.expiration_date)
),
dq08 AS (SELECT COUNT(*) AS n FROM premiums WHERE written_premium <= 0),
dq09 AS (SELECT COUNT(*) AS n FROM vehicles WHERE model_year < 1980 OR model_year > 2026),
summary AS (
    SELECT 'DUPLICATE_QUOTE_ID' AS exception_type, (SELECT n FROM dq01) AS exception_count
    UNION ALL SELECT 'MISSING_POLICY_QUOTE_KEY', (SELECT n FROM dq02)
    UNION ALL SELECT 'ORPHAN_VEHICLE_POLICY', (SELECT n FROM dq03)
    UNION ALL SELECT 'PREMIUM_RECON_MISMATCH', (SELECT n FROM dq04)
    UNION ALL SELECT 'ORPHAN_CLAIM_POLICY', (SELECT n FROM dq05)
    UNION ALL SELECT 'INVALID_POLICY_DATE_RANGE', (SELECT n FROM dq06)
    UNION ALL SELECT 'CLAIM_OUTSIDE_POLICY_TERM', (SELECT n FROM dq07)
    UNION ALL SELECT 'NONPOSITIVE_WRITTEN_PREMIUM', (SELECT n FROM dq08)
    UNION ALL SELECT 'INVALID_VEHICLE_MODEL_YEAR', (SELECT n FROM dq09)
)
SELECT exception_type, exception_count
FROM summary
UNION ALL
SELECT 'TOTAL', SUM(exception_count)
FROM summary;
