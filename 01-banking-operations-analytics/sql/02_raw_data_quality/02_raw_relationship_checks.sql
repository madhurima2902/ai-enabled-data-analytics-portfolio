-- Raw relationship checks
-- Purpose: Check whether raw tables can be joined correctly before staging/warehouse modeling.

-- ============================================================
-- 1. Account to customer relationship
-- ============================================================

SELECT
    'raw.accounts.customer_id -> raw.customers.customer_id' AS relationship_check,
    COUNT(*) AS missing_reference_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END AS validation_status
FROM raw.accounts a
LEFT JOIN raw.customers c
    ON a.customer_id = c.customer_id
WHERE c.customer_id IS NULL;


-- ============================================================
-- 2. Account to product relationship
-- ============================================================

SELECT
    'raw.accounts.product_id -> raw.products.product_id' AS relationship_check,
    COUNT(*) AS missing_reference_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END AS validation_status
FROM raw.accounts a
LEFT JOIN raw.products p
    ON a.product_id = p.product_id
WHERE p.product_id IS NULL;


-- ============================================================
-- 3. Account to branch relationship
-- ============================================================

SELECT
    'raw.accounts.branch_id -> raw.branches.branch_id' AS relationship_check,
    COUNT(*) AS missing_reference_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END AS validation_status
FROM raw.accounts a
LEFT JOIN raw.branches b
    ON a.branch_id = b.branch_id
WHERE b.branch_id IS NULL;


-- ============================================================
-- 4. Complaint relationships
-- ============================================================

SELECT
    'raw.complaints.customer_id -> raw.customers.customer_id' AS relationship_check,
    COUNT(*) AS missing_reference_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END AS validation_status
FROM raw.complaints comp
LEFT JOIN raw.customers c
    ON comp.customer_id = c.customer_id
WHERE c.customer_id IS NULL

UNION ALL

SELECT
    'raw.complaints.account_id -> raw.accounts.account_id' AS relationship_check,
    COUNT(*) AS missing_reference_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END AS validation_status
FROM raw.complaints comp
LEFT JOIN raw.accounts a
    ON comp.account_id = a.account_id
WHERE a.account_id IS NULL

UNION ALL

SELECT
    'raw.complaints.product_id -> raw.products.product_id' AS relationship_check,
    COUNT(*) AS missing_reference_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END AS validation_status
FROM raw.complaints comp
LEFT JOIN raw.products p
    ON comp.product_id = p.product_id
WHERE p.product_id IS NULL

UNION ALL

SELECT
    'raw.complaints.channel_id -> raw.channels.channel_id' AS relationship_check,
    COUNT(*) AS missing_reference_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END AS validation_status
FROM raw.complaints comp
LEFT JOIN raw.channels ch
    ON comp.channel_id = ch.channel_id
WHERE ch.channel_id IS NULL;


-- ============================================================
-- 5. Campaign relationships
-- ============================================================

SELECT
    'raw.campaigns.customer_id -> raw.customers.customer_id' AS relationship_check,
    COUNT(*) AS missing_reference_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END AS validation_status
FROM raw.campaigns camp
LEFT JOIN raw.customers c
    ON camp.customer_id = c.customer_id
WHERE c.customer_id IS NULL

UNION ALL

SELECT
    'raw.campaigns.offer_product_id -> raw.products.product_id' AS relationship_check,
    COUNT(*) AS missing_reference_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END AS validation_status
FROM raw.campaigns camp
LEFT JOIN raw.products p
    ON camp.offer_product_id = p.product_id
WHERE p.product_id IS NULL

UNION ALL

SELECT
    'raw.campaigns.campaign_channel_id -> raw.channels.channel_id' AS relationship_check,
    COUNT(*) AS missing_reference_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END AS validation_status
FROM raw.campaigns camp
LEFT JOIN raw.channels ch
    ON camp.campaign_channel_id = ch.channel_id
WHERE ch.channel_id IS NULL;


-- ============================================================
-- 6. SLA ticket relationships
-- ============================================================

SELECT
    'raw.sla_tickets.complaint_id -> raw.complaints.complaint_id' AS relationship_check,
    COUNT(*) AS missing_reference_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END AS validation_status
FROM raw.sla_tickets st
LEFT JOIN raw.complaints comp
    ON st.complaint_id = comp.complaint_id
WHERE comp.complaint_id IS NULL

UNION ALL

SELECT
    'raw.sla_tickets.customer_id -> raw.customers.customer_id' AS relationship_check,
    COUNT(*) AS missing_reference_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END AS validation_status
FROM raw.sla_tickets st
LEFT JOIN raw.customers c
    ON st.customer_id = c.customer_id
WHERE c.customer_id IS NULL

UNION ALL

SELECT
    'raw.sla_tickets.account_id -> raw.accounts.account_id' AS relationship_check,
    COUNT(*) AS missing_reference_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END AS validation_status
FROM raw.sla_tickets st
LEFT JOIN raw.accounts a
    ON st.account_id = a.account_id
WHERE a.account_id IS NULL;


-- ============================================================
-- 7. Transaction relationships
-- ============================================================

SELECT
    'raw.transactions.account_id -> raw.accounts.account_id' AS relationship_check,
    COUNT(*) AS missing_reference_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END AS validation_status
FROM raw.transactions t
LEFT JOIN raw.accounts a
    ON t.account_id = a.account_id
WHERE a.account_id IS NULL

UNION ALL

SELECT
    'raw.transactions.customer_id -> raw.customers.customer_id' AS relationship_check,
    COUNT(*) AS missing_reference_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END AS validation_status
FROM raw.transactions t
LEFT JOIN raw.customers c
    ON t.customer_id = c.customer_id
WHERE c.customer_id IS NULL

UNION ALL

SELECT
    'raw.transactions.product_id -> raw.products.product_id' AS relationship_check,
    COUNT(*) AS missing_reference_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END AS validation_status
FROM raw.transactions t
LEFT JOIN raw.products p
    ON t.product_id = p.product_id
WHERE p.product_id IS NULL

UNION ALL

SELECT
    'raw.transactions.branch_id -> raw.branches.branch_id' AS relationship_check,
    COUNT(*) AS missing_reference_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END AS validation_status
FROM raw.transactions t
LEFT JOIN raw.branches b
    ON t.branch_id = b.branch_id
WHERE b.branch_id IS NULL

UNION ALL

SELECT
    'raw.transactions.channel_id -> raw.channels.channel_id' AS relationship_check,
    COUNT(*) AS missing_reference_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END AS validation_status
FROM raw.transactions t
LEFT JOIN raw.channels ch
    ON t.channel_id = ch.channel_id
WHERE ch.channel_id IS NULL;


-- ============================================================
-- 8. Cross-field consistency checks
-- These verify that transaction fields match the linked account.
-- ============================================================

SELECT
    'transaction customer matches account customer' AS consistency_check,
    COUNT(*) AS mismatch_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END AS validation_status
FROM raw.transactions t
JOIN raw.accounts a
    ON t.account_id = a.account_id
WHERE t.customer_id <> a.customer_id

UNION ALL

SELECT
    'transaction product matches account product' AS consistency_check,
    COUNT(*) AS mismatch_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END AS validation_status
FROM raw.transactions t
JOIN raw.accounts a
    ON t.account_id = a.account_id
WHERE t.product_id <> a.product_id

UNION ALL

SELECT
    'transaction branch matches account branch' AS consistency_check,
    COUNT(*) AS mismatch_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END AS validation_status
FROM raw.transactions t
JOIN raw.accounts a
    ON t.account_id = a.account_id
WHERE t.branch_id <> a.branch_id;


-- ============================================================
-- 9. Complaint cross-field consistency checks
-- These verify that complaint fields match the linked account.
-- ============================================================

SELECT
    'complaint customer matches account customer' AS consistency_check,
    COUNT(*) AS mismatch_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END AS validation_status
FROM raw.complaints comp
JOIN raw.accounts a
    ON comp.account_id = a.account_id
WHERE comp.customer_id <> a.customer_id

UNION ALL

SELECT
    'complaint product matches account product' AS consistency_check,
    COUNT(*) AS mismatch_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASSED' ELSE 'FAILED' END AS validation_status
FROM raw.complaints comp
JOIN raw.accounts a
    ON comp.account_id = a.account_id
WHERE comp.product_id <> a.product_id;