# ATLAS HUD Design System

## Purpose
The ATLAS HUD Design System defines the interface language for ATLAS Headquarters. It connects the calm default core state with active AI states for Ajani, Hermes, Minerva, and Council.

## Source of Truth
Figma should become the visual source of truth. GitHub stores the implementation contract: design tokens, states, interaction rules, animation rules, and component specifications.

## Core Interface Principle
ATLAS should not feel like separate screens opening. The HUD should feel like one living headquarters changing state.

Default state:
- amber core
- minimal transparent rings
- calm particles
- low visual noise
- mission surfaces available through clear navigation

Active AI state:
- the core remains centered
- the AI color takes over with restraint
- relevant knowledge nodes unfold outward
- banks, missions, standards, and briefings appear around the core

## Headquarters Zones
- Council Chamber: Ajani, Hermes, Minerva, and Council deliberation.
- Headquarters Systems: status, memory, standards, diagnostics, customization.
- Mission Departments: knowledge, lab, projects, blueprints, archive, source intake.
- Knowledge Gate: evidence approval and trusted records.
- Source Clearance: permission-first intake and import review.
- Project Briefing: risks, recommendations, reuse signals.
- Refinement Office: ATLAS polish, generic-feel removal, technical debt.

## AI Colors
- Ajani: crimson / engineering force
- Hermes: blue-white / robotics and design clarity
- Minerva: teal-green / science and nature
- Council: purple / executive synthesis
- ATLAS idle: amber-gold / core standby

## Pages Recommended in Figma
- ATLAS Design System
- Core HUD Idle
- Headquarters Overview
- Council Chamber
- Mission Control
- Knowledge Gate
- Source Clearance
- Project Briefing
- Refinement Office
- Ajani Active State
- Hermes Active State
- Minerva Active State
- Council Active State
- Knowledge Graph
- Research Labs Dashboard
- Engineering Console
- Bank Navigation
- AI Portraits
- Components
- Motion States

## Implementation Notes
Developers should treat this folder as the bridge between Figma and code. Every Figma component should eventually map to a reusable frontend component or design token.

No HUD element should exist only because it looks cool. It must support a real Headquarters function, a verified API, or a clearly marked future surface.
