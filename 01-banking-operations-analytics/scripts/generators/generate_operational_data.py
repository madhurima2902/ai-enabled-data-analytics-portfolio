from pathlib import Path
from datetime import date, datetime, time, timedelta

import numpy as np
import pandas as pd


COMPLAINT_COUNT = 2_000
CAMPAIGN_COUNT = 5_000
SLA_TICKET_COUNT = 4_000
RANDOM_SEED = 44

rng = np.random.default_rng(RANDOM_SEED)

PROJECT_DIR = Path(__file__).resolve().parents[2]
RAW_DATA_DIR = PROJECT_DIR / "data" / "raw"

CUSTOMERS_FILE = RAW_DATA_DIR / "raw_customers.csv"
ACCOUNTS_FILE = RAW_DATA_DIR / "raw_accounts.csv"
PRODUCTS_FILE = RAW_DATA_DIR / "raw_products.csv"
CHANNELS_FILE = RAW_DATA_DIR / "raw_channels.csv"

COMPLAINTS_FILE = RAW_DATA_DIR / "raw_complaints.csv"
CAMPAIGNS_FILE = RAW_DATA_DIR / "raw_campaigns.csv"
SLA_TICKETS_FILE = RAW_DATA_DIR / "raw_sla_tickets.csv"


COMPLAINT_CATEGORIES = [
    "Transaction Failure",
    "Account Service",
    "Card Issue",
    "Loan Service",
    "Digital Banking",
    "Charges and Fees",
    "KYC Update",
]

COMPLAINT_PRIORITIES = ["Low", "Medium", "High", "Critical"]
COMPLAINT_STATUSES = ["Open", "In Progress", "Resolved", "Closed"]

CAMPAIGN_NAMES = [
    "Savings Balance Booster",
    "Credit Card Upgrade",
    "Personal Loan Preapproved",
    "Fixed Deposit Offer",
    "Home Loan Balance Transfer",
]

CAMPAIGN_TYPES = ["Cross Sell", "Upsell", "Retention", "Acquisition"]
CAMPAIGN_RESPONSE_STATUSES = ["Sent", "Opened", "Clicked", "Converted", "Not Interested"]

SLA_TEAMS = [
    "Customer Service",
    "Digital Banking Support",
    "Cards Operations",
    "Loan Operations",
    "Branch Operations",
    "KYC Operations",
]


def random_date_between(start_date: date, end_date: date) -> date:
    days_between = (end_date - start_date).days
    random_days = int(rng.integers(0, days_between + 1))
    return start_date + timedelta(days=random_days)


def random_datetime_from_date(base_date: date) -> datetime:
    random_hour = int(rng.integers(8, 20))
    random_minute = int(rng.integers(0, 60))
    return datetime.combine(base_date, time(hour=random_hour, minute=random_minute))


def get_sla_target_hours(priority: str) -> int:
    if priority == "Critical":
        return 8
    if priority == "High":
        return 24
    if priority == "Medium":
        return 48
    return 72


def get_team_for_category(category: str) -> str:
    if category == "Digital Banking":
        return "Digital Banking Support"
    if category == "Card Issue":
        return "Cards Operations"
    if category == "Loan Service":
        return "Loan Operations"
    if category == "KYC Update":
        return "KYC Operations"
    if category == "Account Service":
        return "Branch Operations"
    return "Customer Service"


def generate_complaints(accounts: pd.DataFrame, channels: pd.DataFrame) -> pd.DataFrame:
    complaints = []
    channel_ids = channels["channel_id"].tolist()

    for i in range(1, COMPLAINT_COUNT + 1):
        complaint_id = f"COMP{i:07d}"

        account = accounts.iloc[int(rng.integers(0, len(accounts)))]
        complaint_date = random_date_between(date(2026, 1, 1), date(2026, 2, 28))

        category = rng.choice(COMPLAINT_CATEGORIES)
        priority = rng.choice(COMPLAINT_PRIORITIES, p=[0.35, 0.40, 0.20, 0.05])
        status = rng.choice(COMPLAINT_STATUSES, p=[0.12, 0.18, 0.50, 0.20])
        channel_id = rng.choice(channel_ids)

        if status in {"Resolved", "Closed"}:
            resolution_days = int(rng.integers(1, 11))
            resolution_date = complaint_date + timedelta(days=resolution_days)
        else:
            resolution_days = None
            resolution_date = None

        complaints.append(
            {
                "complaint_id": complaint_id,
                "customer_id": account["customer_id"],
                "account_id": account["account_id"],
                "product_id": account["product_id"],
                "channel_id": channel_id,
                "complaint_date": complaint_date,
                "complaint_category": category,
                "complaint_priority": priority,
                "complaint_status": status,
                "resolution_date": resolution_date,
                "resolution_days": resolution_days,
            }
        )

    return pd.DataFrame(complaints)


def generate_campaigns(customers: pd.DataFrame, products: pd.DataFrame, channels: pd.DataFrame) -> pd.DataFrame:
    campaigns = []

    product_ids = products["product_id"].tolist()
    campaign_channel_ids = channels[channels["channel_id"].isin(["CH001", "CH002", "CH006"])]["channel_id"].tolist()

    for i in range(1, CAMPAIGN_COUNT + 1):
        campaign_id = f"CAMP{i:07d}"

        customer = customers.iloc[int(rng.integers(0, len(customers)))]
        sent_date = random_date_between(date(2026, 1, 1), date(2026, 2, 28))

        response_status = rng.choice(
            CAMPAIGN_RESPONSE_STATUSES,
            p=[0.35, 0.28, 0.17, 0.08, 0.12],
        )

        if response_status == "Sent":
            response_date = None
        else:
            response_date = sent_date + timedelta(days=int(rng.integers(0, 15)))

        converted_flag = response_status == "Converted"

        campaigns.append(
            {
                "campaign_id": campaign_id,
                "customer_id": customer["customer_id"],
                "campaign_name": rng.choice(CAMPAIGN_NAMES),
                "campaign_type": rng.choice(CAMPAIGN_TYPES),
                "offer_product_id": rng.choice(product_ids),
                "campaign_channel_id": rng.choice(campaign_channel_ids),
                "sent_date": sent_date,
                "response_status": response_status,
                "response_date": response_date,
                "converted_flag": converted_flag,
            }
        )

    return pd.DataFrame(campaigns)


def generate_sla_tickets(complaints: pd.DataFrame) -> pd.DataFrame:
    tickets = []

    for i in range(1, SLA_TICKET_COUNT + 1):
        ticket_id = f"SLA{i:07d}"

        complaint = complaints.iloc[int(rng.integers(0, len(complaints)))]
        priority = complaint["complaint_priority"]
        category = complaint["complaint_category"]

        created_datetime = random_datetime_from_date(pd.to_datetime(complaint["complaint_date"]).date())
        created_datetime = created_datetime + timedelta(hours=int(rng.integers(0, 49)))

        sla_target_hours = get_sla_target_hours(priority)
        due_datetime = created_datetime + timedelta(hours=sla_target_hours)

        ticket_status = rng.choice(COMPLAINT_STATUSES, p=[0.10, 0.18, 0.52, 0.20])

        if ticket_status in {"Resolved", "Closed"}:
            resolution_hours = int(rng.integers(1, int(sla_target_hours * 1.5) + 2))
            resolved_datetime = created_datetime + timedelta(hours=resolution_hours)
            sla_met_flag = resolved_datetime <= due_datetime
        else:
            resolved_datetime = None
            sla_met_flag = None

        tickets.append(
            {
                "ticket_id": ticket_id,
                "complaint_id": complaint["complaint_id"],
                "customer_id": complaint["customer_id"],
                "account_id": complaint["account_id"],
                "created_datetime": created_datetime,
                "due_datetime": due_datetime,
                "resolved_datetime": resolved_datetime,
                "ticket_priority": priority,
                "sla_target_hours": sla_target_hours,
                "ticket_status": ticket_status,
                "sla_met_flag": sla_met_flag,
                "assigned_team": get_team_for_category(category),
            }
        )

    return pd.DataFrame(tickets)


def main() -> None:
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

    customers = pd.read_csv(CUSTOMERS_FILE)
    accounts = pd.read_csv(ACCOUNTS_FILE)
    products = pd.read_csv(PRODUCTS_FILE)
    channels = pd.read_csv(CHANNELS_FILE)

    complaints = generate_complaints(accounts, channels)
    campaigns = generate_campaigns(customers, products, channels)
    sla_tickets = generate_sla_tickets(complaints)

    complaints.to_csv(COMPLAINTS_FILE, index=False)
    campaigns.to_csv(CAMPAIGNS_FILE, index=False)
    sla_tickets.to_csv(SLA_TICKETS_FILE, index=False)

    print("Operational data generation completed.")
    print(f"Complaints file: {COMPLAINTS_FILE} | Rows: {len(complaints):,}")
    print(f"Campaigns file: {CAMPAIGNS_FILE} | Rows: {len(campaigns):,}")
    print(f"SLA tickets file: {SLA_TICKETS_FILE} | Rows: {len(sla_tickets):,}")


if __name__ == "__main__":
    main()