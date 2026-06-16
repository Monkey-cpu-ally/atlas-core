# ATLAS — Lead Architect Audit Report
**Generated:** Feb 2026  
**Scope:** `/app/backend`, `/app/atlas_core`, `/app/frontend/src`  
**Status:** READ-ONLY audit — no code modified.

---

## 1. Executive Summary

| Severity | Count | Examples |
|---|---|---|
| 🟥 **High** | 2 | Duplicate teaching pipelines (5 implementations); missing `pypdf` & `youtube-transcript-api` in requirements.txt |
| 🟧 **Medium** | 3 | Duplicate `route()` function in atlas_core vs routes; 4 orphan frontend files; CORS wildcards in prod |
| 🟨 **Low** | 4 | One stale TODO in `ai_categorizer.py`; chat `/trinity` overlap with council `/deliberate`; legacy file-browser CSS still in App.css; exports/* in repo (debatable) |

**Verdict:** Architecture is **functional and production-shaped**, but there's clear evidence of fast iteration leaving behind 4 redundant lesson/teaching paths and unreferenced UI from the luxury reskin. None of the issues are blocking. The codebase is clean of `eval`, `exec`, `pickle`, hardcoded secrets, or shell injection. **No deletion required for stability — just consolidation.**

---

## 2. Findings

### 🟥 H-1 — FIVE parallel lesson/teaching implementations
There are 5 distinct code paths that turn a topic/transcript into a lesson. They mostly do not share code.

| Path | File | Notes |
|---|---|---|
| `/api/atlas/teach` | `atlas_core/app/main.py:202` → `teaching_engine/teaching.py:88` | Async, council-routed, MongoDB |
| `/api/atlas/teach/sync` | `atlas_core/app/main.py:219` | Synchronous variant of the above |
| `/api/knowledge/teach` | `routes/knowledge.py:60` → `services/knowledge_core.py:194` | In-memory knowledge graph teach |
| `/api/intake/youtube` `_build_lesson` | `routes/intake.py:103` | Heuristic, no LLM — only string slicing |
| `/api/learning/...` `generate_lesson` | `routes/learning.py:102` | LLM-powered, persona-flavoured, persists to `lessons` collection |

**Impact:** Confusion about "the" lesson endpoint. Two of them (`atlas/teach` and `knowledge/teach`) appear to be earlier prototypes superseded by `learning.py`. The intake `_build_lesson` should be replaced by a call to `generate_lesson` — already done structurally (intake now calls `persist_pipeline`) but the legacy 160-word slice still runs first.

**Recommendation (without deletion):** Mark the three legacy paths as `deprecated_*` aliases in their docstrings; pick `routes/learning.py::generate_lesson` as the canonical implementation. Optional: route the older endpoints to the new one internally.

---

### 🟥 H-2 — Missing dependencies in `requirements.txt`
Both libs are **installed in the live environment** but absent from `requirements.txt`, so a fresh deploy would crash:

| Package | Installed | In requirements? | Used by |
|---|---|---|---|
| `pypdf` | 6.11.0 | ❌ | `atlas_core/archive_engine/parser.py:22` |
| `youtube-transcript-api` | 1.2.4 | ❌ | `routes/intake.py` |

**Recommendation:** Append both to `/app/backend/requirements.txt` (already verified safe — already pip-installed).

---

### 🟧 M-1 — Duplicate `route()` function
- `atlas_core/council/router.py:57` — **synchronous** `route(question) → CouncilDecision`, used internally by blueprint/teaching engines.
- `backend/routes/council.py:52` — **async** FastAPI endpoint `route(req) → JSON`, exposed at `/api/council/route`.

**Verdict:** Not actually a collision (different scopes), but the same name causes grep confusion. The atlas_core internal version uses fuzzy keyword scoring; the route endpoint uses `routing.topic_router.route_topic()`. Two different routing implementations exist.

**Recommendation:** Rename `atlas_core/council/router.py::route` → `route_internal` OR consolidate both behind `routing.topic_router.route_topic`. Won't break anything either way; pick one source of truth.

---

### 🟧 M-2 — Four orphan frontend files (luxury reskin leftovers)
The luxury reskin removed these entry points but the source files remain:

| File | Size | Was used for |
|---|---|---|
| `ChatPanel.js` | 8.2 KB | Floating chat FAB (luxury HUD removed it) |
| `FileBrowserPanel.js` | 16 KB | Legacy file browser popover (replaced by `ArchiveBrowser`) |
| `FileUploadModal.js` | 9 KB | Upload modal (luxury HUD removed the upload button) |
| `useVoiceRecognition.js` | 4 KB | "Hey Atlas" wake word (luxury HUD removed mic) |

**Recommendation:**
- Either **delete** them (clean) OR  
- Move them to `frontend/src/_legacy/` with a `README.md` noting they were the pre-luxury entry points.

I recommend **option B** — preserve them, since the user already restored the sound toggle from this batch and may want to restore others later.

---

### 🟧 M-3 — CORS wildcards in production
`backend/.env` has `CORS_ORIGINS="*"` — allows any origin to call the API. Acceptable for development; risky once a real user account / billing layer is added.

**Recommendation:** Lock to `https://youthful-archimedes-7.preview.emergentagent.com,https://atlas-prod.example.com` once a stable prod URL exists.

---

### 🟨 L-1 — Stale TODO in `ai_categorizer.py:111`
```python
# TODO: Integrate with Emergent LLM for deeper analysis
```
The categoriser still runs purely on filename heuristics. Functional but limited.

**Recommendation:** When Phase 2 (Knowledge Bank) is built, this becomes the natural integration point — categorise via Claude/GPT classifier.

---

### 🟨 L-2 — `/api/chat/trinity` overlaps `/api/council/deliberate`
Both fan out to all 3 personas. `trinity` is the older one (uses sequential LLM calls without unique session IDs — known empty-response bug); `deliberate` is the post-fix version with UUID session IDs and gpt-5.2.

**Recommendation:** Keep `trinity` for backward compatibility, but have it call the council logic internally.

---

### 🟨 L-3 — Dead CSS for removed components
`App.css` still has ~150 lines styling `.chat-fab`, `.chat-panel`, `.file-browser-panel`, `.upload-modal` — all unmounted in the luxury HUD.

**Recommendation:** Leave it. CSS is cheap and you may restore the components.

---

### 🟨 L-4 — Static `/app/exports/` in repo
The two architecture zips (`atlas-ai-architecture.zip`, `atlas-hud-architecture.zip`) live in the repo. They're served by `/api/exports/*` endpoints. Not "broken" — but the zips are stale unless someone re-runs the build script.

**Recommendation:** Add a regenerate-on-startup step OR a `POST /api/exports/build` admin endpoint.

---

## 3. Things that are CORRECT (don't touch)

✅ **Import graph** — every backend route is mounted in `server.py`; every frontend HUD component has at least one importer.  
✅ **MongoDB collection naming** — consistent: `atlas_archive`, `atlas_events`, `atlas_settings`, `sandbox_runs`, `sandbox_saved`, `knowledge`, `lessons`, `projects`, `mastery`, `study_journal`.  
✅ **No secrets in code** — All keys come from `.env`; no hardcoded API keys or passwords anywhere.  
✅ **No unsafe primitives** — `eval`, `exec`, `pickle.loads`, `shell=True` are absent from the codebase.  
✅ **All `_id` projections excluded** — every MongoDB read uses `{"_id": 0}`, no BSON serialisation errors possible.  
✅ **Abort-on-close pattern** — `useTTS`, `useAtlasJob`, `ChatPanel` all use `AbortController` properly.  
✅ **Job polling for >60s LLM tasks** — `useAtlasJob` + `/api/atlas/jobs/{id}` correctly handle the K8s ingress timeout.  
✅ **Atlas Core hard rules** are encoded in `shield_core/identity_anchor.py` and respected by all engines.  

---

## 4. Proposed Phase 0 — Audit Cleanup (before Phase 1)

I will only apply these after explicit approval. None of them change behavior; they make the codebase ready for the 7-phase build:

1. ✅ Append `pypdf` + `youtube-transcript-api` to `requirements.txt`. **(2 lines)**
2. ✅ Rename `atlas_core/council/router.py::route` → `route_internal` to disambiguate. **(1 file, ~5 lines)**
3. ✅ Move 4 orphan frontend files to `frontend/src/_legacy/`. **(4 files moved, 0 import changes)**
4. ✅ Add `_LEGACY_NOTICE` docstrings to the 3 superseded teach endpoints. **(3 files, ~6 lines)**
5. ✅ Document `study_journal` collection in PRD.md. **(1 line)**

**Estimated risk:** Zero. All changes are non-functional (docstrings, file moves, dependency listing). The lint suite + existing 12/12 backend pytest will validate.

---

## 5. Build Order — Phase 1–7 Plan

The phases match your spec exactly. Each phase will be implemented only after **explicit phase-by-phase approval**.

### Phase 1 — Real LLM Integration ⏱ ~2 hrs
- ✅ OpenAI support already in via Emergent LLM Key (`gpt-5.2` for council/learning, `tts-1` for voice)
- ✅ Anthropic Claude available via same key (`claude-sonnet-4-5-20250929` for sandbox AI Suggest)
- 🔲 **New**: Local model support — wrap Ollama/LMStudio HTTP endpoint so the same `LlmChat`-style interface picks between `provider=emergent | provider=local`. Default to emergent; switch via `CUSTOMIZATION → model_provider`.
- 🔲 **New**: Per-persona model preference (Ajani → llama3:70b for engineering, Minerva → claude for narrative, Hermes → deepseek-coder for code)

### Phase 2 — Knowledge & Memory ⏱ ~3 hrs
- ✅ `knowledge` collection already exists
- 🔲 **New**: `memory_bank` collection — long-term memories with TTL + reinforcement
- 🔲 **New**: Vector memory via embeddings stored alongside MongoDB documents (use OpenAI `text-embedding-3-small`)
- 🔲 **New**: Graph memory — light entity/relation extraction stored as `{from, to, relation, source_id}` triples

### Phase 3 — Research Pipeline ⏱ ~3 hrs
- ✅ YouTube intake already exists (with paste fallback)
- 🔲 **New**: Web research — query a search API (Tavily / Brave Search), fetch top N pages, extract clean text
- 🔲 **New**: PDF analysis — already partially via `pypdf` in archive_engine; expose `/api/research/pdf`
- 🔲 **New**: Patent analysis — USPTO/Google Patents JSON API integration

### Phase 4 — Voice & HUD ⏱ ~1 hr (mostly polish)
- ✅ TTS multilingual already wired (OpenAI fallback live, ElevenLabs blocked by Free Tier IP)
- ✅ HUD luxury reskin live
- 🔲 **New**: Restore voice command input (currently removed) — wake-word + intent classifier

### Phase 5 — Digital Twin Engine ⏱ ~4 hrs (architectural)
- 🔲 Spec needed. Will require: physics core (existing sandbox is a proto-twin), persistent state per artefact, replay timeline.

### Phase 6 — Weaver Integration ⏱ ~unknown — need spec
- 🔲 Awaiting definition. "Weaver" is an external system the architect has mentioned but not defined here.

### Phase 7 — Robot Control Layer ⏱ ~unknown — needs hardware spec
- 🔲 Awaiting target robot (ROS? ROS2? proprietary?) + command channel.

---

## 6. Next Action

**The user should pick ONE:**

a. ✅ **Approve Phase 0 (audit cleanup)** — I run the 5 risk-free fixes above and then we move to Phase 1.  
b. 🚀 **Skip Phase 0, go straight to Phase 1** — Real LLM Integration (Ollama/local model support).  
c. 🛑 **Pause and review** — read the report carefully, decide what to change.  
d. 🔄 **Different ordering** — for example, prioritise Phase 3 (Research) over Phase 2 (Memory).

I will not modify code without your explicit phase approval.
