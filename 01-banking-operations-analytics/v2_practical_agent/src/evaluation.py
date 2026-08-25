import math
import sys
from typing import Callable

try:
    from .agent import classify_question, run_agent
    from .db_tools import get_dq_summary, get_kpi_metric, validate_readonly_sql
    from .retriever import retrieve_chunks
except ImportError:
    from agent import classify_question, run_agent
    from db_tools import get_dq_summary, get_kpi_metric, validate_readonly_sql
    from retriever import retrieve_chunks


ROUTING_CASES = [
    ("What is Transaction Failure Rate?", "knowledge_question", "none"),
    ("What was Mobile Banking failure rate in March 2026?", "operational_metric", "get_kpi_metric"),
    ("Compare February and March Mobile Banking failure rate.", "comparison", "compare_kpi"),
    ("Was March concerning for transaction failures in Mobile Banking?", "mixed_analysis", "compare_kpi"),
    (
        "Was March concerning for transaction failures compared to January and February?",
        "mixed_analysis",
        "compare_kpi_periods",
    ),
    (
        "Compare transaction failure rate in January, March, April and June.",
        "comparison",
        "compare_kpi_periods",
    ),
    (
        "Compare transaction failure rate in January, February, March, April, May and June.",
        "comparison",
        "compare_kpi_periods",
    ),
    (
        "Compare January, March and June campaign success data.",
        "comparison",
        "compare_kpi_periods",
    ),
    (
        "Compare January, March and June campaign data.",
        "unknown",
        "none",
    ),
    ("How many transaction entries do we have each month?", "basic_aggregate", "get_basic_aggregate"),
    ("How many complaint entries do we have each month?", "basic_aggregate", "get_basic_aggregate"),
    ("How many campaign records do we have each month?", "basic_aggregate", "get_basic_aggregate"),
    ("How many customers do we have?", "basic_aggregate", "get_basic_aggregate"),
    ("What is the average transaction amount each month?", "basic_aggregate", "get_basic_aggregate"),
    ("What is the total account balance?", "basic_aggregate", "get_basic_aggregate"),
    (
        "What is the average number of transactions per user per month?",
        "derived_metric",
        "get_derived_metric",
    ),
    ("How many employee records do we have?", "unknown", "none"),
    ("Show the data quality exception summary.", "dq_investigation", "get_dq_summary"),
    ("DELETE FROM warehouse.fact_transactions", "unsafe_request", "none"),
]

RETRIEVAL_CASES = [
    ("What is Transaction Failure Rate?", "kpi_definitions.md", "Transaction Failure Rate"),
    ("How do we handle duplicate transactions?", "business_rules.md", "Duplicate Transaction Rule"),
    ("Where is channel_id stored?", "data_dictionary.md", "warehouse.dim_channel"),
]

EXPECTED_DB = {
    "feb_mobile_failure_rate": 19.52,
    "mar_mobile_failure_rate": 9.26,
    "transaction_monthly_counts": [25000, 28000, 30000, 32000, 35000, 38000],
    "complaint_monthly_counts": [900, 1250, 1050, 1650, 1300, 1350],
    "campaign_monthly_counts": [2200, 2400, 2600, 2800, 3000, 3400],
    "customer_total_count": 10000,
    "dq_counts": {
        "DUPLICATE_TRANSACTION_ID": 15,
        "FAILED_TRANSACTION_WITH_FEE": 40,
        "MISSING_CHANNEL_ID": 20,
        "HIGH_VALUE_TRANSACTION": 309,
    },
}


MULTI_PERIOD_ROUTING_CASES = [
    (
        "Was March concerning for transaction failures compared to January and February?",
        [1, 2, 3],
    ),
    (
        "Compare transaction failure rate in January, March, April and June.",
        [1, 3, 4, 6],
    ),
    (
        "Compare transaction failure rate in January, February, March, April, May and June.",
        [1, 2, 3, 4, 5, 6],
    ),
]

MULTI_PERIOD_END_TO_END_QUESTION = (
    "Compare transaction failure rate in January, February, March, April, May and June."
)

CAMPAIGN_SUCCESS_QUESTION = "Compare January, March and June campaign success data."
AMBIGUOUS_CAMPAIGN_QUESTION = "Compare January, March and June campaign data."
DERIVED_METRIC_QUESTION = "What is the average number of transactions per user per month?"

AGGREGATE_CASES = {
    "transactions": "How many transaction entries do we have each month?",
    "complaints": "How many complaint entries do we have each month?",
    "campaigns": "How many campaign records do we have each month?",
    "customers": "How many customers do we have?",
}

UNSUPPORTED_AGGREGATE_QUESTION = "How many employee records do we have?"


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

    for question, expected_months in MULTI_PERIOD_ROUTING_CASES:
        result = classify_question(question)
        assert result["tool_name"] == "compare_kpi_periods", (
            f"{question!r}: expected compare_kpi_periods, got {result['tool_name']}"
        )
        assert result["tool_args"].get("months") == expected_months, (
            f"{question!r}: expected months {expected_months}, "
            f"got {result['tool_args'].get('months')}"
        )

    campaign_success = classify_question(CAMPAIGN_SUCCESS_QUESTION)
    assert campaign_success["tool_args"].get("kpi") == "campaign_conversion_rate", (
        "campaign success should map to the approved Campaign Conversion Rate KPI"
    )
    assert campaign_success["tool_args"].get("months") == [1, 3, 6], (
        "campaign success comparison must preserve January, March and June"
    )

    ambiguous = run_agent(AMBIGUOUS_CAMPAIGN_QUESTION)
    assert ambiguous.get("intent") == "unknown", (
        f"generic campaign data should remain ambiguous, got {ambiguous.get('intent')!r}"
    )
    assert ambiguous.get("validation_status") == "ABSTAINED", (
        "generic campaign data should abstain instead of assuming a KPI"
    )

    average_amount = classify_question("What is the average transaction amount each month?")
    assert average_amount["tool_args"].get("operation") == "average"
    assert average_amount["tool_args"].get("entity") == "transactions"
    assert average_amount["tool_args"].get("metric") == "amount"
    assert average_amount["tool_args"].get("group_by_month") is True

    total_balance = classify_question("What is the total account balance?")
    assert total_balance["tool_args"].get("operation") == "sum"
    assert total_balance["tool_args"].get("entity") == "accounts"
    assert total_balance["tool_args"].get("metric") == "current_balance"

    derived = classify_question(DERIVED_METRIC_QUESTION)
    assert derived.get("intent") == "derived_metric"
    assert derived.get("tool_name") == "get_derived_metric"
    assert derived.get("tool_args", {}).get("metric") == "average_transactions_per_active_customer"

    customer_synonym = classify_question("What is the average number of transactions per customer per month?")
    assert customer_synonym.get("intent") == "derived_metric"
    assert customer_synonym.get("tool_args", {}).get("metric") == "average_transactions_per_active_customer"

    unsupported = run_agent(UNSUPPORTED_AGGREGATE_QUESTION)
    assert unsupported.get("intent") == "unknown"
    assert unsupported.get("validation_status") == "ABSTAINED"
    assert unsupported.get("evidence_status") == "INSUFFICIENT"


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


def check_run_id() -> None:
    first = run_agent("What is Transaction Failure Rate?")
    second = run_agent("What is Transaction Failure Rate?")

    assert first.get("run_id"), "run_id was not set on the agent state"
    assert isinstance(first["run_id"], str) and first["run_id"]
    assert first["run_id"] != second["run_id"], "each agent run must receive a unique run_id"
    assert any(f"run_id={first['run_id']}" in event for event in first.get("trace", [])), (
        "run_id should be traceable in the run's trace events"
    )


def check_knowledge_route_validation() -> None:
    found = run_agent("What is Transaction Failure Rate?")
    assert found.get("validation_status") == "PASSED"
    assert found.get("evidence_status") == "SUFFICIENT"

    missing = run_agent("What does the flurbnaxion ratio mean for zzqqxx metric?")
    assert missing.get("intent") == "knowledge_question"
    assert not missing.get("retrieved_context")
    assert missing.get("evidence_status") == "INSUFFICIENT"
    assert "could not find" in missing.get("final_answer", "").lower()


def _monthly_values(result: dict) -> list[int]:
    rows = result.get("tool_result", {}).get("rows", [])
    return [int(round(float(row["value"]))) for row in rows]


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

    multi = run_agent(MULTI_PERIOD_END_TO_END_QUESTION)
    assert multi.get("intent") == "comparison"
    assert multi.get("tool_name") == "compare_kpi_periods"
    assert multi.get("validation_status") == "PASSED"
    assert multi.get("evidence_status") == "SUFFICIENT"

    periods = multi.get("tool_result", {}).get("periods", [])
    starts = [period.get("period_start") for period in periods]
    expected_starts = [
        "2026-01-01",
        "2026-02-01",
        "2026-03-01",
        "2026-04-01",
        "2026-05-01",
        "2026-06-01",
    ]
    assert starts == expected_starts, f"expected Jan-Jun evidence, got {starts}"
    assert all(period.get("metric_value") is not None for period in periods)
    assert all(period_start in multi.get("final_answer", "") for period_start in expected_starts)

    transaction_counts = run_agent(AGGREGATE_CASES["transactions"])
    assert transaction_counts.get("intent") == "basic_aggregate"
    assert transaction_counts.get("validation_status") == "PASSED"
    assert _monthly_values(transaction_counts) == EXPECTED_DB["transaction_monthly_counts"], (
        f"transaction monthly counts differ: {_monthly_values(transaction_counts)}"
    )

    complaint_counts = run_agent(AGGREGATE_CASES["complaints"])
    assert complaint_counts.get("validation_status") == "PASSED"
    assert _monthly_values(complaint_counts) == EXPECTED_DB["complaint_monthly_counts"], (
        f"complaint monthly counts differ: {_monthly_values(complaint_counts)}"
    )

    campaign_counts = run_agent(AGGREGATE_CASES["campaigns"])
    assert campaign_counts.get("validation_status") == "PASSED"
    assert _monthly_values(campaign_counts) == EXPECTED_DB["campaign_monthly_counts"], (
        f"campaign monthly counts differ: {_monthly_values(campaign_counts)}"
    )

    customer_count = run_agent(AGGREGATE_CASES["customers"])
    assert customer_count.get("validation_status") == "PASSED"
    actual_customer_count = int(round(float(customer_count.get("tool_result", {}).get("value"))))
    assert actual_customer_count == EXPECTED_DB["customer_total_count"], (
        f"customer total expected {EXPECTED_DB['customer_total_count']}, got {actual_customer_count}"
    )

    derived = run_agent(DERIVED_METRIC_QUESTION)
    assert derived.get("intent") == "derived_metric"
    assert derived.get("tool_name") == "get_derived_metric"
    assert derived.get("validation_status") == "PASSED"
    assert derived.get("evidence_status") == "SUFFICIENT"

    derived_result = derived.get("tool_result", {})
    derived_rows = derived_result.get("rows", [])
    assert len(derived_rows) == 6, f"expected Jan-Jun derived metric rows, got {len(derived_rows)}"
    assert [int(row["metric_numerator"]) for row in derived_rows] == EXPECTED_DB["transaction_monthly_counts"], (
        "derived metric numerator must reconcile to trusted monthly transaction counts"
    )
    for row in derived_rows:
        numerator = float(row["metric_numerator"])
        denominator = float(row["metric_denominator"])
        metric_value = float(row["metric_value"])
        assert denominator > 0, "active-customer denominator must be positive"
        assert denominator <= EXPECTED_DB["customer_total_count"], (
            "active customers cannot exceed the total customer base"
        )
        assert math.isclose(metric_value, round(numerator / denominator, 2), abs_tol=0.01), (
            f"derived metric formula mismatch for month {row['month']}"
        )

    # Evidence-based interpretation is also deterministic and testable. It must
    # describe the observed movement and supporting numerator/denominator evidence
    # without inventing a business threshold or root cause.
    analysis = derived_result.get("analysis", {})
    assert analysis, "derived metric should include deterministic evidence analysis"
    assert analysis.get("overall_direction") == "increased", (
        f"expected overall increase, got {analysis.get('overall_direction')!r}"
    )
    assert analysis.get("trend_pattern") == "increased in every observed period", (
        f"unexpected trend pattern: {analysis.get('trend_pattern')!r}"
    )
    assert math.isclose(float(analysis.get("metric_change_percent")), 43.38, abs_tol=0.05), (
        f"metric change percent expected ~43.38, got {analysis.get('metric_change_percent')}"
    )
    assert math.isclose(float(analysis.get("numerator_change_percent")), 52.00, abs_tol=0.05), (
        f"transaction-volume growth expected 52.00, got {analysis.get('numerator_change_percent')}"
    )
    assert math.isclose(float(analysis.get("denominator_change_percent")), 5.89, abs_tol=0.05), (
        f"active-customer growth expected ~5.89, got {analysis.get('denominator_change_percent')}"
    )
    assert analysis.get("relative_growth_pattern") == (
        "transaction volume grew faster than the active-customer base"
    )

    answer = derived.get("final_answer", "").lower()
    assert "evidence-based analysis" in answer, "final answer should include evidence-based analysis"
    assert "transaction volume" in answer and "active customers" in answer, (
        "final answer should cite numerator and denominator movement"
    )
    assert "no approved target or threshold" in answer, (
        "final answer should preserve the interpretation boundary"
    )


def main() -> None:
    print("=== Banking Operations Agent V2 Evaluation ===")

    results = [
        run_check("routing golden cases", check_routing),
        run_check("RAG retrieval golden cases", check_retrieval),
        run_check("read-only SQL guard", check_sql_guard),
        run_check("run_id request correlation", check_run_id),
        run_check("knowledge-route evidence validation", check_knowledge_route_validation),
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
