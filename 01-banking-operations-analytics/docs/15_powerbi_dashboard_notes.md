# Power BI Dashboard Notes

## Dashboard Objective

The objective of this Power BI dashboard is to provide a business-facing view of banking operations performance across transactions, channels, complaints, SLA tickets, and campaign engagement.

The dashboard is designed for operations, analytics, and business stakeholders who need to monitor:

- Overall banking operations health
- Digital vs non-digital channel performance
- Customer complaint drivers
- SLA and operational bottlenecks
- Campaign engagement and conversion performance

---

## Data Model Used

The Power BI report connects to the PostgreSQL warehouse layer of the banking operations analytics project.

The model follows a star-schema style structure using fact and dimension tables.

### Fact Tables

- `fact_transactions`
- `fact_complaints`
- `fact_sla_tickets`
- `fact_campaigns`

### Dimension Tables

- `dim_customer`
- `dim_account`
- `dim_product`
- `dim_branch`
- `dim_channel`
- `dim_date`

The fact tables capture business events, while the dimension tables provide business context for filtering and slicing the data.

---

## Dashboard Pages

## 1. Executive Overview

### Business Objective

Provide leadership with a high-level summary of banking operations health.

### Business Questions Answered

- How many transactions occurred?
- What is the total transaction amount?
- What is the transaction success rate?
- What is the complaint volume?
- What is the complaint resolution rate?
- What is the SLA breach rate?
- What is the campaign conversion rate?
- What is the digital transaction rate?

### Key KPIs

- Total Transactions
- Total Transaction Amount
- Transaction Success Rate %
- Digital Transaction Rate %
- Total Complaints
- Complaint Resolution Rate %
- SLA Breach Rate %
- Campaign Conversion Rate %

### Main Visuals

- Transaction trend over time
- SLA breach rate by team
- Total complaints by channel
- Total complaints by complaint category
- Campaign conversion rate by campaign type

### Business Value

This page gives leadership a quick snapshot of operational volume, quality, customer pain, SLA performance, and campaign effectiveness.

---

## 2. Channel Performance: Digital vs Non-Digital Analysis

### Business Objective

Compare digital and non-digital channel performance across transaction volume, value, quality, and complaint burden.

### Business Questions Answered

- Are digital or non-digital channels driving more transactions?
- Is digital adoption increasing or stable over time?
- Which channels have higher transaction failure rates?
- Which channels generate more complaints relative to transaction volume?
- Which channels contribute higher transaction value?

### Key KPIs

- Digital Transaction Rate %
- Non-Digital Transaction Rate %
- Transaction Success Rate %
- Transaction Failure Rate %
- Average Fee per Transaction
- Complaints per 1,000 Transactions

### Main Visuals

- Total transactions by channel group
- Digital transaction rate trend
- Channel health scatter plot
- Complaints per 1,000 transactions by channel
- Transaction amount by channel
- Transaction failure rate by channel

### Business Value

This page helps identify whether digital channels are performing better or worse than non-digital channels. It uses normalized metrics such as complaints per 1,000 transactions to avoid misleading comparisons based only on raw complaint counts.

### Model Note

Channel analysis is based on the relationship between `dim_channel` and the transaction, complaint, and campaign fact tables.

---

## 3. Complaints & Customer Pain Analysis

### Business Objective

Identify complaint drivers and customer pain areas across category, channel, product, customer segment, and resolution status.

### Business Questions Answered

- How many complaints were logged?
- How many complaints are open or resolved?
- What is the complaint resolution rate?
- Are complaints increasing or stable over time?
- Which categories drive the most complaints?
- Which channels and products are associated with more complaints?
- Which complaint categories take longer to resolve?

### Key KPIs

- Total Complaints
- Open Complaints
- Resolved Complaints
- Complaint Resolution Rate %
- Average Resolution Days
- Complaints per 1,000 Transactions

### Main Visuals

- Complaint trend over time
- Complaints by complaint status
- Complaints by customer segment
- Total complaints by category
- Total complaints by channel
- Total complaints by product
- Average resolution days by category

### Business Value

This page is organized into complaint health, complaint drivers, and resolution bottlenecks. It helps business users understand where customer pain is coming from and which issue categories may need operational attention.

---

## 4. SLA & Operations Performance Analysis

### Business Objective

Monitor whether service tickets are being resolved within SLA and identify teams, priorities, and statuses contributing to SLA breaches.

### Business Questions Answered

- How many SLA tickets were created?
- How many tickets met SLA?
- How many tickets breached SLA?
- Is SLA ticket volume changing over time?
- Which teams have higher SLA breach rates?
- Which teams handle the highest ticket volume?
- Which priorities have higher SLA breach rates?
- How are tickets distributed by status?

### Key KPIs

- Total SLA Tickets
- SLA Met Tickets
- SLA Breached Tickets
- SLA Met Rate %
- SLA Breach Rate %

### Main Visuals

- SLA ticket trend over time
- SLA met vs breached over time
- SLA breach rate by customer segment
- SLA breach rate by team
- Ticket volume by team
- SLA breach rate by priority
- SLA tickets by status

### Business Value

This page helps identify operational bottlenecks and teams or ticket priorities that may need attention.

### Model Limitation

Channel and product slicers were not used on this page because the SLA ticket fact table is not directly linked to the channel or product dimensions in the current model. This avoids misleading filter behavior.

---

## 5. Campaign & Customer Engagement Analysis

### Business Objective

Evaluate campaign outreach, engagement, and conversion performance across campaign type, customer segment, product, channel, and time.

### Business Questions Answered

- How many campaign offers were sent?
- How many customers engaged?
- How many customers converted?
- What is the campaign engagement rate?
- What is the campaign conversion rate?
- Which campaign types convert better?
- Which products and customer segments respond better?
- Which channels perform better for campaign outreach?

### Key KPIs

- Campaign Offers Sent
- Engaged Customers
- Converted Customers
- Campaign Engagement Rate %
- Campaign Conversion Rate %
- Targeted Customers

### Main Visuals

- Campaign funnel: offers sent, engaged, converted
- Campaign conversion rate trend
- Conversion rate by campaign type
- Engagement rate by campaign type
- Conversion rate by customer segment
- Conversion rate by product
- Conversion rate by channel

### Business Value

This page shows the customer engagement funnel and helps identify which campaign strategies, products, channels, and customer segments are more effective.

---

## Key Measures Created

The Power BI semantic model includes reusable measures across five analytical areas.

### Transaction Measures

- Total Transactions
- Total Transaction Amount
- Successful Transactions
- Failed Transactions
- Transaction Success Rate %
- Transaction Failure Rate %
- Average Transaction Amount
- Total Fee Amount
- Average Fee per Transaction
- Fee Rate %

### Channel Measures

- Digital Transactions
- Non-Digital Transactions
- Digital Transaction Rate %
- Non-Digital Transaction Rate %
- Complaints per 1,000 Transactions

### Complaint Measures

- Total Complaints
- Open Complaints
- Resolved Complaints
- Complaint Resolution Rate %
- Average Resolution Days
- Average Complaints per Customer

### SLA Measures

- Total SLA Tickets
- SLA Met Tickets
- SLA Breached Tickets
- SLA Met Rate %
- SLA Breach Rate %

### Campaign Measures

- Campaign Offers Sent
- Engaged Customers
- Converted Customers
- Campaign Engagement Rate %
- Campaign Conversion Rate %
- Targeted Customers

---

## Data Analyst Concepts Applied

This dashboard applies the following data analyst and BI concepts:

- Business objective definition
- Business question mapping
- Grain identification
- Fact and dimension modeling
- Star schema design
- Measure creation
- KPI definition
- Filter context
- Valid relationship-based slicing
- Normalized metrics
- Trend analysis
- Operational bottleneck analysis
- Dashboard storytelling

---

## Model Limitations

This is a synthetic portfolio project and not a production banking dataset.

Known limitations:

- The data is synthetic and created for analytics demonstration.
- Some business rules are simplified for portfolio use.
- SLA analysis does not use channel or product slicers because the SLA fact table is not directly related to those dimensions.
- Date slicers use the full date dimension range, which may be broader than the active data range for specific fact tables.
- Some advanced analytics, such as repeat-targeted non-converters and campaign fatigue, can be added in future iterations.

---

## AI-Assisted Workflow Note

AI was used as a productivity assistant for planning, structuring, documentation, and review support.

All business logic, SQL modeling decisions, validation checks, Power BI measures, and dashboard design choices were reviewed and implemented by the analyst.

---

## Interview Explanation

This project is an end-to-end banking operations analytics portfolio project.

I created synthetic banking data, loaded it into PostgreSQL, designed raw, staging, and warehouse layers, and built fact and dimension tables for transactions, complaints, SLA tickets, campaigns, customers, accounts, products, branches, channels, and dates.

I then connected Power BI to the warehouse layer and created a five-page dashboard covering executive KPIs, channel performance, complaints and customer pain, SLA operations, and campaign engagement.

Before creating measures, I identified the grain of each fact table. For example, one row in `fact_transactions` represents one transaction, one row in `fact_complaints` represents one complaint, one row in `fact_sla_tickets` represents one service ticket, and one row in `fact_campaigns` represents one campaign offer sent to one customer.

The dashboard uses reusable measures such as transaction success rate, complaint resolution rate, SLA breach rate, complaints per 1,000 transactions, and campaign conversion rate. I also considered model limitations, such as avoiding channel and product slicers on the SLA page where those relationships are not directly supported.