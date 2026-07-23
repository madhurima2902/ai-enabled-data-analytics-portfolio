# DAX Measures

This document lists the main DAX measures and calculated columns used in the HR Analytics Power BI report.

The report uses a dedicated measure table:

- `_Measure`

## Core Headcount Measures

### TotalEmployees

```DAX
TotalEmployees =
DISTINCTCOUNT ( dim_Employee[EmployeeID] )
```

### ActiveEmployees

```DAX
ActiveEmployees =
CALCULATE (
    [TotalEmployees],
    dim_Employee[Attrition] = "No"
)
```

### InactiveEmployees

```DAX
InactiveEmployees =
COALESCE (
    CALCULATE (
        [TotalEmployees],
        dim_Employee[Attrition] = "Yes"
    ),
    0
)
```

### % Attrition Rate

```DAX
% Attrition Rate =
COALESCE (
    DIVIDE (
        [InactiveEmployees],
        [TotalEmployees]
    ),
    0
)
```

## Hiring Trend Measures

### TotalEmployeesDate

```DAX
TotalEmployeesDate =
CALCULATE (
    [TotalEmployees],
    USERELATIONSHIP (
        Dim_Date[Date],
        dim_Employee[HireDate]
    )
)
```

### InactiveEmployeesDate

```DAX
InactiveEmployeesDate =
CALCULATE (
    [InactiveEmployees],
    USERELATIONSHIP (
        Dim_Date[Date],
        dim_Employee[HireDate]
    )
)
```

### % Attrition Rate Date

```DAX
% Attrition Rate Date =
DIVIDE (
    [InactiveEmployeesDate],
    [TotalEmployeesDate]
)
```

## Demographic Measures

### AverageSalary

```DAX
AverageSalary =
AVERAGE ( dim_Employee[Salary] )
```

## Performance Tracker Display Measures

### Start Date

```DAX
Start Date =
IF (
    HASONEVALUE ( dim_Employee[EmployeeID] ),
    FORMAT (
        SELECTEDVALUE ( dim_Employee[HireDate] ),
        "mm/dd/yyyy"
    ),
    "Select employee"
)
```

### Last Review Date Display

```DAX
Last Review Date Display =
VAR HireDate =
    SELECTEDVALUE ( dim_Employee[HireDate] )
VAR LastValidReview =
    CALCULATE (
        MAX ( fact_PerformanceRating[ReviewDate] ),
        fact_PerformanceRating[ReviewDate] >= HireDate
    )
RETURN
    IF (
        NOT HASONEVALUE ( dim_Employee[EmployeeID] ),
        "Select employee",
        IF (
            ISBLANK ( LastValidReview ),
            "No valid review found",
            FORMAT ( LastValidReview, "mm/dd/yyyy" )
        )
    )
```

### Next Review Date Display

```DAX
Next Review Date Display =
VAR EmployeeStatus =
    SELECTEDVALUE ( dim_Employee[EmployeeStatus] )
VAR HireDate =
    SELECTEDVALUE ( dim_Employee[HireDate] )
VAR LastValidReview =
    CALCULATE (
        MAX ( fact_PerformanceRating[ReviewDate] ),
        fact_PerformanceRating[ReviewDate] >= HireDate
    )
VAR BaseDate =
    COALESCE ( LastValidReview, HireDate )
RETURN
    IF (
        NOT HASONEVALUE ( dim_Employee[EmployeeID] ),
        "Select employee",
        IF (
            EmployeeStatus = "Inactive",
            "Not applicable",
            FORMAT ( BaseDate + 365, "mm/dd/yyyy" )
        )
    )
```

### Current Department

```DAX
Current Department =
IF (
    HASONEVALUE ( dim_Employee[EmployeeID] ),
    SELECTEDVALUE ( dim_Employee[Department] ),
    "Select employee"
)
```

### Current Job Role

```DAX
Current Job Role =
IF (
    HASONEVALUE ( dim_Employee[EmployeeID] ),
    SELECTEDVALUE ( dim_Employee[JobRole] ),
    "Select employee"
)
```

### Selected Years At Company

```DAX
Selected Years At Company =
VAR Years =
    SELECTEDVALUE ( dim_Employee[YearsAtCompany] )
RETURN
    IF (
        NOT HASONEVALUE ( dim_Employee[EmployeeID] ),
        "Select employee",
        IF (
            Years = 0,
            "<1 year",
            FORMAT ( Years, "0" ) & " years"
        )
    )
```

### Selected Employee Status

```DAX
Selected Employee Status =
IF (
    HASONEVALUE ( dim_Employee[EmployeeID] ),
    SELECTEDVALUE ( dim_Employee[EmployeeStatus] ),
    "Select employee"
)
```

## Performance Rating Measures

These measures are used on the Performance Tracker page. They return blank when no single employee is selected.

### JobSatisfaction

```DAX
JobSatisfaction =
VAR HireDate =
    SELECTEDVALUE ( dim_Employee[HireDate] )
RETURN
    IF (
        HASONEVALUE ( dim_Employee[EmployeeID] ),
        CALCULATE (
            MAX ( fact_PerformanceRating[JobSatisfaction] ),
            fact_PerformanceRating[ReviewDate] >= HireDate
        ),
        BLANK ()
    )
```

### EnvironmentSatisfaction

```DAX
EnvironmentSatisfaction =
VAR HireDate =
    SELECTEDVALUE ( dim_Employee[HireDate] )
RETURN
    IF (
        HASONEVALUE ( dim_Employee[EmployeeID] ),
        CALCULATE (
            MAX ( fact_PerformanceRating[EnvironmentSatisfaction] ),
            fact_PerformanceRating[ReviewDate] >= HireDate
        ),
        BLANK ()
    )
```

### RelationshipSatisfaction

```DAX
RelationshipSatisfaction =
VAR HireDate =
    SELECTEDVALUE ( dim_Employee[HireDate] )
RETURN
    IF (
        HASONEVALUE ( dim_Employee[EmployeeID] ),
        CALCULATE (
            MAX ( fact_PerformanceRating[RelationshipSatisfaction] ),
            fact_PerformanceRating[ReviewDate] >= HireDate
        ),
        BLANK ()
    )
```

### WorkLifeBalance

```DAX
WorkLifeBalance =
VAR HireDate =
    SELECTEDVALUE ( dim_Employee[HireDate] )
RETURN
    IF (
        HASONEVALUE ( dim_Employee[EmployeeID] ),
        CALCULATE (
            MAX ( fact_PerformanceRating[WorkLifeBalance] ),
            fact_PerformanceRating[ReviewDate] >= HireDate
        ),
        BLANK ()
    )
```

### SelfRating

```DAX
SelfRating =
VAR HireDate =
    SELECTEDVALUE ( dim_Employee[HireDate] )
RETURN
    IF (
        HASONEVALUE ( dim_Employee[EmployeeID] ),
        CALCULATE (
            MAX ( fact_PerformanceRating[SelfRating] ),
            fact_PerformanceRating[ReviewDate] >= HireDate
        ),
        BLANK ()
    )
```

### ManagerRating

```DAX
ManagerRating =
VAR HireDate =
    SELECTEDVALUE ( dim_Employee[HireDate] )
RETURN
    IF (
        HASONEVALUE ( dim_Employee[EmployeeID] ),
        CALCULATE (
            MAX ( fact_PerformanceRating[ManagerRating] ),
            fact_PerformanceRating[ReviewDate] >= HireDate
        ),
        BLANK ()
    )
```

## Attrition Measure

### Overtime Attrition Gap

```DAX
Overtime Attrition Gap =
CALCULATE (
    [% Attrition Rate],
    dim_Employee[OverTime] = "Yes"
)
-
CALCULATE (
    [% Attrition Rate],
    dim_Employee[OverTime] = "No"
)
```

## Calculated Columns

These are row-level calculated columns used for slicers, legends, grouping, and employee display fields.

### EmployeeStatus

```DAX
EmployeeStatus =
IF (
    dim_Employee[Attrition] = "No",
    "Active",
    "Inactive"
)
```

### FullName

```DAX
FullName =
dim_Employee[FirstName] & " " & dim_Employee[LastName]
```

### Tenure Bin

```DAX
Tenure Bin =
SWITCH (
    TRUE (),
    dim_Employee[YearsAtCompany] <= 1, "0-1 years",
    dim_Employee[YearsAtCompany] <= 3, "2-3 years",
    dim_Employee[YearsAtCompany] <= 5, "4-5 years",
    "6+ years"
)
```

### Tenure Bin Sort

```DAX
Tenure Bin Sort =
SWITCH (
    TRUE (),
    dim_Employee[YearsAtCompany] <= 1, 1,
    dim_Employee[YearsAtCompany] <= 3, 2,
    dim_Employee[YearsAtCompany] <= 5, 3,
    4
)
```

## Important DAX Lessons

- Use calculated columns for slicer and legend categories such as `EmployeeStatus`, `FullName`, and `Tenure Bin`.
- Use measures for dynamic KPIs such as attrition rate, average salary, headcount, and selected employee cards.
- Use `SELECTEDVALUE()` only with columns, not measures.
- Use `USERELATIONSHIP()` only when the inactive relationship already exists in the model.
- For employee-level pages, protect card measures with `HASONEVALUE()` so the page does not show misleading aggregate values.
- For Performance Tracker visuals, review dates are filtered to avoid showing performance records before the selected employee's hire date.
