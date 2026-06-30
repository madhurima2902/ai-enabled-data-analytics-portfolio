from pathlib import Path

import pandas as pd


PROJECT_DIR = Path(__file__).resolve().parents[2]
RAW_DATA_DIR = PROJECT_DIR / "data" / "raw"

PRODUCTS_FILE = RAW_DATA_DIR / "raw_products.csv"
BRANCHES_FILE = RAW_DATA_DIR / "raw_branches.csv"
CHANNELS_FILE = RAW_DATA_DIR / "raw_channels.csv"
ACCOUNTS_FILE = RAW_DATA_DIR / "raw_accounts.csv"


def validate_reference_data() -> None:
    products = pd.read_csv(PRODUCTS_FILE)
    branches = pd.read_csv(BRANCHES_FILE)
    channels = pd.read_csv(CHANNELS_FILE)

    checks = {
        "products_row_count_is_7": len(products) == 7,
        "branches_row_count_is_20": len(branches) == 20,
        "channels_row_count_is_6": len(channels) == 6,
        "product_id_is_unique": products["product_id"].is_unique,
        "branch_id_is_unique": branches["branch_id"].is_unique,
        "channel_id_is_unique": channels["channel_id"].is_unique,
        "product_id_has_no_nulls": products["product_id"].notna().all(),
        "branch_id_has_no_nulls": branches["branch_id"].notna().all(),
        "channel_id_has_no_nulls": channels["channel_id"].notna().all(),
        "product_name_has_no_nulls": products["product_name"].notna().all(),
        "branch_name_has_no_nulls": branches["branch_name"].notna().all(),
        "channel_name_has_no_nulls": channels["channel_name"].notna().all(),
    }

    if ACCOUNTS_FILE.exists():
        accounts = pd.read_csv(ACCOUNTS_FILE)

        checks["all_account_products_exist_in_products"] = accounts["product_id"].isin(
            products["product_id"]
        ).all()

        checks["all_account_branches_exist_in_branches"] = accounts["branch_id"].isin(
            branches["branch_id"]
        ).all()

    print("Reference data validation results:")
    for check_name, passed in checks.items():
        status = "PASSED" if passed else "FAILED"
        print(f"{check_name}: {status}")

    failed_checks = [check_name for check_name, passed in checks.items() if not passed]

    if failed_checks:
        raise ValueError(f"Reference data validation failed: {failed_checks}")

    print("\nAll reference data validation checks passed.")
    print(f"Products: {len(products):,}")
    print(f"Branches: {len(branches):,}")
    print(f"Channels: {len(channels):,}")


if __name__ == "__main__":
    validate_reference_data()