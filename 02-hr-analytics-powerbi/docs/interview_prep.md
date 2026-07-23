# Interview Prep: HR Analytics Power BI Project

## 1. How would you explain this project?

I built an HR Analytics dashboard in Power BI using a fictional technology workforce dataset. The report helps HR stakeholders monitor workforce headcount, hiring trends, demographics, performance review history, and attrition patterns. I used a fact/dimension data model, DAX measures, a date table, inactive relationships, and interactive report pages.

## 2. What business problem does it solve?

The dashboard helps HR leadership understand workforce composition and identify employee segments with higher attrition risk. It supports decisions around onboarding, overtime, travel-heavy roles, retention incentives, and role-level attrition deep-dives.

## 3. What are the main pages?

- Workforce Overview: executive KPIs and hiring trends
- Workforce Demographics: age, gender, marital status, ethnicity, and salary view
- Performance Tracker: employee-level review and rating trends
- Attrition Analysis: attrition by role, hire year, travel, overtime, tenure, and stock options

## 4. What was your data model?

I used a fact/dimension model. `fact_PerformanceRating` stores multiple review records per employee. `dim_Employee` stores one row per employee. Lookup dimensions provide education, rating, and satisfaction-level descriptions. A calculated date table supports time-based reporting.

## 5. Why did you use a date table?

A dedicated date table supports consistent time-based reporting by year, month, quarter, and fiscal period. It also allows separate date logic for review dates and hire dates.

## 6. What is `USERELATIONSHIP()` and where did you use it?

`USERELATIONSHIP()` temporarily activates an inactive relationship for a specific measure. I used it for hire-date analysis because the date table also relates to performance review dates. For example, hiring trends and hire-year attrition need the date table to filter employee hire dates instead of review dates.

## 7. Why did you create `EmployeeStatus`?

The raw attrition field uses `Yes` and `No`. For business readability, I created `EmployeeStatus` so visuals show `Active` and `Inactive`. This makes legends and slicers more intuitive.

## 8. What issue did you find in the Performance Tracker?

An inactive employee could show a future next review date, which is misleading. I changed the logic so inactive employees show `Not applicable` for next review while still allowing historical review trends to be viewed.

## 9. What are the strongest insights?

- Overall attrition rate is 16.1%.
- Overtime employees show much higher attrition than non-overtime employees.
- Frequent travelers show higher attrition than no-travel employees.
- Early-tenure employees have the highest attrition risk.
- Sales Representatives, Recruiters, and Data Scientists show higher role-level attrition.
- Employees with no stock options show higher attrition.

## 10. What recommendations would you give HR?

I would recommend reviewing overtime workload patterns, travel-heavy roles, early-tenure onboarding, and retention incentives. I would also recommend deeper role-level analysis for high-attrition roles before making policy decisions.

## 11. What are the limitations?

The dataset is fictional and does not include all real-world HR variables. It does not prove causation. Salary and demographic patterns should not be interpreted without controlling for role, department, tenure, location, performance, and manager context.

## 12. How did AI help?

AI helped validate DAX logic, suggest dashboard improvements, refine visual titles, and create documentation. I manually reviewed the final measures, visuals, and business interpretation.

## 13. What would you improve in a real company version?

I would add resignation reason, manager ID, engagement survey results, promotion history, compensation bands, performance improvement plans, location, job level, and exit interview data. I would also create alerts for high-risk segments and track attrition trends monthly.
