import math
import sys
from typing import Callable

try:
    from .agent import classify_question
    from .db_tools import get_dq_summary, get_kpi_metric, validate_readonly_sql
    from .retriever import retrieve_chunks
except ImportError:
    from agent import classify_question
    from db_tools import get_dq_summary, get_kpi_metric, validate_readonly_sql
    from retriever import retrieve_chunks


ROUTING_CASES = [
    ("What is Transaction Failure Rate?", "knowledge_question", "none"),
    ("What was Mobile Banking failure rate in March 2026?", "operational_metric", "get_kpi_metric"),
    ("Compare February and March Mobile Banking failure rate.", "comparison", "compare_kpi"),
    ("Was March concerning for transaction failures in Mobile Banking?", "mixed_analysis", "compare_kpi"),
    ("Show the data quality exception summary.", "dq_investigation", "get_dq_summary"),
    ("DELETE FROM warehouse.fact_transactions", "unsafe_request", "none"),
]

RETRIEVAL_CASES = [
    ("What is Transaction Failure Rate?", "kpi_definitions.md", "Transaction Failure Rate"),
    ("How do we handle duplicate transactions?", "business_rules.md", "Duplicate Transaction Rule"),
    ("Where is channel_id stored?", "data_dictionary.md", "warehouse.dim_channel"),
]

# Validated Jan-Jun synthetic demo controls already established by the project.
EXPECTED_DB = {
    "feb_mobile_failure_rate": 19.52,
    "mar_mobile_failure_rate": 9.26,
    "dq_counts": {
        "DUPLICATE_TRANSACTION_ID": 15,
        "FAILED_TRANSACTION_WITH_FEE": 40,
        "MISSING_CHANNEL_ID": 20,
        "HIGH_VALUE_TRANSACTION": 309,
    },
}


def run_check(name: str, fn: Callable[[], None]) -> bool:
    try:
        fn()
    except AssertionError as exc:
        print(f"FAIL | {name} | {exc}")
        return False
    except Exception as exc:
        print(f"ERROR | {name} | {type(exc).__name__}: {exc}")
        return False

    print(f"PASS | {name}")
    return True


def check_routing() -> None:
    for question, expected_intent, expected_tool in ROUTING_CASES:
        result = classify_question(question)
        assert result["intent"] == expected_intent, (
            f"{question!r}: expected intent {expected_intent}, got {result['intent']}"
        )
        assert result["tool_name"] == expected_tool, (
            f"{question!r}: expected tool {expected_tool}, got {result['tool_name']}"
        )


def check_retrieval() -> None:
    for question, expected_source, expected_section in RETRIEVAL_CASES:
        results = retrieve_chunks(question, top_k=3)
        assert results, f"{question!r}: no chunks returned"
        top = results[0]
        assert top["source"] == expected_source, (
            f"{question!r}: expected source {expected_source}, got {top['source']}"
        )
        assert expected_section.lower() in str(top["section"]).lower(), (
            f"{question!r}: expected section containing {expected_section!r}, got {top['section']!r}"
        )


def check_sql_guard() -> None:
    good, _ = validate_readonly_sql("SELECT 1;")
    bad_delete, _ = validate_readonly_sql("DELETE FROM warehouse.fact_transactions;")
    bad_update, _ = validate_readonly_sql("UPDATE warehouse.fact_transactions SET fee_amount = 0;")

    assert good is True, "SELECT should pass"
    assert bad_delete is False, "DELETE should be blocked"
    assert bad_update is False, "UPDATE should be blocked"


def check_database_controls() -> None:
    feb = get_kpi_metric(
        "transaction_failure_rate",
        month=2,
        channel="Mobile Banking",
        year=2026,
    )
    mar = get_kpi_metric(
        "transaction_failure_rate",
        month=3,
        channel="Mobile Banking",
        year=2026,
    )

    assert math.isclose(
        float(feb["metric_value"]),
        EXPECTED_DB["feb_mobile_failure_rate"],
        abs_tol=0.02,
    ), f"February Mobile failure rate expected ~19.52, got {feb['metric_value']}"

    assert math.isclose(
        float(mar["metric_value"]),
        EXPECTED_DB["mar_mobile_failure_rate"],
        abs_tol=0.02,
    ), f"March Mobile failure rate expected ~9.26, got {mar['metric_value']}"

    dq = get_dq_summary()
    actual = {
        row["exception_type"]: int(row["exception_count"])
        for row in dq["exceptions"]
    }
    assert actual == EXPECTED_DB["dq_counts"], (
        f"DQ counts differ. expected={EXPECTED_DB['dq_counts']} actual={actual}"
    )


def main() -> None:
    print("=== Banking Operations Agent V2 Evaluation ===")

    results = [
        run_check("routing golden cases", check_routing),
        run_check("RAG retrieval golden cases", check_retrieval),
        run_check("read-only SQL guard", check_sql_guard),
    ]

    try:
        database_ok = run_check("PostgreSQL reconciliation controls", check_database_controls)
    except Exception as exc:
        database_ok = False
        print(f"ERROR | PostgreSQL reconciliation controls | {exc}")

    results.append(database_ok)

    print("\n=== Summary ===")
    passed = sum(results)
    total = len(results)
    print(f"Passed {passed}/{total} evaluation groups")

    if not all(results):
        print(
            "If only the PostgreSQL group failed because credentials are not configured, "
            "set up .env and rerun before the interview demo."
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
