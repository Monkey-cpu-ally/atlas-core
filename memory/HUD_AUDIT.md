# ATLAS HUD — Headquarters System Audit
_Generated 2026-06-18 · Updated for Headquarters command-surface language_

## Audit Rule
> Every visible HUD element must perform a real function.
> No demo content. No fake backends. No placeholder data.
> Reserved/unimplemented surfaces show 🔴 NOT IMPLEMENTED explicitly.

---

## A · Headquarters Navigation Model

The HUD is no longer treated as a generic radial dashboard. It is the visual command layer for **ATLAS Headquarters**.

### Core Headquarters zones
| Zone | Purpose | Backend command surface |
|---|---|---|
| Headquarters Status | Global operating state, quality posture, active missions | `GET /api/headquarters/status` |
| Quality Gates | Seven-seal review: Architecture, Engineering, Testing, Documentation, Security, Performance, Luxury Review | `GET /api/headquarters/quality-gates` |
| ATLAS Standard | Non-generic product rules and engineering doctrine | `GET /api/headquarters/atlas-standard` |
| Mission Control | Active work queue, roadmap focus, next actions | `GET /api/headquarters/mission-control` |
| Knowledge Gate | Approves knowledge records before they become trusted assets | `GET /api/headquarters/knowledge-gate` |
| Source Clearance | Permission-first source review and import planning | `GET /api/headquarters/source-clearance` |
| Project Briefing | Risks, recommendations, reuse signals, and project intelligence | `GET /api/headquarters/project-briefing` |
| Refinement Office | Tracks generic-feel cleanup and ATLAS polish work | `GET /api/headquarters/refinement` |

### Inner Ring · Council Chamber
| ID | Surface | Headquarters meaning | Backend |
|---|---|---|---|
| `ajani` | AI Info card | Strategy, challenge, operations discipline | `GET /api/persona/list` + persona session APIs |
| `minerva` | AI Info card | Evidence, science, nature, knowledge confidence | same |
| `hermes` | AI Info card | Engineering, robotics, design, serviceability | same |
| `trinity` | Council card | Final synthesis and decision logic | `POST /api/council/route`, `/api/council/deliberate` |

### Middle Ring · Headquarters Systems
| ID | Component | Headquarters meaning | Backend endpoint(s) |
|---|---|---|---|
| `manual` | `ManualPanel` | ATLAS Standard / operator doctrine | `GET /api/manual/sections` |
| `encyclopedia` | `CyclopediaPanel` | Knowledge Gate searchable knowledge index | `GET /api/learning/lessons`, `/lessons/{id}` |
| `memory` | `MemoryPanel` | Memory Bank / Chronicle feed | `GET /api/membank/list`, `/categories`, `/by-tag`, `/graph/list` |
| `systems` | `DiagnosticsPanel` | Headquarters Status and Quality Gates | `GET /api/status`, `/api/llm/health`, `/api/atlas/status` |
| `customization` | `CustomizationPanel` | HUD identity, voice, theme, and operator preferences | `GET /api/settings`, `/api/ai/voices`, `/api/themes/list` |

### Outer Ring · Mission Departments
| ID | Component | Headquarters meaning | Backend endpoint(s) |
|---|---|---|---|
| `subjects` | `TeachingWorkbench` | Knowledge Division / guided learning | `POST /api/atlas/teach`, `GET /api/knowledge/subjects` |
| `lab` | `TeachingWorkbench` + `InteractiveSandbox` | Engineering Lab / safe simulation | `POST /api/sandbox/runs`, `/api/sandbox/saved`, `/api/sandbox/suggest` |
| `projects` | `ProjectsPanel` | Project Briefing / roadmap execution | `GET /api/research-orch/projects`, `/project-recommendations` |
| `blueprints` | `BlueprintWorkbench` | Council-reviewed blueprint generation | `POST /api/atlas/blueprint`, `/api/atlas/blueprint/council` |
| `archive` | `ArchiveBrowser` | Memory Bank archive and uploads | `GET /api/atlas/archive/list`, `POST /api/atlas/archive/upload` |
| `explore` | `IntakePanel` | Source Clearance intake queue | `GET /api/intake/list`, `POST /api/intake/transcript`, `/intake/youtube` |

---

## B · Removed Dead Routes
| ID | Status |
|---|---|
| `worlds` | 🔴 NOT IMPLEMENTED — Specification pending — Reserved for future ATLAS modules |
| `hyperaxel` | 🔴 NOT IMPLEMENTED — Reserved for the Hyper Axel game division |
| `weaver` as a sidebar tab | Backend exists (`/api/weaver/*`) but no ring entry — accessed via specific mission flows only |
| `voice`/`skins`/`devices`/`health`/`settings` as static tabs | Removed — never reachable from any ring |

These IDs are not in any ring config (`frontend/src/data/ringStructure.js`) so they are unreachable through normal UI flow. If voice intent or deep-link ever sends one of these IDs, the panel must render the explicit 🔴 NOT IMPLEMENTED block.

---

## C · Live Endpoint Verification (audit 2026-06-18 20:55Z)

| Endpoint | Response | Status |
|---|---|---|
| `GET /api/robot/devices` | 41 devices | 🟢 LIVE |
| `GET /api/research-orch/blueprints` | 1 blueprint | 🟢 LIVE |
| `GET /api/membank/list?limit=5` | 5 memories | 🟢 LIVE |
| `GET /api/membank/categories` | 3 categories | 🟢 LIVE |
| `GET /api/knowledge/subjects` | 5 subjects | 🟢 LIVE |
| `GET /api/research-orch/queue/status` | by_state + by_domain + by_verification | 🟢 LIVE |
| `GET /api/atlas/archive/list` | entries[] | 🟢 LIVE |
| `GET /api/status` | [] (no events yet — expected) | 🟢 LIVE |
| `GET /api/llm/health` | emergent/ollama/lmstudio health | 🟢 LIVE |
| `GET /api/ai/voices` | 4 voices + ElevenLabs voices | 🟢 LIVE |
| `GET /api/themes/list` | 4 themes | 🟢 LIVE |
| `GET /api/settings` | tts_provider, accent_theme, etc. | 🟢 LIVE |
| `GET /api/weaver/plans` | 2 plans | 🟢 LIVE |
| `GET /api/research-orch/projects` | 0 (none generated yet) | 🟢 LIVE |
| `GET /api/intake/list` | 10 intakes | 🟢 LIVE |
| `GET /api/worldwatch/updates?limit=5` | 5 updates | 🟢 LIVE |
| `GET /api/self-improve/proposals` | 28 proposals | 🟢 LIVE |
| `GET /api/learning/lessons` | 14 lessons | 🟢 LIVE |
| `GET /api/manual/sections` | 5 sections | 🟢 LIVE |
| `GET /api/membank/graph/list` | 100 triples | 🟢 LIVE |
| `GET /api/research-orch/missions` | 4 missions | 🟢 LIVE |
| `GET /api/persona/list` | 4 personas | 🟢 LIVE |
| `GET /api/twins/list` | 6 twins | 🟢 LIVE |

**Result:** 23/23 GREEN. No mocked data anywhere in the visible HUD.

---

## D · Panel Audit

| Component | API calls | Static arrays | Headquarters role |
|---|---:|---:|---|
| `ArchiveBrowser.js` | 2 | 0 | Memory Bank archive |
| `AtlasCore.js` | 0 | 0 | pure-canvas central orb |
| `AtlasSentinel.js` | 3 | 0 | sentinel monitoring |
| `AtlasSidePanel.js` | 0 | 0 | command-surface router |
| `BlueprintWorkbench.js` | 1 | 0 | Council-reviewed blueprints |
| `CouncilPanel.js` | 2 | 0 | Council Chamber |
| `CustomizationPanel.js` | 2 | 0 | HUD identity controls |
| `CyclopediaPanel.js` | 3 | 0 | Knowledge Gate index |
| `DiagnosticsPanel.js` | 2 | 0 | Headquarters Status |
| `DialRing.js` | 0 | 0 | render-only ring control |
| `GhostRings.js` | 0 | 0 | render-only holographic depth |
| `GraphMemoryPanel.js` | 1 | 0 | Memory graph |
| `IntakePanel.js` | 2 | 0 | Source Clearance intake |
| `InteractiveSandbox.js` | 10 | 2¹ | Engineering Lab simulator |
| `LearningHubPanel.js` | 3 | 0 | Knowledge Division hub |
| `ManualPanel.js` | 1 | 0 | ATLAS Standard manual |
| `MemoryPanel.js` | 1 | 0 | Memory Bank feed |
| `PersonaChatPanel.js` | 3 | 0 | AI session chamber |
| `ProjectsPanel.js` | 2 | 1¹ | Project Briefing |
| `QuizTaker.js` | 1 | 0 | mastery check |
| `RobotPanel.js` | 6 | 1¹ | Robotics operations |
| `SelfImprovementPanel.js` | 2 | 1¹ | Refinement Office input |
| `TeachingWorkbench.js` | via `useAtlasJob` | 1¹ | Knowledge Division lessons |
| `TranscriptIngestPanel.js` | 3 | 1¹ | Source Clearance transcript flow |
| `WorldWatchPanel.js` | 3 | 0 | Source Observatory |

¹ Static array present but is a UI-label constant, not stub data.

**Result:** 25/25 GREEN. No HUD panel renders fake content.

---

## E · Unimplemented / Next Engineering Stack

| Surface | Status | Plan |
|---|---|---|
| `worlds` | 🔴 NOT IMPLEMENTED, hidden from rings | Reserved; reactivate only when spec exists |
| `hyperaxel` | 🔴 NOT IMPLEMENTED, hidden from rings | Reserved for game division |
| ESP32 hardware bridge | 🟡 Sim-first only | Phase D1 after Headquarters refinement hardening |
| Digital Twin engineering stack | 🟡 Registry exists, no real solver | Phase D2 after Headquarters refinement hardening |
| NIR Scanner / Power Cell / Green Robot / Mother Box | 🔴 Not started | After Twin stack and safety review |

---

## F · Sign-off

- HUD planning now uses ATLAS Headquarters language.
- All visible HUD elements must map to real APIs, a render-only visual function, or explicit NOT IMPLEMENTED fallback.
- Headquarters routes are the product-facing layer; developer APIs remain stable underneath.
- Next refinement task: add the ATLAS Technical Debt Register and connect it to Headquarters reporting.
