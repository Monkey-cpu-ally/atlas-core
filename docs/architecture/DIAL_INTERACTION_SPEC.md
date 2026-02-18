# Dial Interaction Spec

## Document Control
- Program: Unified Builder Polymath Platform
- Surface: Ajani / Minerva / Hermes Dial Console
- Version: v1.1 (Draft)
- Last Updated: 2026-02-17
- Owner: Interaction Architecture

---

## 1. Purpose

Define how the radial HUD behaves at input, motion, and state levels so the dial UI feels precise, predictable, and high quality on mobile devices.

This document is implementation-facing but code-agnostic.

---

## 2. Scope

In scope:
- Ring touch behavior
- Ring rotation and snap behavior
- Gesture priority between rings and center 3D core
- Selection propagation to mode/domain/module/utility state
- Motion and haptic response rules

Out of scope:
- Visual theme token values (see Skin Token Schema)
- Event payload schemas (see Unity Bridge Event Contract)
- Performance gate criteria (see Performance and QA Test Plan)

---

## 3. Ring Stack Definition

Ring order (inside to outside):
1. Command Ring
2. Domain Ring
3. Module Ring
4. Status/Utility Ring

Each ring has:
- fixed center point
- radius band (`innerRadius`, `outerRadius`)
- segment count `N`
- selected segment index
- independent angular position

## 3.1 Command Ring Segment Set (Voice-First Rule)

Command Ring is mode-only.  
`TALK` is removed from ring navigation.

Recommended command segments:
- Blueprint
- Build
- Modify
- Simulate
- Log
- Reflect

Voice access is always available from the center core (hold + wake word) and is not a ring segment.

---

## 4. Hit Zone and Gesture Priority

Priority order for touch ownership:
1. Center long-press zone (voice-first hold trigger)
2. Ring segment in active radius band
3. Center 3D core viewport (orbit/zoom/tap)
4. Global overlays (modals, pickers)

Rules:
- First valid touch-down target owns the pointer until release/cancel.
- Ring drag should not leak into center orbit while pointer is owned by a ring.
- Multi-touch for center zoom is allowed only if no ring owns touch.
- Skin picker modal has top priority and blocks all ring/center interactions.
- Long-press ownership on center blocks ring rotation until long-press end/cancel.

---

## 5. Rotation and Snap Behavior

## 5.1 Rotation Rules
- Ring rotates only around the shared center.
- Rotation direction follows pointer tangential movement.
- Ring angular velocity is tracked during drag.

## 5.2 Inertia Rules
- On release, ring may continue motion using bounded inertia.
- Inertia must decay smoothly; no abrupt cut-offs.
- Inertia profile comes from active skin motion profile.

## 5.3 Snap Rules
- Ring must snap to nearest valid segment center.
- Snap completes in a bounded duration window.
- Final snap index is deterministic from final angular state.
- Optional overshoot is allowed only if final index does not change.

## 5.4 Selection Commit Rule
- Selection commits only when snap settles.
- During drag/inertia, provisional highlight may be shown but does not change global state.

---

## 6. Ring Coupling Modes

Default mode: **independent rings**.

Optional mode: **linked context rotation** (for curated experiences):
- Changing Command Ring may bias Domain Ring starting position.
- Linked mode must remain reversible and explicitly toggled.
- Linked mode cannot alter segment definitions.

---

## 7. Segment Activation Contract

On committed snap:
1. Active segment index is updated for owning ring.
2. Global app state updates according to ring type:
   - Command Ring -> mode
   - Domain Ring -> domain
   - Module Ring -> module
   - Utility Ring -> utility action
3. Core response event is emitted.
4. UI labels and highlights refresh.

If an action is blocked by policy, selection can highlight but command execution must be denied with explicit feedback.

---

## 8. Voice-First Center Interaction Contract

Center core supports voice-first control independent of rings.

Required interaction paths:
1. Hold-to-activate (`onLongPressStart` -> `onLongPressEnd`)
2. Wake-word activation (hands-free)

Required center states:
- `IDLE`
- `LISTENING_PENDING_NAME`
- `LISTENING_TO_AI`
- `PROCESSING`
- `SPEAKING`

Ring behavior during center voice activation:
- rings remain visually neutral
- ring selection state does not auto-change
- ring input may be locked while active hold ownership exists

---

## 9. Motion and Feedback Rules

Required feedback channels:
- visual highlight transition on active segment
- micro haptic on snap commit
- optional tick haptic for segment boundaries during drag

Motion quality requirements:
- no stutter at normal interaction speed
- no segment skipping on medium-speed flicks
- no “double commit” on one release

---

## 10. Accessibility and Precision Rules

- Ring labels must remain readable under active skin typography rules.
- Interaction must support reduced-motion mode:
  - reduced inertia
  - reduced overshoot
  - shorter transition chains
- Touch target width for segment activation must be mobile-safe.
- Visual active state must be distinguishable without color-only cues.

---

## 11. Error and Recovery States

Defined interaction errors:
- pointer cancel during drag
- ring index out-of-range after config update
- modal interrupted snap flow

Recovery behavior:
- revert to last committed segment
- emit non-fatal interaction warning event
- keep global state unchanged on failed commit

---

## 12. Telemetry Requirements

Track interaction metrics per ring:
- drag duration
- snap duration
- overshoot frequency
- missed taps vs successful activations
- selection reversal rate

Use these metrics to tune motion profile and segment spacing.

---

## 13. Acceptance Criteria

A ring interaction implementation is accepted when:
- snap commit is deterministic
- no gesture conflict between ring and center core in standard cases
- state changes occur only on committed snap
- reduced-motion behavior remains functionally equivalent
- all ring actions emit expected state transitions
- center voice interaction paths do not corrupt ring state

---

## 14. Glossary

- **Commit:** The moment a selection becomes official and updates global state.
- **Inertia:** Continued movement after release based on prior drag velocity.
- **Pointer Ownership:** Which UI element controls a touch sequence until release.
- **Provisional Highlight:** Temporary visual focus during drag before commit.
- **Segment:** A discrete selectable slice on a ring.
- **Snap:** Automatic alignment from arbitrary angle to nearest segment center.
- **Tangential Movement:** Finger movement along the ring direction, not radial in/out.
