# Complete Codebase Inventory — Pod vs GitHub `main`

**Scope:** `backend/routes/`, `backend/services/`, key modified files, HUD components, memory docs.
**Method:** GitHub file listings scraped from public web tree; pod files listed from `/app/`.
**Note:** GitHub `main` has additional folders (`atlas-agent-runtime/`, `atlas-api/`, `atlas_platform/`, `knowledge-division/`, `innovation-lab/`, ~40 more) that the pod does NOT mirror. Those are Cursor-Agent-only side systems not covered here — they don't collide with pod files and should be preserved as-is.

---

## Table 1 · Files ONLY on GitHub `main` (Cursor Agent additions, absent from pod)

**Backend routes (20 files):**
| File | Last GitHub commit |
|---|---|
| `atlas_os.py` | Jul 10 · Mount AtlasOS under Engineering OS router |
| `autonomous_knowledge.py` | Jul 4 · Add Autonomous Knowledge Engine API routes |
| `discovery_approval.py` | Jul 5 · Add Discovery Approval API routes |
| `engineering_os.py` | Jul 10 · Integrate AtlasOS control plane routes |
| `engineering_playbooks.py` | Jul 8 · Add Engineering Playbook routes |
| `external_access.py` | Jul 5 · Add External Access Gateway API routes |
| `global_knowledge.py` | Jul 6 · Add Global Knowledge Network routes |
| `global_sources.py` | Jul 10 · feat: expose source reliability rankings |
| `headquarters.py` | Jul 7 · Expose Headquarters technical debt route |
| `knowledge_chronicle.py` | Jul 6 · Add Knowledge Chronicle routes |
| `knowledge_graph.py` | Jul 4 · Add Knowledge Graph API routes |
| `mission_scheduler.py` | Jul 4 · Add Mission Scheduler API routes |
| `project_intelligence.py` | Jul 5 · Add Project Intelligence API routes |
| `project_knowledge.py` | Jul 6 · Add Project Knowledge Linker routes |
| `research_labs.py` | Jul 4 · Persist Research Lab route mutations to MongoDB |
| `self_improve.py` | Jul 5 · Add self-improvement health scan routes |
| `source_sync.py` | Jul 4 · Add Source Sync API routes |
| `system_inspector.py` | Jul 6 · Add ATLAS System Inspector routes |
| `technology_atlas.py` | Jul 6 · Add Technology Atlas routes |
| `world_knowledge_graph.py` | Jul 6 · Add World Knowledge Graph routes |

**Backend services (23 files):**
`atlas_os_control_plane.py` · `autonomous_knowledge_engine.py` · `chronicle_engine.py` · `discovery_approval_pipeline.py` · `engineering_operating_system.py` · `engineering_playbooks.py` · `evidence_scoring.py` · `external_access_gateway.py` · `global_knowledge_network.py` · `global_source_library.py` · `headquarters_engine.py` · `knowledge_chronicle.py` · `knowledge_graph_engine.py` · `knowledge_record_writer.py` · `mission_scheduler.py` · `project_intelligence.py` · `project_knowledge_linker.py` · `research_lab_engine.py` · `self_improvement.py` · `source_code_connector.py` · `source_reliability.py` · `source_sync_engine.py` · `system_inspector.py` · `technology_atlas.py` · `world_knowledge_connector.py` · `world_knowledge_graph.py` · `world_knowledge_live.py`

**Loss if dropped:** ~20 major subsystems (AtlasOS control plane, Engineering OS, Playbooks, Chronicle, Discovery Approval, Headquarters, Global Knowledge, Global Sources with reliability rankings, Autonomous Knowledge Engine, Knowledge Graph engine, Mission Scheduler, Project Intelligence + Linker, Research Lab Engine w/ Mongo persistence, Self-Improvement engine, Source Sync, System Inspector, Technology Atlas, World Knowledge Graph + Connector + Live).

---

## Table 2 · Files ONLY in the Pod (E1 iter27–iter30, absent from GitHub)

| File | Purpose | Loss if dropped |
|---|---|---|
| `backend/routes/vision.py` | Vision Systems API — 34 endpoints under `/api/vision/*` | All Robotics Perception routes, Vision Console backend |
| `backend/services/vision.py` | 11-section vision service layer (1000 lines) | Camera/sensor registry, driver protocol, detect/track/pose/inspect/fuse, video ingest |
| `backend/models/vision_models.py` | 20 Pydantic models incl. VisionDevice abstraction | All vision data contracts |
| `backend/routes/packet_aliases.py` | `EMERGENT_MASTER_PROMPT.md` alias layer | `/api/memory`, `/api/sources`, `/api/tasks`, `/api/teaching`, `/api/intelligence`, `/api/health` — spec compliance |
| `backend/routes/dev_pipeline.py` + `services/dev_pipeline_service.py` | Engineering Console live probes | `/api/dev/pipeline/status` — HUD dev overlay |
| `backend/scripts/enrich_kn_metadata.py` | Idempotent metadata migration | KN facet population |
| `backend/tests/test_iter27_packet_aliases.py` | 18 tests | Alias contract regression coverage |
| `backend/tests/test_iter28_knowledge_network.py` | 21 tests | KN v1 metadata contract regression |
| `backend/tests/test_iter29_stabilization.py` | 15 tests | 12-subsystem liveness + Knowledge Graph + Research Labs coverage |
| `backend/tests/test_iter30_vision_systems.py` | 38 tests | Full vision perception coverage |
| `frontend/src/components/HUD/VisionConsole.js` | Ctrl+Alt+V overlay | Vision HUD — 12 driver tiles + inspection feed |
| `frontend/src/components/HUD/EngineeringConsole.js` | Ctrl+Shift+E overlay | Dev health HUD |
| `frontend/src/components/HUD/KnowledgeBankPanel.js` | KB HUD panel | Knowledge Bank HUD access |
| `memory/ATLAS_VISION_SYSTEMS.md` + 3 more docs | Architecture specs | Vision + Dev Pipeline documentation |

---

## Table 3 · Conflicting files (both sides modified — TRUE conflicts)

### 3.1 `backend/routes/knowledge_network.py` — HIGH-SEVERITY CONFLICT
- **GitHub version (Jul 4):** "Add live preview endpoint" — has `/preview` endpoint for live source inspection.
- **Pod version (Iter-28):** 315 lines — `/dashboard`, `/stats`, `/sources`, `/sources/{id}`, `/sources/{id}/metadata` (PATCH), `/by-agent/{agent}`, `/by-country/{country}`, `/subjects`, `/youtube/dashboard`, `/kbase/search`, `/research-memory`.

**If GitHub wins:** Pod loses 11-field KN metadata schema, facet dashboard, PATCH endpoint, filter-by-agent/country lookups.
**If pod wins:** GitHub loses `/preview` live-source inspection.
**Correct merge:** Concatenate — keep `/preview` from GitHub + all 10 pod endpoints. Human review required.

### 3.2 `backend/services/research_sources.py` — MEDIUM CONFLICT
- **Pod change:** Added `_metadata_block()` with 11 fields (`country`, `region`, `source_language`, `source_type`, `trust_level`, `ai_owner`, `update_frequency`, `access_method`, `auto_sync`, `private_source`, `culture_tag`), `find_source()`, `update_source_metadata()`, `content_type` routing.
- **GitHub version:** Unchanged from Jun 21 auto-commit. **Non-conflicting** — pod-side is purely additive.

**If GitHub wins:** Pod loses the entire KN metadata field system.
**Correct merge:** Take pod version outright (GitHub has no counter-change).

### 3.3 `backend/server.py` — MODIFICATION CONFLICT
- **Pod change:** +`include_router(vision_router)` + `register_packet_aliases(app)`.
- **GitHub change (Jul 8):** "Mount Engineering Playbook Engine routes" — has 20 additional `include_router` calls for the Cursor-side subsystems.

**If GitHub wins:** Pod loses vision + alias router mounts.
**Correct merge:** Concatenate all `include_router` calls from both sides. Order matters for alias layer (must be last).

### 3.4 `backend/services/memory_bank.py` — MEDIUM CONFLICT
- **Pod change:** `search_memory` gains substring keyword boost (up to +0.35 score).
- **GitHub version:** Unchanged since Jun 18.

**Correct merge:** Take pod version outright.

### 3.5 `atlas_core/council/router.py` — BUG FIX CONFLICT
- **Pod change:** Fixed stale `route(question)` → `route_internal(question)` (crashes `assemble()`).
- **GitHub status:** Unknown — need to inspect after pull.

**Correct merge:** Take pod fix; verify GitHub doesn't have the same bug already fixed.

### 3.6 `frontend/src/components/HUDInterface.js` — LIKELY CONFLICT
- **Pod change:** +Ctrl+Alt+V, +Ctrl+Shift+E hotkeys + component mounts.
- **GitHub change (Jul 16, 12 min ago):** "fix(hud): clean up side panel visibility timer".

**Correct merge:** Concatenate — take pod hotkey/mount additions + GitHub's timer cleanup. Line-level diff needed.

### 3.7 Test files pod-modified (3 files)
`test_ai_services.py`, `test_iter10_hud.py`, `test_iter16_voice_ingest_sentinel.py` — pod applied test-fixes (provider-agnostic TTS, quiz size bump, device pagination). GitHub status unknown until pull.

**Correct merge:** Take pod fixes unless GitHub has newer/better fixes.

---

## Table 4 · Identical files (safe — no merge action needed)

Files present on BOTH sides with the same filename (46 files across `backend/routes/` + `backend/services/`):

**Both-sides routes:** `ai_services.py`, `atlas_v2.py`, `chat.py`, `council.py`, `environments.py`, `files.py`, `hud_surfaces.py`, `intake.py`, `kbase.py`, `knowledge.py`, `learning.py`, `lessons.py`, `llm.py`, `memory.py`, `nir.py`, `persona.py`, `research.py`, `research_orchestrator.py`, `research_sources.py`, `robot.py`, `sandbox.py`, `subjects.py`, `twins.py`, `watchers.py`, `weaver.py`, `youtube.py`

**Both-sides services:** `adaptation.py`, `ai_categorizer.py`, `anomaly.py`, `blueprint_forge.py`, `blueprint_parser.py`, `digital_twin.py`, `environments.py`, `knowledge_core.py`, `knowledge_distiller.py`, `knowledge_ingestion.py`, `knowledge_watcher.py`, `lesson_generator.py`, `llm_provider.py`, `mqtt_bridge.py`, `mtls.py`, `nir.py`, `parts_db.py`, `patent_client.py`, `pdf_reader.py`, `persona_chat.py`, `reference_twins.py`, `research_orchestrator.py`, `research_pipeline.py`, `robot.py`, `self_code.py`, `sentinel_watcher.py`, `source_fetchers.py`, `subjects.py`, `twin_simulator.py`, `weaver.py`, `web_scraper.py`, `worldwatch.py`, `youtube_channels.py`, `youtube_pipeline.py`, `youtube_resolver.py`

**Caveat:** These are same-name matches. Content may still differ — full byte comparison requires the actual pull. Assume any file with a GitHub commit *newer* than the pod's snapshot took precedence-worthy changes; a byte-diff will confirm.

---

## Table 5 · Merge action summary

| Action | Count | Files |
|---|---:|---|
| KEEP FROM GITHUB (pod-absent additions) | 20 routes + 27 services = **47** | See Table 1 |
| KEEP FROM POD (GitHub-absent additions) | 4 routes + 2 services + 3 tests + 3 HUD + 4 docs + 1 script = **17** | See Table 2 |
| MERGE (both sides modified) | **7 files** | See Table 3 |
| BYTE-COMPARE (same name, both sides) | **~61 files** | See Table 4 |

**Total files under active consideration: ~132.**

---

## What this table does NOT cover
- Frontend directories (only HUD panels enumerated; broader `frontend/src/` diffs pending pull).
- Model files under `backend/models/` (only `vision_models.py` enumerated; others need diff).
- `atlas_core/`, `atlas-agent-runtime/`, `atlas_platform/`, `atlas-config/`, `atlas-tests/` and ~40 other top-level GitHub directories — likely Cursor-only, preserve wholesale.
- Memory directory files (only 5 new pod-side docs enumerated).
- CI workflows in `.github/workflows/` — must be preserved from GitHub.

Once you receive the pull staged by support, I'll walk this same table with actual byte-diffs and flag any Table-4 file where content diverges.
