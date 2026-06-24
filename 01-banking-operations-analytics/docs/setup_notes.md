# Setup Notes

## Local Environment

Tool setup for the Banking Operations Analytics project.

## Installed Tools

| Tool | Version / Notes |
|---|---|
| PostgreSQL | 18 |
| pgAdmin | pgAdmin 4 |
| Python | Used for synthetic data generation |
| GitHub | Used for version control |

## Database Configuration

| Item | Value |
|---|---|
| Database Name | banking_analytics_db |
| Database Port | 5432 |
| Database Superuser | postgres |
| Locale | Default |

## PostgreSQL Schemas

| Schema | Purpose |
|---|---|
| raw | Stores source CSV data with minimal transformation |
| staging | Stores cleaned and standardized data |
| warehouse | Stores fact and dimension tables |
| dq | Stores data quality checks and validation queries |
| analytics | Stores reporting views or final analytical outputs |

## Completion Notes

- PostgreSQL installed successfully
- pgAdmin configured successfully
- Local PostgreSQL server connected
- Project database created
- Project schemas created
- Setup SQL script added to repository
