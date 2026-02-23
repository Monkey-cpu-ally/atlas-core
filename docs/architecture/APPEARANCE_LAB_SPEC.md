# Appearance Lab — Final Behavior Spec

## Document Control
- Program: Unified Builder Polymath Platform
- Surface: Dial HUD + 3D Core + Panels
- Version: v1.1 (Final)
- Last Updated: 2026-02-19
- Owner: Visual Systems Architecture

---

## 1. Purpose

**Appearance Lab** is a manual visual customization mode:
- a system-level calibration environment
- technical, controlled, precise
- used to tune modular visual preferences without changing system function

Council Mode is ritual.  
Appearance Lab is calibration.

---

## 2. Activation (Entry Sequence)

Trigger:
- user selects **"Appearance Lab"**

Sequence (in order):
1. Background dims slightly (5–8%)
2. Core rotation slows but does **not** fully stop
3. Hermes becomes active AI identity
4. Center rim shifts to soft Ivory accent
5. Ripple effects disabled
6. Council mode disabled
7. Minimal system tone plays (clean, short)

Hermes optional voice line (allowed):
> "Appearance calibration mode active."

---

## 3. Visual State Constraints (While Active)

The environment is controlled and clean.

Must NOT render:
- sigil
- spiritual halo
- particles
- dramatic glow

---

## 4. Control Overlays (UI Layout)

The dial remains centered.

Floating control panels appear around the dial:

Left:
- Panel tilt (slider)
- Frame selector
- Frame opacity

Right:
- Ring material selector
- Transparency slider
- Line weight adjustment

Bottom:
- Background selector
- Accent preview toggle
- Reset to Default

Top (minimal):
- Exit button

Panels:
- semi-transparent
- soft shadow
- match active skin

---

## 5. Behavior Rules

- All changes update live in real-time.
- No save button required.
- Exit automatically saves configuration.
- "Reset to Default" restores **base skin values** (skin-provided visual defaults).

### 5.1 Interaction Refinement (Silent + Smooth)

Appearance Lab is a precision chamber.

Slider behavior:
- no haptic ticks while dragging
- no sound effects while adjusting
- motion is fluid and continuous (no snapping while dragging)
- changes update in real-time

Easing:
- smooth visual interpolation with a 200–300 ms blend
- no animation spikes on drag or release

Value confirmation (on release):
- no vibration
- no click sound
- only subtle visual stabilization; the UI remains calm

---

## 6. Exit Sequence

On exit (in order):
1. Background dim fades out (400ms)
2. Hermes Ivory rim fades to neutral
3. Normal AI state resumes
4. Core idle motion restores fully
5. Appearance controls dissolve

---

## 7. Persistence Contract

Preferences persisted by Appearance Lab (examples):
- panel tilt + material + depth shadow
- frame type + opacity
- ring material + transparency + line weight
- background type

These persist across:
- app restart
- mode changes
- AI speaker changes
- council activation (when not disabled)

---

## 8. Unity Bridge Note (If Center Core is Unity)

If the center core is rendered in Unity, the UI MUST notify Unity when:
- Appearance Lab enters/exits
- accent preview is enabled/disabled (preview only; no semantic AI speaker change)

Recommended event:
- `v1.appearanceLabChanged` (see Unity Bridge Event Contract)

