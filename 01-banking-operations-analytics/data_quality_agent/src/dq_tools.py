import os
import re
from decimal import Decimal
from pathlib import Path
from typing import Any

import psycopg2
from dotenv import load_dotenv
from psycopg2.extras import RealDictCursor


AGENT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(AGENT_DIR / ".env")


BLOCKED_SQL_PATTERNS = [
    r"\binsert\b",
    r"\bupdate\b",
    r"\bdelete\b",
    r"\bdrop\b",
    r"\balter\b",
    r"\btruncate\b",
    r"\bcreate\b",
    r"\bgrant\b",
    r"\brevoke\b",
    r"\bcopy\b",
    r"\bcall\b",
    r"\bexecute\b",
]


def _json_safe(value: Any) -> Any:
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, dict):
        return {key: _json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    return value


def get_db_connection():
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")

    if not user:
        raise RuntimeError(
            "DB_USER is not configured. Copy .env.example to .env and add local PostgreSQL credentials."
        )

    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME", "banking_analytics_db"),
        user=user,
        password=password,
        connect_timeout=int(os.getenv("DB_CONNECT_TIMEOUT", "5")),
    )


def validate_readonly_sql(sql: str) -> tuple[bool, str]:
    cleaned = sql.strip().lower()

    if not (cleaned.startswith("select") or cleaned.startswith("with")):
        return False, "Only read-only SELECT or WITH statements are allowed."

    for pattern in BLOCKED_SQL_PATTERNS:
        if re.search(pattern, cleaned):
            return False, f"Blocked SQL keyword detected: {pattern}"

    if cleaned.count(";") > 1:
        return False, "Multiple SQL statements are not allowed."

    return True, "SQL passed read-only validation."


def execute_query(sql: str, params: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
    valid, reason = validate_readonly_sql(sql)
    if not valid:
        raise PermissionError(reason)

    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(sql, params)
            rows = cursor.fetchall()

    return _json_safe([dict(row) for row in rows])


def _exception_count(exception_type: str) -> int:
    sql = """
SELECT COUNT(*) AS exception_count
FROM staging.stg_transaction_dq_exceptions
WHERE exception_type = %s;
""".strip()
    rows = execute_query(sql, (exception_type,))
    return int(rows[0]["exception_count"]) if rows else 0


def check_row_reconciliation() -> dict[str, Any]:
    sql = """
SELECT
    (SELECT COUNT(*) FROM raw.transactions) AS raw_rows,
    (SELECT COUNT(DISTINCT transaction_id) FROM raw.transactions) AS unique_transaction_ids,
    (SELECT COUNT(*) FROM staging.stg_transactions) AS staging_rows,
    (SELECT COUNT(*) FROM warehouse.fact_transactions) AS warehouse_rows;
""".strip()
    row = execute_query(sql)[0]

    raw_rows = int(row["raw_rows"])
    unique_ids = int(row["unique_transaction_ids"])
    staging_rows = int(row["staging_rows"])
    warehouse_rows = int(row["warehouse_rows"])

    passed = unique_ids == staging_rows == warehouse_rows and raw_rows >= unique_ids

    return {
        "check": "row_reconciliation",
        "status": "PASS" if passed else "FAIL",
        "evidence": {
            "raw_rows": raw_rows,
            "unique_transaction_ids": unique_ids,
            "staging_rows": staging_rows,
            "warehouse_rows": warehouse_rows,
            "raw_minus_unique": raw_rows - unique_ids,
        },
        "source": "raw.transactions -> staging.stg_transactions -> warehouse.fact_transactions",
        "rule": "Trusted staging and warehouse should reconcile to unique transaction IDs while raw retains source duplicates for audit.",
        "sql_validation": "PASSED",
    }


def check_duplicate_transactions() -> dict[str, Any]:
    sql = """
WITH raw_counts AS (
    SELECT COUNT(*) AS raw_rows, COUNT(DISTINCT transaction_id) AS unique_ids
    FROM raw.transactions
),
warehouse_duplicates AS (
    SELECT COUNT(*) AS duplicate_ids
    FROM (
        SELECT transaction_id
        FROM warehouse.fact_transactions
        GROUP BY transaction_id
        HAVING COUNT(*) > 1
    ) d
)
SELECT
    raw_counts.raw_rows - raw_counts.unique_ids AS raw_duplicate_rows,
    warehouse_duplicates.duplicate_ids AS warehouse_duplicate_ids
FROM raw_counts
CROSS JOIN warehouse_duplicates;
""".strip()
    row = execute_query(sql)[0]
    raw_duplicates = int(row["raw_duplicate_rows"])
    exception_count = _exception_count("DUPLICATE_TRANSACTION_ID")
    warehouse_duplicate_ids = int(row["warehouse_duplicate_ids"])

    passed = raw_duplicates == exception_count and warehouse_duplicate_ids == 0

    return {
        "check": "duplicate_transactions",
        "status": "PASS" if passed else "FAIL",
        "evidence": {
            "raw_duplicate_rows": raw_duplicates,
            "captured_duplicate_exceptions": exception_count,
            "warehouse_duplicate_transaction_ids": warehouse_duplicate_ids,
        },
        "source": "raw.transactions + staging.stg_transaction_dq_exceptions + warehouse.fact_transactions",
        "rule": "Duplicate source rows remain auditable, but the trusted warehouse must retain one row per transaction_id.",
        "sql_validation": "PASSED",
    }


def check_failed_transaction_fees() -> dict[str, Any]:
    sql = """
SELECT
    (SELECT COUNT(*)
     FROM raw.transactions
     WHERE transaction_status = 'Failed' AND COALESCE(fee_amount, 0) > 0) AS raw_failed_with_fee,
    (SELECT COUNT(*)
     FROM warehouse.fact_transactions
     WHERE transaction_status = 'Failed' AND COALESCE(fee_amount, 0) > 0) AS warehouse_failed_with_fee;
""".strip()
    row = execute_query(sql)[0]
    raw_count = int(row["raw_failed_with_fee"])
    exception_count = _exception_count("FAILED_TRANSACTION_WITH_FEE")
    warehouse_count = int(row["warehouse_failed_with_fee"])

    passed = raw_count == exception_count and warehouse_count == 0

    return {
        "check": "failed_transaction_fees",
        "status": "PASS" if passed else "FAIL",
        "evidence": {
            "raw_failed_with_fee": raw_count,
            "captured_failed_fee_exceptions": exception_count,
            "warehouse_failed_with_fee": warehouse_count,
        },
        "source": "raw.transactions + staging.stg_transaction_dq_exceptions + warehouse.fact_transactions",
        "rule": "Failed transactions with non-zero source fees are captured as exceptions and must have zero fee in the trusted warehouse.",
        "sql_validation": "PASSED",
    }


def check_missing_channels() -> dict[str, Any]:
    sql = """
SELECT
    (SELECT COUNT(*)
     FROM raw.transactions
     WHERE channel_id IS NULL OR TRIM(channel_id) = '') AS raw_missing_channel,
    (SELECT COUNT(*)
     FROM warehouse.fact_transactions
     WHERE channel_id IS NULL OR TRIM(channel_id) = '') AS warehouse_missing_channel;
""".strip()
    row = execute_query(sql)[0]
    raw_count = int(row["raw_missing_channel"])
    exception_count = _exception_count("MISSING_CHANNEL_ID")
    warehouse_count = int(row["warehouse_missing_channel"])

    controlled = raw_count == exception_count == warehouse_count
    status = "REVIEW" if controlled and raw_count > 0 else "PASS" if controlled else "FAIL"

    return {
        "check": "missing_channels",
        "status": status,
        "evidence": {
            "raw_missing_channel": raw_count,
            "captured_missing_channel_exceptions": exception_count,
            "warehouse_missing_channel": warehouse_count,
        },
        "source": "raw.transactions + staging.stg_transaction_dq_exceptions + warehouse.fact_transactions",
        "rule": "Missing channel_id is flagged and preserved; the pipeline must not invent or impute a channel value.",
        "recommendation": "Keep the records visible as unknown channel data and exclude/include them in channel-specific KPIs only through an explicit reporting rule.",
        "sql_validation": "PASSED",
    }


def check_high_value_transactions() -> dict[str, Any]:
    sql = """
SELECT
    (SELECT COUNT(*) FROM raw.transactions WHERE amount > 500000) AS raw_high_value,
    (SELECT COUNT(*) FROM warehouse.fact_transactions WHERE amount > 500000) AS warehouse_high_value;
""".strip()
    row = execute_query(sql)[0]
    raw_count = int(row["raw_high_value"])
    exception_count = _exception_count("HIGH_VALUE_TRANSACTION")
    warehouse_count = int(row["warehouse_high_value"])

    controlled = raw_count == exception_count == warehouse_count
    status = "REVIEW" if controlled and raw_count > 0 else "PASS" if controlled else "FAIL"

    return {
        "check": "high_value_transactions",
        "status": status,
        "evidence": {
            "raw_high_value": raw_count,
            "captured_high_value_exceptions": exception_count,
            "warehouse_high_value": warehouse_count,
        },
        "source": "raw.transactions + staging.stg_transaction_dq_exceptions + warehouse.fact_transactions",
        "rule": "High-value transactions are review flags, not automatic errors; valid records remain in trusted reporting data.",
        "recommendation": "Investigate business context before excluding or correcting any high-value record.",
        "sql_validation": "PASSED",
    }


CHECK_FUNCTIONS = {
    "row_reconciliation": check_row_reconciliation,
    "duplicate_transactions": check_duplicate_transactions,
    "failed_transaction_fees": check_failed_transaction_fees,
    "missing_channels": check_missing_channels,
    "high_value_transactions": check_high_value_transactions,
}


def run_checks(check_names: list[str]) -> dict[str, Any]:
    results: dict[str, Any] = {}
    for name in check_names:
        if name not in CHECK_FUNCTIONS:
            raise ValueError(f"Unsupported DQ check: {name}")
        results[name] = CHECK_FUNCTIONS[name]()
    return results


def validate_warehouse_readiness() -> dict[str, Any]:
    results = run_checks(list(CHECK_FUNCTIONS))
    statuses = [result["status"] for result in results.values()]

    if "FAIL" in statuses:
        readiness = "NOT_READY"
    elif "REVIEW" in statuses:
        readiness = "READY_WITH_KNOWN_EXCEPTIONS"
    else:
        readiness = "READY"

    return {
        "check": "warehouse_readiness",
        "status": readiness,
        "results": results,
        "blocking_failures": [
            name for name, result in results.items() if result["status"] == "FAIL"
        ],
        "review_items": [
            name for name, result in results.items() if result["status"] == "REVIEW"
        ],
        "source": "PostgreSQL raw/staging/warehouse validation controls",
        "sql_validation": "PASSED",
    }
