from pathlib import Path
from datetime import date, datetime, time, timedelta

import numpy as np
import pandas as pd


TRANSACTION_COUNT = 25_000
RANDOM_SEED = 45

rng = np.random.default_rng(RANDOM_SEED)

PROJECT_DIR = Path(__file__).resolve().parents[2]
RAW_DATA_DIR = PROJECT_DIR / "data" / "raw"

ACCOUNTS_FILE = RAW_DATA_DIR / "raw_accounts.csv"
CHANNELS_FILE = RAW_DATA_DIR / "raw_channels.csv"
OUTPUT_FILE = RAW_DATA_DIR / "raw_transactions_jan.csv"

TRANSACTION_TYPES = [
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
]

TRANSACTION_STATUSES = ["Success", "Failed", "Reversed"]


def random_datetime_in_january() -> datetime:
    random_day = int(rng.integers(1, 32))
    random_hour = int(rng.integers(0, 24))
    random_minute = int(rng.integers(0, 60))
    random_second = int(rng.integers(0, 60))

    return datetime.combine(
        date(2026, 1, random_day),
        time(hour=random_hour, minute=random_minute, second=random_second),
    )


def generate_amount(transaction_type: str) -> float:
    if transaction_type in {"Deposit", "Transfer", "Bill Payment", "UPI Payment"}:
        return round(float(rng.uniform(100, 75_000)), 2)

    if transaction_type in {"Withdrawal", "ATM Withdrawal"}:
        return round(float(rng.uniform(100, 40_000)), 2)

    if transaction_type == "Card Payment":
        return round(float(rng.uniform(250, 150_000)), 2)

    if transaction_type == "Fee Debit":
        return round(float(rng.uniform(25, 1_500)), 2)

    if transaction_type == "Interest Credit":
        return round(float(rng.uniform(5, 5_000)), 2)

    if transaction_type == "Loan EMI":
        return round(float(rng.uniform(2_000, 150_000)), 2)

    return round(float(rng.uniform(100, 50_000)), 2)


def calculate_fee(transaction_type: str, transaction_status: str) -> float:
    if transaction_status != "Success":
        return 0.0

    if transaction_type in {"ATM Withdrawal", "Transfer", "Bill Payment"}:
        return round(float(rng.uniform(5, 50)), 2)

    if transaction_type == "Fee Debit":
        return 0.0

    return 0.0


def calculate_balance_after(base_balance: float, transaction_type: str, amount: float, fee_amount: float, status: str) -> float:
    if status != "Success":
        return round(float(base_balance), 2)

    credit_types = {"Deposit", "Interest Credit"}
    debit_types = {
        "Withdrawal",
        "Transfer",
        "Bill Payment",
        "Card Payment",
        "UPI Payment",
        "ATM Withdrawal",
        "Fee Debit",
        "Loan EMI",
    }

    if transaction_type in credit_types:
        return round(float(base_balance + amount), 2)

    if transaction_type in debit_types:
        return round(float(max(base_balance - amount - fee_amount, 0)), 2)

    return round(float(base_balance), 2)


def generate_transactions() -> pd.DataFrame:
    accounts = pd.read_csv(ACCOUNTS_FILE)
    channels = pd.read_csv(CHANNELS_FILE)

    channel_ids = channels["channel_id"].tolist()
    transactions = []

    for i in range(1, TRANSACTION_COUNT + 1):
        transaction_id = f"TXN202601{i:08d}"

        account = accounts.iloc[int(rng.integers(0, len(accounts)))]

        transaction_type = rng.choice(
            TRANSACTION_TYPES,
            p=[0.13, 0.11, 0.16, 0.12, 0.11, 0.16, 0.08, 0.03, 0.04, 0.06],
        )

        transaction_status = rng.choice(
            TRANSACTION_STATUSES,
            p=[0.92, 0.06, 0.02],
        )

        amount = generate_amount(transaction_type)
        fee_amount = calculate_fee(transaction_type, transaction_status)
        balance_after_transaction = calculate_balance_after(
            base_balance=float(account["current_balance"]),
            transaction_type=transaction_type,
            amount=amount,
            fee_amount=fee_amount,
            status=transaction_status,
        )

        transactions.append(
            {
                "transaction_id": transaction_id,
                "account_id": account["account_id"],
                "customer_id": account["customer_id"],
                "product_id": account["product_id"],
                "branch_id": account["branch_id"],
                "channel_id": rng.choice(channel_ids),
                "transaction_datetime": random_datetime_in_january(),
                "transaction_type": transaction_type,
                "transaction_status": transaction_status,
                "amount": amount,
                "fee_amount": fee_amount,
                "currency": "INR",
                "balance_after_transaction": balance_after_transaction,
            }
        )

    return pd.DataFrame(transactions)


def main() -> None:
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

    transactions = generate_transactions()
    transactions.to_csv(OUTPUT_FILE, index=False)

    print("January transaction generation completed.")
    print(f"Output file: {OUTPUT_FILE}")
    print(f"Rows generated: {len(transactions):,}")
    print("\nSample records:")
    print(transactions.head())


if __name__ == "__main__":
    main()
    