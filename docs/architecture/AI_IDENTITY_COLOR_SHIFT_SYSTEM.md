# AI Identity Color-Shift System

## Document Control
- Program: Unified Builder Polymath Platform
- Surface: Dial HUD + 3D Core + Voice UI
- Version: v1.0 (Draft)
- Last Updated: 2026-02-17
- Owner: Identity and Visual Systems

---

## 1. Purpose

Define how interface accents shift to the currently speaking AI identity (Ajani, Minerva, Hermes) to improve presence, orientation, and immersion.

This is a dynamic overlay system, not a full theme swap.

---

## 2. Scope

In scope:
- speaker-driven accent color shifts
- transition timing and fade behavior
- affected visual surfaces
- fallback to neutral state

Out of scope:
- full skin changes (see Skin Token Schema)
- ring interaction math (see Dial Interaction Spec)
- bridge transport schema internals (see Unity Bridge Event Contract)

---

## 3. Identity Color Profiles

## 3.1 Ajani
- Accent family: Crimson (deep, non-neon)
- Practical range: red-forward, medium-dark saturation
- Identity intent: strategic, structural, decisive
- Glow behavior: strongest of three profiles (bounded by effect budget)

## 3.2 Minerva
- Accent family: Teal Blue (balanced cyan-blue, non-electric)
- Practical range: medium saturation, softer edges
- Identity intent: reflective, insightful, explanatory
- Glow behavior: soft profile, smoother gradients

## 3.3 Hermes
- Accent family: Warm Ivory (light neutral, slight warmth)
- Practical range: low saturation, high luminance
- Identity intent: precision, control, system clarity
- Glow behavior: minimal glow, sharp highlight contrast

---

## 4. Trigger Conditions

Identity color shift activates when any of the following starts:
1. AI voice playback begins
2. AI text bubble enters active speaking state
3. Voice waveform visualization starts

Identity color shift ends when speaking stops and silence criteria are met.

---

## 5. Visual Surfaces Affected

During active speaking state, apply identity accent to:
- 3D core rim/edge lighting
- active ring segment glow
- ring tick micro-tint
- micro HUD markers
- waveform color and brightness response
- low-strength background gradient tint

The effect must remain subtle enough to preserve readability and status clarity.

---

## 6. Transition Model

## 6.1 Activation Transition
- Fade-in window: 250–500 ms
- No hard snap unless forced by fail-safe mode

## 6.2 Speaker Switch
- Crossfade previous speaker accent -> next speaker accent
- Crossfade must maintain continuous UI legibility

## 6.3 Silence Exit
- Fade to neutral system accent when no speaker is active
- Residual glow hold: up to 1 second
- Residual hold is optional in reduced-motion mode

---

## 7. Intensity and Safety Bounds

Maximum recommended bounds:
- Background tint strength: 10–15%
- Accent glow intensity: profile-dependent, capped by effect budget
- Waveform brightness modulation: tied to amplitude but clamped

Guardrails:
- never reduce contrast below accessibility thresholds
- never hide warnings/errors under identity overlays
- neutral/system alerts always override identity accent when needed

---

## 8. State Contract

Identity system consumes an app-level identity state with:
- `currentSpeaker` (`ajani` | `minerva` | `hermes` | `null`)
- `accentProfileId`
- `glowIntensity`
- `motionProfileModifier`

State consumers:
- HUD renderer
- ring layer renderer
- waveform renderer
- Unity 3D core renderer

`null` speaker must map to neutral accent profile.

---

## 9. Integration Rules

- Identity accent is an overlay on top of active skin tokens.
- Skin defines baseline visuals; identity adds speaker tint and dynamic accents.
- Identity overlay must not modify:
  - command semantics
  - mode/domain/module state
  - policy/safety logic

---

## 10. Advanced Features (Phase 2, Optional)

- Voice intensity -> glow modulation
- Tone analysis -> bounded saturation adjustment
- Dual-speaker split accents for co-dialogue states
- Skin-specific identity profiles (deeper tones for dark skins, softer tones for light skins)

All advanced features must keep readability and effect budgets within limits.

---

## 11. Validation Checklist

System is accepted when:
- identity shift triggers correctly for all three personas
- speaker switch transitions are smooth and deterministic
- silence fallback returns to neutral reliably
- overlay does not break contrast/accessibility checks
- effect intensity stays within performance and visual budget

---

## 12. Glossary

- **Accent Profile:** A persona-specific color/intensity behavior set.
- **Crossfade:** Smooth transition from one active accent state to another.
- **Identity Overlay:** Dynamic color layer applied on top of baseline skin.
- **Neutral Accent:** Default system color state when no speaker is active.
- **Residual Glow:** Short-lived afterglow effect following speech end.
- **Speaker State:** Current AI identity driving active UI accent behavior.
