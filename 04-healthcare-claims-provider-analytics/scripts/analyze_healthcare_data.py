from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"

patients = pd.read_csv(DATA_DIR / "patients.csv")
providers = pd.read_csv(DATA_DIR / "providers.csv")
claims = pd.read_csv(DATA_DIR / "claims.csv", parse_dates=["service_date"])

# Data-quality profile
duplicate_claims = claims["claim_id"].duplicated().sum()
orphan_patients = (~claims["patient_id"].isin(patients["patient_id"])).sum()
orphan_providers = (~claims["provider_id"].isin(providers["provider_id"])).sum()
invalid_amounts = ((claims["submitted_amount"] < 0) | (claims["allowed_amount"] < 0) | (claims["paid_amount"] < 0)).sum()
invalid_processing_days = (claims["processing_days"] < 0).sum()

# KPI calculations use a clean analytical subset so controlled exceptions do not distort results.
clean = claims[
    ~claims["claim_id"].duplicated(keep="first")
    & claims["patient_id"].isin(patients["patient_id"])
    & claims["provider_id"].isin(providers["provider_id"])
    & (claims["submitted_amount"] >= 0)
    & (claims["allowed_amount"] >= 0)
    & (claims["paid_amount"] >= 0)
    & (claims["processing_days"] >= 0)
].copy()

total_claims = len(clean)
denial_rate = (clean["claim_status"].eq("Denied").mean()) * 100
paid_claims = clean[clean["claim_status"].eq("Paid")]
reimbursement_rate = (paid_claims["paid_amount"].sum() / paid_claims["submitted_amount"].sum()) * 100

inpatient = clean[clean["encounter_type"].eq("Inpatient")]
avg_los = inpatient["length_of_stay_days"].mean()
readmission_rate = inpatient["readmission_30d_flag"].mean() * 100

print("DATA QUALITY")
print(f"Duplicate claim IDs: {duplicate_claims}")
print(f"Orphan patient keys: {orphan_patients}")
print(f"Orphan provider keys: {orphan_providers}")
print(f"Rows with invalid monetary amounts: {invalid_amounts}")
print(f"Rows with invalid processing days: {invalid_processing_days}")

print("\nCORE KPIs")
print(f"Clean claim rows: {total_claims:,}")
print(f"Claim denial rate: {denial_rate:.1f}%")
print(f"Paid reimbursement rate: {reimbursement_rate:.1f}%")
print(f"Average inpatient length of stay: {avg_los:.1f} days")
print(f"30-day inpatient readmission rate: {readmission_rate:.1f}%")

payer_summary = (
    clean.groupby("payer_type", as_index=False)
    .agg(
        claims=("claim_id", "count"),
        submitted_amount=("submitted_amount", "sum"),
        paid_amount=("paid_amount", "sum"),
        denial_rate=("claim_status", lambda s: s.eq("Denied").mean() * 100),
    )
    .sort_values("claims", ascending=False)
)
print("\nPAYER SUMMARY")
print(payer_summary.round(2).to_string(index=False))

provider_summary = (
    clean.groupby("provider_id", as_index=False)
    .agg(
        claims=("claim_id", "count"),
        denial_rate=("claim_status", lambda s: s.eq("Denied").mean() * 100),
        avg_processing_days=("processing_days", "mean"),
        paid_amount=("paid_amount", "sum"),
    )
    .merge(providers[["provider_id", "specialty", "facility_type"]], on="provider_id", how="left")
    .sort_values(["denial_rate", "claims"], ascending=[False, False])
)
print("\nPROVIDERS TO REVIEW (TOP 10 BY DENIAL RATE)")
print(provider_summary.head(10).round(2).to_string(index=False))
