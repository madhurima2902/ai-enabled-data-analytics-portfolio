from pathlib import Path

import pandas as pd


PROJECT_DIR = Path(__file__).resolve().parents[2]
RAW_DATA_DIR = PROJECT_DIR / "data" / "raw"

PRODUCTS_FILE = RAW_DATA_DIR / "raw_products.csv"
BRANCHES_FILE = RAW_DATA_DIR / "raw_branches.csv"
CHANNELS_FILE = RAW_DATA_DIR / "raw_channels.csv"


def create_products() -> pd.DataFrame:
    products = [
        {
            "product_id": "PROD001",
            "product_name": "Savings Account",
            "product_category": "Deposit",
            "product_type": "Account",
            "is_active": True,
        },
        {
            "product_id": "PROD002",
            "product_name": "Current Account",
            "product_category": "Deposit",
            "product_type": "Account",
            "is_active": True,
        },
        {
            "product_id": "PROD003",
            "product_name": "Salary Account",
            "product_category": "Deposit",
            "product_type": "Account",
            "is_active": True,
        },
        {
            "product_id": "PROD004",
            "product_name": "Fixed Deposit",
            "product_category": "Deposit",
            "product_type": "Investment",
            "is_active": True,
        },
        {
            "product_id": "PROD005",
            "product_name": "Credit Card",
            "product_category": "Credit",
            "product_type": "Card",
            "is_active": True,
        },
        {
            "product_id": "PROD006",
            "product_name": "Personal Loan",
            "product_category": "Loan",
            "product_type": "Loan",
            "is_active": True,
        },
        {
            "product_id": "PROD007",
            "product_name": "Home Loan",
            "product_category": "Loan",
            "product_type": "Loan",
            "is_active": True,
        },
    ]

    return pd.DataFrame(products)


def create_branches() -> pd.DataFrame:
    branches = [
        ("BR001", "Bengaluru MG Road Branch", "Bengaluru", "Karnataka", "South", "Urban"),
        ("BR002", "Bengaluru Whitefield Branch", "Bengaluru", "Karnataka", "South", "Urban"),
        ("BR003", "Hyderabad Hitech City Branch", "Hyderabad", "Telangana", "South", "Urban"),
        ("BR004", "Hyderabad Secunderabad Branch", "Hyderabad", "Telangana", "South", "Urban"),
        ("BR005", "Mumbai Andheri Branch", "Mumbai", "Maharashtra", "West", "Urban"),
        ("BR006", "Mumbai Fort Branch", "Mumbai", "Maharashtra", "West", "Urban"),
        ("BR007", "Pune Hinjewadi Branch", "Pune", "Maharashtra", "West", "Urban"),
        ("BR008", "Pune Shivaji Nagar Branch", "Pune", "Maharashtra", "West", "Urban"),
        ("BR009", "Chennai T Nagar Branch", "Chennai", "Tamil Nadu", "South", "Urban"),
        ("BR010", "Chennai OMR Branch", "Chennai", "Tamil Nadu", "South", "Urban"),
        ("BR011", "Delhi Connaught Place Branch", "Delhi", "Delhi", "North", "Urban"),
        ("BR012", "Delhi Dwarka Branch", "Delhi", "Delhi", "North", "Urban"),
        ("BR013", "Gurugram Cyber City Branch", "Gurugram", "Haryana", "North", "Urban"),
        ("BR014", "Gurugram Sector 56 Branch", "Gurugram", "Haryana", "North", "Urban"),
        ("BR015", "Noida Sector 62 Branch", "Noida", "Uttar Pradesh", "North", "Urban"),
        ("BR016", "Noida Sector 18 Branch", "Noida", "Uttar Pradesh", "North", "Urban"),
        ("BR017", "Kolkata Salt Lake Branch", "Kolkata", "West Bengal", "East", "Urban"),
        ("BR018", "Kolkata Park Street Branch", "Kolkata", "West Bengal", "East", "Urban"),
        ("BR019", "Ahmedabad CG Road Branch", "Ahmedabad", "Gujarat", "West", "Urban"),
        ("BR020", "Ahmedabad SG Highway Branch", "Ahmedabad", "Gujarat", "West", "Urban"),
    ]

    return pd.DataFrame(
        branches,
        columns=[
            "branch_id",
            "branch_name",
            "city",
            "state",
            "region",
            "branch_type",
        ],
    )


def create_channels() -> pd.DataFrame:
    channels = [
        {
            "channel_id": "CH001",
            "channel_name": "Mobile Banking",
            "channel_category": "Digital",
            "is_digital": True,
        },
        {
            "channel_id": "CH002",
            "channel_name": "Internet Banking",
            "channel_category": "Digital",
            "is_digital": True,
        },
        {
            "channel_id": "CH003",
            "channel_name": "ATM",
            "channel_category": "Self Service",
            "is_digital": False,
        },
        {
            "channel_id": "CH004",
            "channel_name": "Branch",
            "channel_category": "Physical",
            "is_digital": False,
        },
        {
            "channel_id": "CH005",
            "channel_name": "POS",
            "channel_category": "Merchant",
            "is_digital": False,
        },
        {
            "channel_id": "CH006",
            "channel_name": "Call Center",
            "channel_category": "Assisted",
            "is_digital": False,
        },
    ]

    return pd.DataFrame(channels)


def main() -> None:
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

    products = create_products()
    branches = create_branches()
    channels = create_channels()

    products.to_csv(PRODUCTS_FILE, index=False)
    branches.to_csv(BRANCHES_FILE, index=False)
    channels.to_csv(CHANNELS_FILE, index=False)

    print("Reference data generation completed.")
    print(f"Products file: {PRODUCTS_FILE} | Rows: {len(products):,}")
    print(f"Branches file: {BRANCHES_FILE} | Rows: {len(branches):,}")
    print(f"Channels file: {CHANNELS_FILE} | Rows: {len(channels):,}")


if __name__ == "__main__":
    main()