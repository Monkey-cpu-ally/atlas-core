# ATLAS HUD V2 · Style Guide

> **2026-06-18 · Part 4 of ATLAS V2 build.**
> Theme tokens are JSON. Visual rendering is the next implementation step.

---

## What was built (honest scope)

**Theme foundation only — no full HUD reskin.** The user explicitly said:
> *"Do not rewrite the whole app. Do not remove v1 systems. Visual changes
>  must be theme-based so we can switch styles."*

So this build delivers:
1. Four JSON theme/token files at `/app/themes/*.json`
2. Two read-only endpoints (`/api/themes/list`, `/api/themes/{id}`) to serve them
3. Visual-style memory backend (Part 5 — separate report)
4. A documented contract for how the HUD will consume these tokens (this file)

It does **not** yet apply the tokens to the existing HUD CSS. That is a
deliberate follow-up so the v1 HUD continues working untouched while the
v2 reskin is built incrementally.

---

## Files shipped

| File | Purpose |
| ---- | ------- |
| `/app/themes/atlas_hud_v2.theme.json` | Top-level theme manifest — principles, rings, core, panels, registered feature panels |
| `/app/themes/atlas_color_tokens.json` | Color palette: agents, surfaces, semantic, text, blueprint overlay |
| `/app/themes/atlas_motion_tokens.json` | Durations, easings, physics constants, reduced-motion fallbacks |
| `/app/themes/atlas_layout_tokens.json` | Spacing, z-indexes, panel geometry, ring geometry, feature-panel registry, anti-patterns |

All four are GET-able via `/api/themes/{id}` (omit the `.json` extension —
`atlas_hud_v2.theme` is the id).

---

## Core principles (from `atlas_hud_v2.theme.json`)

1. Central transparent rotating core
2. Slow ring motion (24-48s idle drift)
3. Snap-back animation after interaction
4. **Small side-by-side AI face panels OUTSIDE the rings** (NOT inside)
5. Agent color pulses on hover and on receive-of-data
6. Never plain. Never messy. Never cartoonish. Never flat-basic.

## Influence mix (intentionally cross-pollinated)

| Influence | Pulled from |
| --------- | ----------- |
| JARVIS precision | Tony Stark's HUD readouts |
| Wakanda layered tech | Black Panther's holographic interfaces |
| Horizon Zero Dawn organic-machine detail | Aloy's Focus interface |
| Pragmata industrial sci-fi | Pragmata trailer aesthetic |
| Luxury car dashboard polish | Lucid Air / Aston Martin DBX |
| Transparent ATLAS ring system | the existing v1 rings, kept |

## Agent colors (locked across all surfaces)

| Agent | Color | Use |
| ----- | ----- | --- |
| Ajani | `#E63946` crimson | engineering · robotics — heat / urgency |
| Minerva | `#2EC4B6` teal | science · biology — calm / depth |
| Hermes | `#F4EFE4` off-white | math · logic · code — neutral |
| Council | `#9B6BD8` purple | deliberation — fusion |

Each color has `primary / soft / edge` variants in `atlas_color_tokens.json`
so panels never look monochrome.

## Motion tokens (compact summary)

| Token | Value |
| ----- | ----- |
| panel_enter | 180 ms · `cubic-bezier(0.16, 1, 0.3, 1)` |
| ring_snap_back | 520 ms · `cubic-bezier(0.18, 0.9, 0.22, 1.02)` |
| core_breathing | 6000 ms · amplitude 4% |
| ring_idle | 36000 ms (24-48 s acceptable range) |
| ai_pulse_ajani | 1800 ms (faster — hot persona) |
| ai_pulse_minerva | 2200 ms |
| ai_pulse_hermes | 1400 ms (fastest — analytical) |
| ai_pulse_council | 2600 ms (slowest — deliberative) |

`reduced_motion.honors_prefers_reduced_motion: true` is set —
all durations collapse to 0 on user opt-in.

## Layout tokens (compact summary)

- 1920×1080 baseline
- Right-dock panels: top 24, right 24, bottom 24, width min(820, 92vw)
- AI face dock OUTSIDE the rings, at bottom-center
- Sentinel ribbon at bottom 92 px
- Spacing scale: 4 / 8 / 12 / 16 / 24 / 32 / 48 / 72
- Z-index registry covers void → toast (12 layers)

## Feature panels registered (10)

| Panel | Status today | Style notes |
| ----- | ------------ | ----------- |
| memory_bank | v1 live | needs v2 reskin (cards too uniform) |
| knowledge_bank | v1 live | needs v2 (Cyclopedia tile still legacy 22-subject) |
| graph_memory | ❌ not built | needs `vis-network` or sigma.js panel |
| world_watch | ❌ not built | data ready (`/api/worldwatch/updates`), no UI yet |
| self_improvement | ❌ not built | data ready (`/api/self-improve/proposals`), no UI yet |
| digital_twin | v1 live | OK |
| weaver | v1 live | OK |
| robot_control | v1 live | OK |
| sentinel_alert | v1 live | OK (already pulsing in v1) |
| transcript_ingest | **v1.5 live this session** | new panel built in earlier message |

---

## Anti-patterns (locked rejection list)

From `atlas_hud_v2.theme.json.anti_patterns`:
- purple-violet-gradient-on-white  ← classic "AI slop"
- Inter / Roboto everywhere
- centered grid of identical cards
- neon emoji icons
- ALL CAPS for body text
- flat 2D with no depth cue

From `atlas_layout_tokens.json.anti_patterns`:
- fixed-pixel-only layouts (must use pct + clamp)
- ai face dock INSIDE the rings (must be OUTSIDE)
- panel widths > 90 vw on desktop
- central core obscured by foreground panels

These are intentionally restrictive. When the design_agent_full_stack is
invoked for the v2 reskin, it must respect this list.

---

## What is REAL
- 4 theme files on disk + 2 endpoints serving them
- Agent colors locked to the values the user specified
- 10 feature panels enumerated with `anchor` and `min_width_px`
- Anti-pattern list enforced as a hard rule for the next design pass

## What is SIMULATED
- HUD has not yet been re-rendered using these tokens — current HUD CSS is
  hand-written for v1 in `App.css`. The CSS-tokens-to-HUD step is the
  follow-up build (likely a single `useAtlasTheme()` hook + CSS variables).

## What requires keys / external services
- Nothing for Part 4 itself. The design_agent_full_stack subagent can be
  invoked at any time to drive the actual reskin against these tokens.

## What needs user approval
- The **full HUD v2 reskin** is a `category: hud_layout` proposal-class
  change. Before it's applied, the design pass should be reviewed by the
  user. The current build sets the foundation only.

---

## Recommended next steps (in order)

1. **`useAtlasTheme()` React hook** — fetch `/api/themes/atlas_hud_v2.theme`
   on mount, dump tokens onto `:root` as CSS variables, expose helpers
   `useColor('ajani')`, `useMotion('panel_enter')`, etc.
2. **HUD v2 graph-memory panel** — first new panel to be built with the v2
   tokens; serves as the proof that the token contract works.
3. **HUD v2 world-watch panel** — second new panel; uses agent color pulses
   per update.
4. **HUD v2 self-improvement panel** — exposes the 27 pending proposals.
5. **v1-to-v2 panel reskin** — page through existing panels one at a time;
   no panel touches v1 until the v2 contract has been proven on the 3 new
   panels above.

Throughout: every visual change becomes a `self_improvements` proposal with
`category: hud_layout` so the v2 evolution itself is logged.

---

_Sister documents: `ATLAS_WORLDWATCH_REPORT.md` (Part 1) ·
`ATLAS_V2_SELF_IMPROVEMENT_REPORT.md` (Parts 2 + 3 + 5)._
