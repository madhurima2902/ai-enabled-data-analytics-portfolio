# Project Walkthrough

This document is a presenter-friendly guide to the project. It is written in full sentences so the project can be explained naturally while the files and dashboard screenshots are open.

## 1. Start with the business objective

I built this project to understand the full path from source data to a business-facing report.

The reporting scenario is retail banking operations. I wanted to answer operational questions such as whether transactions are succeeding, whether problems are concentrated in a particular channel, whether customer complaints are being resolved, and whether service teams are meeting SLA expectations.

The important point is that I do not start with the dashboard. I first make sure the data behind the dashboard is reliable.

## 2. Explain the data flow

The source data is synthetic and stored as files.

I use Python and Pandas for initial profiling because they make it easy to inspect files for row counts, missing values, duplicates, and status distributions.

I use PostgreSQL as the relational database.

Once the data is in the database, I use SQL for validation, reconciliation, reporting-model construction, and business analysis.

Power BI is the final visualization and investigation layer.

The overall flow is:

```text
Source files
→ Python/Pandas profiling
→ PostgreSQL staging
→ SQL validation and transformation
→ Fact/dimension reporting model
→ Power BI
→ Operational investigation
```

## 3. Explain the Power BI pages before showing code

### Executive overview

The executive overview answers whether the overall operation appears healthy and whether any KPI needs deeper investigation.

I would not read every card on the page. I would choose one metric, such as transaction failure rate, and explain what I would do if it changed materially.

If failure rate increases, the next question is not simply “why is the number higher?” The next question is “where is the increase concentrated?”

### Channel performance

The channel page helps answer that question.

If the total failure rate rises but most of the increase comes from mobile banking while other channels remain stable, the issue is likely more localized than a bank-wide failure.

That gives the operations team a more useful starting point for investigation.

### Complaints

Complaints provide a second perspective: customer impact.

If a channel has worsening transaction performance and customer complaints rise in the same period, that strengthens the evidence that the operational issue is real and customer-facing.

### SLA performance

The SLA page looks at the internal service process.

If one support team or priority level has a higher breach rate, I would investigate capacity, prioritization, handoffs, queue management, or opportunities to automate part of the process.

This is where the project connects most directly to process improvement.

## 4. Show one data-quality check

I would then open `sql/02_data_quality_checks.sql`.

I would explain that a dashboard can look correct even when the underlying data is wrong, so I included checks before trusting the KPIs.

A good example is the orphan-account query.

The business question is: **Do I have any transaction referencing an account that does not exist in the account data?**

Technically, I use a LEFT JOIN from transactions to accounts and look for NULL on the account side.

If the query returns records, I investigate the cause before deleting or changing anything. Possible causes include an incomplete source load, an identifier mismatch, or genuinely invalid data.

## 5. Explain reconciliation

Another important check is row-count reconciliation.

If 25,000 validated transactions enter the transformation process and only 24,700 reach the reporting table, I need to explain the missing 300 records before trusting the dashboard.

The difference may be expected, for example because known duplicate records were removed. It may also indicate a transformation or relationship problem.

The important point is that the difference must be explainable.

## 6. Explain grain and the reporting model

I would next open `docs/DATA_MODEL.md`.

The grain of `fact_transactions` is one row per transaction.

The grain of `fact_complaints` is one row per complaint.

The grain of `fact_sla_tickets` is one row per service ticket.

This matters because a join can accidentally multiply rows. One real transaction can become several reporting rows if the dimension key on the other side is not unique.

That can create a believable but incorrect KPI.

## 7. Show a business SQL query if the reviewer wants technical depth

I would open `sql/03_business_queries.sql`.

One useful example is transaction failure rate by channel.

The query groups transactions by channel, counts failed transactions, divides by the total transaction count, and sorts the channels by failure rate.

The business purpose is not to demonstrate GROUP BY syntax. The purpose is to identify where an operational problem is concentrated.

## 8. Close with what I learned

The main learning from this project is that visualization is only the final layer.

Before a KPI becomes useful, I need to understand the source data, define the row grain, validate relationships, reconcile the processing layers, and make sure the KPI definition is correct.

The project also reinforces how I like to work: use data to identify where an operation is underperforming, then investigate the process behind that result.

This project uses a controlled learning environment and synthetic data. The next level for me is applying the same reasoning in an existing client environment with real schemas, refresh dependencies, change controls, failures, and downstream users.
