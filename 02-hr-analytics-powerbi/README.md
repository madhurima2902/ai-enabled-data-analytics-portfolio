# HR Analytics | Attrition and Workforce Performance Dashboard

## Project Overview

<<<<<<< HEAD
This project is an HR analytics dashboard built in Power BI using a fictional technology workforce dataset. The report helps HR stakeholders monitor employee headcount, active and inactive employees, attrition, hiring trends, workforce demographics, employee performance review history, and key attrition risk patterns.
=======
This project is an HR analytics dashboard built in Power BI for a fictional technology workforce scenario. The report helps HR stakeholders monitor employee headcount, active/inactive workforce, attrition, hiring trends, demographics, employee performance review history, and key attrition risk patterns.
>>>>>>> a3a6b12dd8d60cfe99c2b3ed41a21f2ef58f24fb

The dashboard was redesigned as a portfolio project to demonstrate Power BI data modeling, DAX measure design, inactive relationship handling, HR KPI development, stakeholder-focused dashboard design, and AI-assisted analytics workflow.

## Business Problem

<<<<<<< HEAD
HR leadership needs a reusable dashboard that can answer:
=======
HR leadership needs a reusable report that can answer:
>>>>>>> a3a6b12dd8d60cfe99c2b3ed41a21f2ef58f24fb

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

<<<<<<< HEAD
Purpose: provide HR leadership with a high-level snapshot of headcount, employee status, hiring trends, and workforce distribution.

Key visuals:
=======
Purpose: give HR leadership a high-level snapshot of headcount, employee status, hiring trends, and department structure.

Key elements:
>>>>>>> a3a6b12dd8d60cfe99c2b3ed41a21f2ef58f24fb

- Total Employees
- Active Employees
- Inactive Employees
- Attrition Rate
- Employee Hiring Trends
- Active Employees by Department
- Active Employees by Department and Job Role
<<<<<<< HEAD
- Executive summary panel

![Overview](assets/overview.png)

### 2. Workforce Demographics

Purpose: analyze employee composition across age, gender, marital status, ethnicity, and salary.

Key visuals:

=======
- Executive summary

### 2. Workforce Demographics

Purpose: analyze workforce composition by demographic and salary-related fields.

Key elements:

- Total Employees
- Average Age
- Average Salary
- Employee Status slicer
>>>>>>> a3a6b12dd8d60cfe99c2b3ed41a21f2ef58f24fb
- Employees by Age Group
- Employees by Age and Gender
- Employees by Marital Status
- Employees by Ethnicity and Average Salary
<<<<<<< HEAD
- Employee Status filter

![Demographics](assets/demographics.png)

### 3. Performance Tracker

Purpose: provide an employee-level view of performance review history, satisfaction scores, and self-vs-manager ratings.

Key visuals:

- Select Employee slicer
=======

### 3. Performance Tracker

Purpose: provide an employee-level view of review dates, satisfaction scores, and self-vs-manager ratings over time.

Key elements:

- Employee selector
>>>>>>> a3a6b12dd8d60cfe99c2b3ed41a21f2ef58f24fb
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

<<<<<<< HEAD
![Performance Tracker](assets/performance_tracker.png)

### 4. Attrition Analysis

Purpose: identify attrition patterns by department, job role, hire year, travel frequency, overtime, tenure, and retention-related factors.

Key visuals:
=======
Important logic added:

- Cards display `Select employee` when no employee is selected.
- Inactive employees do not show a misleading future review due date.
- Historical review details are shown for selected employees.

### 4. Attrition Analysis

Purpose: identify employee segments with higher turnover risk and support HR follow-up actions.

Key elements:
>>>>>>> a3a6b12dd8d60cfe99c2b3ed41a21f2ef58f24fb

- Attrition Rate
- Inactive Employees
- Overtime Attrition Gap
<<<<<<< HEAD
- Attrition by Department and Job Role
=======
- Department and Job Role attrition matrix
>>>>>>> a3a6b12dd8d60cfe99c2b3ed41a21f2ef58f24fb
- Attrition by Hire Year
- Attrition by Travel Frequency
- Attrition by Overtime Requirement
- Attrition by Tenure
- Attrition by Stock Option Level

<<<<<<< HEAD
![Attrition Analysis](assets/attrition_analysis.png)

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
=======
## Data Model
>>>>>>> a3a6b12dd8d60cfe99c2b3ed41a21f2ef58f24fb

The report uses a fact and dimension model.

Main tables:

| Table | Type | Purpose |
|---|---|---|
<<<<<<< HEAD
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

## Project Files
=======
| `fact_PerformanceRating` | Fact | Stores yearly performance review records by employee |
| `dim_Employee` | Dimension | Stores employee profile, department, role, salary, tenure, hire date, and attrition fields |
| `dim_EducationLevel` | Dimension | Provides education-level descriptions |
| `dim_RatingLevel` | Dimension | Provides rating-level descriptions |
| `dim_SatisfiedLevel` | Dimension | Provides satisfaction-level descriptions |
| `DimDate` | Dimension | Supports time-based analysis |

Important modeling concepts used:

- Fact/dimension table separation
- Date dimension
- Active and inactive relationships
- `USERELATIONSHIP()` for hire-date-based analysis
- Employee-level profile filtering

## Key Metrics

| Metric | Meaning |
|---|---|
| Total Employees | Count of all employees |
| Active Employees | Employees where attrition is `No` |
| Inactive Employees | Employees where attrition is `Yes` |
| Attrition Rate | Inactive Employees divided by Total Employees |
| Average Age | Average employee age |
| Average Salary | Average employee salary |
| Overtime Attrition Gap | Attrition rate difference between overtime and non-overtime employees |
| Tenure Bin | Grouped employee tenure categories |

## Key Insights

Based on the available dataset:

- Total employee count is 1,470.
- Active employees: 1,233.
- Inactive employees: 237.
- Overall attrition rate is 16.1%.
- Employees with overtime show much higher attrition than employees without overtime.
- Frequent travelers show higher attrition than employees with no travel.
- Early-tenure employees have higher attrition than long-tenure employees.
- Sales Representatives, Recruiters, and Data Scientists show higher attrition rates than several other roles.
- Employees with no stock options show higher attrition than employees with some stock option level.
- Salary and ethnicity views should be treated as initial monitoring views and reviewed further by role, department, tenure, and performance before drawing conclusions.

## Recommendations

Potential HR follow-up actions:

- Review workload distribution and overtime-heavy roles.
- Investigate travel-heavy roles and flexibility policies.
- Strengthen onboarding and manager check-ins for early-tenure employees.
- Review retention incentives for groups with high attrition and no stock options.
- Analyze high-attrition roles in more detail before taking action.
- Avoid drawing causal conclusions without deeper statistical analysis and business context.

## AI-Assisted Development

AI was used as a productivity assistant during development. It helped with:

- Validating DAX logic
- Reviewing `USERELATIONSHIP()` usage
- Improving chart titles and business wording
- Identifying misleading visuals and label issues
- Suggesting dashboard layout improvements
- Drafting insight summaries and documentation

Final model decisions, DAX validation, dashboard formatting, navigation, and business interpretation were manually reviewed and applied in Power BI.

## Data Source Note

This project uses a fictional HR analytics dataset from a DataCamp Power BI case study. The dashboard was redesigned, documented, and reframed as a portfolio project. Course instructions, transcripts, and course UI screenshots are not included in this repository.

## Repository Contents
>>>>>>> a3a6b12dd8d60cfe99c2b3ed41a21f2ef58f24fb

```text
02-hr-analytics-powerbi/
│
├── README.md
├── powerbi/
<<<<<<< HEAD
│   ├── README.md
│   └── hr_analytics_attrition_dashboard.pbix
│
├── assets/
│   ├── README.md
│   ├── overview.png
│   ├── demographics.png
│   ├── performance_tracker.png
│   ├── attrition_analysis.png
│   └── data_model.png
│
├── docs/
│   ├── data_source_notes.md
│   ├── data_model.md
│   ├── dashboard_pages.md
│   ├── dax_measures.md
│   ├── insights_and_recommendations.md
│   ├── ai_assisted_workflow.md
│   ├── dashboard_review_checklist.md
│   └── interview_prep.md
│
└── theme/
    └── HR_Analytics_Theme.json
=======
│   └── README.md
├── assets/
│   └── README.md
├── docs/
│   ├── ai_assisted_workflow.md
│   ├── dashboard_pages.md
│   ├── data_model.md
│   ├── data_source_notes.md
│   ├── dax_measures.md
│   ├── insights_and_recommendations.md
│   └── interview_prep.md
└── theme/
    └── HR_Analytics_Theme.json
```

## Status

Dashboard design and documentation are complete. Final Power BI file and dashboard screenshots should be added to the `powerbi/` and `assets/` folders respectively.
>>>>>>> a3a6b12dd8d60cfe99c2b3ed41a21f2ef58f24fb
