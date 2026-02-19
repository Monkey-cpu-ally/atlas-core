# Skin Token Schema

## Document Control
- Program: Unified Builder Polymath Platform
- Surface: Dial HUD + 3D Core Visual Layer
- Version: v1.1 (Draft)
- Last Updated: 2026-02-19
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

## 3.1 Free Selection Model (Mode != Skin)

Core rule:
- skins are fully user-selectable at any time
- skins do not auto-switch based on mode

Definition:
- **Mode = function.** (what the system does)
- **Skin = atmosphere.** (how the system feels)

Persistence rule:
- the selected skin persists across:
  - app restart
  - mode change
  - AI speaker change
  - council activation
- skin remains active until manually changed

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

## 7. Baseline Skin Profiles (Initial Set)

## 7.1 Lumen Core
- Intent: minimal, clean background with a single accent energy line
- Material bias: smooth, low-noise surfaces
- Density bias: minimal to standard

## 7.2 Archive Grid
- Intent: bold geometric blocks with cultural strength and structure
- Material bias: strong panel separation, crisp edges
- Density bias: standard (structured layout)

## 7.3 Circuit Veil
- Intent: white/tech/angular precision with subtle micro circuit lines
- Material bias: high-contrast precision look (clean, surgical)
- Density bias: minimal to standard

## 7.4 Module Array
- Intent: modular panels and component-style engineering aesthetic
- Material bias: visible structure without clutter
- Density bias: standard to telemetry (component-forward)

---

## 8. Runtime Apply Rules

- User selects a skin from the outer ring "Skins" tab (Status/Utility ring).
- Skin apply must be a smooth crossfade:
  - target: 400–600 ms
  - no hard cuts
- Confirmed apply writes active skin state and persists it.
- Skin changes must not reset selected mode/domain/module.

Optional preview model (allowed but not required):
- Skin preview may apply non-destructively.
- Canceled preview restores previous skin without state drift.

AI accent compatibility rule:
- skins must not override AI accent colors
- speaker accent overlays remain global and independent from skins

Council compatibility rule:
- Ghost Purple overlay must render correctly on all skins
- it must remain muted/translucent and never clash with skin base colors

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
