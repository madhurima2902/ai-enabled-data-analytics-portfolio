-- Commercial Auto Insurance Analytics
-- Business KPI analysis examples

-- 1. Quote-to-bind conversion
SELECT
    COUNT(*) AS total_quotes,
    COUNT(*) FILTER (WHERE quote_status = 'Bound') AS bound_quotes,
    ROUND(100.0 * COUNT(*) FILTER (WHERE quote_status = 'Bound') / NULLIF(COUNT(*),0), 2) AS conversion_rate_pct
FROM quotes;

-- 2. Written premium (policy system is treated as source of truth for portfolio KPI)
SELECT ROUND(SUM(written_premium)::numeric,2) AS total_written_premium
FROM policies;

-- 3. Claim frequency: claims per 100 policies
-- Orphan claims are excluded because they cannot be attributed to a valid policy.
SELECT
    COUNT(DISTINCT c.claim_id) AS valid_claims,
    COUNT(DISTINCT p.policy_id) AS policies,
    ROUND(100.0 * COUNT(DISTINCT c.claim_id) / NULLIF(COUNT(DISTINCT p.policy_id),0), 2) AS claims_per_100_policies
FROM policies p
LEFT JOIN claims c ON p.policy_id = c.policy_id;

-- 4. Claim severity: average paid loss for valid claims
SELECT ROUND(AVG(c.paid_loss)::numeric,2) AS avg_claim_severity
FROM claims c
JOIN policies p ON c.policy_id = p.policy_id;

-- 5. Loss ratio using paid loss / written premium for a simple portfolio view
SELECT
    ROUND(SUM(c.paid_loss)::numeric,2) AS paid_loss,
    ROUND(SUM(DISTINCT p.written_premium)::numeric,2) AS written_premium_note,
    ROUND(100.0 * SUM(c.paid_loss) /
          NULLIF((SELECT SUM(written_premium) FROM policies),0),2) AS paid_loss_ratio_pct
FROM claims c
JOIN policies p ON c.policy_id = p.policy_id;

-- 6. Monthly quote and conversion trend
SELECT
    DATE_TRUNC('month', quote_date)::date AS quote_month,
    COUNT(*) AS quotes,
    COUNT(*) FILTER (WHERE quote_status='Bound') AS bound_quotes,
    ROUND(100.0 * COUNT(*) FILTER (WHERE quote_status='Bound') / NULLIF(COUNT(*),0),2) AS conversion_rate_pct
FROM quotes
GROUP BY 1
ORDER BY 1;

-- 7. Performance by state
SELECT
    state,
    COUNT(*) AS quotes,
    COUNT(*) FILTER (WHERE quote_status='Bound') AS bound_quotes,
    ROUND(100.0 * COUNT(*) FILTER (WHERE quote_status='Bound') / NULLIF(COUNT(*),0),2) AS conversion_rate_pct,
    ROUND(AVG(quoted_premium)::numeric,2) AS avg_quoted_premium
FROM quotes
GROUP BY state
ORDER BY quotes DESC;

-- 8. Claim performance by claim type
SELECT
    c.claim_type,
    COUNT(*) AS claim_count,
    ROUND(SUM(c.paid_loss)::numeric,2) AS paid_loss,
    ROUND(AVG(c.paid_loss)::numeric,2) AS avg_severity
FROM claims c
JOIN policies p ON c.policy_id=p.policy_id
GROUP BY c.claim_type
ORDER BY paid_loss DESC;

-- Retention normally requires renewal linkage between expiring and renewed policy terms.
-- It is intentionally not fabricated from policy_status alone. Add a renewal/previous-policy
-- relationship before calculating a defensible retention KPI.
