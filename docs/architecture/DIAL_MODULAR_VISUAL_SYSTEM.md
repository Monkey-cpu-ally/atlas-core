# Dial Interface — Full Modular Visual System

## Document Control
- Program: Unified Builder Polymath Platform
- Surface: Dial HUD + 3D Core + Panels
- Version: v1.0 (Draft)
- Last Updated: 2026-02-19
- Owner: Visual Systems Architecture

---

## 1. Core Rule (Non-Negotiable)

All visual layers are **optional** and **independently configurable**.

Nothing is permanently baked into the UI.

This means:
- a user can enable/disable each layer,
- a skin can provide defaults for a layer,
- the user can override per-layer preferences without changing mode or function.

Function is fixed.  
Atmosphere is configurable.

---

## 2. Panel Perspective System

Panel options (user-selectable):

### 2.1 Panel Tilt
- `OFF` (flat)
- `SUBTLE` (5°–8° perspective)
- `NOTICEABLE` (10°–15° console look)
- `DYNAMIC` (slight tilt responds to drag / gyro)

### 2.2 Panel Depth Shadow
- `OFF`
- `SOFT_SHADOW`
- `ELEVATED_PLATE_SHADOW`

### 2.3 Panel Material
- `MATTE`
- `GLASS`
- `BRUSHED_METAL`
- `MINIMAL_TRANSPARENT`

Constraints:
- panel tilt and shadow must not reduce text legibility
- glass/blur effects must respect device performance tier budgets

---

## 3. Frame System (Optional Structural Shapes)

Frame types:
- `NONE` (floating dial)
- `HEXAGONAL_PLATE`
- `CIRCULAR_PLATE`
- `ANGULAR_TECH_FRAME`
- `ORGANIC_SOFT_FRAME`

Frame opacity:
- `SOLID`
- `SEMI_TRANSPARENT`
- `OUTLINE_ONLY`

Rules:
- frame must adapt to active skin color tokens (no hardcoded colors)
- frame must not obscure the core, sigil, or ring labels

---

## 4. Ring Material System

Each ring can be configured independently.

Material:
- `SOLID_MATTE`
- `FROSTED_GLASS`
- `TRANSPARENT_GLASS`
- `LINE_ONLY_MINIMAL`
- `MIXED_INNER_SOLID_OUTER_TRANSPARENT`

Transparency strength:
- 0% – 60%

Label contrast auto-adjust:
- `ON` (recommended)
- `OFF`

Rules:
- rings remain neutral under identity overlays (no persona recolor)
- active selection emphasis must remain readable on all skins

---

## 5. Color System (Skin Tokens)

Each skin defines at minimum:
- Primary Color
- Secondary Support
- Accent Energy
- Neutral Base
- Micro Detail Tone

Rules:
- only 1 dominant accent should read as “dominant” at a time
- AI accent overlays must remain visible on all skins
- Council Ghost Purple must remain compatible (muted and translucent)

---

## 6. Background System

Background types:
- `SOLID_COLOR`
- `GRADIENT`
- `SUBTLE_TEXTURE`
- `SOFT_NOISE_GRAIN`
- `LIGHT_PANEL_SURFACE`
- `DEEP_COSMIC_SPACE`
- `MATTE_MINIMAL`

Dim overlay (Council Mode):
- `ON/OFF` (user preference)

Rules:
- dim overlay must be subtle (5–10%) and never “flashy”
- background effects must respect performance budgets

---

## 7. Canonical Layer Stack Order

From top to bottom:

1. AI ripple + accent (center-only identity)
2. 3D Core
3. Rings
4. Optional Sigil (Council only)
5. Optional Frame Plate
6. Background Surface

Notes:
- rings remain neutral at all times
- sigil represents unity and stays Ghost Purple during all council speakers

---

## 8. Persistence

All visual preferences:
- persist across sessions
- saved to user profile (or device storage until profiles exist)
- independent from app mode

This includes:
- skin selection
- panel perspective settings
- frame settings
- ring material settings
- background settings

---

## 9. Design Philosophy

Function is fixed.  
Atmosphere is configurable.

The system is an instrument.  
The user tunes it.

