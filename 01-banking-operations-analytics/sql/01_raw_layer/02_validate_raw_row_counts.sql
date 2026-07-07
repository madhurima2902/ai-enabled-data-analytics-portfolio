-- Raw layer row count validation

SELECT
    'raw.customers' AS table_name,
    COUNT(*) AS actual_rows,
    10000 AS expected_rows,
    CASE WHEN COUNT(*) = 10000 THEN 'PASSED' ELSE 'FAILED' END AS validation_status
FROM raw.customers

UNION ALL

SELECT
    'raw.accounts' AS table_name,
    COUNT(*) AS actual_rows,
    15000 AS expected_rows,
    CASE WHEN COUNT(*) = 15000 THEN 'PASSED' ELSE 'FAILED' END AS validation_status
FROM raw.accounts

UNION ALL

SELECT
    'raw.products' AS table_name,
    COUNT(*) AS actual_rows,
    7 AS expected_rows,
    CASE WHEN COUNT(*) = 7 THEN 'PASSED' ELSE 'FAILED' END AS validation_status
FROM raw.products

UNION ALL

SELECT
    'raw.branches' AS table_name,
    COUNT(*) AS actual_rows,
    20 AS expected_rows,
    CASE WHEN COUNT(*) = 20 THEN 'PASSED' ELSE 'FAILED' END AS validation_status
FROM raw.branches

UNION ALL

SELECT
    'raw.channels' AS table_name,
    COUNT(*) AS actual_rows,
    6 AS expected_rows,
    CASE WHEN COUNT(*) = 6 THEN 'PASSED' ELSE 'FAILED' END AS validation_status
FROM raw.channels

UNION ALL

SELECT
    'raw.complaints' AS table_name,
    COUNT(*) AS actual_rows,
    2000 AS expected_rows,
    CASE WHEN COUNT(*) = 2000 THEN 'PASSED' ELSE 'FAILED' END AS validation_status
FROM raw.complaints

UNION ALL

SELECT
    'raw.campaigns' AS table_name,
    COUNT(*) AS actual_rows,
    5000 AS expected_rows,
    CASE WHEN COUNT(*) = 5000 THEN 'PASSED' ELSE 'FAILED' END AS validation_status
FROM raw.campaigns

UNION ALL

SELECT
    'raw.sla_tickets' AS table_name,
    COUNT(*) AS actual_rows,
    4000 AS expected_rows,
    CASE WHEN COUNT(*) = 4000 THEN 'PASSED' ELSE 'FAILED' END AS validation_status
FROM raw.sla_tickets

UNION ALL

SELECT
    'raw.transactions' AS table_name,
    COUNT(*) AS actual_rows,
    25000 AS expected_rows,
    CASE WHEN COUNT(*) = 25000 THEN 'PASSED' ELSE 'FAILED' END AS validation_status
FROM raw.transactions;