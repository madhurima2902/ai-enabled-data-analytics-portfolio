-- Healthcare Claims & Provider Operations Analytics
-- Business analysis and data-quality checks.

-- ------------------------------------------------------------
-- 1. DATA QUALITY
-- ------------------------------------------------------------

-- Duplicate claim IDs
SELECT
    claim_id,
    COUNT(*) AS row_count
FROM fact_claims
GROUP BY claim_id
HAVING COUNT(*) > 1;

-- Orphan patient keys
SELECT COUNT(*) AS orphan_patient_rows
FROM fact_claims c
LEFT JOIN dim_patient p
    ON c.patient_id = p.patient_id
WHERE p.patient_id IS NULL;

-- Orphan provider keys
SELECT COUNT(*) AS orphan_provider_rows
FROM fact_claims c
LEFT JOIN dim_provider p
    ON c.provider_id = p.provider_id
WHERE p.provider_id IS NULL;

-- Invalid monetary values or processing duration
SELECT *
FROM fact_claims
WHERE submitted_amount < 0
   OR allowed_amount < 0
   OR paid_amount < 0
   OR processing_days < 0;

-- ------------------------------------------------------------
-- 2. CLEAN ANALYTICAL SUBSET
-- ------------------------------------------------------------

WITH deduped AS (
    SELECT
        c.*,
        ROW_NUMBER() OVER (
            PARTITION BY claim_id
            ORDER BY service_date, patient_id, provider_id
        ) AS rn
    FROM fact_claims c
),
clean_claims AS (
    SELECT d.*
    FROM deduped d
    INNER JOIN dim_patient pt
        ON d.patient_id = pt.patient_id
    INNER JOIN dim_provider pr
        ON d.provider_id = pr.provider_id
    WHERE d.rn = 1
      AND d.submitted_amount >= 0
      AND d.allowed_amount >= 0
      AND d.paid_amount >= 0
      AND d.processing_days >= 0
)
SELECT COUNT(*) AS clean_claim_rows
FROM clean_claims;

-- ------------------------------------------------------------
-- 3. CORE KPI SUMMARY
-- ------------------------------------------------------------

WITH deduped AS (
    SELECT
        c.*,
        ROW_NUMBER() OVER (PARTITION BY claim_id ORDER BY service_date) AS rn
    FROM fact_claims c
),
clean_claims AS (
    SELECT d.*
    FROM deduped d
    INNER JOIN dim_patient pt ON d.patient_id = pt.patient_id
    INNER JOIN dim_provider pr ON d.provider_id = pr.provider_id
    WHERE d.rn = 1
      AND d.submitted_amount >= 0
      AND d.allowed_amount >= 0
      AND d.paid_amount >= 0
      AND d.processing_days >= 0
)
SELECT
    COUNT(*) AS total_claims,
    ROUND(
        100.0 * SUM(CASE WHEN claim_status = 'Denied' THEN 1 ELSE 0 END) / COUNT(*),
        2
    ) AS denial_rate_pct,
    ROUND(AVG(processing_days), 2) AS avg_processing_days,
    ROUND(
        100.0 * SUM(CASE WHEN claim_status = 'Paid' THEN paid_amount ELSE 0 END)
        / NULLIF(SUM(CASE WHEN claim_status = 'Paid' THEN submitted_amount ELSE 0 END), 0),
        2
    ) AS paid_reimbursement_rate_pct
FROM clean_claims;

-- ------------------------------------------------------------
-- 4. PAYER PERFORMANCE
-- ------------------------------------------------------------

WITH clean_claims AS (
    SELECT DISTINCT ON (c.claim_id) c.*
    FROM fact_claims c
    INNER JOIN dim_patient pt ON c.patient_id = pt.patient_id
    INNER JOIN dim_provider pr ON c.provider_id = pr.provider_id
    WHERE c.submitted_amount >= 0
      AND c.allowed_amount >= 0
      AND c.paid_amount >= 0
      AND c.processing_days >= 0
    ORDER BY c.claim_id, c.service_date
)
SELECT
    payer_type,
    COUNT(*) AS claim_count,
    ROUND(SUM(submitted_amount), 2) AS submitted_amount,
    ROUND(SUM(paid_amount), 2) AS paid_amount,
    ROUND(
        100.0 * SUM(CASE WHEN claim_status = 'Denied' THEN 1 ELSE 0 END) / COUNT(*),
        2
    ) AS denial_rate_pct
FROM clean_claims
GROUP BY payer_type
ORDER BY claim_count DESC;

-- ------------------------------------------------------------
-- 5. PROVIDERS TO REVIEW
-- ------------------------------------------------------------

WITH clean_claims AS (
    SELECT DISTINCT ON (c.claim_id) c.*
    FROM fact_claims c
    INNER JOIN dim_patient pt ON c.patient_id = pt.patient_id
    INNER JOIN dim_provider pr ON c.provider_id = pr.provider_id
    WHERE c.submitted_amount >= 0
      AND c.allowed_amount >= 0
      AND c.paid_amount >= 0
      AND c.processing_days >= 0
    ORDER BY c.claim_id, c.service_date
)
SELECT
    c.provider_id,
    p.specialty,
    p.facility_type,
    COUNT(*) AS claim_count,
    ROUND(
        100.0 * SUM(CASE WHEN c.claim_status = 'Denied' THEN 1 ELSE 0 END) / COUNT(*),
        2
    ) AS denial_rate_pct,
    ROUND(AVG(c.processing_days), 2) AS avg_processing_days,
    ROUND(SUM(c.paid_amount), 2) AS paid_amount
FROM clean_claims c
JOIN dim_provider p
    ON c.provider_id = p.provider_id
GROUP BY c.provider_id, p.specialty, p.facility_type
HAVING COUNT(*) >= 20
ORDER BY denial_rate_pct DESC, claim_count DESC
LIMIT 10;

-- ------------------------------------------------------------
-- 6. UTILIZATION: INPATIENT LOS AND 30-DAY READMISSION
-- ------------------------------------------------------------

WITH clean_claims AS (
    SELECT DISTINCT ON (c.claim_id) c.*
    FROM fact_claims c
    INNER JOIN dim_patient pt ON c.patient_id = pt.patient_id
    INNER JOIN dim_provider pr ON c.provider_id = pr.provider_id
    WHERE c.submitted_amount >= 0
      AND c.allowed_amount >= 0
      AND c.paid_amount >= 0
      AND c.processing_days >= 0
    ORDER BY c.claim_id, c.service_date
)
SELECT
    COUNT(*) AS inpatient_encounters,
    ROUND(AVG(length_of_stay_days), 2) AS avg_length_of_stay_days,
    ROUND(100.0 * AVG(readmission_30d_flag), 2) AS readmission_30d_rate_pct
FROM clean_claims
WHERE encounter_type = 'Inpatient';
