# Healthcare KPI Dictionary

## 1. Claim Denial Rate

**Definition:** Percentage of clean claim rows with `claim_status = 'Denied'`.

**Formula:**

```text
Denied Claims / Total Clean Claims
```

**Use:** Helps identify payer, provider, authorization, coding, eligibility, or documentation issues that may affect revenue-cycle performance.

---

## 2. Paid Reimbursement Rate

**Definition:** Paid amount divided by submitted amount for claims that reached paid status.

**Formula:**

```text
Total Paid Amount on Paid Claims / Total Submitted Amount on Paid Claims
```

**Use:** Shows how much of the originally submitted charge was ultimately reimbursed in the simplified dataset.

**Important:** This project does not treat the metric as a universal industry benchmark. Contracting rules and claim adjudication are more complex in real organizations.

---

## 3. Average Processing Days

**Definition:** Mean number of days recorded between claim submission/processing milestones in the synthetic analytical fact.

**Formula:**

```text
SUM(Processing Days) / Number of Claims
```

**Use:** Operational indicator for claim turnaround.

---

## 4. Payer Mix

**Definition:** Distribution of claim count, submitted amount, or paid amount by payer type.

**Payer Types in This Project:**
- Commercial
- Medicare
- Medicaid
- Self-Pay

**Use:** Helps explain differences in volume, reimbursement, and denial patterns.

---

## 5. Average Inpatient Length of Stay

**Definition:** Average `length_of_stay_days` for inpatient encounters only.

**Formula:**

```text
Total Inpatient Days / Inpatient Encounters
```

**Use:** Utilization and operational-efficiency indicator. In real healthcare settings, comparisons should account for case mix and clinical context.

---

## 6. 30-Day Inpatient Readmission Rate

**Definition:** Share of inpatient encounters with `readmission_30d_flag = 1`.

**Formula:**

```text
30-Day Readmission-Flagged Inpatient Encounters / Total Inpatient Encounters
```

**Use:** Demonstrates familiarity with a common healthcare utilization concept.

**Important:** This synthetic flag is generated for analytics practice. It is not built from a real clinical readmission methodology and should not be compared with regulatory or hospital-quality benchmarks.

---

## 7. Provider Denial Rate

**Definition:** Denied claims divided by total clean claims for each provider.

**Use:** Supports provider-level operational review. A high rate should trigger investigation, not an automatic conclusion about provider quality.

---

## Data-Quality Rule Before KPI Reporting

A claim is excluded from the clean analytical subset when it has any of the following:

- duplicate `claim_id`
- patient key not found in patient dimension
- provider key not found in provider dimension
- negative submitted, allowed, or paid amount
- negative processing days

This keeps data-quality profiling separate from KPI reporting.
