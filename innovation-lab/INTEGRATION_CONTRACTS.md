# ATLAS Innovation Lab — Integration Contracts

## Purpose
This file defines how the Innovation Lab connects to the rest of ATLAS.

The goal is clean system boundaries. Each subsystem should know what it receives, what it produces, and what it must not fake.

---

# 1. Innovation Lab → Research Pipeline

## Sends
- Project idea
- Research questions
- Required evidence areas
- Unknowns
- Source needs

## Receives
- Source notes
- Reliability ratings
- Extracted claims
- Evidence labels
- Research gaps
- Follow-up research recommendations

## Contract Rule
The Research Pipeline provides evidence. The Innovation Lab decides how that evidence affects the project.

---

# 2. Innovation Lab → Graph Memory

## Sends
- Project records
- Concepts
- Risks
- Decisions
- AI ownership
- Project relationships
- Source relationships

## Receives
- Related projects
- Related risks
- Similar concepts
- Prior decisions
- Supporting sources
- Contradicting sources

## Contract Rule
Graph Memory stores relationships. It should not invent proof.

---

# 3. Innovation Lab → Digital Twin Engine

## Sends
- Project definition
- Subsystems
- Components
- Materials
- Sensors
- Simulation questions
- Failure modes
- Validation criteria

## Receives
- Simulation reports
- Estimate reports
- Confidence levels
- Warnings
- Data needs
- Validation updates

## Contract Rule
The Digital Twin Engine predicts behavior. It does not guarantee real-world performance without validation.

---

# 4. Innovation Lab → Prototype Manager

## Sends
- Approved concept
- Prototype level recommendation
- Safety risks
- Test goals
- Stop conditions
- Required data

## Receives
- Prototype readiness status
- Bill of materials
- Test plan
- Failure logs
- Test results
- Digital Twin feedback notes

## Contract Rule
The Prototype Manager controls safe testing. It can block a build even if the idea is exciting.

---

# 5. Innovation Lab → ATLAS Council

## Sends
- Project intake
- Evidence summary
- Score report
- Risk report
- Digital Twin recommendation
- Prototype recommendation

## Receives
- Continue
- Redesign
- Pause
- Archive
- Prototype
- Patent review
- Manufacturing readiness review

## Contract Rule
The Council decides project direction. Each AI must give a distinct review from its role.

---

# 6. Innovation Lab → ATLAS Memory Bank

## Sends
- Stable decisions
- Project summaries
- User preferences
- Design rules
- Major lessons learned
- Long-term project state

## Receives
- Prior user preferences
- Older project history
- Design standards
- Past failures
- Locked decisions

## Contract Rule
Memory Bank stores durable knowledge. Temporary brainstorming should not be promoted unless reviewed.

---

# 7. Innovation Lab → HUD / UX Division

## Sends
- Project state
- AI owner
- Risk level
- Prototype readiness
- Council decision
- Simulation status

## Receives
- Visualization requirements
- Interaction patterns
- User display format
- Alert styles
- AI face/HUD behavior

## Contract Rule
UX makes the system understandable. It must not hide uncertainty or risk.

---

# Contract Standard

Every integration should answer:

1. What data is sent?
2. What data is received?
3. Who owns the decision?
4. What confidence level is attached?
5. What must not be assumed?
