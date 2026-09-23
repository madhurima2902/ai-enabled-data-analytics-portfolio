# MAXX Interview Walkthrough

Target length: **5–6 minutes**

## 1. Why I built it — 30–45 sec

"I built this as a learning project because I wanted to understand what happens before a dashboard. In consulting I often worked with downloaded or already-prepared data. Here I wanted to practice profiling the source, loading it into a database, validating it with SQL, modeling it for reporting, and then using Power BI."

## 2. Business objective — 30–45 sec

"The goal is to create an operational view of banking activity: whether transactions are succeeding, which channels are having problems, whether complaints are being resolved, and whether service teams are meeting SLA."

## 3. Data flow — 45 sec

Show the README flow:

```text
CSV -> Python/Pandas -> PostgreSQL -> SQL checks/model -> Power BI
```

Explain that Python is used for source profiling and basic checks, while SQL is used for database validation, transformation, reconciliation, and KPI logic.

## 4. Data model — 45–60 sec

Show `DATA_MODEL.md`.

Key sentence:

"The grain of the transaction fact is one row per transaction. I learned that being clear about grain is important because a wrong join can duplicate events and distort KPIs."

## 5. One SQL quality check — 60 sec

Open `sql/02_data_quality_checks.sql`.

Show the orphan-account check or duplicate-ID check.

Explain:

"I don't assume that because data loaded successfully it is correct. If this query returned exceptions, I would investigate the source or mapping issue before deciding how to fix it."

## 6. Business query + dashboard — 60–90 sec

Open `sql/03_business_queries.sql` and then an executive/dashboard screenshot.

Explain one KPI, such as transaction failure rate or SLA breach rate.

Then connect it to process improvement:

"If the failure rate suddenly increased, I would break it down by channel, branch, or time period and then investigate what operational process changed."

## 7. Close — 30–45 sec

"The main thing I learned is that the dashboard is only as reliable as the data and definitions behind it. This is still a controlled learning environment that I built myself. What I want next is experience in a real client environment where the schemas already exist, refreshes can fail, requirements change, and other people depend on the output."

## Likely follow-ups to prepare

- Why PostgreSQL?
- Why not load the CSV directly into Power BI?
- What is the grain of each fact table?
- INNER JOIN vs LEFT JOIN?
- Why can a join increase row count?
- How would you detect duplicates?
- How would you investigate a source/warehouse count mismatch?
- What is the difference between validation and reconciliation?
- Why use Python if SQL can also clean data?
- What would be different in production?
