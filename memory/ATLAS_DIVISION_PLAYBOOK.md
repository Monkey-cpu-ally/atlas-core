# ATLAS Division Playbook

This document lets ATLAS development move through multiple focused chats without losing precision, quality, or architectural control.

## Core Rule

Use GitHub as the shared source of truth. Each chat works on one division only. The main ATLAS Core chat remains the integration authority.

No division should edit the same files at the same time unless the Core chat approves it.

## Luxury Engineering Standard

Every subsystem must be:

1. Functional
2. Tested
3. Cleanly named
4. Modular
5. Documented
6. Safe by default
7. Easy to upgrade
8. Consistent with Ajani, Hermes, Minerva, and Council roles
9. Integrated with the larger ATLAS roadmap

## Division Structure

### 1. ATLAS Core Engineering

Owner: Council

Focus:
- Architecture
- Integration
- GitHub repository health
- CI/testing
- Backend route/service consistency
- Final review

Current priority:
- Stabilize External Access Gateway
- Add tests for newest services
- Continue Discovery Approval Pipeline

Avoid:
- HUD-only work
- Random feature expansion without roadmap alignment

### 2. Knowledge Division

Owner: Minerva

Focus:
- Discovery Approval Pipeline
- Knowledge Record Writer
- Chronicle Engine
- Ivy Tech learning integration
- YouTube learning integration
- Source validation
- Evidence scoring

Must connect to:
- Knowledge Bank
- Research Labs
- Source Sync
- Knowledge Graph
- Project Intelligence

### 3. Robotics Division

Owner: Hermes

Focus:
- Weaver OS
- Robot Fleet Manager
- Digital Twins
- Sensor Fusion
- NIR Scanner
- CAD/Blueprint workflow
- Manufacturing planning

Must connect to:
- Project Intelligence
- Blueprint Bank
- Digital Twin Engine
- Mission Scheduler

### 4. HUD and Luxury UX Division

Owner: Hermes

Focus:
- Luxury HUD
- Figma handoff
- AI faces
- Voice UI
- Animated rings
- Council chamber
- Mission Control panels

Must connect to:
- Backend APIs only after they are stable
- Project Intelligence
- External Access Gateway
- Mission Scheduler

### 5. Innovation Lab

Owner: Ajani + Hermes + Minerva + Council

Focus:
- Quantum Outcome Engine
- Probability Engine
- Innovation Engine
- Evolution Engine
- Experiment Engine

Must wait until:
- Discovery Approval Pipeline exists
- Knowledge records exist
- Project Intelligence is stable

## Standard Prompt for New Division Chats

Use this prompt when starting another focused ATLAS chat:

```text
You are working on ATLAS in the [DIVISION NAME] division.

Repository: Monkey-cpu-ally/atlas-core

Follow the ATLAS Luxury Engineering Standard:
- functional
- precise
- tested
- modular
- safe by default
- documented
- no random architecture changes

Do not edit files outside this division unless the Core Engineering chat approves it.

Current mission:
[PASTE MISSION]

Before coding:
1. Inspect existing related files.
2. Identify integration points.
3. Avoid duplicate systems.
4. Write service + routes + tests where appropriate.
5. Report files changed and next steps.
```

## Current Phase Order

1. External Access Gateway stabilization
2. Discovery Approval Pipeline
3. Knowledge Record Writer
4. Chronicle Engine
5. Quantum Outcome Engine
6. Innovation Engine
7. Evolution Engine
8. Experiment Engine
9. Robotics/Digital Twin expansion
10. Luxury HUD

## Merge Rule

All division work should pass CI before being considered stable.

If CI fails:
- inspect failure report
- create repair plan
- fix the smallest root cause
- do not remove ATLAS features just to pass tests
