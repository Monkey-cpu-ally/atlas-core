# Phase 5 Implementation Roadmap

## Sprint 1 — Foundation Scaffold

Purpose: create the permanent code-ready structure.

Deliverables:

```text
atlas-core-runtime/
atlas-memory-engine/
atlas-knowledge-engine/
atlas-agent-runtime/
atlas-api/
atlas-config/
atlas-events/
atlas-tasks/
atlas-diagnostics/
atlas-tests/
```

## Sprint 2 — Core Runtime

Build:

- service registry
- module loading
- configuration loading
- startup sequence
- shutdown sequence
- health checks

## Sprint 3 — Event Bus

Build:

- event contract
- publish/subscribe interface
- event logging
- division message routing
- task completion events

## Sprint 4 — Memory Engine

Build:

- memory record model
- user memory
- project memory
- knowledge memory
- research memory
- archive memory
- relationship model

## Sprint 5 — Knowledge Engine

Build:

- knowledge bank model
- source passport model
- source registry
- knowledge entry model
- evidence rating model
- source-to-knowledge pipeline

## Sprint 6 — Agent Runtime

Build:

- agent identity model
- agent role permissions
- task assignment
- agent responses
- Council review workflow

## Sprint 7 — Hermes V1

Build Hermes as the first working specialist.

Responsibilities:

- software engineering
- robotics
- electronics
- manufacturing
- engineering reports
- GitHub review

## Sprint 8 — Minerva V1

Responsibilities:

- biology
- botany
- medicine
- environment
- art/design
- storytelling
- education

## Sprint 9 — Ajani V1

Responsibilities:

- strategy
- risk
- business
- economics
- operations
- planning

## Sprint 10 — Council V1

Build:

- multi-agent review
- final recommendation format
- confidence scoring
- risk summary
- next action output

## Rule

Do not build the HUD before the backend foundations exist. The HUD should display real system state, not fake data.
