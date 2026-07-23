# Insights and Recommendations

<<<<<<< HEAD
## Executive Summary

The dashboard identifies workforce patterns across headcount, demographics, performance review tracking, and attrition. The strongest business insights come from attrition analysis, especially overtime, travel frequency, early tenure, job role, and stock option level.

The project should be interpreted as an HR analytics reporting exercise using fictional data. The insights show patterns and associations, not proven causation.

## Key Metrics
=======
## Executive Metrics
>>>>>>> a3a6b12dd8d60cfe99c2b3ed41a21f2ef58f24fb

| Metric | Value |
|---|---:|
| Total Employees | 1,470 |
| Active Employees | 1,233 |
| Inactive Employees | 237 |
<<<<<<< HEAD
| Attrition Rate | 16.1% |
| Average Age | 29 |
| Average Salary | $112,956 |

## Workforce Overview Insights

- Technology is the largest department by active employee count.
- The dashboard separates active and inactive employees to give HR leadership a clear workforce snapshot.
- Hiring trend analysis helps identify how employee cohorts vary by year.

## Demographics Insights

- Most employees are concentrated in the 20–29 age group.
- Married and Single employees represent the largest marital-status groups.
- Average salary varies by ethnicity, but this should be reviewed further by department, job role, tenure, and performance before drawing conclusions.

## Performance Tracker Insights

- The Performance Tracker page supports employee-level review analysis.
- HR users can select an employee and review start date, last review, next review, department, job role, tenure, and employee status.
- Satisfaction and performance rating trends help compare employee self-ratings and manager ratings over time.
- Inactive employees should not show a misleading future review date, so the dashboard displays next review as not applicable for inactive employees.

## Attrition Insights

### 1. Overtime is strongly associated with attrition

Employees working overtime show a higher attrition rate than employees not working overtime.

Business recommendation:

- Review workload distribution.
- Investigate overtime-heavy teams and roles.
- Evaluate whether overtime is linked to burnout, manager capacity, or staffing gaps.

### 2. Frequent travel is associated with higher attrition

Frequent travelers show higher attrition than employees with no travel.

Business recommendation:

- Review travel-heavy roles.
- Evaluate travel support, rotation policies, flexibility, and travel-related compensation.

### 3. Early-tenure employees are higher risk

Employees in the 0–1 year tenure group show higher attrition risk.

Business recommendation:

- Strengthen onboarding.
- Add structured 30/60/90-day check-ins.
- Review role clarity and manager support during the first year.

### 4. Some job roles show elevated attrition

Roles such as Sales Representative, Recruiter, and Data Scientist show higher attrition rates.

Business recommendation:

- Run role-specific retention reviews.
- Compare workload, compensation, career progression, and manager support for these roles.

### 5. Stock option level appears related to retention

Employees with no stock options show higher attrition than employees with some stock option level.

Business recommendation:

- Review whether equity or retention incentives could support employee retention.
- Avoid assuming causation because stock option eligibility may be linked to level, role, or tenure.

## Caution on Interpretation

The dashboard identifies risk patterns but does not prove causation. A real HR team should follow up with:

- Employee engagement survey data
- Exit interview analysis
- Manager-level review
- Compensation benchmarking
- Role and department-level workload analysis
- Tenure and promotion history analysis
=======
| Overall Attrition Rate | 16.1% |

## Attrition Drivers Observed

### 1. Overtime

Employees who work overtime show materially higher attrition than employees who do not.

| OverTime | Employees | Inactive | Attrition Rate |
|---|---:|---:|---:|
| Yes | 416 | 127 | 30.5% |
| No | 1,054 | 110 | 10.4% |

Recommended follow-up:

- Review overtime-heavy roles and departments.
- Identify recurring workload spikes.
- Assess staffing levels, work-life balance, and manager practices.

### 2. Business Travel

Frequent travelers have higher attrition than employees with no travel.

| Travel Frequency | Employees | Inactive | Attrition Rate |
|---|---:|---:|---:|
| Frequent Traveller | 277 | 69 | 24.9% |
| Some Travel | 1,043 | 156 | 15.0% |
| No Travel | 150 | 12 | 8.0% |

Recommended follow-up:

- Review travel-heavy roles.
- Consider rotation, flexibility, travel support, or compensation policies.

### 3. Tenure

Early-tenure employees show higher attrition risk.

| Tenure Group | Employees | Inactive | Attrition Rate |
|---|---:|---:|---:|
| 0-1 years | 367 | 121 | 33.0% |
| 2-3 years | 272 | 49 | 18.0% |
| 4-5 years | 244 | 35 | 14.3% |
| 6+ years | 587 | 32 | 5.5% |

Recommended follow-up:

- Strengthen onboarding for the first 12 months.
- Add structured manager check-ins.
- Review role clarity and early engagement survey feedback.

### 4. Job Role

Some roles show higher attrition than others.

| Job Role | Employees | Inactive | Attrition Rate |
|---|---:|---:|---:|
| Sales Representative | 83 | 33 | 39.8% |
| Recruiter | 24 | 9 | 37.5% |
| Data Scientist | 261 | 62 | 23.8% |
| Sales Executive | 327 | 57 | 17.4% |
| Software Engineer | 294 | 47 | 16.0% |

Recommended follow-up:

- Prioritize role-level root cause analysis for Sales Representative, Recruiter, and Data Scientist groups.
- Compare attrition with overtime, travel frequency, salary band, tenure, and manager patterns.

### 5. Stock Option Level

Employees with no stock options show higher attrition.

| Stock Option Level | Employees | Inactive | Attrition Rate |
|---|---:|---:|---:|
| 0 | 631 | 154 | 24.4% |
| 1 | 596 | 56 | 9.4% |
| 2 | 158 | 12 | 7.6% |
| 3 | 85 | 15 | 17.6% |

Recommended follow-up:

- Review whether retention incentives are reaching high-risk groups.
- Compare stock option level with role, tenure, salary, and performance rating.

## Responsible Interpretation

These patterns should be treated as business signals, not causal proof. Recommended next steps include deeper analysis with role, department, tenure, compensation, manager, performance, and employee engagement context.
>>>>>>> a3a6b12dd8d60cfe99c2b3ed41a21f2ef58f24fb
