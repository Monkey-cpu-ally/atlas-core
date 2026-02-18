# Skin Token Schema

## Document Control
- Program: Unified Builder Polymath Platform
- Surface: Dial HUD + 3D Core Visual Layer
- Version: v1.0 (Draft)
- Last Updated: 2026-02-17
- Owner: Visual Systems Architecture

---

## 1. Purpose

Define a strict token schema for skins so visual identity can change significantly while system logic remains unchanged.

This is the contract that separates:
- **Function layer** (state machine, ring logic, routing) from
- **Skin layer** (style, motion tuning, visual density).

---

## 2. Scope

In scope:
- skin token categories
- required vs optional token fields
- skin validation rules
- profile constraints for performance and accessibility

Out of scope:
- ring math and snapping rules
- bridge event semantics
- project/domain business logic

---

## 3. Non-Negotiable Separation Rule

Skins may change:
- visual tokens
- motion profile values
- panel and icon style

Skins may not change:
- event semantics
- mode/domain/module identifiers
- routing behavior
- policy/safety behavior
- command meaning

---

## 4. Token Families

Every skin definition must include these families:

1. **Color Tokens**
- background layers
- primary/secondary accents
- warning/success/error states
- text hierarchy colors

2. **Material Tokens**
- panel surface type (glass/solid/matte)
- edge treatment
- noise/grain overlays
- depth/shadow style

3. **Ring Tokens**
- ring thickness
- segment spacing
- tick mark style
- active segment emphasis style

4. **Typography Tokens**
- font families
- heading/body/label weights
- tracking and line-height multipliers

5. **Motion Tokens**
- inertia intensity
- snap duration target
- overshoot amplitude
- bounce damping

6. **HUD Density Tokens**
- layout density (`minimal`, `standard`, `telemetry`)
- panel padding scale
- info block stacking behavior

7. **Icon Tokens**
- icon style family
- stroke/fill behavior
- active-state icon treatment

8. **Effect Budget Tokens**
- max blur strength
- max glow intensity
- shader complexity tier

---

## 5. Required Field Matrix

| Family | Required | Notes |
|---|---|---|
| Color | Yes | Must include contrast-safe text pairings |
| Material | Yes | Must define default panel and ring material behavior |
| Ring | Yes | Required for consistent radial rendering |
| Typography | Yes | Must include all heading/body/meta tiers |
| Motion | Yes | Must include snap and inertia values |
| HUD Density | Yes | Must define at least one default density |
| Icon | Yes | Must define active/inactive states |
| Effect Budget | Yes | Required for performance guardrails |

---

## 6. Skin Validation Rules

A skin is valid only if:
1. all required token families exist
2. no forbidden function-layer fields are present
3. contrast checks pass for key text surfaces
4. motion values remain within approved interaction bounds
5. effect budget does not exceed target device tier limits

Invalid skin definitions must fail before runtime apply.

---

## 7. Baseline Skin Profiles

## 7.1 Obsidian Lab
- Density: telemetry-heavy
- Material bias: dark slate + restrained glow
- Motion bias: deliberate, low-bounce
- Typical use: simulate, diagnostics, logs

## 7.2 Atlas Command
- Density: standard
- Material bias: map/terrain-informed overlays + metallic framing
- Motion bias: moderate inertia with clear snap feedback
- Typical use: global project navigation and domain switching

## 7.3 Ivory Surgical
- Density: minimal to standard
- Material bias: clean high-contrast precision surfaces
- Motion bias: tight, fast settle, minimal overshoot
- Typical use: stepwise blueprint and learning modes

---

## 8. Runtime Apply Rules

- Skin preview may apply non-destructively.
- Confirmed apply writes active skin state.
- Canceled preview restores previous skin without state drift.
- Skin changes must not reset selected mode/domain/module.

---

## 9. Fallback Rules

If a skin fails validation at runtime:
1. reject apply
2. retain prior valid skin
3. log validation errors for diagnostics

If active skin degrades performance beyond budget:
- switch effect budget to reduced tier
- preserve core color/material identity where possible

---

## 10. Accessibility Guardrails

- Active segment and focused control must be distinguishable without color-only cues.
- Font tokens must preserve readability at scaled text sizes.
- Reduced-motion profile must be available for every skin.
- Critical status indicators must remain legible across all skins.

---

## 11. Glossary

- **Effect Budget:** Upper limit for expensive visual effects allowed on target hardware.
- **Function Layer:** System behavior that remains fixed across all skins.
- **HUD Density:** Amount of on-screen telemetry and panel complexity.
- **Motion Profile:** Numeric rules controlling inertia, snap speed, and bounce feel.
- **Skin Token:** A named style value used by the renderer/UI layer.
- **Validation Rule:** Requirement a skin must satisfy before it can be applied.
