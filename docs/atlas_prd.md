# Atlas Core (Hybrid Orchestrator) - Product Requirements Document

## Product Name
Atlas Core (Hybrid Orchestrator)

## Product Type
Hybrid AI orchestration system:
- Frontend: Node/Next UI
- Backend: FastAPI orchestration brain

## Purpose
Atlas routes user requests to specialized modules (Ajani, Minerva, Hermes),
combines outputs, enforces safety policy, and maintains structured project pipelines.

Atlas does not think. Atlas governs and routes.

## Core Objectives
- Structured blueprint generation
- Teachable breakdowns
- Validation and safety gates
- Per-project memory
- Blueprint -> Build -> Modify lifecycle

## Target User
- Primary: builder/engineer mindset user
- Future: collaborators and internal AI modules

## MVP Features
- `POST /route` endpoint
- Intent classification
- Ordered agent execution (Ajani -> Minerva -> Hermes)
- Validation gates
- Pipeline tracking
- Project-scoped memory

## Non-Goals (Current Scope)
- Autonomous execution
- Hardware control
- Unsupervised self-updating
- Global shared memory

## Success Criteria
- One input -> structured triple output
- Blueprint outputs include measurable steps
- Hermes can block unsafe inputs
- Project memory is isolated by project

