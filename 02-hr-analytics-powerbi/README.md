# HR Analytics | Attrition and Workforce Performance Dashboard

## Project Overview

This project is an HR analytics dashboard built in Power BI using a fictional technology workforce dataset. The report helps HR stakeholders monitor employee headcount, active and inactive employees, attrition, hiring trends, workforce demographics, employee performance review history, and key attrition risk patterns.

The dashboard was redesigned as a portfolio project to demonstrate Power BI data modeling, DAX measure design, inactive relationship handling, HR KPI development, stakeholder-focused dashboard design, and AI-assisted analytics workflow.

## Business Problem

HR leadership needs a reusable dashboard that can answer:

- How many employees are active and inactive?
- What is the overall attrition rate?
- How has hiring changed by year?
- Which departments and job roles have the highest employee concentration?
- What does the workforce look like by age, gender, marital status, ethnicity, and salary?
- How can HR review individual employee performance history?
- Which employee segments show higher attrition risk?

## Tools Used

- Power BI Desktop
- Power Query
- DAX
- Data modeling
- GitHub documentation
- AI-assisted dashboard review, DAX validation, title refinement, and insight summarization

## Dashboard Pages

### 1. Workforce Overview

Purpose: provide HR leadership with a high-level snapshot of headcount, employee status, hiring trends, and workforce distribution.

Key visuals:

- Total Employees
- Active Employees
- Inactive Employees
- Attrition Rate
- Employee Hiring Trends
- Active Employees by Department
- Active Employees by Department and Job Role
- Executive summary panel

![Overview](https://github.com/madhurima2902/ai-enabled-data-analytics-portfolio/blob/main/02-hr-analytics-powerbi/assets/01_overview.png)

### 2. Workforce Demographics

Purpose: analyze employee composition across age, gender, marital status, ethnicity, and salary.

Key visuals:

- Total Employees
- Average Age
- Average Salary
- Employee Status filter
- Employees by Age Group
- Employees by Age and Gender
- Employees by Marital Status
- Employees by Ethnicity and Average Salary

![Demographics](https://github.com/madhurima2902/ai-enabled-data-analytics-portfolio/blob/main/02-hr-analytics-powerbi/assets/02_demographics.png)

### 3. Performance Tracker

Purpose: provide an employee-level view of performance review history, satisfaction scores, and self-vs-manager ratings.

Key visuals:

- Select Employee slicer
- Start Date
- Last Review
- Next Review
- Department
- Job Role
- Tenure
- Employee Status
- Satisfaction Ratings by Year
- Self vs Manager Rating by Year
- Review Details table

Important logic added:

- Cards display `Select employee` when no employee is selected.
- Inactive employees do not show a misleading future review due date.
- Historical review details are shown for selected employees.

![Performance Tracker](https://github.com/madhurima2902/ai-enabled-data-analytics-portfolio/blob/main/02-hr-analytics-powerbi/assets/03_performance_tracker.png)

### 4. Attrition Analysis

Purpose: identify attrition patterns by department, job role, hire year, travel frequency, overtime, tenure, and retention-related factors.

Key visuals:

- Attrition Rate
- Inactive Employees
- Overtime Attrition Gap
- Attrition by Department and Job Role
- Attrition by Hire Year
- Attrition by Travel Frequency
- Attrition by Overtime Requirement
- Attrition by Tenure
- Attrition by Stock Option Level

![Attrition Analysis](https://github.com/madhurima2902/ai-enabled-data-analytics-portfolio/blob/main/02-hr-analytics-powerbi/assets/04_attrition_analysis.png)

## Dataset Summary

The project uses a fictional HR dataset from a DataCamp Power BI case study. The dashboard was redesigned and documented as a portfolio project.

Main entities include:

- Employees
- Performance reviews
- Education levels
- Rating levels
- Satisfaction levels
- Date dimension

Dataset size:

- 1,470 employees
- 1,233 active employees
- 237 inactive employees
- 6,709 performance review records
- Overall attrition rate: 16.1%

## Power BI Model

The report uses a fact and dimension model.

Main tables:

| Table | Type | Purpose |
|---|---|---|
| `fact_PerformanceRating` | Fact | Stores yearly employee performance review records |
| `dim_Employee` | Dimension | Stores employee profile, job, salary, status, hire date, and demographic attributes |
| `dim_EducationLevel` | Dimension | Stores education level lookup values |
| `dim_RatingLevel` | Dimension | Stores rating level lookup values |
| `dim_SatisfiedLevel` | Dimension | Stores satisfaction level lookup values |
| `Dim_Date` | Dimension | Supports time-based reporting |
| `_Measure` | Measure table | Stores DAX measures used in the report |

## Key Insights

- The organization has 1,470 employees, with 1,233 active and 237 inactive employees.
- Overall attrition rate is 16.1%.
- Technology has the largest active workforce.
- The workforce is concentrated in the 20–29 age group.
- Overtime employees show a much higher attrition rate than non-overtime employees.
- Frequent travelers show higher attrition than employees with no travel.
- Early-tenure employees have higher attrition risk.
- Sales Representatives, Recruiters, and Data Scientists show elevated attrition rates.
- Employees with no stock options show higher attrition than employees with some stock option level.

## Recommendations

Potential HR follow-up actions:

- Review workload distribution and overtime-heavy roles.
- Investigate travel-heavy roles and flexibility policies.
- Strengthen onboarding and manager check-ins for early-tenure employees.
- Review retention incentives for groups with high attrition and no stock options.
- Analyze high-attrition roles in more detail before taking action.
- Avoid drawing causal conclusions without deeper statistical analysis and business context.

## AI-Assisted Workflow

AI was used as a productivity assistant during the project. It supported:

- DAX validation
- `USERELATIONSHIP()` explanation and debugging
- Visual selection review
- Dashboard layout critique
- Chart title refinement
- Insight summarization
- GitHub documentation drafting
- Interview explanation preparation

Final modeling, DAX implementation, formatting, validation, and dashboard review were completed manually in Power BI Desktop.

## Repository Contents

```text
02-hr-analytics-powerbi/
│
├── README.md
├── powerbi/
│   └── hr_analytics_attrition_dashboard.pbix
│
├── assets/
│   ├── overview.png
│   ├── demographics.png
│   ├── performance_tracker.png
│   ├── attrition_analysis.png
│   └── data_model.png
│
├── docs/
│   ├── data_model.md
│   ├── dax_measures.md
│   ├── insights_and_recommendations.md
│   └── ai_assisted_workflow.md
│
└── theme/
    └── HR_Analytics_Theme.json
```

## Data Source Note

This project uses a fictional HR analytics dataset from a DataCamp Power BI case study. The dashboard was redesigned, renamed, formatted, documented, and extended as a portfolio project. Course instructions and transcripts are not included in this repository.

## Skills Demonstrated

- Power BI report development
- Power Query transformations
- Fact and dimension modeling
- Date table usage
- Active and inactive relationship handling
- DAX measure development
- KPI design
- Attrition analysis
- Workforce demographics reporting
- Performance review tracking
- Business insight communication
- AI-assisted analytics documentation
