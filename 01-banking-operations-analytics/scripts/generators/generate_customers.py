from pathlib import Path
from datetime import date, timedelta

import numpy as np
import pandas as pd
from faker import Faker


REFERENCE_DATE = date(2026, 6, 24)
CUSTOMER_COUNT = 10_000
RANDOM_SEED = 42

fake = Faker("en_IN")
Faker.seed(RANDOM_SEED)
rng = np.random.default_rng(RANDOM_SEED)


PROJECT_DIR = Path(__file__).resolve().parents[2]
RAW_DATA_DIR = PROJECT_DIR / "data" / "raw"
OUTPUT_FILE = RAW_DATA_DIR / "raw_customers.csv"


CITY_STATE_LIST = [
    ("Bengaluru", "Karnataka"),
    ("Hyderabad", "Telangana"),
    ("Mumbai", "Maharashtra"),
    ("Pune", "Maharashtra"),
    ("Chennai", "Tamil Nadu"),
    ("Delhi", "Delhi"),
    ("Gurugram", "Haryana"),
    ("Noida", "Uttar Pradesh"),
    ("Kolkata", "West Bengal"),
    ("Ahmedabad", "Gujarat"),
]

GENDERS = ["Male", "Female"]
CUSTOMER_SEGMENTS = ["Mass", "Affluent", "Premium"]
KYC_STATUSES = ["Complete", "Pending", "Failed"]
RISK_BANDS = ["Low", "Medium", "High"]


def calculate_age(dob: date) -> int:
    return REFERENCE_DATE.year - dob.year - (
        (REFERENCE_DATE.month, REFERENCE_DATE.day) < (dob.month, dob.day)
    )


def get_age_group(age: int) -> str:
    if age < 25:
        return "18-24"
    if age < 35:
        return "25-34"
    if age < 45:
        return "35-44"
    if age < 55:
        return "45-54"
    if age < 65:
        return "55-64"
    return "65+"


def random_date_between(start_date: date, end_date: date) -> date:
    days_between = (end_date - start_date).days
    random_days = int(rng.integers(0, days_between + 1))
    return start_date + timedelta(days=random_days)


def generate_customers() -> pd.DataFrame:
    customers = []

    for i in range(1, CUSTOMER_COUNT + 1):
        customer_id = f"CUST{i:06d}"

        gender = rng.choice(GENDERS, p=[0.52, 0.48])
        customer_name = fake.name()

        dob = random_date_between(date(1950, 1, 1), date(2006, 12, 31))
        age = calculate_age(dob)
        age_group = get_age_group(age)

        city, state = CITY_STATE_LIST[int(rng.integers(0, len(CITY_STATE_LIST)))]

        customer_segment = rng.choice(
            CUSTOMER_SEGMENTS,
            p=[0.72, 0.22, 0.06],
        )

        onboarding_date = random_date_between(date(2018, 1, 1), REFERENCE_DATE)

        kyc_status = rng.choice(
            KYC_STATUSES,
            p=[0.91, 0.07, 0.02],
        )

        risk_band = rng.choice(
            RISK_BANDS,
            p=[0.68, 0.25, 0.07],
        )

        customers.append(
            {
                "customer_id": customer_id,
                "customer_name": customer_name,
                "gender": gender,
                "date_of_birth": dob,
                "age_group": age_group,
                "city": city,
                "state": state,
                "customer_segment": customer_segment,
                "onboarding_date": onboarding_date,
                "kyc_status": kyc_status,
                "risk_band": risk_band,
            }
        )

    return pd.DataFrame(customers)


def main() -> None:
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

    df_customers = generate_customers()
    df_customers.to_csv(OUTPUT_FILE, index=False)

    print("Customer generation completed.")
    print(f"Output file: {OUTPUT_FILE}")
    print(f"Rows generated: {len(df_customers):,}")
    print("\nSample records:")
    print(df_customers.head())


if __name__ == "__main__":
    main()