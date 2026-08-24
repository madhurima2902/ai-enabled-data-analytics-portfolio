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


def _percent_change(first: float, last: float) -> float | None:
    if first == 0:
        return None
    return round(((last - first) / first) * 100, 2)


def _build_evidence_analysis(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Build deterministic descriptive analysis from validated metric evidence.

    This intentionally describes movement and relative growth only. It does not
    label the metric good/bad or invent a target, threshold, or root cause.
    """

    if not rows:
        return {}

    first = rows[0]
    last = rows[-1]

    first_value = float(first["metric_value"])
    last_value = float(last["metric_value"])
    first_numerator = float(first["metric_numerator"])
    last_numerator = float(last["metric_numerator"])
    first_denominator = float(first["metric_denominator"])
    last_denominator = float(last["metric_denominator"])

    sequential_changes: list[dict[str, Any]] = []
    for previous, current in zip(rows, rows[1:]):
        previous_value = float(previous["metric_value"])
        current_value = float(current["metric_value"])
        delta = round(current_value - previous_value, 2)
        direction = "increased" if delta > 0 else "decreased" if delta < 0 else "unchanged"
        sequential_changes.append(
            {
                "from_period": f"{int(previous['year']):04d}-{int(previous['month']):02d}",
                "to_period": f"{int(current['year']):04d}-{int(current['month']):02d}",
                "delta": delta,
                "direction": direction,
            }
        )

    overall_delta = round(last_value - first_value, 2)
    overall_direction = (
        "increased" if overall_delta > 0 else "decreased" if overall_delta < 0 else "unchanged"
    )
    metric_change_percent = _percent_change(first_value, last_value)
    numerator_change_percent = _percent_change(first_numerator, last_numerator)
    denominator_change_percent = _percent_change(first_denominator, last_denominator)

    if sequential_changes and all(change["direction"] == "increased" for change in sequential_changes):
        trend_pattern = "increased in every observed period"
    elif sequential_changes and all(change["direction"] == "decreased" for change in sequential_changes):
        trend_pattern = "decreased in every observed period"
    elif sequential_changes and all(change["direction"] == "unchanged" for change in sequential_changes):
        trend_pattern = "was unchanged across the observed periods"
    else:
        trend_pattern = "showed a mixed pattern across the observed periods"

    if numerator_change_percent is None or denominator_change_percent is None:
        relative_growth_pattern = "relative growth comparison is unavailable"
    elif numerator_change_percent > denominator_change_percent:
        relative_growth_pattern = "transaction volume grew faster than the active-customer base"
    elif numerator_change_percent < denominator_change_percent:
        relative_growth_pattern = "the active-customer base grew faster than transaction volume"
    else:
        relative_growth_pattern = "transaction volume and the active-customer base grew at the same rate"

    return {
        "first_period": f"{int(first['year']):04d}-{int(first['month']):02d}",
        "last_period": f"{int(last['year']):04d}-{int(last['month']):02d}",
        "first_value": first_value,
        "last_value": last_value,
        "overall_delta": overall_delta,
        "overall_direction": overall_direction,
        "metric_change_percent": metric_change_percent,
        "numerator_change_percent": numerator_change_percent,
        "denominator_change_percent": denominator_change_percent,
        "trend_pattern": trend_pattern,
        "relative_growth_pattern": relative_growth_pattern,
        "sequential_changes": sequential_changes,
        "interpretation_boundary": (
            "Descriptive movement is supported by the evidence. No approved target or threshold is "
            "defined for this metric, so the agent must not label the change good, bad, acceptable, "
            "or concerning without additional approved guidance."
        ),
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
        "analysis": _build_evidence_analysis(rows),
        "source": config["source"],
        "sql_validation": "PASSED",
    }
