from pathlib import Path
from getpass import getpass

import psycopg2

DB_HOST = "localhost"
DB_PORT = 5432
DB_NAME = "banking_analytics_db"
DB_USER = "postgres"

PROJECT_DIR = Path(__file__).resolve().parents[2]

SQL_FILES = [
    PROJECT_DIR / "sql" / "03_staging_tables" / "01_create_staging_tables.sql",
    PROJECT_DIR / "sql" / "03_staging_tables" / "03_transaction_dq_exceptions_and_cleaning.sql",
    PROJECT_DIR / "sql" / "04_warehouse_tables" / "01_create_dimension_tables.sql",
    PROJECT_DIR / "sql" / "04_warehouse_tables" / "03_create_fact_tables.sql",
]


def execute_sql_file(cursor, file_path: Path) -> None:
    if not file_path.exists():
        raise FileNotFoundError(f"SQL file not found: {file_path}")

    sql_text = file_path.read_text(encoding="utf-8")
    cursor.execute(sql_text)
    print(f"Executed: {file_path.relative_to(PROJECT_DIR)}")


def print_validation_summary(cursor) -> None:
    print("\n=== JAN-JUN WAREHOUSE REFRESH SUMMARY ===")

    cursor.execute("SELECT COUNT(*) FROM raw.transactions;")
    raw_rows = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(DISTINCT transaction_id) FROM raw.transactions;")
    raw_unique = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM staging.stg_transactions;")
    staging_rows = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM warehouse.fact_transactions;")
    warehouse_rows = cursor.fetchone()[0]

    cursor.execute(
        "SELECT MIN(transaction_datetime)::date, MAX(transaction_datetime)::date "
        "FROM warehouse.fact_transactions;"
    )
    min_date, max_date = cursor.fetchone()

    print(f"Raw transaction rows:       {raw_rows:,}")
    print(f"Unique transaction IDs:     {raw_unique:,}")
    print(f"Clean staging transactions: {staging_rows:,}")
    print(f"Warehouse transactions:     {warehouse_rows:,}")
    print(f"Warehouse date coverage:    {min_date} to {max_date}")

    print("\nDQ exceptions retained for audit / agent investigation:")
    cursor.execute(
        """
        SELECT exception_type, COUNT(*)
        FROM staging.stg_transaction_dq_exceptions
        GROUP BY exception_type
        ORDER BY exception_type;
        """
    )
    for exception_type, count in cursor.fetchall():
        print(f"- {exception_type}: {count:,}")

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM warehouse.fact_transactions
        WHERE transaction_status = 'Failed' AND COALESCE(fee_amount, 0) > 0;
        """
    )
    failed_with_fee_in_warehouse = cursor.fetchone()[0]
    print(f"\nFailed-with-fee rows remaining in warehouse: {failed_with_fee_in_warehouse}")

    if staging_rows != raw_unique:
        raise RuntimeError(
            f"Staging row count {staging_rows:,} does not match unique raw transaction IDs {raw_unique:,}."
        )

    if warehouse_rows != staging_rows:
        raise RuntimeError(
            f"Warehouse row count {warehouse_rows:,} does not match clean staging rows {staging_rows:,}."
        )

    if failed_with_fee_in_warehouse != 0:
        raise RuntimeError("Failed-with-fee exceptions were not cleaned from the warehouse layer.")

    print("\nValidation status: PASSED")


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
                for sql_file in SQL_FILES:
                    execute_sql_file(cursor, sql_file)

                print_validation_summary(cursor)

        print("\nJan-Jun staging and warehouse refresh completed successfully.")

    finally:
        connection.close()


if __name__ == "__main__":
    main()
