# Operational Data Generation

## Objective

Generate clean operational datasets for complaints, campaigns, and SLA tickets for the Banking Operations Analytics project.

## Output Files

- `data/raw/raw_complaints.csv`
- `data/raw/raw_campaigns.csv`
- `data/raw/raw_sla_tickets.csv`

## Target Volumes

- Complaints: 2,000 records
- Campaigns: 5,000 records
- SLA tickets: 4,000 records

## Input Files Used

- `data/raw/raw_customers.csv`
- `data/raw/raw_accounts.csv`
- `data/raw/raw_products.csv`
- `data/raw/raw_channels.csv`

## Business Logic

The complaints dataset represents customer service issues across different banking products and service channels.

The campaigns dataset represents marketing outreach activity across eligible banking customers and product offers.

The SLA tickets dataset represents operational service tickets linked to complaints, including priority, target resolution time, due datetime, resolved datetime, and SLA met flag.

## Validation Checks

The validation script checks:

- Row counts for complaints, campaigns, and SLA tickets
- Unique complaint, campaign, and ticket IDs
- Complaint customers exist in customer master data
- Complaint accounts exist in account master data
- Complaint products exist in product reference data
- Complaint channels exist in channel reference data
- Campaign customers exist in customer master data
- Campaign offer products exist in product reference data
- Campaign channels exist in channel reference data
- SLA ticket complaints exist in complaint data
- SLA ticket customers and accounts exist in master data
- Status values are valid
- Resolved complaints have valid resolution dates
- Open complaints do not have resolution dates
- Campaign response dates are valid
- Ticket due datetime is not before created datetime
- Resolved tickets have valid resolved datetime

## AI-Assisted Dataset Generation Approach

This operational data was generated using Python with AI assistance to accelerate the creation of realistic synthetic banking datasets.

AI was used as a productivity assistant to help draft the Python structure for complaints, campaigns, and SLA tickets, including reusable date logic, controlled category values, row count targets, and validation checks.

The generated code was reviewed before execution to ensure that:

- Complaints link to valid customers, accounts, products, and channels
- Campaigns link to valid customers, product offers, and channels
- SLA tickets link to valid complaints, customers, and accounts
- Date fields follow realistic business rules
- Validation logic is separated from generation logic
- The generated datasets support downstream SQL, warehouse modeling, and Power BI reporting

The datasets were then validated using a separate Python validation script. This helped confirm row counts, uniqueness, referential integrity, valid statuses, and date consistency.

This approach demonstrates practical AI-assisted analytics development, where AI helps reduce manual coding time while the analyst remains responsible for reviewing business rules, validating outputs, and ensuring the generated data is fit for analytics.

## Status

Operational data generation completed successfully.
