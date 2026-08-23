import sys
from typing import Callable

try:
    from .agent import classify_question, run_agent
    from .dq_tools import (
        check_duplicate_transactions,
        check_failed_transaction_fees,
        check_high_value_transactions,
        check_missing_channels,
        check_row_reconciliation,
        validate_readonly_sql,
        validate_warehouse_readiness,
    )
    from .knowledge import retrieve_rules
except ImportError:
    from agent import classify_question, run_agent
    from dq_tools import (
        check_duplicate_transactions,
        check_failed_transaction_fees,
        check_high_value_transactions,
        check_missing_channels,
        check_row_reconciliation,
        validate_readonly_sql,
        validate_warehouse_readiness,
    )
    from knowledge import retrieve_rules


ROUTING_CASES = [
    ("Validate the current transaction load.", "full_validation", 5),
    ("Are there duplicate transaction IDs?", "duplicate_check", 1),
    ("Are failed transactions carrying fees?", "failed_fee_check", 1),
    ("Are any channel IDs missing?", "missing_channel_check", 1),
    ("Should high-value transactions be removed?", "high_value_check", 1),
    ("Why do raw and warehouse row counts differ?", "reconciliation_check", 1),
    ("Is the warehouse ready for KPI reporting?", "warehouse_readiness", 5),
    ("DELETE FROM warehouse.fact_transactions", "unsafe_request", 0),
]

EXPECTED = {
    "raw_rows": 188015,
    "unique_ids": 188000,
    "staging_rows": 188000,
    "warehouse_rows": 188000,
    "duplicate_rows": 15,
    "failed_with_fee": 40,
    "missing_channel": 20,
    "high_value": 309,
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
    for question, expected_intent, expected_count in ROUTING_CASES:
        result = classify_question(question)
        assert result["intent"] == expected_intent, (
            f"{question!r}: expected {expected_intent}, got {result['intent']}"
        )
        assert len(result["checks_requested"]) == expected_count, (
            f"{question!r}: expected {expected_count} checks, got {len(result['checks_requested'])}"
        )


def check_shared_knowledge() -> None:
    duplicate = retrieve_rules(["duplicate_transactions"])
    missing = retrieve_rules(["missing_channels"])
    reconciliation = retrieve_rules(["row_reconciliation"])

    assert duplicate and duplicate[0]["section"] == "Duplicate Transaction Rule"
    assert duplicate[0]["source"] == "v2_practical_agent/knowledge/business_rules.md"
    assert missing and missing[0]["section"] == "Missing Channel Rule"
    assert reconciliation and reconciliation[0]["section"] == "Jan-Jun 2026 Transaction Reconciliation"


def check_sql_guard() -> None:
    good, _ = validate_readonly_sql("SELECT 1;")
    bad_delete, _ = validate_readonly_sql("DELETE FROM warehouse.fact_transactions;")
    bad_update, _ = validate_readonly_sql("UPDATE warehouse.fact_transactions SET fee_amount = 0;")

    assert good is True
    assert bad_delete is False
    assert bad_update is False


def check_database_controls() -> None:
    recon = check_row_reconciliation()["evidence"]
    assert recon["raw_rows"] == EXPECTED["raw_rows"]
    assert recon["unique_transaction_ids"] == EXPECTED["unique_ids"]
    assert recon["staging_rows"] == EXPECTED["staging_rows"]
    assert recon["warehouse_rows"] == EXPECTED["warehouse_rows"]

    duplicate = check_duplicate_transactions()
    assert duplicate["status"] == "PASS"
    assert duplicate["evidence"]["raw_duplicate_rows"] == EXPECTED["duplicate_rows"]
    assert duplicate["evidence"]["warehouse_duplicate_transaction_ids"] == 0

    failed_fee = check_failed_transaction_fees()
    assert failed_fee["status"] == "PASS"
    assert failed_fee["evidence"]["raw_failed_with_fee"] == EXPECTED["failed_with_fee"]
    assert failed_fee["evidence"]["warehouse_failed_with_fee"] == 0

    missing = check_missing_channels()
    assert missing["status"] == "REVIEW"
    assert missing["evidence"]["raw_missing_channel"] == EXPECTED["missing_channel"]

    high_value = check_high_value_transactions()
    assert high_value["status"] == "REVIEW"
    assert high_value["evidence"]["raw_high_value"] == EXPECTED["high_value"]

    readiness = validate_warehouse_readiness()
    assert readiness["status"] == "READY_WITH_KNOWN_EXCEPTIONS", readiness["status"]
    assert readiness["blocking_failures"] == []


def check_end_to_end() -> None:
    result = run_agent("Validate the current transaction load.")
    assert result["intent"] == "full_validation"
    assert result["validation_status"] == "PASSED_WITH_REVIEW"
    assert result["evidence_status"] == "SUFFICIENT"
    assert "READY_WITH_KNOWN_EXCEPTIONS" in result["final_answer"]
    assert any("[TOOLS]" in event for event in result["trace"])
    assert any("[VALIDATION]" in event for event in result["trace"])


def main() -> None:
    print("=== Banking Data Quality & Validation Agent Evaluation ===")

    results = [
        run_check("routing golden cases", check_routing),
        run_check("shared-rule knowledge consistency", check_shared_knowledge),
        run_check("read-only SQL guard", check_sql_guard),
        run_check("PostgreSQL DQ reconciliation controls", check_database_controls),
        run_check("end-to-end warehouse readiness flow", check_end_to_end),
    ]

    print("\n=== Summary ===")
    passed = sum(results)
    total = len(results)
    print(f"Passed {passed}/{total} evaluation groups")

    if not all(results):
        print(
            "If only PostgreSQL-dependent groups failed, configure .env with the same local "
            "banking_analytics_db credentials used by the Banking Investigation Agent and rerun."
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
