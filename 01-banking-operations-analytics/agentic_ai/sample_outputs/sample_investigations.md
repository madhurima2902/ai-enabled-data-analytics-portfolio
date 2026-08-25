# Sample Banking Investigation Outputs

These samples show the intended output style of the Banking Operations Investigation Agent.

The actual numbers will depend on the local PostgreSQL warehouse data when the agent is executed.

---

## 1. Digital Channel Investigation

### Question

```text
Why are digital channels creating more customer pain?
```

### Expected Investigation Logic

The agent compares channels using:

- Total transactions
- Transaction failure rate
- Total complaints
- Complaints per 1,000 transactions
- Open complaints
- Average resolution days

### Expected Output Style

```text
Finding:
Digital channel performance should be evaluated using both transaction failure rate and complaints per 1,000 transactions. This avoids judging channels only by raw complaint volume.

Evidence:
The SQL result ranks channels by normalized complaint burden and failure rate. Channels with both high failure rate and high complaint rate should be treated as higher-risk.

Likely root cause:
The issue is likely linked to failed or friction-heavy digital transactions, especially if Mobile Banking or Internet Banking appear near the top of the result.

Recommended action:
Prioritize reliability review for the highest-risk digital channel. Monitor transaction failure rate, complaints per 1,000 transactions, and open complaints monthly.
```

---

## 2. SLA Breach Investigation

### Question

```text
Which team is driving SLA breaches?
```

### Expected Investigation Logic

The agent compares assigned teams and priorities using:

- Total SLA tickets
- Breached tickets
- SLA breach rate
- SLA met rate

### Expected Output Style

```text
Finding:
The SLA investigation ranks assigned teams by breach rate and ticket volume.

Evidence:
The highest-priority operational focus should be teams where breach rate is high and ticket volume is meaningful.

Likely root cause:
High breach rate may indicate capacity constraints, routing delays, or unresolved high-priority ticket queues.

Recommended action:
Review staffing, escalation rules, and queue routing for high-breach teams. Track SLA breach rate by team and priority monthly.
```

---

## 3. Complaint Root Cause Investigation

### Question

```text
Which complaint categories should operations prioritize?
```

### Expected Investigation Logic

The agent compares complaint categories using:

- Total complaints
- Open complaints
- Resolved complaints
- Resolution rate
- Average resolution days
- Channel and product context

### Expected Output Style

```text
Finding:
Complaint categories should be prioritized based on a combination of volume, open workload, and resolution time.

Evidence:
The SQL result ranks complaint-category, channel, and product combinations by complaint volume and average resolution days.

Likely root cause:
A high-volume category with slow resolution may indicate process complexity, unclear ownership, or support capacity gaps.

Recommended action:
Create a focused complaint reduction workstream for the highest-volume and slowest-resolution category. Monitor complaint volume, open complaints, and average resolution days monthly.
```

---

## 4. Campaign Conversion Investigation

### Question

```text
Which campaign type has weak conversion?
```

### Expected Investigation Logic

The agent compares campaign types using:

- Offers sent
- Engaged customers
- Converted customers
- Engagement rate
- Conversion rate

### Expected Output Style

```text
Finding:
Campaign performance should be assessed by both engagement and conversion. High engagement with low conversion may signal poor product fit or friction after customer interest.

Evidence:
The SQL result ranks campaign types by conversion rate.

Likely root cause:
Campaigns may be generating initial customer interest but not converting due to targeting, offer relevance, or product mismatch.

Recommended action:
Review campaign-product fit and customer segment targeting for low-conversion campaign types.
```
