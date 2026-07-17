# Pre-Merge Preservation Report

**Date:** 2026-07-17
**Pod branch (to be created):** `emergent-vision-systems-iter30`
**Target branch on GitHub:** `main` (do NOT overwrite)
**Merge strategy:** Three-way merge — GitHub `main` ∪ pod state, no deletions on either side.

---

## Section 1 — Pod-only NEW files (21 files)
Every file in this table exists in this pod but does **not** exist on
GitHub `main`. All must be preserved in the merged branch.

### Backend routes (4 new)
| Path | Lines | Purpose |
|---|---:|---|
| `backend/routes/vision.py` | 367 | Vision Systems API (34 endpoints under `/api/vision/*`) |
| `backend/routes/packet_aliases.py` | 245 | EMERGENT_MASTER_PROMPT.md alias layer + `mount_alias` helper |
| `backend/routes/dev_pipeline.py` | 26 | `/api/dev/pipeline/status` — Engineering Console live probes |
| `backend/routes/knowledge_network.py` | 315 | **CONFLICT-PRONE** — see Section 4 |

### Backend services (2 new)
| Path | Lines | Purpose |
|---|---:|---|
| `backend/services/vision.py` | 1000 | Vision service layer: 11 sections (registry, driver protocol, calibration, ingest, detect, track, pose, inspect, fuse, twin-link, video) |
| `backend/services/dev_pipeline_service.py` | 252 | Engineering Console aggregator + 9 live probes |

### Backend models (1 new)
| Path | Lines | Purpose |
|---|---:|---|
| `backend/models/vision_models.py` | 432 | 20 Pydantic models: VisionDevice, driver protocol types, Camera, Sensor, Calibration, HandEye, Frame, Detection, BoundingBox, Track, Pose, Inspection, TwinLink, VideoSession + request DTOs |

### Backend scripts (1 new)
| Path | Lines | Purpose |
|---|---:|---|
| `backend/scripts/enrich_kn_metadata.py` | 217 | Idempotent metadata migration for 19 seeded sources |

### Backend tests (4 new — ~100 tests total)
| Path | Lines | Test count |
|---|---:|---:|
| `backend/tests/test_iter27_packet_aliases.py` | 162 | 18 |
| `backend/tests/test_iter28_knowledge_network.py` | 364 | 21 |
| `backend/tests/test_iter29_stabilization.py` | 211 | 15 |
| `backend/tests/test_iter30_vision_systems.py` | 751 | 38 |

### Frontend components (3 new)
| Path | Lines | Purpose |
|---|---:|---|
| `frontend/src/components/HUD/VisionConsole.js` | 287 | Ctrl+Alt+V overlay — driver tiles + inspection feed |
| `frontend/src/components/HUD/EngineeringConsole.js` | 266 | Ctrl+Shift+E overlay — system health probes |
| `frontend/src/components/HUD/KnowledgeBankPanel.js` | 246 | Knowledge Bank HUD panel |

### Memory / docs (4 new)
| Path | Lines | Purpose |
|---|---:|---|
| `memory/ATLAS_VISION_SYSTEMS.md` | 123 | Vision Systems architecture spec |
| `memory/ATLAS_DEVELOPMENT_PIPELINE.md` | 55 | Dev pipeline packet docs |
| `memory/ATLAS_SYSTEM_INDEX_TEMPLATE.md` | 14 | System index template |
| `memory/CURSOR_EMERGENT_APPLY_PIPELINE.md` | 19 | Cursor↔Emergent workflow doc |

---

## Section 2 — Pod-modified files (must MERGE, not overwrite)
These files exist on **both** sides but have pod-side edits. Merge
strategy: preserve GitHub structure, layer pod edits on top.

| Path | Pod-side change |
|---|---|
| `backend/server.py` | +5 lines: `include_router(vision_router)` + `register_packet_aliases(app)` |
| `backend/services/research_sources.py` | Added `_metadata_block()` helper + `KN_METADATA_FIELDS` allow-list + `find_source()` / `update_source_metadata()` helpers + `content_type` field routing |
| `backend/services/memory_bank.py` | `search_memory` gains substring keyword boost (up to +0.35 score) |
| `atlas_core/council/router.py` | **Bug fix**: stale `route(question)` → `route_internal(question)` inside `assemble()` |
| `frontend/src/components/HUDInterface.js` | +Ctrl+Alt+V hotkey (Vision) + Ctrl+Shift+E hotkey (Engineering) + mount points |
| `backend/tests/test_ai_services.py` | Provider-agnostic (accept OpenAI voice name OR ElevenLabs voice ID) |
| `backend/tests/test_iter10_hud.py` | Quiz size upper bound 5→10; proxy 502 HTML body tolerant |
| `backend/tests/test_iter16_voice_ingest_sentinel.py` | Paginate device list (limit=200) so seed rows aren't buried |
| `memory/PRD.md` | +Iter27 · Iter28 · Iter28b · Iter30 sections |

---

## Section 3 — GitHub-only files (must be preserved through merge)
Cursor Agent built these on `main` while this pod was in isolation.
**None of them exist in the pod**. All must land in the merged branch.

### Backend routes (18 files)
`atlas_os.py` · `autonomous_knowledge.py` · `discovery_approval.py` ·
`engineering_os.py` · `engineering_playbooks.py` · `external_access.py` ·
`global_knowledge.py` · `global_sources.py` · `headquarters.py` ·
`knowledge_chronicle.py` · `knowledge_graph.py` · `mission_scheduler.py` ·
`project_intelligence.py` · `project_knowledge.py` · `research_labs.py` ·
`self_improve.py` · `source_sync.py` · `system_inspector.py` ·
`technology_atlas.py` · `world_knowledge_graph.py`

Plus corresponding services + tests + models — I couldn't enumerate
these from a truncated GitHub listing; the merge must walk the full
tree.

---

## Section 4 — Known conflict points (require human review)

### 4.1 `backend/routes/knowledge_network.py` — TRUE CONFLICT
Both sides have this file with different implementations.

- **GitHub version** (Jul 4): "Add live preview endpoint for Knowledge Network sources"
- **Pod version** (Iter-28): 315 lines with `/dashboard`, `/stats`,
  `/sources/{id}/metadata` PATCH, `/by-agent/{agent}`, `/by-country/{country}`,
  11 metadata field extensions, proxies for kbase/youtube/subjects/research-memory,
  deep-alias mounts.

**Resolution:** Keep GitHub's `/preview` endpoint, add pod's 8 new endpoints
alongside. Human review required on the file post-merge.

### 4.2 `backend/services/research_sources.py`
Pod added the 11-field metadata block + `content_type` routing.
GitHub may have added competing schema. Human review required.

### 4.3 `backend/server.py`
Both sides register different additional routers. Concatenate `include_router` calls, don't overwrite.

---

## Section 5 — Verification checklist for the merged branch
Before pushing merged branch to `main`, confirm:
- [ ] All 21 pod-only files are present at their pod paths
- [ ] All 20+ GitHub-only route files still exist
- [ ] `knowledge_network.py` merged file contains BOTH the `/preview` endpoint AND the pod's 8 KN v1 endpoints
- [ ] `backend/server.py` calls `include_router(vision_router)` AND any GitHub-only include_router lines
- [ ] Tests: `pytest backend/tests/test_iter27_packet_aliases.py test_iter28_knowledge_network.py test_iter29_stabilization.py test_iter30_vision_systems.py` returns 92 passed
- [ ] Tests: GitHub-side test files still pass on the merged branch
- [ ] `/api/vision/health` returns 200 with driver_count=12
- [ ] `/api/knowledge-network/health` returns 200
- [ ] Frontend: Ctrl+Alt+V opens VisionConsole, Ctrl+Shift+E opens EngineeringConsole
- [ ] CI status on the merged PR is green (or failures are pre-existing, not introduced by merge)

---

## Section 6 — What must NOT happen
- ❌ Force-push to `main`
- ❌ Delete any file listed in Section 1 or Section 3
- ❌ Overwrite `backend/routes/knowledge_network.py` without preserving both feature sets
- ❌ Skip the `emergent-vision-systems-iter30` backup branch
- ❌ Auto-resolve conflicts with `--strategy=ours` or `--strategy=theirs`

---

**Total files under preservation:** 21 pod-only + 20+ GitHub-only + 9 pod-modified = **50+ files** across both trees, all of which must land intact in the merged branch.
