# Dashboard Page Design

## Design System

The report uses a consistent dashboard theme:

- Header/nav background: dark navy
- Selected page accent: green
- Canvas background: very light grey
- KPI cards: light lavender/neutral card background
- Main chart color: blue
- Attrition/risk lines: darker blue or risk color where appropriate
- Font: Segoe UI / Segoe UI Semibold

## Page 1: Workforce Overview

Purpose: executive snapshot of workforce size, active/inactive status, hiring trend, and department structure.

Recommended layout:

- Header and navigator
- KPI row: Total Employees, Active Employees, Inactive Employees, Attrition Rate
- Employee Hiring Trends
- Active Employees by Department
- Department and Job Role matrix
- Executive Summary

## Page 2: Workforce Demographics

Purpose: understand workforce composition.

Recommended layout:

- Left summary panel: Total Employees, Average Age, Average Salary, Employee Status slicer, Executive Summary
- Right visual grid: Age Group, Age and Gender, Marital Status, Ethnicity and Average Salary

## Page 3: Performance Tracker

Purpose: employee-level performance review view.

Recommended layout:

- Left panel: Select Employee, Start Date, Last Review, Next Review, Department, Job Role, Tenure, Employee Status
- Right side: Satisfaction Ratings by Year, Self vs Manager Rating by Year, Review Details table

## Page 4: Attrition Analysis

Purpose: identify segments with higher employee turnover.

Recommended layout:

- Left panel: Attrition Rate, Inactive Employees, Overtime Attrition Gap, slicers, Key Insight
- Main area: Department/Role matrix, Hire Year trend, Travel Frequency, Overtime Requirement, Tenure, Stock Option Level

## Design Review Notes

Several design improvements were made from the initial build:

- Reduced extra pages into a final 4-page dashboard.
- Replaced raw names such as `TotalEmployees` with business-friendly labels.
- Avoided stacked percentage charts for attrition rate.
- Used matrix views where role-level categories were too dense for charts.
- Added status-aware logic to the Performance Tracker page.
- Added insight text boxes to make the dashboard analyst-led rather than chart-only.
