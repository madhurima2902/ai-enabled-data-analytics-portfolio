from pathlib import Path
from datetime import date, timedelta

import numpy as np
import pandas as pd


REFERENCE_DATE = date(2026, 6, 24)
ACCOUNT_COUNT = 15_000
RANDOM_SEED = 43

rng = np.random.default_rng(RANDOM_SEED)

PROJECT_DIR = Path(__file__).resolve().parents[2]
RAW_DATA_DIR = PROJECT_DIR / "data" / "raw"

CUSTOMERS_FILE = RAW_DATA_DIR / "raw_customers.csv"
OUTPUT_FILE = RAW_DATA_DIR / "raw_accounts.csv"


PRODUCTS = {
    "PROD001": {"name": "Savings Account", "category": "Deposit", "balance_min": 500, "balance_max": 400_000},
    "PROD002": {"name": "Current Account", "category": "Deposit", "balance_min": 5_000, "balance_max": 1_500_000},
    "PROD003": {"name": "Salary Account", "category": "Deposit", "balance_min": 0, "balance_max": 600_000},
    "PROD004": {"name": "Fixed Deposit", "category": "Deposit", "balance_min": 25_000, "balance_max": 2_000_000},
    "PROD005": {"name": "Credit Card", "category": "Credit", "balance_min": 0, "balance_max": 250_000},
    "PROD006": {"name": "Personal Loan", "category": "Loan", "balance_min": 50_000, "balance_max": 1_000_000},
    "PROD007": {"name": "Home Loan", "category": "Loan", "balance_min": 500_000, "balance_max": 8_000_000},
}

PRODUCT_IDS = list(PRODUCTS.keys())
BRANCH_IDS = [f"BR{i:03d}" for i in range(1, 21)]
ACCOUNT_STATUSES = ["Active", "Dormant", "Closed"]


def random_date_between(start_date: date, end_date: date) -> date:
    days_between = (end_date - start_date).days
    random_days = int(rng.integers(0, days_between + 1))
    return start_date + timedelta(days=random_days)


def generate_account_balance(product_id: str) -> float:
    product = PRODUCTS[product_id]
    balance = rng.uniform(product["balance_min"], product["balance_max"])
    return round(float(balance), 2)


def generate_interest_rate(product_id: str) -> float:
    if product_id in {"PROD001", "PROD002", "PROD003"}:
        return round(float(rng.uniform(2.5, 4.0)), 2)
    if product_id == "PROD004":
        return round(float(rng.uniform(5.5, 7.5)), 2)
    if product_id == "PROD005":
        return round(float(rng.uniform(24.0, 38.0)), 2)
    if product_id == "PROD006":
        return round(float(rng.uniform(10.0, 18.0)), 2)
    if product_id == "PROD007":
        return round(float(rng.uniform(8.0, 10.5)), 2)
    return 0.0


def generate_credit_limit(product_id: str) -> float:
    if product_id == "PROD005":
        return round(float(rng.uniform(50_000, 500_000)), 2)
    return 0.0


def generate_accounts() -> pd.DataFrame:
    customers = pd.read_csv(CUSTOMERS_FILE)
    customers["onboarding_date"] = pd.to_datetime(customers["onboarding_date"]).dt.date

    accounts = []

    for i in range(1, ACCOUNT_COUNT + 1):
        account_id = f"ACC{i:07d}"

        customer = customers.sample(
            n=1,
            random_state=int(rng.integers(1, 1_000_000))
        ).iloc[0]

        customer_id = customer["customer_id"]
        onboarding_date = customer["onboarding_date"]

        product_id = rng.choice(
            PRODUCT_IDS,
            p=[0.33, 0.10, 0.25, 0.12, 0.12, 0.06, 0.02],
        )

        branch_id = rng.choice(BRANCH_IDS)
        account_open_date = random_date_between(onboarding_date, REFERENCE_DATE)

        account_status = rng.choice(
            ACCOUNT_STATUSES,
            p=[0.88, 0.08, 0.04],
        )

        current_balance = generate_account_balance(product_id)
        interest_rate = generate_interest_rate(product_id)
        credit_limit = generate_credit_limit(product_id)

        accounts.append(
            {
                "account_id": account_id,
                "customer_id": customer_id,
                "product_id": product_id,
                "branch_id": branch_id,
                "account_open_date": account_open_date,
                "account_status": account_status,
                "current_balance": current_balance,
                "interest_rate": interest_rate,
                "credit_limit": credit_limit,
            }
        )

    return pd.DataFrame(accounts)


def main() -> None:
    if not CUSTOMERS_FILE.exists():
        raise FileNotFoundError(
            f"Customer file not found: {CUSTOMERS_FILE}. Run generate_customers.py first."
        )

    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

    df_accounts = generate_accounts()
    df_accounts.to_csv(OUTPUT_FILE, index=False)

    print("Account generation completed.")
    print(f"Output file: {OUTPUT_FILE}")
    print(f"Rows generated: {len(df_accounts):,}")
    print("\nSample records:")
    print(df_accounts.head())


if __name__ == "__main__":
    main()