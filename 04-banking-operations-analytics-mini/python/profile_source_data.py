from pathlib import Path
import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_DIR / "data" / "raw"


def profile_dataframe(name: str, df: pd.DataFrame, id_column: str | None = None) -> None:
    print(f"\n=== {name.upper()} ===")
    print(f"rows: {len(df):,}")
    print(f"columns: {len(df.columns)}")

    missing = df.isna().sum()
    missing = missing[missing > 0]
    print("\nmissing values:")
    print(missing if not missing.empty else "none")

    print(f"\nfull-row duplicates: {df.duplicated().sum():,}")

    if id_column and id_column in df.columns:
        print(
            f"duplicate {id_column}: "
            f"{df.duplicated(subset=[id_column]).sum():,}"
        )


def main() -> None:
    transactions = pd.read_csv(
        RAW_DIR / "raw_transactions.csv",
        parse_dates=["transaction_datetime"],
    )

    complaints = pd.read_csv(
        RAW_DIR / "raw_complaints.csv",
        parse_dates=["complaint_date", "resolution_date"],
    )

    sla_tickets = pd.read_csv(
        RAW_DIR / "raw_sla_tickets.csv",
        parse_dates=["created_datetime", "due_datetime", "resolved_datetime"],
    )

    profile_dataframe("transactions", transactions, "transaction_id")
    profile_dataframe("complaints", complaints, "complaint_id")
    profile_dataframe("sla tickets", sla_tickets, "ticket_id")

    print("\n=== TRANSACTION STATUS ===")
    print(transactions["transaction_status"].value_counts(dropna=False))

    print("\n=== COMPLAINT STATUS ===")
    print(complaints["complaint_status"].value_counts(dropna=False))

    print("\n=== CONTROL CHECKS ===")
    print(
        "missing transaction channel_id:",
        transactions["channel_id"].isna().sum(),
    )

    failed_with_fee = (
        (transactions["transaction_status"] == "Failed")
        & (transactions["fee_amount"] > 0)
    ).sum()

    print("failed transactions with non-zero fee:", failed_with_fee)


if __name__ == "__main__":
    main()
