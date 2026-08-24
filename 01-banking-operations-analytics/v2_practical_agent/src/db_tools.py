import os
import re
from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import Any

import psycopg2
from dotenv import load_dotenv
from psycopg2.extras import RealDictCursor


PROJECT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_DIR / ".env")


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


KPI_LABELS = {
    "transaction_failure_rate": "Transaction Failure Rate",
    "transaction_success_rate": "Transaction Success Rate",
    "complaint_resolution_rate": "Complaint Resolution Rate",
    "sla_breach_rate": "SLA Breach Rate",
    "campaign_conversion_rate": "Campaign Conversion Rate",
    "complaints_per_1000_transactions": "Complaints per 1,000 Transactions",
}


def _json_safe(value: Any) -> Any:
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, (date,)):
        return value.isoformat()
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
    """Deterministic SQL guard used before every database query."""

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
    valid, message = validate_readonly_sql(sql)
    if not valid:
        raise PermissionError(message)

    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(sql, params)
            rows = cursor.fetchall()

    return _json_safe([dict(row) for row in rows])


def month_bounds(month: int, year: int = 2026) -> tuple[date, date]:
    if month < 1 or month > 12:
        raise ValueError("month must be between 1 and 12")

    start = date(year, month, 1)
    if month == 12:
        end = date(year + 1, 1, 1)
    else:
        end = date(year, month + 1, 1)
    return start, end


def _channel_clause(channel: str | None, alias: str = "dc") -> tuple[str, tuple[Any, ...]]:
    if not channel:
        return "", ()
    return f" AND {alias}.channel_name = %s", (channel,)


def get_kpi_metric(
    kpi: str,
    month: int,
    channel: str | None = None,
    year: int = 2026,
) -> dict[str, Any]:
    """Return one approved KPI from the trusted warehouse for a month."""

    if kpi not in KPI_LABELS:
        raise ValueError(f"Unsupported KPI: {kpi}")

    start, end = month_bounds(month, year)

    if kpi in {"transaction_failure_rate", "transaction_success_rate"}:
        numerator_field = (
            "failed_transaction_count"
            if kpi == "transaction_failure_rate"
            else "successful_transaction_count"
        )
        channel_clause, channel_params = _channel_clause(channel)
        sql = f"""
SELECT
    SUM(ft.{numerator_field}) AS metric_numerator,
    SUM(ft.transaction_count) AS metric_denominator,
    ROUND(
        100.0 * SUM(ft.{numerator_field})
        / NULLIF(SUM(ft.transaction_count), 0),
        2
    ) AS metric_value
FROM warehouse.fact_transactions ft
LEFT JOIN warehouse.dim_channel dc
    ON ft.channel_key = dc.channel_key
WHERE ft.transaction_date >= %s
  AND ft.transaction_date < %s
  {channel_clause};
""".strip()
        params = (start, end) + channel_params

    elif kpi == "complaint_resolution_rate":
        channel_clause, channel_params = _channel_clause(channel)
        sql = f"""
SELECT
    SUM(fc.resolved_complaint_count) AS metric_numerator,
    SUM(fc.complaint_count) AS metric_denominator,
    ROUND(
        100.0 * SUM(fc.resolved_complaint_count)
        / NULLIF(SUM(fc.complaint_count), 0),
        2
    ) AS metric_value
FROM warehouse.fact_complaints fc
LEFT JOIN warehouse.dim_channel dc
    ON fc.channel_key = dc.channel_key
WHERE fc.complaint_date >= %s
  AND fc.complaint_date < %s
  {channel_clause};
""".strip()
        params = (start, end) + channel_params

    elif kpi == "sla_breach_rate":
        sql = """
SELECT
    SUM(sla_breached_count) AS metric_numerator,
    SUM(ticket_count) AS metric_denominator,
    ROUND(
        100.0 * SUM(sla_breached_count)
        / NULLIF(SUM(ticket_count), 0),
        2
    ) AS metric_value
FROM warehouse.fact_sla_tickets
WHERE created_datetime::date >= %s
  AND created_datetime::date < %s;
""".strip()
        params = (start, end)

    elif kpi == "campaign_conversion_rate":
        channel_clause = ""
        channel_params: tuple[Any, ...] = ()
        if channel:
            channel_clause = " AND dc.channel_name = %s"
            channel_params = (channel,)
        sql = f"""
SELECT
    SUM(fc.converted_count) AS metric_numerator,
    SUM(fc.campaign_sent_count) AS metric_denominator,
    ROUND(
        100.0 * SUM(fc.converted_count)
        / NULLIF(SUM(fc.campaign_sent_count), 0),
        2
    ) AS metric_value
FROM warehouse.fact_campaigns fc
LEFT JOIN warehouse.dim_channel dc
    ON fc.campaign_channel_key = dc.channel_key
WHERE fc.sent_date >= %s
  AND fc.sent_date < %s
  {channel_clause};
""".strip()
        params = (start, end) + channel_params

    else:  # complaints_per_1000_transactions
        tx_channel_clause, tx_channel_params = _channel_clause(channel, "tdc")
        complaint_channel_clause, complaint_channel_params = _channel_clause(channel, "cdc")
        sql = f"""
WITH transaction_base AS (
    SELECT SUM(ft.transaction_count) AS total_transactions
    FROM warehouse.fact_transactions ft
    LEFT JOIN warehouse.dim_channel tdc
        ON ft.channel_key = tdc.channel_key
    WHERE ft.transaction_date >= %s
      AND ft.transaction_date < %s
      {tx_channel_clause}
),
complaint_base AS (
    SELECT SUM(fc.complaint_count) AS total_complaints
    FROM warehouse.fact_complaints fc
    LEFT JOIN warehouse.dim_channel cdc
        ON fc.channel_key = cdc.channel_key
    WHERE fc.complaint_date >= %s
      AND fc.complaint_date < %s
      {complaint_channel_clause}
)
SELECT
    complaint_base.total_complaints AS metric_numerator,
    transaction_base.total_transactions AS metric_denominator,
    ROUND(
        1000.0 * complaint_base.total_complaints
        / NULLIF(transaction_base.total_transactions, 0),
        2
    ) AS metric_value
FROM transaction_base
CROSS JOIN complaint_base;
""".strip()
        params = (
            start,
            end,
        ) + tx_channel_params + (
            start,
            end,
        ) + complaint_channel_params

    rows = execute_query(sql, params)
    row = rows[0] if rows else {}

    return {
        "tool": "get_kpi_metric",
        "kpi": kpi,
        "kpi_label": KPI_LABELS[kpi],
        "period_start": start.isoformat(),
        "period_end_exclusive": end.isoformat(),
        "channel": channel or "All Channels",
        "metric_numerator": row.get("metric_numerator"),
        "metric_denominator": row.get("metric_denominator"),
        "metric_value": row.get("metric_value"),
        "source": "PostgreSQL trusted warehouse",
        "sql_validation": "PASSED",
    }


def compare_kpi(
    kpi: str,
    month_a: int,
    month_b: int,
    channel: str | None = None,
    year: int = 2026,
) -> dict[str, Any]:
    first = get_kpi_metric(kpi, month_a, channel, year)
    second = get_kpi_metric(kpi, month_b, channel, year)

    first_value = first.get("metric_value")
    second_value = second.get("metric_value")
    delta = None
    if first_value is not None and second_value is not None:
        delta = round(float(second_value) - float(first_value), 2)

    return {
        "tool": "compare_kpi",
        "kpi": kpi,
        "kpi_label": KPI_LABELS[kpi],
        "channel": channel or "All Channels",
        "first_period": first,
        "second_period": second,
        "delta_percentage_points": delta,
        "source": "PostgreSQL trusted warehouse",
        "sql_validation": "PASSED",
    }


def compare_kpi_periods(
    kpi: str,
    months: list[int],
    channel: str | None = None,
    year: int = 2026,
) -> dict[str, Any]:
    """Compare an approved KPI across two or more explicitly requested months."""

    ordered_months = sorted(dict.fromkeys(months))
    if len(ordered_months) < 2:
        raise ValueError("At least two distinct months are required for multi-period comparison.")

    periods = [
        get_kpi_metric(kpi, month, channel, year)
        for month in ordered_months
    ]

    changes: list[dict[str, Any]] = []
    for first, second in zip(periods, periods[1:]):
        first_value = first.get("metric_value")
        second_value = second.get("metric_value")
        delta = None
        if first_value is not None and second_value is not None:
            delta = round(float(second_value) - float(first_value), 2)
        changes.append(
            {
                "from_period": first.get("period_start"),
                "to_period": second.get("period_start"),
                "delta_percentage_points": delta,
            }
        )

    return {
        "tool": "compare_kpi_periods",
        "kpi": kpi,
        "kpi_label": KPI_LABELS[kpi],
        "channel": channel or "All Channels",
        "periods": periods,
        "changes": changes,
        "source": "PostgreSQL trusted warehouse",
        "sql_validation": "PASSED",
    }


def get_transaction_details(transaction_id: str) -> dict[str, Any]:
    sql = """
SELECT
    ft.transaction_id,
    ft.transaction_datetime,
    ft.transaction_status,
    ft.amount,
    ft.fee_amount,
    ft.currency,
    dc.channel_name,
    ft.account_id,
    ft.product_id
FROM warehouse.fact_transactions ft
LEFT JOIN warehouse.dim_channel dc
    ON ft.channel_key = dc.channel_key
WHERE ft.transaction_id = %s
LIMIT 1;
""".strip()

    rows = execute_query(sql, (transaction_id.upper(),))
    return {
        "tool": "get_transaction_details",
        "transaction_id": transaction_id.upper(),
        "found": bool(rows),
        "record": rows[0] if rows else None,
        "source": "PostgreSQL trusted warehouse",
        "sql_validation": "PASSED",
    }


def get_dq_summary() -> dict[str, Any]:
    sql = """
SELECT exception_type, COUNT(*) AS exception_count
FROM staging.stg_transaction_dq_exceptions
GROUP BY exception_type
ORDER BY exception_type;
""".strip()

    rows = execute_query(sql)
    return {
        "tool": "get_dq_summary",
        "exceptions": rows,
        "source": "staging.stg_transaction_dq_exceptions",
        "sql_validation": "PASSED",
    }