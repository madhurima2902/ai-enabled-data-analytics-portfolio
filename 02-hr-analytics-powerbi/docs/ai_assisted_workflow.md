<<<<<<< HEAD
# AI-Assisted Workflow

## Purpose

AI was used as a productivity assistant during this project. It supported dashboard refinement, DAX debugging, insight development, and GitHub documentation.

The final Power BI model, DAX implementation, visual formatting, navigation, and validation were completed manually in Power BI Desktop.

## Areas Where AI Helped

### 1. DAX Validation

AI helped review and debug DAX patterns for:

- Active employees
- Inactive employees
- Attrition rate
- Hire-year analysis
- `USERELATIONSHIP()`
- Employee-level selected-value measures
- Next review date logic
- Inactive employee handling

### 2. Data Model Reasoning

AI helped explain:

- Difference between fact and dimension tables
- Why `dim_EducationLevel` is a dimension table
- Why inactive relationships are needed
- Why ambiguous filter paths occur in Power BI
- How date relationships should be handled

### 3. Dashboard Design Review

AI helped review dashboard screenshots and suggest improvements such as:

- Reducing pages to four final pages
- Creating consistent navigation
- Using a clear header pattern
- Using a left KPI/filter panel for detail pages
- Cleaning visual titles
- Avoiding misleading stacked percentage charts
- Adding business-friendly insight boxes

### 4. Insight Development

AI helped convert chart outputs into stakeholder-ready observations and recommendations.

Examples:

- Overtime employees show higher attrition.
- Frequent travelers show higher attrition.
- Early-tenure employees show higher attrition.
- Certain job roles show elevated attrition.
- Stock option level may be related to retention patterns.

### 5. GitHub Documentation

AI helped structure documentation for:

- Project README
- Data model notes
- Dashboard page descriptions
- DAX measure documentation
- Insights and recommendations
- Interview preparation

## Responsible AI Use

AI was used to accelerate thinking and documentation, not to replace validation.

Final dashboard decisions were manually reviewed in Power BI Desktop, including:

- Measure behavior
- Visual titles
- Filter behavior
- Page layout
- Chart interpretation
- Business recommendation wording

## Portfolio Positioning

This project demonstrates practical AI-assisted analytics workflow:

> Used AI as a productivity assistant to validate DAX logic, refine visual choices, improve dashboard storytelling, summarize insights, and prepare GitHub documentation. Final modeling, formatting, validation, and business interpretation were reviewed manually.
=======
# AI-Assisted Analytics Workflow

AI was used as a productivity assistant during this project, not as a replacement for manual analysis.

## AI Use Cases

AI helped with:

- Reviewing DAX logic
- Debugging common DAX issues such as row context vs filter context
- Understanding when to use calculated columns vs measures
- Validating `USERELATIONSHIP()` usage
- Suggesting visual alternatives for crowded charts
- Improving chart titles and business labels
- Identifying misleading dashboard behavior
- Drafting executive summaries and GitHub documentation

## Examples of AI-Assisted Improvements

### 1. Employee Status Logic

The original `Attrition` field used `Yes` and `No`. For reporting, this was reframed as:

- `No` → Active
- `Yes` → Inactive

This made visuals and legends easier for business users to interpret.

### 2. Performance Tracker Validation

The Performance Tracker initially showed a future next review date even for inactive employees. This was corrected so inactive employees show `Not applicable` for next review.

### 3. Attrition Visual Selection

Stacked percentage charts were avoided for attrition rate because stacked percentages can be misleading. A matrix was used for Department and Job Role because it shows both population size and risk.

### 4. Documentation Support

AI helped convert the Power BI build into interview-ready project documentation, including business problem, data model, DAX measures, insights, limitations, and recommendations.

## Human Validation

Final decisions were manually reviewed in Power BI, including:

- Data model relationships
- DAX measure output
- Visual formatting
- Dashboard layout
- Business interpretation
- GitHub documentation wording

## Interview-Safe Explanation

I used AI as a productivity assistant to validate DAX logic, improve dashboard design choices, refine business labels, and draft documentation. I manually reviewed all final calculations, visuals, and insights to ensure they made business sense.
>>>>>>> a3a6b12dd8d60cfe99c2b3ed41a21f2ef58f24fb
