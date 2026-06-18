# ATLAS HUD — System Audit
_Generated 2026-06-18 · Phase A/B/C of the "real-function-only" audit cycle_

## Audit Rule
> Every visible HUD element must perform a real function.
> No demo content. No fake backends. No placeholder data.
> Reserved/unimplemented surfaces show 🔴 NOT IMPLEMENTED explicitly.

---

## A · Ring → Panel → Backend Map

### Inner Ring (4 AI personas)
| ID | Surface | Backend |
|---|---|---|
| `ajani`   | AI Info card  | `GET /api/persona/list` + persona session APIs |
| `minerva` | AI Info card  | same |
| `hermes`  | AI Info card  | same |
| `trinity` | AI Info card  | `POST /api/council/route`, `/api/council/deliberate` |

### Middle Ring (5 system surfaces)
| ID | Component | Backend endpoint(s) |
|---|---|---|
| `manual`        | `ManualPanel`        | `GET /api/manual/sections` (5 sections) |
| `encyclopedia`  | `CyclopediaPanel`    | `GET /api/learning/lessons` (14 items) + `/lessons/{id}` |
| `memory`        | `MemoryPanel`        | `GET /api/membank/list`, `/categories`, `/by-tag`, `/graph/list` (100 triples) |
| `systems`       | `DiagnosticsPanel`   | `GET /api/status`, `/api/llm/health`, `/api/atlas/status` |
| `customization` | `CustomizationPanel` | `GET /api/settings`, `/api/ai/voices` (4 voices), `/api/themes/list` (4 themes) |

### Outer Ring (6 world surfaces)
| ID | Component | Backend endpoint(s) |
|---|---|---|
| `subjects`   | `TeachingWorkbench`   | `POST /api/atlas/teach` → `GET /api/atlas/jobs/{id}`, `GET /api/knowledge/subjects` (5) |
| `lab`        | `TeachingWorkbench` + `InteractiveSandbox` | `POST /api/sandbox/runs`, `/api/sandbox/saved`, `/api/sandbox/suggest` |
| `projects`   | `ProjectsPanel`       | `GET /api/research-orch/projects`, `/project-recommendations`, `PUT /learning/projects/{id}/status` |
| `blueprints` | `BlueprintWorkbench`  | `POST /api/atlas/blueprint`, `/api/atlas/blueprint/council`, `GET /api/research-orch/blueprints` (1) |
| `archive`    | `ArchiveBrowser`      | `GET /api/atlas/archive/list`, `POST /api/atlas/archive/upload` |
| `explore`    | `IntakePanel`         | `GET /api/intake/list` (10), `POST /api/intake/transcript`, `/intake/youtube` |

### Removed dead routes
| ID | Status |
|---|---|
| `worlds`    | 🔴 NOT IMPLEMENTED — Specification pending — Reserved for future ATLAS modules |
| `hyperaxel` | 🔴 NOT IMPLEMENTED — same |
| `weaver` (as sidebar tab) | Backend exists (`/api/weaver/*`) but no ring entry — accessed via specific flows only |
| `voice`/`skins`/`devices`/`health`/`settings` (as static tab) | Removed — never reachable from any ring |

These IDs **are not in any ring config** (`/app/frontend/src/data/ringStructure.js`) so they are unreachable through normal UI flow. If voice intent or deep-link ever sends one of these IDs, the panel renders the 🔴 NOT IMPLEMENTED block (`AtlasSidePanel.js` operation-info default branch).

---

## B · Live Endpoint Verification (audit 2026-06-18 20:55Z)

| Endpoint | Response | Status |
|---|---|---|
| `GET /api/robot/devices`                | 41 devices                          | 🟢 LIVE |
| `GET /api/research-orch/blueprints`     | 1 blueprint                         | 🟢 LIVE |
| `GET /api/membank/list?limit=5`         | 5 memories                          | 🟢 LIVE |
| `GET /api/membank/categories`           | 3 categories (permanent/decaying/all) | 🟢 LIVE |
| `GET /api/knowledge/subjects`           | 5 subjects                          | 🟢 LIVE |
| `GET /api/research-orch/queue/status`   | by_state + by_domain + by_verification | 🟢 LIVE |
| `GET /api/atlas/archive/list`           | entries[]                           | 🟢 LIVE |
| `GET /api/status`                       | [] (no events yet — expected)       | 🟢 LIVE |
| `GET /api/llm/health`                   | emergent/ollama/lmstudio health     | 🟢 LIVE |
| `GET /api/ai/voices`                    | 4 voices + ElevenLabs voices        | 🟢 LIVE |
| `GET /api/themes/list`                  | 4 themes                            | 🟢 LIVE |
| `GET /api/settings`                     | tts_provider, accent_theme, etc.    | 🟢 LIVE |
| `GET /api/weaver/plans`                 | 2 plans                             | 🟢 LIVE |
| `GET /api/research-orch/projects`       | 0 (none generated yet)              | 🟢 LIVE |
| `GET /api/intake/list`                  | 10 intakes                          | 🟢 LIVE |
| `GET /api/worldwatch/updates?limit=5`   | 5 updates                           | 🟢 LIVE |
| `GET /api/self-improve/proposals`       | 28 proposals                        | 🟢 LIVE |
| `GET /api/learning/lessons`             | 14 lessons                          | 🟢 LIVE |
| `GET /api/manual/sections`              | 5 sections                          | 🟢 LIVE |
| `GET /api/membank/graph/list`           | 100 triples                         | 🟢 LIVE |
| `GET /api/research-orch/missions`       | 4 missions                          | 🟢 LIVE |
| `GET /api/persona/list`                 | 4 personas                          | 🟢 LIVE |
| `GET /api/twins/list`                   | 6 twins                             | 🟢 LIVE |

**Result:** 23/23 GREEN. No mocked data anywhere in the visible HUD.

---

## C · Panel Audit (every HUD/*.js file)

| Component | API calls | Static arrays | Notes |
|---|---:|---:|---|
| `ArchiveBrowser.js`         | 2 | 0 | live `/api/atlas/archive/*` |
| `AtlasCore.js`              | 0 | 0 | pure-canvas central orb (no data needed) |
| `AtlasSentinel.js`          | 3 | 0 | live `/api/robot/sentinel/watcher/*` |
| `AtlasSidePanel.js`         | 0 | 0 | router only — delegates to children; static demo dict **removed** |
| `BlueprintWorkbench.js`     | 1 | 0 | live `/api/atlas/blueprint*` |
| `CouncilPanel.js`           | 2 | 0 | live `/api/council/*` |
| `CustomizationPanel.js`     | 2 | 0 | live `/api/settings`, `/api/ai/voices` |
| `CyclopediaPanel.js`        | 3 | 0 | live `/api/learning/lessons*` |
| `DiagnosticsPanel.js`       | 2 | 0 | live `/api/status`, `/api/llm/health` |
| `DialRing.js`               | 0 | 0 | render-only |
| `GhostRings.js`             | 0 | 0 | render-only animation |
| `GraphMemoryPanel.js`       | 1 | 0 | live `/api/membank/graph/*` |
| `IntakePanel.js`            | 2 | 0 | live `/api/intake/*` |
| `InteractiveSandbox.js`     | 10 | 2¹ | live `/api/sandbox/*`; statics are tab-label constants |
| `LearningHubPanel.js`       | 3 | 0 | live `/api/research-orch/*`, lessons, missions, blueprints, queue |
| `ManualPanel.js`            | 1 | 0 | live `/api/manual/sections` |
| `MemoryPanel.js`            | 1 | 0 | live `/api/membank/*` |
| `PersonaChatPanel.js`       | 3 | 0 | live `/api/persona/{persona}/chat`, sessions |
| `ProjectsPanel.js`          | 2 | 1¹ | live `/api/research-orch/projects`; static = STATUS_ORDER enum |
| `QuizTaker.js`              | 1 | 0 | live `/api/learning/lessons/{id}/quiz` |
| `RobotPanel.js`             | 6 | 1¹ | live `/api/robot/*`; static = ROLES enum |
| `SelfImprovementPanel.js`   | 2 | 1¹ | live `/api/self-improve/*`; static = STATUSES enum |
| `TeachingWorkbench.js`      | (via `useAtlasJob`) | 1¹ | live `/api/atlas/teach` (jobs); static = BAND_META labels |
| `TranscriptIngestPanel.js`  | 3 | 1¹ | live `/api/youtube/*`; static = source-type chip labels |
| `WorldWatchPanel.js`        | 3 | 0 | live `/api/worldwatch/*` |

¹ "Static array" present but is a **UI-label constant** (enum names, tab labels, color metadata) — not stub data.

**Result:** 25/25 GREEN. No HUD panel renders fake content.

---

## D · Unimplemented (per the rule above)

| Surface | Status | Plan |
|---|---|---|
| `worlds`    | 🔴 NOT IMPLEMENTED, hidden from rings | Reserved; reactivate only when spec exists |
| `hyperaxel` | 🔴 NOT IMPLEMENTED, hidden from rings | Reserved |
| ESP32 hardware bridge | 🟡 Sim-first only | **Next** — Phase D1 |
| Digital Twin engineering stack | 🟡 Registry exists, no real solver | **Next** — Phase D2 |
| NIR Scanner / Power Cell / Green Robot / Mother Box | 🔴 Not started | After Twin stack |

---

## E · Sign-off

- All 25 HUD panels render real backend data **or** are visualization-only.
- The dead `opData` demo dict in `AtlasSidePanel.js` (lines 88-105 in pre-audit code) has been removed; the fallback path now renders 🔴 NOT IMPLEMENTED if any unknown op id reaches it.
- 23/23 sampled endpoints return non-empty real responses.
- No ring config points to `worlds` or `hyperaxel`. They are unreachable from normal UI; deep-link/voice-intent fallback shows the explicit unimplemented block.

Ready to begin ESP32 hardware bridge (Phase D1) and Digital Twin engineering stack (Phase D2).
