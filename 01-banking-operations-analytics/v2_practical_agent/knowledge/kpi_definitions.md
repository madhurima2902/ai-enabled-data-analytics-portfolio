# Banking Operations KPI Definitions

## Purpose

This document contains approved KPI definitions used by the Banking Operations Agent.

The agent must use these definitions when explaining or interpreting KPIs.
If a requested KPI is not defined in an approved source, the agent must not invent a definition.

## Approved Sources

- `sql/06_business_queries/01_business_kpi_queries.sql`
- `docs/12_business_kpi_queries_notes.md`

## Transaction Success Rate

### Definition

Transaction Success Rate measures the percentage of total transactions that were completed successfully during the selected time period.

### Formula

Transaction Success Rate =  
Successful Transactions / Total Transactions × 100

### Numerator

The numerator is the number of transactions that were completed successfully according to the approved transaction-status logic.

### Denominator

The denominator is the total number of transactions included in the selected reporting period.

### Business Meaning

A higher success rate generally indicates better transaction-processing reliability.

A lower success rate can indicate processing issues, channel problems, system failures, or other operational issues that may require investigation.

## Transaction Failure Rate

### Definition

Transaction Failure Rate measures the percentage of total transactions that failed during the selected time period.

### Formula

Transaction Failure Rate =  
Failed Transactions / Total Transactions × 100

### Numerator

The numerator is the number of transactions that failed according to the approved transaction-status logic.

### Denominator

The denominator is the total number of transactions included in the selected reporting period.

### Business Meaning

A lower failure rate generally indicates better transaction-processing reliability.

A higher failure rate can indicate processing issues, channel problems, system failures, or other operational issues that may require investigation.

## Complaint Resolution Rate

### Definition

Complaint Resolution Rate measures the percentage of total complaints that were resolved during the selected time period.

### Formula

Complaint Resolution Rate =  
Resolved Complaints / Total Complaints × 100

### Numerator

The numerator is the number of complaints classified as resolved according to the approved complaint-resolution logic.

### Denominator

The denominator is the total number of complaints included in the selected reporting period.

### Business Meaning

A higher Complaint Resolution Rate generally indicates that a larger proportion of customer complaints are being resolved.

A lower rate may indicate unresolved backlog, process delays, capacity constraints, complex complaint cases, or other operational issues that may require investigation.

## SLA Breach Rate

### Definition

SLA Breach Rate measures the percentage of service tickets that breached their defined SLA during the selected time period.

### Formula

SLA Breach Rate =  
SLA-Breached Tickets / Total Tickets × 100

### Numerator

The numerator is the number of tickets that breached the applicable SLA according to the approved SLA logic.

### Denominator

The denominator is the total number of tickets included in the selected reporting period.

### Business Meaning

A lower SLA Breach Rate generally indicates better adherence to service-level expectations.

A higher breach rate may indicate processing delays, workload or capacity issues, system problems, process bottlenecks, or other operational issues that may require investigation.

## Campaign Conversion Rate

### Definition

Campaign Conversion Rate measures the percentage of campaign offers sent that resulted in a conversion during the selected reporting period.

### Formula

Campaign Conversion Rate =  
Converted Campaign Offers / Campaign Offers Sent × 100

### Numerator

The numerator is the number of campaign records classified as converted according to the approved campaign-conversion logic.

### Denominator

The denominator is the total number of campaign offers sent during the selected reporting period.

### Business Meaning

A higher Campaign Conversion Rate indicates that a larger proportion of campaign offers resulted in the desired conversion outcome.

A lower conversion rate may indicate issues with campaign targeting, offer relevance, product-market fit, communication strategy, or other factors that require further investigation.

## Complaints per 1,000 Transactions

### Definition

Complaints per 1,000 Transactions measures the number of complaints recorded for every 1,000 transactions during the selected reporting period.

### Formula

Complaints per 1,000 Transactions =  
Complaints / Transactions × 1,000

### Numerator

The numerator is the number of complaints included in the selected reporting period according to the approved complaint logic.

### Denominator

The denominator is the total number of transactions included in the selected reporting period.

### Business Meaning

A lower value generally indicates fewer complaints relative to transaction activity.

A higher value indicates greater complaint volume relative to transaction activity and may require investigation into products, channels, processes, or other operational drivers.