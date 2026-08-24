from typing import Any

try:
    from .db_tools import execute_query
except ImportError:
    from db_tools import execute_query


# Controlled allow-list for basic analyst-style aggregates. The model/router may
# request only these entities/measures; it never receives arbitrary table/column access.
APPROVED_AGGREGATES: dict[str, dict[str, Any]] = {
    "transactions": {
        "label": "Transactions",
        "table": "warehouse.fact_transactions",
        "date_column": "transaction_date",
        "metrics": {
            "amount": "amount",
            "fee_amount": "fee_amount",
        },
    },
    "complaints": {
        "label": "Complaints",
        "table": "warehouse.fact_complaints",
        "date_column": "complaint_date",
        "metrics": {
            "resolution_days": "resolution_days",
        },
    },
    "campaigns": {
        "label": "Campaigns",
        "table": "warehouse.fact_campaigns",
        "date_column": "sent_date",
        "metrics": {
            "converted_count": "converted_count",
            "engaged_count": "engaged_count",
            "campaign_sent_count": "campaign_sent_count",
        },
    },
    "sla_tickets": {
        "label": "SLA Tickets",
        "table": "warehouse.fact_sla_tickets",
        "date_column": "created_datetime",
        "metrics": {
            "sla_target_hours": "sla_target_hours",
        },
    },
    "customers": {
        "label": "Customers",
        "table": "warehouse.dim_customer",
        "date_column": "onboarding_date",
        "metrics": {
            "customer_age": "customer_age",
        },
    },
    "accounts": {
        "label": "Accounts",
        "table": "warehouse.dim_account",
        "date_column": "account_open_date",
        "metrics": {
            "current_balance": "current_balance",
            "credit_limit": "credit_limit",
            "interest_rate": "interest_rate",
        },
    },
    "products": {
        "label": "Products",
        "table": "warehouse.dim_product",
        "date_column": None,
        "metrics": {},
    },
    "branches": {
        "label": "Branches",
        "table": "warehouse.dim_branch",
        "date_column": None,
        "metrics": {},
    },
    "channels": {
        "label": "Channels",
        "table": "warehouse.dim_channel",
        "date_column": None,
        "metrics": {},
    },
}


def get_basic_aggregate(
    operation: str,
    entity: str,
    metric: str | None = None,
    months: list[int] | None = None,
    year: int = 2026,
    group_by_month: bool = False,
) -> dict[str, Any]:
    """Run COUNT/SUM/AVG only against approved entities and measures."""

    operation = operation.lower().strip()
    entity = entity.lower().strip()

    if operation not in {"count", "sum", "average"}:
        raise ValueError(f"Unsupported aggregate operation: {operation}")
    if entity not in APPROVED_AGGREGATES:
        raise ValueError(f"Unsupported aggregate entity: {entity}")

    config = APPROVED_AGGREGATES[entity]
    table = config["table"]
    date_column = config["date_column"]
    metric_map = config["metrics"]

    if operation == "count":
        aggregate_sql = "COUNT(*)"
        metric_label = "record count"
    else:
        if not metric or metric not in metric_map:
            approved = ", ".join(sorted(metric_map)) or "none"
            raise ValueError(
                f"{operation} for {entity} requires an approved metric. Approved metrics: {approved}"
            )
        column = metric_map[metric]
        sql_function = "SUM" if operation == "sum" else "AVG"
        aggregate_sql = f"{sql_function}({column})"
        metric_label = metric

    requested_months = sorted(set(months or []))
    params: list[Any] = []
    filters: list[str] = []

    if requested_months:
        if not date_column:
            raise ValueError(f"{config['label']} does not have an approved business date for monthly filtering.")
        placeholders = ", ".join(["%s"] * len(requested_months))
        filters.append(f"EXTRACT(YEAR FROM {date_column}) = %s")
        params.append(year)
        filters.append(f"EXTRACT(MONTH FROM {date_column}) IN ({placeholders})")
        params.extend(requested_months)
    elif group_by_month:
        if not date_column:
            raise ValueError(f"{config['label']} does not have an approved business date for monthly grouping.")
        filters.append(f"EXTRACT(YEAR FROM {date_column}) = %s")
        params.append(year)

    where_clause = ""
    if filters:
        where_clause = "WHERE " + " AND ".join(filters)

    if group_by_month or requested_months:
        if not date_column:
            raise ValueError(f"{config['label']} does not support monthly aggregation.")
        sql = f"""
SELECT
    EXTRACT(YEAR FROM {date_column})::INT AS year,
    EXTRACT(MONTH FROM {date_column})::INT AS month,
    ROUND(({aggregate_sql})::NUMERIC, 2) AS value
FROM {table}
{where_clause}
GROUP BY 1, 2
ORDER BY 1, 2;
""".strip()
        rows = execute_query(sql, tuple(params))
        return {
            "tool": "get_basic_aggregate",
            "operation": operation,
            "entity": entity,
            "entity_label": config["label"],
            "metric": metric,
            "metric_label": metric_label,
            "grouping": "month",
            "year": year,
            "requested_months": requested_months,
            "rows": rows,
            "source": table,
            "sql_validation": "PASSED",
        }

    sql = f"""
SELECT ROUND(({aggregate_sql})::NUMERIC, 2) AS value
FROM {table};
""".strip()
    rows = execute_query(sql)
    value = rows[0].get("value") if rows else None
    return {
        "tool": "get_basic_aggregate",
        "operation": operation,
        "entity": entity,
        "entity_label": config["label"],
        "metric": metric,
        "metric_label": metric_label,
        "grouping": "total",
        "value": value,
        "source": table,
        "sql_validation": "PASSED",
    }
