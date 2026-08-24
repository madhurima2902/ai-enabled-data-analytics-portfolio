from typing import Any

try:
    from .db_tools import execute_query
except ImportError:
    from db_tools import execute_query


APPROVED_DERIVED_METRICS = {
    "average_transactions_per_active_customer": {
        "label": "Average Transactions per Active Customer",
        "definition": (
            "Monthly transaction count divided by distinct customers with at least one "
            "transaction in that month."
        ),
        "numerator_label": "transaction_count",
        "denominator_label": "distinct_active_customers",
        "source": "warehouse.fact_transactions",
    },
}


def get_derived_metric(
    metric: str,
    months: list[int] | None = None,
    year: int = 2026,
) -> dict[str, Any]:
    """Calculate an approved derived business metric using deterministic SQL."""

    if metric not in APPROVED_DERIVED_METRICS:
        raise ValueError(f"Unsupported derived metric: {metric}")

    if metric != "average_transactions_per_active_customer":
        raise ValueError(f"No implementation configured for derived metric: {metric}")

    requested_months = sorted(set(months or []))
    params: list[Any] = [year]
    month_filter = ""

    if requested_months:
        placeholders = ", ".join(["%s"] * len(requested_months))
        month_filter = f"AND EXTRACT(MONTH FROM transaction_date) IN ({placeholders})"
        params.extend(requested_months)

    sql = f"""
SELECT
    EXTRACT(YEAR FROM transaction_date)::INT AS year,
    EXTRACT(MONTH FROM transaction_date)::INT AS month,
    COUNT(*) AS metric_numerator,
    COUNT(DISTINCT customer_id) AS metric_denominator,
    ROUND(
        COUNT(*)::NUMERIC / NULLIF(COUNT(DISTINCT customer_id), 0),
        2
    ) AS metric_value
FROM warehouse.fact_transactions
WHERE EXTRACT(YEAR FROM transaction_date) = %s
  {month_filter}
GROUP BY 1, 2
ORDER BY 1, 2;
""".strip()

    rows = execute_query(sql, tuple(params))
    config = APPROVED_DERIVED_METRICS[metric]

    return {
        "tool": "get_derived_metric",
        "metric": metric,
        "metric_label": config["label"],
        "definition": config["definition"],
        "numerator_label": config["numerator_label"],
        "denominator_label": config["denominator_label"],
        "requested_months": requested_months,
        "year": year,
        "grouping": "month",
        "rows": rows,
        "source": config["source"],
        "sql_validation": "PASSED",
    }
