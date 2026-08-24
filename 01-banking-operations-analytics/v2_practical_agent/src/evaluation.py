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

    # Multi-period routing must preserve every explicitly requested month, whether
    # the user names three, four, six, or another supported count within Jan-Jun 2026.
    for question, expected_months in MULTI_PERIOD_ROUTING_CASES:
        result = classify_question(question)
        assert result["tool_name"] == "compare_kpi_periods", (
            f"{question!r}: expected compare_kpi_periods, got {result['tool_name']}"
        )
        assert result["tool_args"].get("months") == expected_months, (
            f"{question!r}: expected months {expected_months}, "
            f"got {result['tool_args'].get('months')}"
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


def check_run_id() -> None:
    first = run_agent("What is Transaction Failure Rate?")
    second = run_agent("What is Transaction Failure Rate?")

    assert first.get("run_id"), "run_id was not set on the agent state"
    assert isinstance(first["run_id"], str) and first["run_id"], (
        "run_id must be a non-empty string"
    )
    assert first["run_id"] != second["run_id"], (
        "each agent run must receive a unique run_id"
    )
    assert any(f"run_id={first['run_id']}" in event for event in first.get("trace", [])), (
        "run_id should be traceable in the run's trace events"
    )


def check_knowledge_route_validation() -> None:
    # An approved chunk exists: validation must be explicit, not left empty.
    found = run_agent("What is Transaction Failure Rate?")
    assert found.get("validation_status") == "PASSED", (
        f"expected PASSED when an approved chunk is retrieved, got {found.get('validation_status')!r}"
    )
    assert found.get("evidence_status") == "SUFFICIENT", (
        f"expected SUFFICIENT evidence when an approved chunk is retrieved, got {found.get('evidence_status')!r}"
    )

    # No approved chunk matches: the agent must abstain rather than invent an answer.
    missing = run_agent("What does the flurbnaxion ratio mean for zzqqxx metric?")
    assert missing.get("intent") == "knowledge_question", (
        f"expected a knowledge_question route for this case, got {missing.get('intent')!r}"
    )
    assert not missing.get("retrieved_context"), (
        "test question was expected to retrieve no approved chunk"
    )
    assert missing.get("evidence_status") == "INSUFFICIENT", (
        f"expected INSUFFICIENT evidence when no approved chunk matches, got {missing.get('evidence_status')!r}"
    )
    assert "could not find" in missing.get("final_answer", "").lower(), (
        "agent should abstain rather than invent a definition when no approved chunk is found"
    )


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

    # End-to-end regression: the multi-period tool must return every explicitly
    # requested month. Testing all Jan-Jun months proves the path is not hard-coded
    # to the original three-month defect case.
    multi = run_agent(MULTI_PERIOD_END_TO_END_QUESTION)
    assert multi.get("intent") == "comparison", (
        f"expected comparison, got {multi.get('intent')!r}"
    )
    assert multi.get("tool_name") == "compare_kpi_periods", (
        f"expected compare_kpi_periods, got {multi.get('tool_name')!r}"
    )
    assert multi.get("validation_status") == "PASSED", (
        f"multi-period evidence should validate, got {multi.get('validation_status')!r}"
    )
    assert multi.get("evidence_status") == "SUFFICIENT", (
        f"multi-period evidence should be sufficient, got {multi.get('evidence_status')!r}"
    )

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
    assert starts == expected_starts, (
        f"expected Jan-Jun evidence, got {starts}"
    )
    assert all(period.get("metric_value") is not None for period in periods), (
        "each requested comparison period must contain a KPI value"
    )
    assert all(period_start in multi.get("final_answer", "") for period_start in expected_starts), (
        "final answer must include every requested period"
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
