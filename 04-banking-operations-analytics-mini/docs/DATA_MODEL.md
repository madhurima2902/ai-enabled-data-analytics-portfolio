# Data Model Walkthrough

## What I would explain first

The purpose of the reporting model is to make business KPIs easier to calculate reliably.

I separate **events** from **descriptive information**. Transactions, complaints, and service tickets are events, so they become fact tables. Customer, account, branch, channel, and date provide context for those events, so they become dimensions.

This is a dimensional reporting model designed for analysis and Power BI.

## Fact tables and grain

| Table | Grain | What one row means |
|---|---|---|
| `fact_transactions` | One row per transaction | One banking transaction event |
| `fact_complaints` | One row per complaint | One customer complaint |
| `fact_sla_tickets` | One row per service ticket | One operational service ticket |

The word **grain** means the business meaning of a single row.

I define grain before calculating KPIs because an incorrect join can duplicate event rows. For example, if one transaction joins to three dimension rows, Power BI may count three transactions even though only one transaction occurred.

## Dimension tables

| Dimension | Purpose |
|---|---|
| `dim_customer` | Customer attributes such as segment and risk band |
| `dim_account` | Account attributes and links to customer and branch |
| `dim_branch` | Branch, city, state, and region information |
| `dim_channel` | Channel name, category, and digital/non-digital classification |
| `dim_date` | Calendar attributes used for time-based reporting |

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
                  └── support-team attributes remain on the ticket fact
```

## Why I use dimension keys

The reporting fact tables store links to dimensions such as `customer_key`, `account_key`, and `channel_key`.

The source systems may provide business IDs such as `customer_id` or `account_id`. In the reporting model I generate keys for the dimensions and retain the business IDs for traceability.

This gives me a controlled reporting relationship while still allowing me to trace a record back to the source identifier.

## What I validate before trusting the model

Before using the model for reporting, I check:

- Each dimension business ID that should be unique is actually unique.
- Event IDs such as `transaction_id` are not duplicated in the fact table.
- Row counts reconcile between validated staging and the reporting layer.
- Fact records can successfully resolve the dimension keys they require.
- KPI totals match trusted source or staging totals after expected cleaning rules.

## How I would explain this to a nontechnical reviewer

I would describe the model as separating **what happened** from **information about where, when, and to whom it happened**.

For example:

- A transaction is **what happened**.
- The customer, account, channel, branch, and date explain **the context around that transaction**.

That structure lets a business user ask questions such as:

- Which channels have the highest failure rate?
- Which branches have unusual transaction patterns?
- Which customer segments are seeing more complaints?
- Are service problems concentrated in a specific period?

## How I would explain this to a technical reviewer

I would describe it as a dimensional/star-style reporting model with clearly defined fact-table grain, dimension keys, unique business IDs, and validation checks designed to prevent join-driven duplication or unresolved relationships.
