# ATLAS HUD Design System

## Purpose
The ATLAS HUD Design System defines the next-generation interface language for ATLAS OS. It connects the calm default core state with active AI awakening states for Ajani, Hermes, Minerva, and Council.

## Source of Truth
Figma should become the visual source of truth. GitHub stores the implementation contract: design tokens, states, interaction rules, animation rules, and component specifications.

## Core Interface Principle
ATLAS should not feel like separate screens opening. The HUD should feel like one living system changing state.

Default state:
- amber core
- minimal rings
- calm particles
- low visual noise

Active AI state:
- the core remains centered
- the AI color takes over
- knowledge nodes unfold outward
- relevant banks and missions appear around the core

## AI Colors
- Ajani: crimson / engineering force
- Hermes: blue-white / robotics and design clarity
- Minerva: teal-green / science and nature
- Council: purple / executive synthesis
- ATLAS idle: amber-gold / core standby

## Pages Recommended in Figma
- ATLAS Design System
- Core HUD Idle
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
