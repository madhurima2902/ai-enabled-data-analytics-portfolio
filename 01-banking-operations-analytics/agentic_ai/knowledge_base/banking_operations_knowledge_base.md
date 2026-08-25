# Banking Operations Knowledge Base

## Project Context

The Banking Operations Analytics project simulates a retail banking analytics environment using Python-generated data, PostgreSQL, SQL transformations, data quality checks, warehouse modeling, and Power BI reporting.

The current V1 project includes January data and covers transactions, complaints, SLA tickets, campaigns, customers, accounts, products, branches, channels, and dates.

## Warehouse Model

The Power BI report connects to the PostgreSQL warehouse layer.

Core fact tables:

- `warehouse.fact_transactions`
- `warehouse.fact_complaints`
- `warehouse.fact_sla_tickets`
- `warehouse.fact_campaigns`

Core dimension tables:

- `warehouse.dim_customer`
- `warehouse.dim_account`
- `warehouse.dim_product`
- `warehouse.dim_branch`
- `warehouse.dim_channel`
- `warehouse.dim_date`

## KPI Definitions

### Transaction Success Rate

Transaction Success Rate measures the share of successful transactions out of total transactions.

Formula:

```text
Successful Transactions / Total Transactions
```

Business interpretation: lower success rate or higher failure rate can indicate channel reliability issues, customer friction, or operational processing problems.

### Transaction Failure Rate

Transaction Failure Rate measures failed transactions out of total transactions.

Formula:

```text
Failed Transactions / Total Transactions
```

Business interpretation: high failure rate should be reviewed by channel, product, customer segment, and date.

### Digital Transaction Rate

Digital Transaction Rate measures the share of transactions coming from digital channels.

Formula:

```text
Digital Transactions / Total Transactions
```

Digital channels include channels where `dim_channel.is_digital = true`.

Business interpretation: high digital adoption is positive only if failure rates and complaint rates remain controlled.

### Complaints per 1,000 Transactions

Complaints per 1,000 Transactions normalizes complaint volume by transaction volume.

Formula:

```text
1000 * Total Complaints / Total Transactions
```

Business interpretation: this is stronger than raw complaint count because large-volume channels naturally receive more complaints. A high normalized complaint rate signals customer friction.

### Complaint Resolution Rate

Complaint Resolution Rate measures resolved complaints out of total complaints.

Formula:

```text
Resolved Complaints / Total Complaints
```

Business interpretation: low resolution rate or high open complaint volume can indicate operational backlog or process bottlenecks.

### Average Resolution Days

Average Resolution Days measures the average time taken to resolve complaints.

Business interpretation: higher values suggest slower customer issue resolution and potential customer dissatisfaction.

### SLA Breach Rate

SLA Breach Rate measures breached SLA tickets out of total SLA tickets.

Formula:

```text
SLA Breached Tickets / Total SLA Tickets
```

Business interpretation: high breach rate can indicate support capacity gaps, queue management issues, team-level bottlenecks, or high-priority ticket delays.

### Campaign Engagement Rate

Campaign Engagement Rate measures engaged customers out of campaign offers sent.

Formula:

```text
Engaged Customers / Campaign Offers Sent
```

### Campaign Conversion Rate

Campaign Conversion Rate measures converted customers out of campaign offers sent.

Formula:

```text
Converted Customers / Campaign Offers Sent
```

Business interpretation: high engagement but low conversion may indicate poor product fit, weak offer design, friction after customer interest, or repeat targeting issues.

## Investigation Playbook

### Digital Channel Reliability

Question pattern:

```text
Why are digital channels creating more customer pain?
```

Recommended investigation:

1. Compare total transactions by channel.
2. Compare transaction failure rate by channel.
3. Compare complaints per 1,000 transactions by channel.
4. Identify whether digital channels have higher failure or complaint burden.
5. Review complaint categories related to transaction failure or digital banking.
6. Recommend reliability review for the highest-risk digital channel.

Suggested action:

```text
Prioritize reliability review for channels with high transaction failure rate and high complaints per 1,000 transactions. Track failure rate, complaint rate, and SLA impact monthly.
```

### Complaint Root Cause

Question pattern:

```text
Which complaint categories should operations prioritize?
```

Recommended investigation:

1. Rank complaint categories by total complaint count.
2. Review open complaints by category.
3. Review average resolution days by category.
4. Prioritize categories with high volume and slow resolution.

Suggested action:

```text
Create category-level complaint reduction workstreams for high-volume and slow-resolution categories.
```

### SLA Breach Investigation

Question pattern:

```text
Which team is driving SLA breaches?
```

Recommended investigation:

1. Rank assigned teams by SLA breach rate.
2. Compare team ticket volume.
3. Review ticket priority distribution.
4. Prioritize teams with high breach rate and meaningful ticket volume.

Suggested action:

```text
Review capacity, routing, and escalation processes for teams with high SLA breach rate and high ticket volume.
```

### Campaign Conversion Investigation

Question pattern:

```text
Which campaign type has weak conversion?
```

Recommended investigation:

1. Rank campaign types by conversion rate.
2. Compare engagement rate and conversion rate.
3. Identify campaign types with high engagement but weak conversion.
4. Review product and customer segment alignment.

Suggested action:

```text
Refine targeting and product fit for campaign types where engagement does not translate into conversion.
```
