from pathlib import Path
from getpass import getpass

import psycopg2


DB_HOST = "localhost"
DB_PORT = 5432
DB_NAME = "banking_analytics_db"
DB_USER = "postgres"

PROJECT_DIR = Path(__file__).resolve().parents[2]
RAW_DATA_DIR = PROJECT_DIR / "data" / "raw"


LOAD_CONFIG = [
    {
        "table_name": "raw.customers",
        "file_path": RAW_DATA_DIR / "raw_customers.csv",
    },
    {
        "table_name": "raw.accounts",
        "file_path": RAW_DATA_DIR / "raw_accounts.csv",
    },
    {
        "table_name": "raw.products",
        "file_path": RAW_DATA_DIR / "raw_products.csv",
    },
    {
        "table_name": "raw.branches",
        "file_path": RAW_DATA_DIR / "raw_branches.csv",
    },
    {
        "table_name": "raw.channels",
        "file_path": RAW_DATA_DIR / "raw_channels.csv",
    },
    {
        "table_name": "raw.complaints",
        "file_path": RAW_DATA_DIR / "raw_complaints.csv",
    },
    {
        "table_name": "raw.campaigns",
        "file_path": RAW_DATA_DIR / "raw_campaigns.csv",
    },
    {
        "table_name": "raw.sla_tickets",
        "file_path": RAW_DATA_DIR / "raw_sla_tickets.csv",
    },
    {
        "table_name": "raw.transactions",
        "file_path": RAW_DATA_DIR / "raw_transactions_jan.csv",
    },
]


def load_csv_to_table(cursor, table_name: str, file_path: Path) -> None:
    if not file_path.exists():
        raise FileNotFoundError(f"CSV file not found: {file_path}")

    truncate_sql = f"TRUNCATE TABLE {table_name};"
    cursor.execute(truncate_sql)

    with file_path.open("r", encoding="utf-8") as csv_file:
        copy_sql = f"""
            COPY {table_name}
            FROM STDIN
            WITH (
                FORMAT CSV,
                HEADER TRUE,
                NULL ''
            );
        """
        cursor.copy_expert(copy_sql, csv_file)

    cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
    row_count = cursor.fetchone()[0]

    print(f"Loaded {table_name}: {row_count:,} rows")


def main() -> None:
    password = getpass("Enter PostgreSQL password for user postgres: ")

    connection = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=password,
    )

    try:
        with connection:
            with connection.cursor() as cursor:
                for config in LOAD_CONFIG:
                    load_csv_to_table(
                        cursor=cursor,
                        table_name=config["table_name"],
                        file_path=config["file_path"],
                    )

        print("\nRaw CSV loading completed successfully.")

    finally:
        connection.close()


if __name__ == "__main__":
    main()