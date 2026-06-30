from pathlib import Path

import pandas as pd


EXPECTED_COMPLAINT_COUNT = 2_000
EXPECTED_CAMPAIGN_COUNT = 5_000
EXPECTED_SLA_TICKET_COUNT = 4_000

PROJECT_DIR = Path(__file__).resolve().parents[2]
RAW_DATA_DIR = PROJECT_DIR / "data" / "raw"

CUSTOMERS_FILE = RAW_DATA_DIR / "raw_customers.csv"
ACCOUNTS_FILE = RAW_DATA_DIR / "raw_accounts.csv"
PRODUCTS_FILE = RAW_DATA_DIR / "raw_products.csv"
CHANNELS_FILE = RAW_DATA_DIR / "raw_channels.csv"

COMPLAINTS_FILE = RAW_DATA_DIR / "raw_complaints.csv"
CAMPAIGNS_FILE = RAW_DATA_DIR / "raw_campaigns.csv"
SLA_TICKETS_FILE = RAW_DATA_DIR / "raw_sla_tickets.csv"

VALID_COMPLAINT_STATUSES = {"Open", "In Progress", "Resolved", "Closed"}
VALID_CAMPAIGN_RESPONSES = {"Sent", "Opened", "Clicked", "Converted", "Not Interested"}


def validate_operational_data() -> None:
    customers = pd.read_csv(CUSTOMERS_FILE)
    accounts = pd.read_csv(ACCOUNTS_FILE)
    products = pd.read_csv(PRODUCTS_FILE)
    channels = pd.read_csv(CHANNELS_FILE)

    complaints = pd.read_csv(COMPLAINTS_FILE)
    campaigns = pd.read_csv(CAMPAIGNS_FILE)
    sla_tickets = pd.read_csv(SLA_TICKETS_FILE)

    complaints["complaint_date"] = pd.to_datetime(complaints["complaint_date"])
    complaints["resolution_date"] = pd.to_datetime(complaints["resolution_date"], errors="coerce")

    campaigns["sent_date"] = pd.to_datetime(campaigns["sent_date"])
    campaigns["response_date"] = pd.to_datetime(campaigns["response_date"], errors="coerce")

    sla_tickets["created_datetime"] = pd.to_datetime(sla_tickets["created_datetime"])
    sla_tickets["due_datetime"] = pd.to_datetime(sla_tickets["due_datetime"])
    sla_tickets["resolved_datetime"] = pd.to_datetime(sla_tickets["resolved_datetime"], errors="coerce")

    resolved_complaints = complaints["complaint_status"].isin(["Resolved", "Closed"])
    open_complaints = complaints["complaint_status"].isin(["Open", "In Progress"])

    responded_campaigns = campaigns["response_status"] != "Sent"
    converted_campaigns = campaigns["response_status"] == "Converted"

    resolved_tickets = sla_tickets["ticket_status"].isin(["Resolved", "Closed"])

    checks = {
        "complaints_row_count_is_2000": len(complaints) == EXPECTED_COMPLAINT_COUNT,
        "campaigns_row_count_is_5000": len(campaigns) == EXPECTED_CAMPAIGN_COUNT,
        "sla_tickets_row_count_is_4000": len(sla_tickets) == EXPECTED_SLA_TICKET_COUNT,

        "complaint_id_is_unique": complaints["complaint_id"].is_unique,
        "campaign_id_is_unique": campaigns["campaign_id"].is_unique,
        "ticket_id_is_unique": sla_tickets["ticket_id"].is_unique,

        "complaint_customers_exist": complaints["customer_id"].isin(customers["customer_id"]).all(),
        "complaint_accounts_exist": complaints["account_id"].isin(accounts["account_id"]).all(),
        "complaint_products_exist": complaints["product_id"].isin(products["product_id"]).all(),
        "complaint_channels_exist": complaints["channel_id"].isin(channels["channel_id"]).all(),

        "campaign_customers_exist": campaigns["customer_id"].isin(customers["customer_id"]).all(),
        "campaign_offer_products_exist": campaigns["offer_product_id"].isin(products["product_id"]).all(),
        "campaign_channels_exist": campaigns["campaign_channel_id"].isin(channels["channel_id"]).all(),

        "sla_ticket_complaints_exist": sla_tickets["complaint_id"].isin(complaints["complaint_id"]).all(),
        "sla_ticket_customers_exist": sla_tickets["customer_id"].isin(customers["customer_id"]).all(),
        "sla_ticket_accounts_exist": sla_tickets["account_id"].isin(accounts["account_id"]).all(),

        "complaint_status_values_are_valid": set(complaints["complaint_status"]).issubset(VALID_COMPLAINT_STATUSES),
        "campaign_response_values_are_valid": set(campaigns["response_status"]).issubset(VALID_CAMPAIGN_RESPONSES),
        "ticket_status_values_are_valid": set(sla_tickets["ticket_status"]).issubset(VALID_COMPLAINT_STATUSES),

        "resolved_complaints_have_resolution_date": complaints.loc[resolved_complaints, "resolution_date"].notna().all(),
        "open_complaints_do_not_have_resolution_date": complaints.loc[open_complaints, "resolution_date"].isna().all(),
        "resolution_date_not_before_complaint_date": (
            complaints.loc[resolved_complaints, "resolution_date"]
            >= complaints.loc[resolved_complaints, "complaint_date"]
        ).all(),

        "responded_campaigns_have_response_date": campaigns.loc[responded_campaigns, "response_date"].notna().all(),
        "converted_campaigns_have_converted_flag_true": campaigns.loc[converted_campaigns, "converted_flag"].astype(str).str.lower().eq("true").all(),

        "ticket_due_datetime_not_before_created_datetime": (
            sla_tickets["due_datetime"] >= sla_tickets["created_datetime"]
        ).all(),
        "resolved_tickets_have_resolved_datetime": sla_tickets.loc[resolved_tickets, "resolved_datetime"].notna().all(),
        "resolved_ticket_datetime_not_before_created_datetime": (
            sla_tickets.loc[resolved_tickets, "resolved_datetime"]
            >= sla_tickets.loc[resolved_tickets, "created_datetime"]
        ).all(),
    }

    print("Operational data validation results:")
    for check_name, passed in checks.items():
        status = "PASSED" if passed else "FAILED"
        print(f"{check_name}: {status}")

    failed_checks = [check_name for check_name, passed in checks.items() if not passed]

    if failed_checks:
        raise ValueError(f"Operational data validation failed: {failed_checks}")

    print("\nAll operational data validation checks passed.")
    print(f"Complaints: {len(complaints):,}")
    print(f"Campaigns: {len(campaigns):,}")
    print(f"SLA tickets: {len(sla_tickets):,}")


if __name__ == "__main__":
    validate_operational_data()