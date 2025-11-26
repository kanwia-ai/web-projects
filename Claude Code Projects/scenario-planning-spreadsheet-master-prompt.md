# Master Prompt: Scenario Planning & Budgeting Spreadsheet Development

## Purpose
This prompt guides Claude through a Socratic discovery process to develop comprehensive Excel-based planning models (capacity planning, budgeting, forecasting, scenario analysis, etc.) that are production-ready with functioning formulas, data validation, and professional formatting.

---

## Phase 1: Discovery & Context Gathering

Before building anything, walk the user through these questions to understand the problem:

### 1.1 Business Context
- **What decision(s) will this model help you make?**
  - (e.g., "When to hire," "How much to budget," "Which scenario to pursue")
- **Who will use this model?** (You? Leadership? Finance? Cross-functional?)
- **How often will it be updated?** (Monthly, quarterly, ad-hoc scenarios)

### 1.2 Inputs & Data Sources
- **What data do you have available?**
  - Existing spreadsheets (attach/describe)
  - Historical actuals (what time period?)
  - Transcripts or meeting notes with context
  - Assumptions from leadership
- **What are the key input variables?** (Things users will change to run scenarios)
- **What's fixed vs. variable?**

### 1.3 Outputs & Answers Needed
- **What questions should the finished model answer?**
  - (e.g., "How many people do we need?" "What's our revenue at X growth?")
- **What's the "command center" view?** (Key metrics at a glance)
- **What triggers action?** (e.g., "Hire when gap > 0.5 FTE")

### 1.4 Time Horizon & Granularity
- **What time period?** (12 months, 3 years, etc.)
- **What granularity?** (Monthly, quarterly, annual)
- **Is there a start date or planning period?**

---

## Phase 2: Structure & Logic Design

Once context is gathered, define the model architecture:

### 2.1 Workbook Structure
Recommend a standard structure (user can modify):

| Sheet | Purpose |
|-------|---------|
| **Dashboard / Command Center** | Executive summary, key metrics, decisions at a glance |
| **Assumptions & Inputs** | All user-editable inputs in one place (blue cells) |
| **[Core Model]** | Main calculations (monthly projections, capacity, revenue, etc.) |
| **[Supporting Detail]** | Breakdowns, rosters, catalogs, rates |
| **Scenarios** (optional) | Side-by-side scenario comparison |
| **Instructions** | How to use, color coding legend, troubleshooting |

### 2.2 Input Categories
Identify and categorize all inputs:
- **Volume/Quantity inputs** (units, headcount, workshops, etc.)
- **Rate/Price inputs** (hourly rates, prices, costs)
- **Growth/Change inputs** (% growth, inflation, ramp rates)
- **Timing inputs** (start dates, horizons, frequencies)
- **Allocation inputs** (% splits, mix assumptions)
- **Constraint inputs** (capacity limits, targets, thresholds)

### 2.3 Calculation Logic
Map out the core calculations:
```
[Input A] × [Input B] = [Intermediate Result]
[Intermediate Result] - [Input C] = [Output]
```

Ask:
- What compounds vs. what's linear?
- What has minimums/maximums (use MAX/MIN functions)?
- What triggers conditional logic (IF statements)?

### 2.4 Cross-References
Identify what connects across sheets:
- Which inputs feed into which calculations?
- What rolls up to the dashboard?
- What needs named ranges for clarity?

---

## Phase 3: Technical Specifications

Apply these standards to ensure professional, error-free output:

### 3.1 Color Coding (Financial Modeling Standard)
| Color | Meaning | RGB |
|-------|---------|-----|
| **Blue text + light fill** | Hard-coded inputs (user edits these) | (68, 114, 196) |
| **Black text** | Formulas referencing same sheet | (0, 0, 0) |
| **Green text** | Cross-sheet references | (112, 173, 71) |
| **Red text/fill** | Warnings, over-capacity, negative values | (255, 0, 0) |

### 3.2 Formatting Standards
- **Headers**: 12pt bold, light gray background (#D9D9D9)
- **Titles**: 14-16pt bold
- **Data**: 10pt regular
- **Notes**: 9pt italic gray
- **Numbers**: Use appropriate format (%, #,##0.0, dates as MMM-YY)
- **Freeze panes**: Lock header rows for scrolling

### 3.3 Data Validation
- Percentage inputs that must sum to 100%
- Dropdown lists for categories (role levels, types, etc.)
- Date validation for planning horizons
- Error messages for invalid inputs

### 3.4 Conditional Formatting
- **Green**: On track, within capacity, positive variance
- **Yellow**: Warning zone (e.g., 85-100% utilization)
- **Red**: Over capacity, negative variance, action required

### 3.5 Named Ranges
Create named ranges for frequently-referenced cells:
- `GrowthRate`, `StartDate`, `HoursPerPerson`, etc.
- Makes formulas readable: `=Revenue*GrowthRate` vs `='Sheet1'!$B$15`

### 3.6 Error Prevention
- Use `IFERROR()` to handle divide-by-zero
- Use `IF(A1="","",formula)` for optional input rows
- Use `MAX(0, result)` to prevent negative values where inappropriate

---

## Phase 4: Build Specifications

For each sheet, provide detailed specifications:

### Sheet Template
```
SHEET: [Name]
PURPOSE: [What this sheet does]

SECTION A: [Section Name] (Rows X-Y)
---
Row X: "Header Text" (formatting notes)
Row Y:
  - Column A: "Label"
  - Column B: [value or =FORMULA] (Input_Blue / Formula_Black / CrossRef_Green)
  - Column C: "Note text" (gray italic)

SECTION B: [Next Section]...

NAMED RANGES TO CREATE:
- RangeName = 'Sheet'!$B$5

CONDITIONAL FORMATTING:
- Range: Apply rule

DATA VALIDATION:
- Cell: Validation rule
```

---

## Phase 5: Testing & Validation

Before delivery, specify test scenarios:

### 5.1 Input Sensitivity Tests
- Change key input → verify downstream recalculation
- Set growth to 0% → should show flat projection
- Set input to extreme value → should still calculate (no errors)

### 5.2 Edge Cases
- Empty optional fields → no #VALUE! errors
- 100% allocation → still works
- Delete a row → formulas don't break

### 5.3 Cross-Reference Validation
- All green-text cells actually reference other sheets
- Named ranges resolve correctly
- Dashboard pulls correct values

### 5.4 Logic Validation
- Totals sum correctly
- Percentages add to expected values
- Triggers fire at correct thresholds

---

## Phase 6: Documentation

Include in the Instructions sheet:

1. **Overview**: What the model does, what decisions it supports
2. **Step-by-step guide**: How to update inputs and interpret outputs
3. **Color coding legend**: What each color means
4. **Key assumptions**: What's baked in, what can be changed
5. **Troubleshooting**: Common issues and fixes
6. **Important notes**: Caveats, limitations, update frequency

---

## Example Prompt Structure

When ready to build, provide Claude with:

```markdown
# [Model Name] - Complete Specification

## Executive Summary
[1-2 paragraphs: what this model does and why]

## Background & Context
[Business context, current state, goals]

## Data Inputs Provided
- [Spreadsheet 1]: [description]
- [Transcript]: [key context extracted]
- [Assumptions]: [from leadership/stakeholders]

## Technical Requirements
[Platform, color coding, formatting standards]

## Workbook Structure
[List of sheets with purposes]

## SHEET 1: [Name]
[Detailed specification per template above]

## SHEET 2: [Name]
[...]

## Key Formulas & Logic
[Explain complex calculations]

## Testing Scenarios
[What to verify]

## Success Criteria
[What questions should the model answer?]
```

---

## Quick-Start Questions

To begin any new planning model, ask:

1. **What decision are you trying to make?**
2. **What data/context do you have?** (Share files, transcripts, notes)
3. **What time horizon and granularity?**
4. **Who uses this and how often?**
5. **What's the "dashboard view" you need?**

From there, iterate through discovery → structure → build → test.

---

## Example: Workshop Capacity Calculator

This framework was tested with a workshop capacity planning model:

**Inputs provided:**
- 2025 Workshop Actuals (67 workshops with categories)
- Capacity Planning Session transcript (team discussion)
- Iterative refinements via conversation

**Output generated:**
- 4-sheet workbook (Control Panel, Team Roster, Capacity Model, Instructions)
- Role-based overhead assumptions (Lead 50%, Level 2 30%, Level 3 20%)
- Workshop mix based on historical actuals
- Command center with hiring decisions, annual goal tracking, capacity status
- 12-month projections with conditional formatting
- All formulas functioning with cross-sheet references

**Key features:**
- All inputs editable (blue cells)
- Cross-sheet references in green
- Conditional formatting for utilization (green/yellow/red)
- Hire signal triggers at 0.5 FTE gap
- Compound monthly growth
- Team roster feeds capacity model automatically
