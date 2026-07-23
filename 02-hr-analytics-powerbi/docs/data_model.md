# Data Model Documentation

## Model Overview

The Power BI report uses a fact and dimension model to support HR analytics reporting across employees, performance reviews, dates, ratings, satisfaction levels, and education levels.

The model is designed around one main fact table:

- `fact_PerformanceRating`

and supporting dimension tables:

- `dim_Employee`
- `dim_EducationLevel`
- `dim_RatingLevel`
- `dim_SatisfiedLevel`
- `Dim_Date`

A separate `_Measure` table stores DAX measures.

## Tables

| Table | Type | Description |
|---|---|---|
| `fact_PerformanceRating` | Fact | Stores employee performance review records. One employee can have multiple review records across years. |
| `dim_Employee` | Dimension | Stores employee-level attributes such as department, job role, salary, hire date, attrition status, demographics, overtime, travel, and tenure. |
| `dim_EducationLevel` | Dimension | Lookup table for employee education levels. |
| `dim_RatingLevel` | Dimension | Lookup table for rating score labels. |
| `dim_SatisfiedLevel` | Dimension | Lookup table for satisfaction score labels. |
| `Dim_Date` | Dimension | Date table used for hire-year and review-year analysis. |
| `_Measure` | Measure table | Stores report-level DAX measures. |

# Data Model Documentation

## Model Approach

The dashboard uses a fact and dimension structure to support clean filtering, reusable measures, and stakeholder-focused reporting.

## Table Grain

| Table | Grain |
|---|---|
| `dim_Employee` | One row per employee |
| `fact_PerformanceRating` | One row per employee performance review |
| `dim_EducationLevel` | One row per education level |
| `dim_RatingLevel` | One row per rating level |
| `dim_SatisfiedLevel` | One row per satisfaction level |
| `Dim_Date` | One row per calendar date |

## Key Modeling Decisions

### 1. Employee and performance review separation

Employee profile data is stored in `dim_Employee`, while yearly review scores are stored in `fact_PerformanceRating`.

This is important because employees can have multiple performance reviews over time.

### 2. Date table

A dedicated `Dim_Date` table supports time-based analysis.

It is used for:

- Hiring trend analysis
- Hire-year attrition analysis
- Performance review trend analysis

### 3. Inactive relationships

Some relationships are intentionally inactive because Power BI cannot keep multiple active paths between the same tables without ambiguity.

For example:

- `Dim_Date` can support both hire date and review date analysis.
- Rating and satisfaction lookup tables can map to multiple rating columns.

DAX measures use `USERELATIONSHIP()` where specific inactive relationships need to be activated.

### 4. Measure table

The `_Measure` table keeps DAX measures centralized and easier to manage.

## Main Fields Used

### `dim_Employee`

Important fields include:

- `EmployeeID`
- `FullName`
- `Gender`
- `Age`
- `AgeBin`
- `BusinessTravel`
- `Department`
- `Ethnicity`
- `JobRole`
- `MaritalStatus`
- `Salary`
- `StockOptionLevel`
- `OverTime`
- `HireDate`
- `Attrition`
- `EmployeeStatus`
- `YearsAtCompany`
- `Tenure Bin`

### `fact_PerformanceRating`

Important fields include:

- `EmployeeID`
- `ReviewDate`
- `JobSatisfaction`
- `EnvironmentSatisfaction`
- `RelationshipSatisfaction`
- `WorkLifeBalance`
- `SelfRating`
- `ManagerRating`

### `Dim_Date`

Important fields include:

- `Date`
- `Year`
- `MonthNumber`
- `MonthName`
- `Quarter`
- `FiscalYear`
- `FiscalMonth`

## Model Strengths

- Separates employee attributes from review records.
- Supports both summary reporting and employee-level drill analysis.
- Handles inactive relationships using DAX.
- Supports business-friendly HR KPIs such as attrition rate, active employees, hiring trends, and performance review tracking.

## Model Limitations

- The dataset is fictional and should not be treated as real employee data.
- Attrition patterns show association, not causation.
- Salary analysis should be interpreted carefully because salary can be affected by role, department, tenure, location, and performance.
- Some review-date and hire-date combinations required validation logic to avoid misleading performance timelines.

| `fact_PerformanceRating` | Multiple rows per employee, one row per performance review |
| `dim_EducationLevel` | One row per education level |
| `dim_RatingLevel` | One row per rating level |
| `dim_SatisfiedLevel` | One row per satisfaction level |
| `DimDate` | One row per date |

## Relationship Logic

Important relationships include:

- `dim_Employee[EmployeeID]` to `fact_PerformanceRating[EmployeeID]`
- `dim_EducationLevel[EducationLevelID]` to `dim_Employee[Education]`
- `DimDate[Date]` to review/hire date logic
- Satisfaction and rating lookup relationships for label context

## Active vs Inactive Relationships

The report uses inactive relationships where a table can relate to another table in more than one way.

Examples:

- Review date analysis uses performance review dates.
- Hiring trend analysis uses employee hire dates.
- `USERELATIONSHIP()` is used in selected DAX measures to activate an inactive relationship only for that measure.

## Data Modeling Lessons

- A lookup table such as Education Level is a dimension table because it describes an attribute, not a transaction/event.
- Performance ratings are fact records because they are repeated employee review events.
- Date logic must distinguish between `HireDate` and `ReviewDate`.
- Inactive relationships are useful when multiple business dates exist in the model.
