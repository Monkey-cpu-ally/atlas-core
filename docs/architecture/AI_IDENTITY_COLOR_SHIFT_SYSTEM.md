# AI Center Ripple + Color Activation System

## Document Control
- Program: Unified Builder Polymath Platform
- Surface: Dial HUD + 3D Core + Voice UI
- Version: v1.1 (Draft)
- Last Updated: 2026-02-17
- Owner: Identity and Visual Systems

---

## 1. Purpose

Define a speaker-driven visual identity system where only the **center 3D core** activates with persona color and ripple behavior.

Design intent:
- preserve a clean, premium interface,
- express AI identity clearly,
- avoid full-UI color flooding.

This is a dynamic center-core activation layer, not a full theme switch.

---

## 2. Scope

In scope:
- center-core accent activation by active AI speaker
- ripple/wave surface behavior while speaking
- fade-in/fade-out timing rules
- waveform-linked pulse behavior

Out of scope:
- ring recolor behavior (rings remain neutral)
- skin replacement behavior
- routing/state-machine behavior
- policy/safety logic

---

## 3. Core Concept (Non-Negotiable)

Default state:
- center core is neutral
- subtle idle motion only
- no accent color and no ripple

Active speaker state:
- center core applies speaker accent rim light
- surface ripple effect activates
- speaking-end fades back to neutral

Hard rule:
- rings and outer UI do not change identity color.

---

## 4. Identity Color Profiles

## 4.1 Ajani
- Accent family: deep crimson (non-neon)
- Identity intent: strategic strength and structural decisiveness
- Motion character: slightly sharper pulse and clearer ripple edges

## 4.2 Minerva
- Accent family: balanced teal-blue (non-electric)
- Identity intent: reflective guidance and calm depth
- Motion character: softer ripple edges and smoother transitions

## 4.3 Hermes
- Accent family: warm ivory (light neutral with slight warmth)
- Identity intent: precision, logic, and controlled execution
- Motion character: minimal distortion and cleaner light band

---

## 5. Trigger Model

Activate center identity state when any of the following begins:
1. AI voice playback starts
2. AI text response starts typing
3. Voice waveform begins active animation

Deactivate center identity state when:
- audio playback ends, and
- typing/waveform activity is complete.

---

## 6. Center-Core Visual Behavior

When active:
1. Accent rim light fades in
2. Ripple effect begins across core surface
3. Pulse intensity modulates lightly with voice amplitude

When inactive:
1. Ripple fades out
2. Accent rim light fades to neutral
3. Core returns to baseline idle material and motion

---

## 7. Ripple Effect Specification

Effect style:
- radial wave distortion
- subtle, elegant propagation
- no harsh flashing
- no full-surface recolor

Behavior constraints:
- low distortion amplitude
- amplitude clamped to preserve surface readability
- temporal smoothing required (avoid jitter at noisy audio input)

---

## 8. Transition Rules

## 8.1 Activate
- Fade-in: 300–500 ms
- No hard snap transitions

## 8.2 Speaker Switch
- Crossfade prior accent to new accent
- Crossfade must preserve visual continuity

## 8.3 Deactivate
- Ripple fade-out target: ~400 ms
- Accent fade-to-neutral: smooth, no hard cut
- Optional residual afterglow up to 1 second

---

## 9. Non-Affected Surfaces Rule

The following must remain neutral during identity activation:
- Command Ring
- Domain Ring
- Module Ring
- Status/Utility Ring
- Outer HUD panels and navigation chrome

Only center-core identity surfaces may shift accent color.

---

## 10. State Contract

Identity renderer consumes:
- `currentSpeaker` (`ajani` | `minerva` | `hermes` | `null`)
- `accentColor`
- `glowIntensity`
- `rippleProfileId`
- `motionProfileModifier` (optional)

State consumers:
- Unity 3D core renderer (primary)
- waveform renderer (accent only)

`currentSpeaker = null` must map to neutral core state.

---

## 11. Implementation Paths

## 11.1 Unity Path (Preferred)
- shader-based radial distortion
- emission/rim-light modulation
- optional normal-map ripple animation
- amplitude input from voice envelope signal

## 11.2 Flutter 3D Path (Fallback)
- animated shader parameter where supported
- low-amplitude surface displacement or overlay ripple texture
- clamped brightness modulation from waveform amplitude

Both paths must honor the same behavioral constraints and timing windows.

---

## 12. Integration Rules

- Identity activation overlays the center core on top of current skin baseline.
- Skin controls baseline look; identity controls temporary speaker activation.
- Identity behavior must not modify:
  - command semantics,
  - mode/domain/module state,
  - policy/safety behavior.

---

## 13. Validation Checklist

Accept only when:
- each AI profile triggers correct center accent and ripple behavior
- rings remain neutral in all speaker states
- activation/deactivation timing stays within specified windows
- transitions remain smooth with no hard color snaps
- contrast/readability remains acceptable during active pulse

---

## 14. Glossary

- **Accent Rim Light:** Colored edge highlight around the center core.
- **Center Activation State:** Temporary visual state while an AI is actively speaking.
- **Neutral State:** Default center-core visual condition with no speaker accent.
- **Ripple Profile:** Persona-specific wave behavior (speed, softness, edge definition).
- **Speaker Switch Crossfade:** Smooth transition from one active speaker profile to another.
- **Wave Envelope:** Smoothed voice intensity signal used for light pulse modulation.
