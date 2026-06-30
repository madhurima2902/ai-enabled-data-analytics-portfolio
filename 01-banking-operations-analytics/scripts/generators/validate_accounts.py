from pathlib import Path

import pandas as pd


EXPECTED_ROW_COUNT = 15_000

ALLOWED_PRODUCT_IDS = {
    "PROD001",
    "PROD002",
    "PROD003",
    "PROD004",
    "PROD005",
    "PROD006",
    "PROD007",
}

ALLOWED_BRANCH_IDS = {f"BR{i:03d}" for i in range(1, 21)}
ALLOWED_ACCOUNT_STATUSES = {"Active", "Dormant", "Closed"}


PROJECT_DIR = Path(__file__).resolve().parents[2]
RAW_DATA_DIR = PROJECT_DIR / "data" / "raw"

CUSTOMERS_FILE = RAW_DATA_DIR / "raw_customers.csv"
ACCOUNTS_FILE = RAW_DATA_DIR / "raw_accounts.csv"


def validate_accounts() -> None:
    customers = pd.read_csv(CUSTOMERS_FILE)
    accounts = pd.read_csv(ACCOUNTS_FILE)

    customers["onboarding_date"] = pd.to_datetime(customers["onboarding_date"])
    accounts["account_open_date"] = pd.to_datetime(accounts["account_open_date"])

    merged = accounts.merge(
        customers[["customer_id", "onboarding_date"]],
        on="customer_id",
        how="left",
    )

    checks = {
        "row_count_is_15000": len(accounts) == EXPECTED_ROW_COUNT,
        "account_id_is_unique": accounts["account_id"].is_unique,
        "account_id_has_no_nulls": accounts["account_id"].notna().all(),
        "customer_id_has_no_nulls": accounts["customer_id"].notna().all(),
        "all_account_customers_exist": accounts["customer_id"].isin(customers["customer_id"]).all(),
        "product_ids_are_valid": set(accounts["product_id"]).issubset(ALLOWED_PRODUCT_IDS),
        "branch_ids_are_valid": set(accounts["branch_id"]).issubset(ALLOWED_BRANCH_IDS),
        "account_status_values_are_valid": set(accounts["account_status"]).issubset(ALLOWED_ACCOUNT_STATUSES),
        "current_balance_is_non_negative": (accounts["current_balance"] >= 0).all(),
        "interest_rate_is_non_negative": (accounts["interest_rate"] >= 0).all(),
        "account_open_date_not_before_onboarding": (
            merged["account_open_date"] >= merged["onboarding_date"]
        ).all(),
    }

    print("Account validation results:")
    for check_name, passed in checks.items():
        status = "PASSED" if passed else "FAILED"
        print(f"{check_name}: {status}")

    failed_checks = [check_name for check_name, passed in checks.items() if not passed]

    if failed_checks:
        raise ValueError(f"Account validation failed: {failed_checks}")

    print("\nAll account validation checks passed.")
    print(f"Validated file: {ACCOUNTS_FILE}")
    print(f"Total rows: {len(accounts):,}")
    print(f"Unique customers with accounts: {accounts['customer_id'].nunique():,}")


if __name__ == "__main__":
    validate_accounts()