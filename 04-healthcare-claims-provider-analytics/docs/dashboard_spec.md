# Power BI Dashboard Specification

## Goal

Create a simple two-page report that lets an operations or analytics manager move from enterprise-level claims performance to provider and utilization detail.

## Recommended Model

Relationships:

- `dim_patient[patient_id]` 1:* `fact_claims[patient_id]`
- `dim_provider[provider_id]` 1:* `fact_claims[provider_id]`

Use a separate Date table related to `fact_claims[service_date]`.

## Page 1 — Claims Operations Overview

### KPI Cards

- Total Clean Claims
- Denial Rate
- Submitted Amount
- Paid Amount
- Paid Reimbursement Rate
- Average Processing Days

### Visuals

1. Monthly claim count by status
2. Denial rate by payer type
3. Submitted vs paid amount by payer type
4. Denial reasons
5. Encounter mix: inpatient / outpatient / emergency

### Slicers

- service month
- payer type
- encounter type
- provider specialty
- facility type

## Page 2 — Provider & Utilization Review

### KPI Cards

- Inpatient Encounters
- Average Inpatient Length of Stay
- 30-Day Readmission Rate

### Visuals

1. Provider denial rate vs claim volume
2. Paid amount by specialty
3. Average processing days by provider
4. Average length of stay by facility type
5. Readmission rate by provider specialty

## Recommended DAX Measures

```DAX
Total Claims =
COUNTROWS(fact_claims)

Denied Claims =
CALCULATE(
    [Total Claims],
    fact_claims[claim_status] = "Denied"
)

Denial Rate =
DIVIDE([Denied Claims], [Total Claims])

Submitted Amount =
SUM(fact_claims[submitted_amount])

Paid Amount =
SUM(fact_claims[paid_amount])

Average Processing Days =
AVERAGE(fact_claims[processing_days])

Inpatient Encounters =
CALCULATE(
    [Total Claims],
    fact_claims[encounter_type] = "Inpatient"
)

Average Inpatient LOS =
CALCULATE(
    AVERAGE(fact_claims[length_of_stay_days]),
    fact_claims[encounter_type] = "Inpatient"
)

30-Day Readmission Rate =
DIVIDE(
    CALCULATE(
        SUM(fact_claims[readmission_30d_flag]),
        fact_claims[encounter_type] = "Inpatient"
    ),
    [Inpatient Encounters]
)
```

For a final Power BI build, use the cleaned data subset rather than the deliberately injected exception rows.
