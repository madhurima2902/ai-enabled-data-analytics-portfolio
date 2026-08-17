from __future__ import annotations

from calendar import monthrange
from datetime import date, datetime, time, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parents[2]
RAW = PROJECT_DIR / "data" / "raw"
SEED = 20260817
rng = np.random.default_rng(SEED)

MONTH_VOLUME = {1: 25_000, 2: 28_000, 3: 30_000, 4: 32_000, 5: 35_000, 6: 38_000}
COMPLAINT_VOLUME = {1: 900, 2: 1_250, 3: 1_050, 4: 1_650, 5: 1_300, 6: 1_350}
CAMPAIGN_VOLUME = {1: 2_200, 2: 2_400, 3: 2_600, 4: 2_800, 5: 3_000, 6: 3_400}
SLA_VOLUME = {1: 1_400, 2: 1_700, 3: 1_600, 4: 2_000, 5: 2_400, 6: 2_100}

TRANSACTION_TYPES = ["Deposit", "Withdrawal", "Transfer", "Bill Payment", "Card Payment", "UPI Payment", "ATM Withdrawal", "Fee Debit", "Interest Credit", "Loan EMI"]
TRANSACTION_TYPE_P = [0.13, 0.11, 0.16, 0.12, 0.11, 0.16, 0.08, 0.03, 0.04, 0.06]
COMPLAINT_CATEGORIES = ["Transaction Failure", "Account Service", "Card Issue", "Loan Service", "Digital Banking", "Charges and Fees", "KYC Update"]
PRIORITIES = ["Low", "Medium", "High", "Critical"]
STATUSES = ["Open", "In Progress", "Resolved", "Closed"]
CAMPAIGN_NAMES = ["Savings Balance Booster", "Credit Card Upgrade", "Personal Loan Preapproved", "Fixed Deposit Offer", "Home Loan Balance Transfer"]
CAMPAIGN_TYPES = ["Cross Sell", "Upsell", "Retention", "Acquisition"]


def random_datetime(month: int) -> datetime:
    day = int(rng.integers(1, monthrange(2026, month)[1] + 1))
    return datetime(2026, month, day, int(rng.integers(0, 24)), int(rng.integers(0, 60)), int(rng.integers(0, 60)))


def random_date(month: int) -> date:
    return random_datetime(month).date()


def amount_for(tx_type: str) -> float:
    ranges = {
        "Deposit": (100, 75_000), "Transfer": (100, 75_000), "Bill Payment": (100, 75_000), "UPI Payment": (100, 75_000),
        "Withdrawal": (100, 40_000), "ATM Withdrawal": (100, 40_000), "Card Payment": (250, 150_000),
        "Fee Debit": (25, 1_500), "Interest Credit": (5, 5_000), "Loan EMI": (2_000, 150_000),
    }
    lo, hi = ranges.get(tx_type, (100, 50_000))
    return round(float(rng.uniform(lo, hi)), 2)


def transaction_status(month: int, channel_id: str) -> str:
    # February mobile incident; March partial recovery. Other months remain stable.
    if month == 2 and channel_id == "CH001":
        p = [0.79, 0.19, 0.02]
    elif month == 3 and channel_id == "CH001":
        p = [0.89, 0.09, 0.02]
    elif month == 2 and channel_id == "CH002":
        p = [0.88, 0.10, 0.02]
    else:
        p = [0.92, 0.06, 0.02]
    return str(rng.choice(["Success", "Failed", "Reversed"], p=p))


def generate_transactions(accounts: pd.DataFrame, channels: pd.DataFrame) -> pd.DataFrame:
    rows = []
    channel_ids = channels["channel_id"].tolist()
    global_seq = 1
    for month, count in MONTH_VOLUME.items():
        for _ in range(count):
            account = accounts.iloc[int(rng.integers(0, len(accounts)))]
            channel_id = str(rng.choice(channel_ids))
            tx_type = str(rng.choice(TRANSACTION_TYPES, p=TRANSACTION_TYPE_P))
            status = transaction_status(month, channel_id)
            amount = amount_for(tx_type)
            # A few legitimate high-value outliers for anomaly detection demos.
            if rng.random() < 0.0015:
                amount = round(float(rng.uniform(500_000, 2_500_000)), 2)
            fee = 0.0
            if status == "Success" and tx_type in {"ATM Withdrawal", "Transfer", "Bill Payment"}:
                fee = round(float(rng.uniform(5, 50)), 2)
            base = float(account["current_balance"])
            credit = tx_type in {"Deposit", "Interest Credit"}
            balance = base if status != "Success" else (base + amount if credit else max(base - amount - fee, 0))
            rows.append({
                "transaction_id": f"TXN2026{month:02d}{global_seq:09d}",
                "account_id": account["account_id"], "customer_id": account["customer_id"],
                "product_id": account["product_id"], "branch_id": account["branch_id"], "channel_id": channel_id,
                "transaction_datetime": random_datetime(month), "transaction_type": tx_type, "transaction_status": status,
                "amount": amount, "fee_amount": fee, "currency": "INR", "balance_after_transaction": round(balance, 2),
            })
            global_seq += 1
    df = pd.DataFrame(rows)

    # Controlled raw-layer DQ exceptions: detectable but small enough not to distort KPIs materially.
    failed_idx = df.index[df["transaction_status"].eq("Failed")]
    fee_idx = rng.choice(failed_idx, size=min(40, len(failed_idx)), replace=False)
    df.loc[fee_idx, "fee_amount"] = rng.uniform(10, 75, len(fee_idx)).round(2)  # failed-with-fee exception

    dup_source = df[df["transaction_datetime"].dt.month.isin([4, 5])].sample(15, random_state=SEED)
    duplicates = dup_source.copy()  # exact duplicate transaction_id rows for DQ/dedup demonstration
    df = pd.concat([df, duplicates], ignore_index=True)

    null_idx = rng.choice(df.index, size=20, replace=False)
    df.loc[null_idx, "channel_id"] = pd.NA  # missing FK exception
    return df


def complaint_category(month: int, channel_id: str) -> str:
    if month == 4 and channel_id in {"CH001", "CH002"}:
        return str(rng.choice(COMPLAINT_CATEGORIES, p=[0.28, 0.08, 0.08, 0.06, 0.34, 0.08, 0.08]))
    return str(rng.choice(COMPLAINT_CATEGORIES, p=[0.18, 0.15, 0.14, 0.12, 0.17, 0.13, 0.11]))


def generate_complaints(accounts: pd.DataFrame, channels: pd.DataFrame) -> pd.DataFrame:
    rows, seq = [], 1
    channel_ids = channels["channel_id"].tolist()
    for month, count in COMPLAINT_VOLUME.items():
        for _ in range(count):
            account = accounts.iloc[int(rng.integers(0, len(accounts)))]
            channel_id = str(rng.choice(channel_ids))
            category = complaint_category(month, channel_id)
            priority = str(rng.choice(PRIORITIES, p=[0.35, 0.40, 0.20, 0.05]))
            status = str(rng.choice(STATUSES, p=[0.12, 0.18, 0.50, 0.20]))
            opened = random_date(month)
            resolution_date, resolution_days = None, None
            if status in {"Resolved", "Closed"}:
                # April backlog: digital complaints resolve materially slower.
                max_days = 24 if month == 4 and category in {"Digital Banking", "Transaction Failure"} else 11
                resolution_days = int(rng.integers(1, max_days))
                resolution_date = opened + timedelta(days=resolution_days)
            rows.append({
                "complaint_id": f"COMP2026{seq:08d}", "customer_id": account["customer_id"], "account_id": account["account_id"],
                "product_id": account["product_id"], "channel_id": channel_id, "complaint_date": opened,
                "complaint_category": category, "complaint_priority": priority, "complaint_status": status,
                "resolution_date": resolution_date, "resolution_days": resolution_days,
            })
            seq += 1
    return pd.DataFrame(rows)


def generate_campaigns(customers: pd.DataFrame, products: pd.DataFrame, channels: pd.DataFrame) -> pd.DataFrame:
    rows, seq = [], 1
    product_ids = products["product_id"].tolist()
    campaign_channels = channels[channels["channel_id"].isin(["CH001", "CH002", "CH006"])]["channel_id"].tolist()
    for month, count in CAMPAIGN_VOLUME.items():
        # June deliberately has higher engagement but lower conversion.
        probs = [0.31, 0.30, 0.21, 0.05, 0.13] if month == 6 else [0.35, 0.28, 0.17, 0.08, 0.12]
        for _ in range(count):
            customer = customers.iloc[int(rng.integers(0, len(customers)))]
            sent = random_date(month)
            response = str(rng.choice(["Sent", "Opened", "Clicked", "Converted", "Not Interested"], p=probs))
            response_date = None if response == "Sent" else sent + timedelta(days=int(rng.integers(0, 15)))
            rows.append({
                "campaign_id": f"CAMP2026{seq:08d}", "customer_id": customer["customer_id"],
                "campaign_name": str(rng.choice(CAMPAIGN_NAMES)), "campaign_type": str(rng.choice(CAMPAIGN_TYPES)),
                "offer_product_id": str(rng.choice(product_ids)), "campaign_channel_id": str(rng.choice(campaign_channels)),
                "sent_date": sent, "response_status": response, "response_date": response_date,
                "converted_flag": response == "Converted",
            })
            seq += 1
    return pd.DataFrame(rows)


def team_for(category: str) -> str:
    return {"Digital Banking": "Digital Banking Support", "Card Issue": "Cards Operations", "Loan Service": "Loan Operations", "KYC Update": "KYC Operations", "Account Service": "Branch Operations"}.get(category, "Customer Service")


def target_hours(priority: str) -> int:
    return {"Critical": 8, "High": 24, "Medium": 48, "Low": 72}[priority]


def generate_sla_tickets(complaints: pd.DataFrame) -> pd.DataFrame:
    rows, seq = [], 1
    complaints = complaints.copy()
    complaints["month"] = pd.to_datetime(complaints["complaint_date"]).dt.month
    for month, count in SLA_VOLUME.items():
        pool = complaints[complaints["month"].eq(month)]
        for _ in range(count):
            c = pool.iloc[int(rng.integers(0, len(pool)))]
            priority = str(c["complaint_priority"])
            team = team_for(str(c["complaint_category"]))
            created = datetime.combine(pd.to_datetime(c["complaint_date"]).date(), time(9, 0)) + timedelta(hours=int(rng.integers(0, 49)))
            target = target_hours(priority)
            due = created + timedelta(hours=target)
            ticket_status = str(rng.choice(STATUSES, p=[0.10, 0.18, 0.52, 0.20]))
            resolved, met = None, None
            if ticket_status in {"Resolved", "Closed"}:
                if month == 5 and team == "Digital Banking Support":
                    resolution_hours = int(rng.integers(max(1, target), int(target * 2.4) + 2))
                else:
                    resolution_hours = int(rng.integers(1, int(target * 1.5) + 2))
                resolved = created + timedelta(hours=resolution_hours)
                met = resolved <= due
            rows.append({
                "ticket_id": f"SLA2026{seq:08d}", "complaint_id": c["complaint_id"], "customer_id": c["customer_id"],
                "account_id": c["account_id"], "created_datetime": created, "due_datetime": due,
                "resolved_datetime": resolved, "ticket_priority": priority, "sla_target_hours": target,
                "ticket_status": ticket_status, "sla_met_flag": met, "assigned_team": team,
            })
            seq += 1
    return pd.DataFrame(rows)


def main() -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    accounts = pd.read_csv(RAW / "raw_accounts.csv")
    customers = pd.read_csv(RAW / "raw_customers.csv")
    products = pd.read_csv(RAW / "raw_products.csv")
    channels = pd.read_csv(RAW / "raw_channels.csv")

    tx = generate_transactions(accounts, channels)
    complaints = generate_complaints(accounts, channels)
    campaigns = generate_campaigns(customers, products, channels)
    sla = generate_sla_tickets(complaints)

    tx.to_csv(RAW / "raw_transactions.csv", index=False)
    complaints.to_csv(RAW / "raw_complaints.csv", index=False)
    campaigns.to_csv(RAW / "raw_campaigns.csv", index=False)
    sla.to_csv(RAW / "raw_sla_tickets.csv", index=False)

    print("Jan-Jun 2026 demo data generated")
    print(f"transactions: {len(tx):,}")
    print(f"complaints:   {len(complaints):,}")
    print(f"campaigns:    {len(campaigns):,}")
    print(f"sla tickets:  {len(sla):,}")
    print("\nDesigned analytical signals:")
    print("- Feb: Mobile Banking transaction failure incident")
    print("- Mar: Partial recovery")
    print("- Apr: Digital complaint volume + resolution backlog")
    print("- May: Digital Banking Support SLA deterioration")
    print("- Jun: Higher campaign engagement but weaker conversion")
    print("\nControlled DQ exceptions in transactions:")
    print("- 15 duplicate rows")
    print("- 40 failed transactions with fees")
    print("- 20 missing channel_id values")
    print("- small population of legitimate high-value amount outliers")


if __name__ == "__main__":
    main()
