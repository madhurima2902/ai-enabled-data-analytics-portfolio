# Healthcare Claims & Provider Operations Analytics

A compact portfolio project that demonstrates healthcare-domain analytics awareness using **synthetic, de-identified data only**.

The project is designed for Data Analyst, BI Analyst, Reporting Analyst, Operations Analyst, and Healthcare Analytics roles. It focuses on claims operations, provider performance, payer mix, utilization, reimbursement, readmissions, and data quality rather than clinical diagnosis or prediction.

## Business Scenario

A healthcare analytics team wants a reliable view of claim and encounter performance across providers and payers. Leadership needs to understand:

- How many claims are paid, denied, or still pending?
- Which payer groups and providers have higher denial rates?
- How much of the submitted amount is ultimately reimbursed?
- How long are claims taking to process?
- What is the average inpatient length of stay?
- What is the 30-day inpatient readmission rate?
- Are data-quality problems affecting reporting accuracy?

## Dataset Design

The project uses a simplified analytics model:

- **dim_patient** — de-identified patient attributes such as age band, state, and chronic-condition flag
- **dim_provider** — provider specialty, facility type, and state
- **fact_claims** — one analytical row per claim/encounter with service, payer, financial, processing, and utilization fields

This is intentionally a reporting-oriented model, not a complete EHR or claims-adjudication system.

## Core Healthcare KPIs

| KPI | Business Meaning |
| --- | --- |
| Claim Denial Rate | Share of claims ending in denied status |
| Paid Reimbursement Rate | Paid amount divided by submitted amount for paid claims |
| Average Processing Days | Average days required to process a claim |
| Payer Mix | Distribution of claim volume and paid amount by payer type |
| Average Inpatient Length of Stay | Average inpatient days per inpatient encounter |
| 30-Day Readmission Rate | Share of inpatient encounters flagged as a readmission within 30 days |
| Provider Denial Rate | Denied claims as a share of claims for each provider |

Detailed definitions are in `docs/kpi_dictionary.md`.

## Healthcare Domain Awareness Demonstrated

This project intentionally includes concepts commonly encountered in healthcare analytics:

- claim status: paid, denied, pending
- submitted, allowed, and paid amounts
- denial reasons
- payer types: Commercial, Medicare, Medicaid, Self-Pay
- provider specialty and facility type
- inpatient, outpatient, and emergency encounters
- length of stay
- 30-day readmission
- claims-processing turnaround
- de-identification and PHI awareness

The data is synthetic. No real patient names, dates of birth, addresses, member IDs, medical record numbers, or other PHI are used.

## Data Quality Checks

The generator deliberately inserts a few controlled exceptions so the analyst can identify and explain them:

- duplicate claim ID
- orphan provider key
- negative submitted amount
- negative processing days

The Python analysis and SQL checks detect these exceptions before KPI reporting.

## Expected Output From the Synthetic Dataset

With the fixed random seed in the generator, the analysis should produce approximately:

- **4,997 clean claim rows**
- **11.9% claim denial rate**
- **74.5% paid reimbursement rate**
- **3.2 days average inpatient length of stay**
- **11.2% 30-day inpatient readmission rate**

The purpose is not to benchmark real healthcare organizations. These numbers are synthetic and exist only to make the analytics workflow reproducible.

## Project Structure

```text
04-healthcare-claims-provider-analytics/
├── data/
│   └── README.md
├── docs/
│   ├── dashboard_spec.md
│   └── kpi_dictionary.md
├── scripts/
│   ├── analyze_healthcare_data.py
│   └── generate_synthetic_data.py
├── sql/
│   ├── 01_schema.sql
│   └── 02_analysis_and_quality.sql
└── README.md
```

## How to Run

From the repository root:

```bash
python 04-healthcare-claims-provider-analytics/scripts/generate_synthetic_data.py
python 04-healthcare-claims-provider-analytics/scripts/analyze_healthcare_data.py
```

The generator creates:

- `data/patients.csv`
- `data/providers.csv`
- `data/claims.csv`

The SQL scripts can then be loaded into PostgreSQL for the same KPI and data-quality analysis.

## Power BI Story

A simple two-page Power BI report can be built from the generated CSVs.

**Page 1 — Claims Operations Overview**
- total claims
- denial rate
- total submitted and paid amount
- reimbursement rate
- average processing days
- payer mix
- monthly claim-status trend

**Page 2 — Provider & Utilization Review**
- provider denial rate
- paid amount by specialty
- average inpatient length of stay
- 30-day readmission rate
- encounter mix
- denial-reason breakdown

The dashboard specification is in `docs/dashboard_spec.md`.

## Interview-Ready Project Summary

> I built a small healthcare claims and provider-operations analytics project using synthetic de-identified data. I modeled patients, providers, and claim-level facts, then used Python and SQL to validate data quality and calculate denial rate, reimbursement, processing time, payer mix, length of stay, readmissions, and provider-level performance. I also documented a Power BI dashboard design. The goal was to demonstrate healthcare-domain understanding while keeping the project focused on analytics rather than clinical prediction.

## Tools

- Python
- Pandas
- NumPy
- PostgreSQL / SQL
- Power BI design
- Git / GitHub
- Data quality profiling
- Dimensional modeling
