from pathlib import Path

import pandas as pd


EXPECTED_ROW_COUNT = 25_000

PROJECT_DIR = Path(__file__).resolve().parents[2]
RAW_DATA_DIR = PROJECT_DIR / "data" / "raw"

ACCOUNTS_FILE = RAW_DATA_DIR / "raw_accounts.csv"
CHANNELS_FILE = RAW_DATA_DIR / "raw_channels.csv"
TRANSACTIONS_FILE = RAW_DATA_DIR / "raw_transactions_jan.csv"

VALID_TRANSACTION_TYPES = {
    "Deposit",
    "Withdrawal",
    "Transfer",
    "Bill Payment",
    "Card Payment",
    "UPI Payment",
    "ATM Withdrawal",
    "Fee Debit",
    "Interest Credit",
    "Loan EMI",
}

VALID_TRANSACTION_STATUSES = {"Success", "Failed", "Reversed"}


def validate_transactions() -> None:
    accounts = pd.read_csv(ACCOUNTS_FILE)
    channels = pd.read_csv(CHANNELS_FILE)
    transactions = pd.read_csv(TRANSACTIONS_FILE)

    transactions["transaction_datetime"] = pd.to_datetime(transactions["transaction_datetime"])

    transactions_with_accounts = transactions.merge(
        accounts[
            [
                "account_id",
                "customer_id",
                "product_id",
                "branch_id",
            ]
        ],
        on="account_id",
        how="left",
        suffixes=("", "_account"),
    )

    checks = {
        "row_count_is_25000": len(transactions) == EXPECTED_ROW_COUNT,
        "transaction_id_is_unique": transactions["transaction_id"].is_unique,
        "transaction_id_has_no_nulls": transactions["transaction_id"].notna().all(),
        "account_id_has_no_nulls": transactions["account_id"].notna().all(),
        "customer_id_has_no_nulls": transactions["customer_id"].notna().all(),
        "all_transaction_accounts_exist": transactions["account_id"].isin(accounts["account_id"]).all(),
        "all_transaction_channels_exist": transactions["channel_id"].isin(channels["channel_id"]).all(),
        "transaction_types_are_valid": set(transactions["transaction_type"]).issubset(VALID_TRANSACTION_TYPES),
        "transaction_statuses_are_valid": set(transactions["transaction_status"]).issubset(VALID_TRANSACTION_STATUSES),
        "all_transactions_are_in_january_2026": (
            (transactions["transaction_datetime"].dt.date >= pd.to_datetime("2026-01-01").date())
            & (transactions["transaction_datetime"].dt.date <= pd.to_datetime("2026-01-31").date())
        ).all(),
        "amount_is_positive": (transactions["amount"] > 0).all(),
        "fee_amount_is_non_negative": (transactions["fee_amount"] >= 0).all(),
        "balance_after_transaction_is_non_negative": (transactions["balance_after_transaction"] >= 0).all(),
        "failed_transactions_have_zero_fee": (
            transactions.loc[transactions["transaction_status"] == "Failed", "fee_amount"] == 0
        ).all(),
        "transaction_customer_matches_account_customer": (
            transactions_with_accounts["customer_id"] == transactions_with_accounts["customer_id_account"]
        ).all(),
        "transaction_product_matches_account_product": (
            transactions_with_accounts["product_id"] == transactions_with_accounts["product_id_account"]
        ).all(),
        "transaction_branch_matches_account_branch": (
            transactions_with_accounts["branch_id"] == transactions_with_accounts["branch_id_account"]
        ).all(),
    }

    print("January transaction validation results:")
    for check_name, passed in checks.items():
        status = "PASSED" if passed else "FAILED"
        print(f"{check_name}: {status}")

    failed_checks = [check_name for check_name, passed in checks.items() if not passed]

    if failed_checks:
        raise ValueError(f"January transaction validation failed: {failed_checks}")

    print("\nAll January transaction validation checks passed.")
    print(f"Validated file: {TRANSACTIONS_FILE}")
    print(f"Total rows: {len(transactions):,}")
    print(f"Unique accounts with transactions: {transactions['account_id'].nunique():,}")


if __name__ == "__main__":
    validate_transactions()