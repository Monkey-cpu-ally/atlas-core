# ATLAS Platform Package

This folder is reserved for the executable ATLAS platform code.

The goal is to turn the documented ATLAS systems into maintainable Python modules.

---

# Planned Packages

```text
atlas_platform/
  core/
  schemas/
  graph_memory/
  digital_twin/
  research_pipeline/
  prototype_manager/
  innovation_lab/
```

---

# Package Responsibilities

## core
Shared utilities, IDs, configuration, validation helpers, and common types.

## schemas
Shared Python data models used by all ATLAS systems.

## graph_memory
Node, edge, and relationship logic.

## digital_twin
Project models, components, risks, simulation questions, reports, and estimates.

## research_pipeline
Source intake, reliability scoring, claim extraction, and evidence routing.

## prototype_manager
Prototype readiness, bill of materials, test plans, failure logs, and test feedback.

## innovation_lab
Project intake, scoring, Council review, handoff decisions, and project lifecycle.

---

# Rule

Code should follow the documents, not wander away from them.

If a module does not map to a documented ATLAS responsibility, it should not be added yet.
