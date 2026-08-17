from pathlib import Path
import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parents[2]
RAW = PROJECT_DIR / "data" / "raw"


def pct(n, d):
    return round(100.0 * n / d, 2) if d else 0.0


def main() -> None:
    tx = pd.read_csv(RAW / "raw_transactions.csv", parse_dates=["transaction_datetime"])
    complaints = pd.read_csv(RAW / "raw_complaints.csv", parse_dates=["complaint_date", "resolution_date"])
    campaigns = pd.read_csv(RAW / "raw_campaigns.csv", parse_dates=["sent_date", "response_date"])
    sla = pd.read_csv(RAW / "raw_sla_tickets.csv", parse_dates=["created_datetime", "due_datetime", "resolved_datetime"])

    print("=== ROW COUNTS ===")
    print(f"transactions: {len(tx):,}")
    print(f"complaints:   {len(complaints):,}")
    print(f"campaigns:    {len(campaigns):,}")
    print(f"sla tickets:  {len(sla):,}")

    print("\n=== MONTH COVERAGE ===")
    print(tx.groupby(tx["transaction_datetime"].dt.month).size().rename("transactions"))

    print("\n=== TRANSACTION FAILURE RATE BY MONTH / CHANNEL ===")
    t = tx.dropna(subset=["channel_id"]).copy()
    t["month"] = t["transaction_datetime"].dt.month
    summary = (
        t.groupby(["month", "channel_id"])["transaction_status"]
        .agg(total="size", failed=lambda s: (s == "Failed").sum())
        .reset_index()
    )
    summary["failure_rate_pct"] = (100 * summary["failed"] / summary["total"]).round(2)
    print(summary[summary["channel_id"].isin(["CH001", "CH002"])].to_string(index=False))

    print("\n=== COMPLAINT VOLUME / RESOLUTION BY MONTH ===")
    complaints["month"] = complaints["complaint_date"].dt.month
    c = complaints.groupby("month").agg(
        complaints=("complaint_id", "size"),
        avg_resolution_days=("resolution_days", "mean"),
    ).round(2)
    print(c)

    print("\n=== MAY DIGITAL BANKING SUPPORT SLA ===")
    sla["month"] = sla["created_datetime"].dt.month
    may = sla[(sla["month"] == 5) & (sla["assigned_team"] == "Digital Banking Support")]
    resolved = may[may["sla_met_flag"].notna()]
    breached = (resolved["sla_met_flag"].astype(str).str.lower() == "false").sum()
    print(f"resolved tickets: {len(resolved):,}")
    print(f"breach rate: {pct(breached, len(resolved))}%")

    print("\n=== CAMPAIGN PERFORMANCE BY MONTH ===")
    campaigns["month"] = campaigns["sent_date"].dt.month
    rows = []
    for month, g in campaigns.groupby("month"):
        engaged = g["response_status"].isin(["Opened", "Clicked", "Converted"]).sum()
        converted = (g["response_status"] == "Converted").sum()
        rows.append({
            "month": month,
            "sent": len(g),
            "engagement_rate_pct": pct(engaged, len(g)),
            "conversion_rate_pct": pct(converted, len(g)),
        })
    print(pd.DataFrame(rows).to_string(index=False))

    print("\n=== CONTROLLED DATA-QUALITY EXCEPTIONS ===")
    print(f"duplicate transaction_id rows: {tx.duplicated(subset=['transaction_id']).sum():,}")
    print(f"missing transaction channel_id: {tx['channel_id'].isna().sum():,}")
    print(f"failed transactions with fee: {((tx['transaction_status'] == 'Failed') & (tx['fee_amount'] > 0)).sum():,}")
    print(f"high-value transactions > 500,000: {(tx['amount'] > 500_000).sum():,}")

    print("\nExpected demo signals:")
    print("1. February CH001 failure rate should be much higher than January.")
    print("2. March CH001 should improve versus February.")
    print("3. April should show the highest complaint volume and slower digital resolution.")
    print("4. May Digital Banking Support should show worse SLA performance.")
    print("5. June should show stronger engagement but lower campaign conversion.")


if __name__ == "__main__":
    main()
