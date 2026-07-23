# DAX Measures

<<<<<<< HEAD
This document lists the main DAX logic used in the Power BI report.

The report uses a dedicated measure table:

- `_Measure`

## Core Headcount Measures

### TotalEmployees

```DAX
TotalEmployees =
DISTINCTCOUNT ( dim_Employee[EmployeeID] )

ActiveEmployees =
CALCULATE (
    [TotalEmployees],
    dim_Employee[Attrition] = "No"
)

InactiveEmployees =
COALESCE (
    CALCULATE (
        [TotalEmployees],
=======
This document lists key DAX patterns used in the HR Analytics dashboard.

> Table names may vary slightly in the Power BI file. The examples below use the project naming convention used during development.

## Core Employee Measures

```DAX
Total Employees =
DISTINCTCOUNT ( dim_Employee[EmployeeID] )
```

```DAX
Active Employees =
CALCULATE (
    [Total Employees],
    dim_Employee[Attrition] = "No"
)
```

```DAX
Inactive Employees =
COALESCE (
    CALCULATE (
        [Total Employees],
>>>>>>> a3a6b12dd8d60cfe99c2b3ed41a21f2ef58f24fb
        dim_Employee[Attrition] = "Yes"
    ),
    0
)
<<<<<<< HEAD

% Attrition Rate =
COALESCE (
    DIVIDE (
        [InactiveEmployees],
        [TotalEmployees]
    ),
    0
)

TotalEmployeesDate =
CALCULATE (
    [TotalEmployees],
    USERELATIONSHIP (
        Dim_Date[Date],
        dim_Employee[HireDate]
    )
)

InactiveEmployeesDate =
CALCULATE (
    [InactiveEmployees],
    USERELATIONSHIP (
        Dim_Date[Date],
        dim_Employee[HireDate]
    )
)

% Attrition Rate Date =
DIVIDE (
    [InactiveEmployeesDate],
    [TotalEmployeesDate]
)

AverageSalary =
AVERAGE ( dim_Employee[Salary] )

EmployeeStatus =
=======
```

```DAX
% Attrition Rate =
COALESCE (
    DIVIDE ( [Inactive Employees], [Total Employees] ),
    0
)
```

## Hiring Trend Measures

```DAX
Total Employees Date =
CALCULATE (
    [Total Employees],
    USERELATIONSHIP ( DimDate[Date], dim_Employee[HireDate] )
)
```

```DAX
Inactive Employees Date =
CALCULATE (
    [Inactive Employees],
    USERELATIONSHIP ( DimDate[Date], dim_Employee[HireDate] )
)
```

```DAX
% Attrition Rate Date =
DIVIDE ( [Inactive Employees Date], [Total Employees Date] )
```

## Demographic Measures

```DAX
Average Age =
AVERAGE ( dim_Employee[Age] )
```

```DAX
Average Salary =
AVERAGE ( dim_Employee[Salary] )
```

```DAX
Employee Status =
>>>>>>> a3a6b12dd8d60cfe99c2b3ed41a21f2ef58f24fb
IF (
    dim_Employee[Attrition] = "No",
    "Active",
    "Inactive"
)
<<<<<<< HEAD

FullName =
dim_Employee[FirstName] & " " & dim_Employee[LastName]

Tenure Bin =
SWITCH (
    TRUE (),
    dim_Employee[YearsAtCompany] <= 1, "0-1 years",
    dim_Employee[YearsAtCompany] <= 3, "2-3 years",
    dim_Employee[YearsAtCompany] <= 5, "4-5 years",
    "6+ years"
)

Tenure Bin Sort =
SWITCH (
    TRUE (),
    dim_Employee[YearsAtCompany] <= 1, 1,
    dim_Employee[YearsAtCompany] <= 3, 2,
    dim_Employee[YearsAtCompany] <= 5, 3,
    4
)

Start Date =
IF (
    HASONEVALUE ( dim_Employee[EmployeeID] ),
    FORMAT (
        SELECTEDVALUE ( dim_Employee[HireDate] ),
        "mm/dd/yyyy"
    ),
    "Select employee"
)

Last Review Date Display =
VAR HireDate =
    SELECTEDVALUE ( dim_Employee[HireDate] )
VAR LastValidReview =
    CALCULATE (
        MAX ( fact_PerformanceRating[ReviewDate] ),
        fact_PerformanceRating[ReviewDate] >= HireDate
    )
=======
```

## Performance Tracker Display Measures

```DAX
Start Date Display =
IF (
    HASONEVALUE ( dim_Employee[EmployeeID] ),
    FORMAT ( SELECTEDVALUE ( dim_Employee[HireDate] ), "mm/dd/yyyy" ),
    "Select employee"
)
```

```DAX
Last Review Date Display =
VAR LastReview =
    MAX ( fact_PerformanceRating[ReviewDate] )
>>>>>>> a3a6b12dd8d60cfe99c2b3ed41a21f2ef58f24fb
RETURN
    IF (
        NOT HASONEVALUE ( dim_Employee[EmployeeID] ),
        "Select employee",
        IF (
<<<<<<< HEAD
            ISBLANK ( LastValidReview ),
            "No valid review found",
            FORMAT ( LastValidReview, "mm/dd/yyyy" )
        )
    )

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
=======
            ISBLANK ( LastReview ),
            "No review found",
            FORMAT ( LastReview, "mm/dd/yyyy" )
        )
    )
```

```DAX
Next Review Date Display =
VAR EmployeeStatus =
    SELECTEDVALUE ( dim_Employee[EmployeeStatus] )
VAR LastReview =
    MAX ( fact_PerformanceRating[ReviewDate] )
VAR HireDate =
    SELECTEDVALUE ( dim_Employee[HireDate] )
VAR BaseDate =
    COALESCE ( LastReview, HireDate )
>>>>>>> a3a6b12dd8d60cfe99c2b3ed41a21f2ef58f24fb
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
<<<<<<< HEAD

Current Department =
IF (
    HASONEVALUE ( dim_Employee[EmployeeID] ),
    SELECTEDVALUE ( dim_Employee[Department] ),
    "Select employee"
)

Current Job Role =
IF (
    HASONEVALUE ( dim_Employee[EmployeeID] ),
    SELECTEDVALUE ( dim_Employee[JobRole] ),
    "Select employee"
)

Selected Years At Company =
=======
```

```DAX
Selected Years At Company Display =
>>>>>>> a3a6b12dd8d60cfe99c2b3ed41a21f2ef58f24fb
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
<<<<<<< HEAD

Selected Employee Status =
IF (
    HASONEVALUE ( dim_Employee[EmployeeID] ),
    SELECTEDVALUE ( dim_Employee[EmployeeStatus] ),
    "Select employee"
)

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

=======
```

## Performance Rating Measures

For the Performance Tracker charts, numeric rating values are used directly. The measures return blank when no employee is selected.

```DAX
Job Satisfaction =
VAR SelectedHireDate =
    SELECTEDVALUE ( dim_Employee[HireDate] )
RETURN
    IF (
        NOT HASONEVALUE ( dim_Employee[EmployeeID] ),
        BLANK (),
        CALCULATE (
            MAX ( fact_PerformanceRating[JobSatisfaction] ),
            fact_PerformanceRating[ReviewDate] >= SelectedHireDate
        )
    )
```

```DAX
Environment Satisfaction =
VAR SelectedHireDate =
    SELECTEDVALUE ( dim_Employee[HireDate] )
RETURN
    IF (
        NOT HASONEVALUE ( dim_Employee[EmployeeID] ),
        BLANK (),
        CALCULATE (
            MAX ( fact_PerformanceRating[EnvironmentSatisfaction] ),
            fact_PerformanceRating[ReviewDate] >= SelectedHireDate
        )
    )
```

```DAX
Self Rating =
VAR SelectedHireDate =
    SELECTEDVALUE ( dim_Employee[HireDate] )
RETURN
    IF (
        NOT HASONEVALUE ( dim_Employee[EmployeeID] ),
        BLANK (),
        CALCULATE (
            MAX ( fact_PerformanceRating[SelfRating] ),
            fact_PerformanceRating[ReviewDate] >= SelectedHireDate
        )
    )
```

```DAX
Manager Rating =
VAR SelectedHireDate =
    SELECTEDVALUE ( dim_Employee[HireDate] )
RETURN
    IF (
        NOT HASONEVALUE ( dim_Employee[EmployeeID] ),
        BLANK (),
        CALCULATE (
            MAX ( fact_PerformanceRating[ManagerRating] ),
            fact_PerformanceRating[ReviewDate] >= SelectedHireDate
        )
    )
```

## Attrition Measures

```DAX
>>>>>>> a3a6b12dd8d60cfe99c2b3ed41a21f2ef58f24fb
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
<<<<<<< HEAD
=======
```

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

- Use calculated columns for slicer/legend categories such as `Employee Status`, `AgeBin`, and `Tenure Bin`.
- Use measures for dynamic KPIs such as attrition rate and average salary.
- Use `SELECTEDVALUE()` only with columns, not measures.
- Use `USERELATIONSHIP()` only when the exact inactive relationship already exists in the model.
- For employee-level pages, protect measures with `HASONEVALUE()` so visuals do not accidentally show aggregate values.
>>>>>>> a3a6b12dd8d60cfe99c2b3ed41a21f2ef58f24fb
