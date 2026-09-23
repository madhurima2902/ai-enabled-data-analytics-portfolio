# Data Model Notes

## Why a dimensional model?

The reporting layer separates business events from descriptive attributes so Power BI can aggregate operational measures without repeatedly joining large flat extracts.

## Grain

| Table | Grain |
|---|---|
| fact_transactions | One row per transaction |
| fact_complaints | One row per complaint |
| fact_sla_tickets | One row per service ticket |
| dim_customer | One row per customer |
| dim_account | One row per account |
| dim_branch | One row per branch |
| dim_channel | One row per channel |
| dim_date | One row per calendar date |

## Main relationships

```text
dim_customer ─────┐
dim_account  ─────┤
dim_branch   ─────┼──> fact_transactions
dim_channel  ─────┤
dim_date     ─────┘

dim_customer ─────┐
dim_account  ─────┼──> fact_complaints
dim_channel  ─────┤
dim_date     ─────┘

dim_customer ─────┐
dim_date     ─────┼──> fact_sla_tickets
                  └── support-team attributes are stored on the ticket fact
```

## Why grain matters

If one transaction is joined to multiple dimension rows because a supposed business key is not unique, the transaction can be counted more than once. That can inflate transaction counts, amounts, and failure-rate calculations.

Before trusting the dashboard I therefore check:

1. business-ID uniqueness in dimensions
2. duplicate event IDs in facts
3. row counts before and after transformations
4. unmatched foreign-key lookups
5. KPI totals against trusted source counts
