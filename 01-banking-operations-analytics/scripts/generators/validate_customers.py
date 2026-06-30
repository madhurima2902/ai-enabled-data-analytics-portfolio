from pathlib import Path

import pandas as pd


EXPECTED_ROW_COUNT = 10_000

ALLOWED_GENDERS = {"Male", "Female"}
ALLOWED_SEGMENTS = {"Mass", "Affluent", "Premium"}
ALLOWED_KYC_STATUSES = {"Complete", "Pending", "Failed"}
ALLOWED_RISK_BANDS = {"Low", "Medium", "High"}


PROJECT_DIR = Path(__file__).resolve().parents[2]
CUSTOMERS_FILE = PROJECT_DIR / "data" / "raw" / "raw_customers.csv"


def validate_customers() -> None:
    df = pd.read_csv(CUSTOMERS_FILE)

    checks = {
        "row_count_is_10000": len(df) == EXPECTED_ROW_COUNT,
        "customer_id_is_unique": df["customer_id"].is_unique,
        "customer_id_has_no_nulls": df["customer_id"].notna().all(),
        "customer_name_has_no_nulls": df["customer_name"].notna().all(),
        "gender_values_are_valid": set(df["gender"]).issubset(ALLOWED_GENDERS),
        "customer_segment_values_are_valid": set(df["customer_segment"]).issubset(ALLOWED_SEGMENTS),
        "kyc_status_values_are_valid": set(df["kyc_status"]).issubset(ALLOWED_KYC_STATUSES),
        "risk_band_values_are_valid": set(df["risk_band"]).issubset(ALLOWED_RISK_BANDS),
    }

    print("Customer validation results:")
    for check_name, passed in checks.items():
        status = "PASSED" if passed else "FAILED"
        print(f"{check_name}: {status}")

    failed_checks = [check_name for check_name, passed in checks.items() if not passed]

    if failed_checks:
        raise ValueError(f"Customer validation failed: {failed_checks}")

    print("\nAll customer validation checks passed.")
    print(f"Validated file: {CUSTOMERS_FILE}")
    print(f"Total rows: {len(df):,}")


if __name__ == "__main__":
    validate_customers()