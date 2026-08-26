from pathlib import Path
import numpy as np
import pandas as pd

SEED = 42
N_PATIENTS = 800
N_PROVIDERS = 40
N_CLAIMS = 5000

rng = np.random.default_rng(SEED)
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

patient_ids = [f"PT{i:05d}" for i in range(1, N_PATIENTS + 1)]
patients = pd.DataFrame({
    "patient_id": patient_ids,
    "age_band": rng.choice(
        ["0-17", "18-34", "35-49", "50-64", "65+"],
        size=N_PATIENTS,
        p=[0.12, 0.20, 0.23, 0.25, 0.20],
    ),
    "gender": rng.choice(["Female", "Male", "Other/Unknown"], size=N_PATIENTS, p=[0.49, 0.49, 0.02]),
    "state": rng.choice(["TX", "CA", "FL", "NY", "IL", "GA"], size=N_PATIENTS),
    "chronic_condition_flag": rng.choice([0, 1], size=N_PATIENTS, p=[0.68, 0.32]),
})

provider_ids = [f"PR{i:04d}" for i in range(1, N_PROVIDERS + 1)]
specialties = ["Primary Care", "Cardiology", "Orthopedics", "Emergency Medicine", "General Surgery", "Endocrinology"]
providers = pd.DataFrame({
    "provider_id": provider_ids,
    "specialty": rng.choice(specialties, size=N_PROVIDERS, p=[0.30, 0.13, 0.15, 0.17, 0.10, 0.15]),
    "facility_type": rng.choice(["Hospital", "Clinic", "Ambulatory Center"], size=N_PROVIDERS, p=[0.45, 0.40, 0.15]),
    "state": rng.choice(["TX", "CA", "FL", "NY", "IL", "GA"], size=N_PROVIDERS),
})

service_dates = pd.to_datetime("2026-01-01") + pd.to_timedelta(rng.integers(0, 181, size=N_CLAIMS), unit="D")
encounter_types = rng.choice(["Outpatient", "Inpatient", "Emergency"], size=N_CLAIMS, p=[0.62, 0.20, 0.18])
payer_types = rng.choice(["Commercial", "Medicare", "Medicaid", "Self-Pay"], size=N_CLAIMS, p=[0.48, 0.25, 0.18, 0.09])
diagnosis_categories = rng.choice(
    ["Cardiovascular", "Musculoskeletal", "Respiratory", "Diabetes", "Digestive", "General/Preventive"],
    size=N_CLAIMS,
    p=[0.15, 0.20, 0.13, 0.12, 0.12, 0.28],
)

base_cost = np.select(
    [encounter_types == "Inpatient", encounter_types == "Emergency"],
    [rng.normal(12500, 4500, N_CLAIMS), rng.normal(3200, 1200, N_CLAIMS)],
    default=rng.normal(850, 350, N_CLAIMS),
)
submitted_amount = np.maximum(base_cost, 75).round(2)

denial_probability = np.select(
    [payer_types == "Medicaid", payer_types == "Self-Pay", encounter_types == "Emergency"],
    [0.16, 0.20, 0.14],
    default=0.10,
)
is_denied = rng.random(N_CLAIMS) < denial_probability
is_pending = (~is_denied) & (rng.random(N_CLAIMS) < 0.05)
claim_status = np.where(is_denied, "Denied", np.where(is_pending, "Pending", "Paid"))

allowed_factor = rng.uniform(0.68, 0.92, N_CLAIMS)
allowed_amount = np.where(claim_status == "Pending", 0, submitted_amount * allowed_factor)
paid_factor = rng.uniform(0.86, 1.0, N_CLAIMS)
paid_amount = np.where(claim_status == "Paid", allowed_amount * paid_factor, 0)

processing_days = np.where(
    claim_status == "Paid",
    rng.integers(5, 31, N_CLAIMS),
    np.where(claim_status == "Denied", rng.integers(7, 46, N_CLAIMS), rng.integers(15, 61, N_CLAIMS)),
)

denial_reasons = rng.choice(
    ["Missing information", "Eligibility issue", "Authorization required", "Coding mismatch", "Duplicate claim"],
    size=N_CLAIMS,
)
denial_reason = np.where(claim_status == "Denied", denial_reasons, "")

length_of_stay_days = np.where(
    encounter_types == "Inpatient",
    np.maximum(1, rng.poisson(3.2, N_CLAIMS)),
    0,
)
readmission_30d_flag = np.where(
    encounter_types == "Inpatient",
    (rng.random(N_CLAIMS) < 0.11).astype(int),
    0,
)

claims = pd.DataFrame({
    "claim_id": [f"CL{i:06d}" for i in range(1, N_CLAIMS + 1)],
    "patient_id": rng.choice(patient_ids, size=N_CLAIMS),
    "provider_id": rng.choice(provider_ids, size=N_CLAIMS),
    "service_date": service_dates.date,
    "encounter_type": encounter_types,
    "diagnosis_category": diagnosis_categories,
    "payer_type": payer_types,
    "claim_status": claim_status,
    "submitted_amount": submitted_amount,
    "allowed_amount": np.round(allowed_amount, 2),
    "paid_amount": np.round(paid_amount, 2),
    "processing_days": processing_days,
    "denial_reason": denial_reason,
    "length_of_stay_days": length_of_stay_days,
    "readmission_30d_flag": readmission_30d_flag,
})

# Controlled data-quality exceptions to make profiling exercises realistic.
claims.loc[12, "provider_id"] = "PR9999"       # orphan provider
claims.loc[24, "processing_days"] = -2         # invalid duration
claims.loc[36, "submitted_amount"] = -500      # invalid monetary amount
claims = pd.concat([claims, claims.iloc[[48]]], ignore_index=True)  # duplicate claim_id

patients.to_csv(DATA_DIR / "patients.csv", index=False)
providers.to_csv(DATA_DIR / "providers.csv", index=False)
claims.to_csv(DATA_DIR / "claims.csv", index=False)

print(f"Created {len(patients):,} patients, {len(providers):,} providers and {len(claims):,} claim rows in {DATA_DIR}")
