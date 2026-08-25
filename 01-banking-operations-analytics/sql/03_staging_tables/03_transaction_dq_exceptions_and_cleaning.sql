-- Capture raw transaction data-quality exceptions and clean the staging layer.
-- Raw data remains unchanged for audit / agent DQ investigation.

CREATE SCHEMA IF NOT EXISTS staging;

DROP TABLE IF EXISTS staging.stg_transaction_dq_exceptions;

CREATE TABLE staging.stg_transaction_dq_exceptions AS
WITH ranked_duplicates AS (
    SELECT
        r.*,
        ROW_NUMBER() OVER (
            PARTITION BY transaction_id
            ORDER BY transaction_datetime, account_id, amount, ctid
        ) AS duplicate_rank
    FROM raw.transactions r
)
SELECT
    transaction_id,
    'DUPLICATE_TRANSACTION_ID'::TEXT AS exception_type,
    account_id,
    customer_id,
    channel_id,
    transaction_datetime,
    transaction_status,
    amount,
    fee_amount,
    CURRENT_TIMESTAMP AS detected_at
FROM ranked_duplicates
WHERE duplicate_rank > 1

UNION ALL

SELECT
    transaction_id,
    'FAILED_TRANSACTION_WITH_FEE'::TEXT AS exception_type,
    account_id,
    customer_id,
    channel_id,
    transaction_datetime,
    transaction_status,
    amount,
    fee_amount,
    CURRENT_TIMESTAMP AS detected_at
FROM raw.transactions
WHERE transaction_status = 'Failed'
  AND COALESCE(fee_amount, 0) > 0

UNION ALL

SELECT
    transaction_id,
    'MISSING_CHANNEL_ID'::TEXT AS exception_type,
    account_id,
    customer_id,
    channel_id,
    transaction_datetime,
    transaction_status,
    amount,
    fee_amount,
    CURRENT_TIMESTAMP AS detected_at
FROM raw.transactions
WHERE channel_id IS NULL OR TRIM(channel_id) = ''

UNION ALL

SELECT
    transaction_id,
    'HIGH_VALUE_TRANSACTION'::TEXT AS exception_type,
    account_id,
    customer_id,
    channel_id,
    transaction_datetime,
    transaction_status,
    amount,
    fee_amount,
    CURRENT_TIMESTAMP AS detected_at
FROM raw.transactions
WHERE amount > 500000;

-- Keep one row per transaction_id in the clean staging layer.
WITH ranked AS (
    SELECT
        ctid,
        ROW_NUMBER() OVER (
            PARTITION BY transaction_id
            ORDER BY transaction_datetime, account_id, amount, ctid
        ) AS rn
    FROM staging.stg_transactions
)
DELETE FROM staging.stg_transactions t
USING ranked r
WHERE t.ctid = r.ctid
  AND r.rn > 1;

-- Business rule: failed transactions should not carry a fee in the trusted KPI layer.
-- The original fee remains visible in raw.transactions and the exception table above.
UPDATE staging.stg_transactions
SET fee_amount = 0
WHERE transaction_status = 'Failed'
  AND COALESCE(fee_amount, 0) > 0;

-- Missing channel_id is intentionally NOT imputed. It remains NULL so it can be
-- treated as Unknown / excluded from channel-specific KPI analysis by explicit rule.
-- High-value transactions are also retained because they are plausible business events,
-- not automatically bad data.

SELECT exception_type, COUNT(*) AS exception_count
FROM staging.stg_transaction_dq_exceptions
GROUP BY exception_type
ORDER BY exception_type;
