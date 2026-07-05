# ATLAS Digital Twin Engine — Reports

## Purpose
Reports turn raw project data into useful engineering documents for Frazier, the AIs, and the Council.

---

# Required Reports

## 1. Project Twin Summary

Shows the current state of a digital twin.

Sections:
- Project name
- Purpose
- Lead AI
- Status
- Subsystems
- Components
- Known data
- Unknown data
- Main risks
- Simulation questions
- Council decision

## 2. Component Report

Shows details for one subsystem or component.

Sections:
- Name
- Function
- Material
- Power draw
- Mass
- Cost
- Failure modes
- Replacement options
- Unknowns

## 3. Risk Report

Shows hazards and mitigation.

Sections:
- Risk type
- Severity
- Likelihood
- Mitigation
- Stop condition
- Prototype level allowed

## 4. Simulation Report

Shows calculation results.

Sections:
- Simulation module
- Inputs
- Assumptions
- Outputs
- Warnings
- Confidence level
- Recommended next step

## 5. Prototype Gate Report

Shows whether a physical test is ready.

Sections:
- Prototype level
- Required tools
- Required parts
- Required skills
- Test environment
- Safety controls
- Stop conditions
- Pass criteria
- Fail criteria
- Council decision

## 6. Validation Report

Compares simulation predictions to real test data.

Sections:
- Predicted result
- Measured result
- Difference
- Cause of difference
- Model update needed
- New confidence level

---

# Markdown Report Template

```markdown
# Digital Twin Report — Project Name

## Status

## Purpose

## Lead AI

## Subsystems

## Components

## Known Facts

## Assumptions

## Unknowns

## Risks

## Simulation Questions

## Simulation Results

## Prototype Readiness

## Council Decision

## Next Action
```

---

# Report Rule
Every report should be understandable to a beginner but still useful to an engineer.

No fluff. No fake certainty. No magic numbers.
