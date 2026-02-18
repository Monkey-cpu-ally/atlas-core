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

Voice-first rule:
- `TALK` is removed from the command ring.
- Voice is always available through center hold or wake word.

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

## 5. Hold-to-Activate Flow (Touch)

## 5.1 Press Down
Trigger: `onLongPressStart`

Center animation (150–250 ms):
- scale to 1.05x–1.08x
- neutral glow increases slightly
- thin listening band appears around core

State transition:
- `IDLE -> LISTENING_PENDING_NAME`

## 5.2 AI Name Detected
Accepted names:
- Ajani
- Minerva
- Hermes

On detection:
- set `activeSpeaker`
- apply speaker accent rim light
- tint listening band to speaker accent
- start ripple effect

Transition window:
- ~300 ms fade

State transition:
- `LISTENING_PENDING_NAME -> LISTENING_TO_AI`

## 5.3 Release
Trigger: `onLongPressEnd`

If speaker detected:
- continue to processing and response flow

If speaker not detected:
- fade to neutral (200–300 ms)
- scale returns to 1.0
- listening band disappears

---

## 6. Wake Word Flow (Hands-Free)

Trigger:
- `wakeWordDetected("Ajani" | "Minerva" | "Hermes")`

Behavior:
- no touch required
- core expands to ~1.05x
- speaker accent activates
- ripple and listening waveform begin

State transition:
- `IDLE -> LISTENING_TO_AI`

---

## 7. Processing and Speaking Flow

## 7.1 Processing
Trigger:
- user input complete while in listening state

Behavior:
- keep speaker accent rim light
- ripple slows
- soft inner pulse remains active

State:
- `PROCESSING`

## 7.2 Speaking
Trigger:
- `aiResponseStart`

Behavior:
- ripple lightly synced to output waveform
- accent glow slightly stronger
- optional subtle rotation lift

State:
- `SPEAKING`

## 7.3 Done Speaking
Trigger:
- `aiResponseEnd`

Behavior (~400 ms):
- ripple fades out
- accent fades to neutral
- scale returns to 1.0
- listening band disappears

State transition:
- `SPEAKING -> IDLE`

---

## 8. Ripple Effect Specification

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

## 9. Transition Rules

## 9.1 Activate
- Fade-in: 300–500 ms
- No hard snap transitions

## 9.2 Speaker Switch
- Crossfade prior accent to new accent
- Crossfade must preserve visual continuity

## 9.3 Deactivate
- Ripple fade-out target: ~400 ms
- Accent fade-to-neutral: smooth, no hard cut
- Optional residual afterglow up to 1 second

---

## 10. Non-Affected Surfaces Rule

The following must remain neutral during identity activation:
- Command Ring
- Domain Ring
- Module Ring
- Status/Utility Ring
- Outer HUD panels and navigation chrome

Only center-core identity surfaces may shift accent color.

---

## 11. State Contract

Identity renderer consumes:
- `currentSpeaker` (`ajani` | `minerva` | `hermes` | `null`)
- `currentState` (`IDLE` | `LISTENING_PENDING_NAME` | `LISTENING_TO_AI` | `PROCESSING` | `SPEAKING`)
- `accentColor`
- `glowIntensity`
- `rippleProfileId`
- `motionProfileModifier` (optional)

State consumers:
- Unity 3D core renderer (primary)
- waveform renderer (accent only)

`currentSpeaker = null` must map to neutral core state.

---

## 12. State Machine (Canonical)

States:
- `IDLE`
- `LISTENING_PENDING_NAME`
- `LISTENING_TO_AI`
- `PROCESSING`
- `SPEAKING`

Transitions:
- `IDLE -> LISTENING_PENDING_NAME` (hold start)
- `LISTENING_PENDING_NAME -> LISTENING_TO_AI` (AI name detected)
- `LISTENING_TO_AI -> PROCESSING` (user input complete)
- `PROCESSING -> SPEAKING` (AI response start)
- `SPEAKING -> IDLE` (AI response end)

Wake-word path:
- `IDLE -> LISTENING_TO_AI` (wake word detected)

---

## 13. Implementation Paths

## 13.1 Unity Path (Preferred)
- shader-based radial distortion
- emission/rim-light modulation
- optional normal-map ripple animation
- amplitude input from voice envelope signal

## 13.2 Flutter 3D Path (Fallback)
- animated shader parameter where supported
- low-amplitude surface displacement or overlay ripple texture
- clamped brightness modulation from waveform amplitude

Both paths must honor the same behavioral constraints and timing windows.

---

## 14. Animation Guidelines

Expansion:
- ease-out curve
- maximum scale 1.08

Ripple:
- radial shader distortion
- low speed, low intensity

Glow:
- emission/rim-light layer
- do not tint full UI

Performance target:
- 60 fps
- avoid heavy particle effects

---

## 15. Integration Rules

- Identity activation overlays the center core on top of current skin baseline.
- Skin controls baseline look; identity controls temporary speaker activation.
- Identity behavior must not modify:
  - command semantics,
  - mode/domain/module state,
  - policy/safety behavior.

---

## 16. Validation Checklist

Accept only when:
- each AI profile triggers correct center accent and ripple behavior
- rings remain neutral in all speaker states
- activation/deactivation timing stays within specified windows
- transitions remain smooth with no hard color snaps
- contrast/readability remains acceptable during active pulse
- hold and wake-word paths produce identical state correctness

---

## 17. Glossary

- **Accent Rim Light:** Colored edge highlight around the center core.
- **Center Activation State:** Temporary visual state while an AI is actively speaking.
- **Listening Pending Name:** Hold-start state before an AI name is detected.
- **Neutral State:** Default center-core visual condition with no speaker accent.
- **Ripple Profile:** Persona-specific wave behavior (speed, softness, edge definition).
- **Speaker Switch Crossfade:** Smooth transition from one active speaker profile to another.
- **Wave Envelope:** Smoothed voice intensity signal used for light pulse modulation.
