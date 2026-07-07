# PostgreSQL Raw Layer Loading

## Objective

Create PostgreSQL raw layer tables and load clean source CSV files into the `raw` schema.

## Database

`banking_analytics_db`

## Schema

`raw`

## Tables Created

- raw.customers
- raw.accounts
- raw.products
- raw.branches
- raw.channels
- raw.complaints
- raw.campaigns
- raw.sla_tickets
- raw.transactions

## Source CSV Files Loaded

- `data/raw/raw_customers.csv`
- `data/raw/raw_accounts.csv`
- `data/raw/raw_products.csv`
- `data/raw/raw_branches.csv`
- `data/raw/raw_channels.csv`
- `data/raw/raw_complaints.csv`
- `data/raw/raw_campaigns.csv`
- `data/raw/raw_sla_tickets.csv`
- `data/raw/raw_transactions_jan.csv`

## Row Count Validation

Expected row counts:

| Table | Expected Rows |
|---|---:|
| raw.customers | 10,000 |
| raw.accounts | 15,000 |
| raw.products | 7 |
| raw.branches | 20 |
| raw.channels | 6 |
| raw.complaints | 2,000 |
| raw.campaigns | 5,000 |
| raw.sla_tickets | 4,000 |
| raw.transactions | 25,000 |

## Loading Approach

CSV files were loaded into PostgreSQL using a Python loader script with `psycopg2`.

The loader script performs the following steps:

1. Connects to PostgreSQL database `banking_analytics_db`
2. Truncates each raw table before loading
3. Loads each CSV file into the matching raw table
4. Prints row counts after each load

## Validation Approach

A SQL validation script was created to compare actual row counts against expected row counts.

This confirms that the clean raw source files were loaded successfully into PostgreSQL before downstream staging and warehouse transformations.

## AI-Assisted Development Approach

AI assistance was used to accelerate the creation of the raw table DDL, Python loading script, and SQL row-count validation script.

The generated logic was reviewed before execution to ensure that:

- Table columns matched the generated CSV file structures
- Data types were appropriate for raw-layer ingestion
- CSV loading used local files safely through Python
- No credentials were stored in code
- Row counts were validated after loading
- Raw tables avoided strict constraints so future controlled data-quality issues can still be loaded and detected later

This approach demonstrates practical AI-assisted analytics development, where AI helps reduce setup time while the analyst remains responsible for validating schema design, load logic, and data quality results.

## Status

PostgreSQL raw layer creation and CSV loading completed successfully.