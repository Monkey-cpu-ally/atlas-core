# ATLAS Digital Twin Engine — Requirements

## Purpose
This file defines what the Digital Twin Engine must do in its first serious version.

The Digital Twin Engine is not expected to be industrial-grade simulation on day one. It must start as a precise modeling and reporting system that can grow into deeper simulation.

---

# Functional Requirements

## DT-FR-001 — Project Modeling
The system must represent an invention as a structured project with name, category, purpose, lead AI, status, operating environment, and Council decision.

## DT-FR-002 — Subsystem Modeling
The system must break a project into subsystems with clear functions.

## DT-FR-003 — Component Modeling
The system must record components, including type, function, material, estimated mass, estimated cost, power draw, and failure modes.

## DT-FR-004 — Risk Modeling
The system must record risks with type, severity, likelihood, mitigation, and stop condition.

## DT-FR-005 — Simulation Question Tracking
The system must track what a simulation is trying to answer before calculations begin.

## DT-FR-006 — Basic Estimation Modules
The first version must support simple estimates for:
- Mass
- Power draw
- Runtime
- Heat concern
- Load concern
- Risk level

## DT-FR-007 — Report Generation
The system must generate human-readable Markdown reports for project state, components, risks, simulation results, prototype readiness, and validation.

## DT-FR-008 — Confidence Labels
Every estimate must include a confidence level: low, medium, or high.

## DT-FR-009 — Validation Updates
The system must accept real prototype test results and mark whether the model needs updates.

---

# Non-Functional Requirements

## DT-NFR-001 — Explainability
Every calculation must show its assumptions and warnings.

## DT-NFR-002 — Modularity
New simulation modules must be added without rewriting the whole system.

## DT-NFR-003 — Safety Awareness
The system must not treat simulation as proof of safety.

## DT-NFR-004 — Human Readability
Outputs must be readable by Frazier and useful to ATLAS AIs.

## DT-NFR-005 — Growth Path
The first version must be simple enough to build, but structured enough to later support CAD, robotics, thermal, electrical, and control-system simulation.

---

# MVP Completion Standard

The Digital Twin MVP is complete when it can:

1. Load a project record
2. Load components
3. Load risks
4. Run basic estimates
5. Generate a Markdown report
6. Mark confidence levels
7. Accept test-result feedback

---

# Rule
A useful rough model with clear assumptions is better than a beautiful fake simulation.
