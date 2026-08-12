# Commercial Auto Insurance Analytics

> **Portfolio note:** This project is inspired by a real one-time pro bono analytics engagement I supported. The business problem, analytical workflow, KPI definitions, reconciliation logic, and data-quality issue categories reflect the work I actually performed. However, **no client or source-system data is included in this repository**. All records, identifiers, dates, names, amounts, and distributions published here are **synthetically generated** to preserve confidentiality while reproducing the same type of analysis.

## Project Overview

The project analyzes 24 months of commercial auto insurance data across the quote-to-policy-to-claim lifecycle. The synthetic dataset is designed to mirror the approximate scale and structure needed to reproduce the original analytical work while remaining safe for public GitHub use.

Approximate synthetic volumes:

- 80,000 quotes
- 32,000 policy terms
- 40,000 vehicles
- 6,500 claims
- Premium records aligned to policy terms
- Approximately 1,200 intentionally seeded data-quality exceptions

## Business Objectives

### Performance analytics

- Quote-to-bind conversion
- Retention
- Written premium
- Loss ratio
- Claim frequency
- Claim severity

### Data quality and reconciliation

- Duplicate records
- Missing or orphan keys
- Quote-to-policy mismatches
- Policy-to-vehicle mismatches
- Policy-to-premium inconsistencies
- Claim-to-policy inconsistencies
- Invalid date relationships
- Business-rule exceptions

These exception categories are based on the types of issues investigated during the original work. The public synthetic dataset intentionally recreates comparable defects so the profiling and reconciliation approach can be demonstrated without exposing confidential information.

## Technology Stack

- SQL
- PostgreSQL
- Snowflake / Snowflake-compatible SQL analysis
- Power Query
- Power BI
- Python for synthetic data generation

## Planned Repository Structure

```text
03-commercial-auto-insurance-analytics/
├── README.md
├── data/
│   ├── quotes.csv
│   ├── policies.csv
│   ├── vehicles.csv
│   ├── premiums.csv
│   └── claims.csv
├── scripts/
│   └── generate_synthetic_data.py
├── sql/
│   ├── 01_data_profiling.sql
│   ├── 02_reconciliation_checks.sql
│   └── 03_kpi_analysis.sql
├── agent/
│   └── dq_exception_agent.py
└── docs/
    └── exception_catalog.md
```

## Data-Quality Validation Goal

The synthetic data generator will intentionally seed approximately 1,200 exceptions across quote, policy, vehicle, premium, and claims data. The reconciliation SQL will independently rediscover those exceptions and summarize them by exception type.

This provides a reproducible demonstration of the original analytical approach while keeping the underlying engagement confidential.

## Simple Agentic AI Use Case

The AI component is intentionally small and practical.

A **Data Quality Exception Investigation Agent** will take a flagged exception category, run the relevant SQL check, inspect the affected records, and return a short business-facing summary containing:

- What failed
- How many records were affected
- Where the issue is concentrated
- A likely root cause
- A recommended remediation action

The goal is not to build an unnecessarily complex multi-agent architecture. The agent demonstrates how AI can support an analyst by accelerating a repetitive exception-investigation workflow.

## Resume Alignment

This portfolio project is designed to demonstrate the work represented by the following experience statements:

- Analyzed 24 months of anonymized commercial auto insurance data using SQL and Snowflake, covering approximately 80,000 quotes, 32,000 policy terms, 40,000 vehicles, and 6,500 claims.
- Developed Excel and Power BI dashboards tracking written premium and KPIs including conversion, retention, loss ratio, claim frequency, and claim severity.
- Profiled and reconciled quote, policy, vehicle, premium, and claims data using PostgreSQL and Power Query, identifying approximately 1,200 duplicate, missing-key, and business-rule exceptions.

## Confidentiality Statement

This repository contains **no original client data, proprietary source-system extracts, real customer information, real policy or claim identifiers, or confidential business information**. The public dataset is synthetically generated specifically for portfolio demonstration. The project preserves the nature of the business problem and analytical methods while replacing the underlying confidential records and values.
