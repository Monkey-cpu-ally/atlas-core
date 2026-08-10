# ATLAS Wearables UX Bible

**Version:** 1.0  
**Classification:** Wearable Interface Standard

## Purpose

ATLAS wearable interfaces provide glanceable, context-sensitive access to useful information without turning the user's body into another crowded dashboard.

This standard covers future watches, glasses, field displays, haptic devices, and other wearable endpoints.

## Core Principles

1. **Glanceable** — the user should understand the most important state quickly.
2. **Minimal** — show only information justified by the immediate context.
3. **Low interruption** — alerts are prioritized and rate-limited.
4. **Private by default** — sensitive content is protected from accidental exposure.
5. **Contextual** — the interface adapts to device capability and task.
6. **Energy-aware** — battery and thermal limits influence presentation and background activity.

## Information Hierarchy

Wearables prioritize:

- Critical safety alerts
- Time-sensitive project or system status
- Current task
- Navigation or step guidance
- AI response summaries
- Quick capture
- Communication

Long-form research, complex editing, and dense engineering work should hand off to a larger interface.

## Smartwatch Experience

Suitable functions include:

- Notifications
- Task status
- Short AI responses
- Timers
- Approvals appropriate to the risk level
- Quick notes
- Device status

## Smart Glasses Experience

Suitable functions include:

- Hands-free instructions
- Contextual labels
- Navigation
- Assembly guidance
- Inspection notes
- Robot or machine status
- Spatial annotations

Glasses must preserve real-world visibility and avoid placing persistent content directly over hazards.

## Haptics

Haptic patterns should be limited, learnable, and mapped consistently to meanings such as confirmation, navigation cue, warning, or critical alert.

Every essential haptic event requires another accessible communication path.

## AI Interaction

Wearables should favor short interactions. Complex conversations may begin on the wearable and continue seamlessly on mobile or desktop.

## Privacy & Security

Design must account for shoulder surfing, public audio, visible displays, biometric data, location data, and sensors that may capture bystanders.

Sensitive actions require authentication appropriate to their consequences.

## Offline & Failure Behavior

Wearables should clearly distinguish cached information from live information and communicate loss of connectivity, sensor uncertainty, and synchronization state.

## Accessibility

Support adjustable text, reduced motion, strong contrast, captions, configurable haptics, voice alternatives, and companion-device configuration where practical.

## Final Principle

A wearable should disappear into the user's activity. ATLAS should provide the smallest useful amount of information at the right moment and move complex work to the device best suited for it.
