from pathlib import Path
from typing import Any


BANKING_ROOT = Path(__file__).resolve().parents[2]
SHARED_BUSINESS_RULES = BANKING_ROOT / "v2_practical_agent" / "knowledge" / "business_rules.md"
STAGING_NOTES = BANKING_ROOT / "docs" / "8_staging_layer_notes.md"


CHECK_TO_KNOWLEDGE = {
    "row_reconciliation": (STAGING_NOTES, "Jan-Jun 2026 Transaction Reconciliation"),
    "duplicate_transactions": (SHARED_BUSINESS_RULES, "Duplicate Transaction Rule"),
    "failed_transaction_fees": (SHARED_BUSINESS_RULES, "Failed Transaction Fee Rule"),
    "missing_channels": (SHARED_BUSINESS_RULES, "Missing Channel Rule"),
    "high_value_transactions": (SHARED_BUSINESS_RULES, "High-Value Transaction Rule"),
}


def load_h2_sections(file_path: Path) -> dict[str, str]:
    """Load H2 Markdown sections so both agents can share governed rule files."""

    text = file_path.read_text(encoding="utf-8")
    sections: dict[str, str] = {}
    current_title: str | None = None
    current_lines: list[str] = []

    for line in text.splitlines():
        if line.startswith("## "):
            if current_title is not None:
                sections[current_title] = "\n".join(current_lines).strip()
            current_title = line[3:].strip()
            current_lines = [line]
        elif current_title is not None:
            current_lines.append(line)

    if current_title is not None:
        sections[current_title] = "\n".join(current_lines).strip()

    return sections


def verify_rule_coverage(
    check_names: list[str], retrieved_rules: list[dict[str, Any]]
) -> dict[str, Any]:
    """Confirm every requested check has a corresponding approved rule.

    ``retrieve_rules`` silently skips a check when it has no entry in
    ``CHECK_TO_KNOWLEDGE`` or when its section text cannot be found in the
    shared Markdown file. That silence is fine for retrieval, but the
    workflow must not go on to present a "governed" validation result built
    on a rule that was never actually found. This is the explicit control
    that catches that gap before synthesis happens.
    """

    covered_checks = {item["check"] for item in retrieved_rules}
    missing_checks = [name for name in check_names if name not in covered_checks]

    return {
        "status": "SUFFICIENT" if not missing_checks else "INSUFFICIENT",
        "missing_checks": missing_checks,
    }


def retrieve_rules(check_names: list[str]) -> list[dict[str, Any]]:
    """Return the exact shared rule sections required by selected DQ checks."""

    retrieved: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()

    for check_name in check_names:
        source_info = CHECK_TO_KNOWLEDGE.get(check_name)
        if not source_info:
            continue

        file_path, section_name = source_info
        key = (file_path.name, section_name)
        if key in seen:
            continue

        sections = load_h2_sections(file_path)
        content = sections.get(section_name)
        if not content:
            continue

        retrieved.append(
            {
                "check": check_name,
                "source": str(file_path.relative_to(BANKING_ROOT)).replace("\\", "/"),
                "section": section_name,
                "content": content,
            }
        )
        seen.add(key)

    return retrieved
