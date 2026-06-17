# ATLAS · Complete Architecture Report

> **Status as of Feb 2026** — Phases 0-6 complete · Phase 7 awaiting hardware spec
> **Backend** FastAPI + Motor + MongoDB · **Frontend** React (CRA) + Luxury HUD reskin
> **Total backend tests passing** 81/81 (Phase-6 + Phase-2/5 regression) · `iteration_14.json`

This document is the architect's single source of truth before Phase 7. It supersedes individual phase reports for navigation purposes (phase reports remain authoritative for their own details).

---

## 1 · Completed phases

| # | Phase | Status | Key artefacts |
|---|-------|--------|---------------|
| 0 | Architecture Audit & Cleanup | ✅ | `AUDIT-REPORT.md`; duplicate routes removed; legacy files relocated to `_legacy/`; `requirements.txt` fixed |
| 1 | Real LLM Integration | ✅ | `services/llm_provider.py` (Emergent / Ollama / LMStudio, with fallback); `routes/llm.py`; per-persona model overrides stored in `atlas_settings._id="persona_models"` |
| 2 | Knowledge / Memory Bank / Vector / Graph | ✅ | `services/memory_bank.py`; `routes/memory.py`; 11 memory categories (4 permanent, 7 decaying); MongoDB-internal hash embedding (default), Ollama/Emergent optional; graph triples; freshness decay + reinforcement |
| 3 | Research Pipeline | ✅ | `services/web_scraper.py`, `pdf_reader.py`, `patent_client.py`, `research_pipeline.py`; `routes/research.py`; DuckDuckGo + Google Patents (no API key), pypdf; every result auto-stores into `category='research'` |
| 4 | Voice System & ATLAS HUD | ✅ | `hooks/useVoiceRecognition.js` (3 modes: off / push-to-talk / wake-word); `utils/voiceCommands.js` (persona + tile aliases); mic chip in HUDInterface top-right; HUD geometry untouched |
| 5 | Digital Twin Engine | ✅ | `models/twin_models.py`, `services/twin_simulator.py` (6 engines), `services/digital_twin.py`, `routes/twins.py`; registry + state revisions + parallel council deliberation; auto-spawns project & research memories |
| 6 | Weaver (manufacturing planning) | ✅ | `models/weaver_models.py`, `services/parts_db.py`, `blueprint_parser.py`, `weaver.py`, `routes/weaver.py`; 25-row starter library; full pipeline: parse → enrich → spawn twin → 4 sims → build/manufacturing/failure plans → optional council |
| K | Knowledge Ingestion System | ✅ | `models/knowledge_models.py`, `services/source_fetchers.py`, `knowledge_distiller.py`, `knowledge_ingestion.py`, `routes/kbase.py`; ingests GitHub / YouTube / PDF / Web / Patent / Academic URLs; LLM-distilled MemoryRecords with dedup-by-URL + reinforce-on-revisit + graph triples |
| 7 | Robot Control Layer | ⏳ | awaits target hardware spec |

Detail: `/app/memory/PHASE2-REPORT.md`, `PHASE3-4-REPORT.md`, `PHASE5-REPORT.md`, `PHASE6-REPORT.md`, `PRD.md`.

---

## 2 · Database schemas

All collections live in a single MongoDB database (`DB_NAME` env var; default `test_database`). Two persistence patterns are used:

* **Lazy module client** (Phase 2+): each service creates an `AsyncIOMotorClient` on first call; no startup hook required, easy to unit-test.
* **Legacy startup-bound client** (atlas_core only): the original `_atlas_attach_mongo` startup hook in `server.py` wires the older archive/conversations/events collections.

### 2.1 Collections in use

| # | Collection | Owner phase | Purpose |
|---|------------|-------------|---------|
| 1 | `atlas_settings` | 1 + 2 | KV doc store keyed by `_id` for per-persona overrides (`persona_models`, `embedding_models`) |
| 2 | `atlas_archive` | atlas_core | Legacy archive — surface-level memory before Phase 2 |
| 3 | `atlas_conversations` | atlas_core | Legacy conversation snapshots |
| 4 | `atlas_events` | atlas_core | Legacy event feed (used by MEMORY HUD tile) |
| 5 | `knowledge` | 1 | Intake-derived knowledge entries (title, topic, transcript, summary, ai_owner) |
| 6 | `lessons` | 1 | LLM-generated lessons keyed to knowledge entries; includes `quiz` payload |
| 7 | `projects` | 1 | LLM-generated project suggestions tied to lessons |
| 8 | `mastery` | 1 | Mastery tracking per student × topic |
| 9 | `students` | 1 | Student profiles |
| 10 | `study_journal` | 1 | Activity / reflection log |
| 11 | `sandbox_saved` | 1 | Saved Interactive Sandbox configurations |
| 12 | `sandbox_runs` | 1 | Sandbox simulation run history |
| 13 | **`memory_bank`** | **2** | **Vector + categorised long-term memory (see §3)** |
| 14 | **`graph_triples`** | **2** | **Entity-relation graph (from/to/relation/weight/hits)** |
| 15 | `digital_twins` | 5 | Twin registry (one row per twin) |
| 16 | `twin_simulations` | 5 | Full simulation history (every run kept) |
| 17 | `twin_deliberations` | 5 | Council voices + verdict per twin/sim |
| 18 | `weaver_parts` | 6 | Reusable parts library (25-row starter seed) |
| 19 | `weaver_plans` | 6 | One row per WeaverPlan; cross-links `twin_id` |

### 2.2 Per-collection key fields (compact)

```jsonc
// atlas_settings (Phase 1 + 2)
{
  "_id": "persona_models" | "embedding_models",
  "<persona>": { "provider": "emergent|ollama|lmstudio|hash", "model": "..." }
}

// memory_bank (Phase 2)
{
  "id": "uuid", "content": "text", "persona": "...",
  "category": "user|project|blueprint|council|research|temporary|lesson|intake|chat|sandbox|manual",
  "permanent": true/false, "pinned": true/false,
  "source_type": "...", "source_id": "uuid|null",
  "tags": ["..."], "freshness": 0..1, "reinforce_count": 0,
  "created_at": "ISO-8601", "last_referenced": "ISO-8601",
  "embedding": [float; 384], "embed_meta": { "provider_used": "...", "model": "...", "fallback_reason"?: "..." }
}

// graph_triples (Phase 2)  ── upsert key: (from_node, to_node, relation)
{ "from_node": "...", "to_node": "...", "relation": "...", "source_id": "?",
  "weight": float, "hits": int, "updated_at": "ISO-8601" }

// digital_twins (Phase 5)
{
  "id": "uuid", "name": "...", "category": "device|robot|vehicle|environment|building|manufacturing_system|power_system",
  "owner_agent": "ajani|minerva|hermes|council",
  "related_project_id": "?", "description": "?", "tags": ["..."],
  "state": {
    "status": "draft|spec|simulated|approved|deprecated",
    "components": [ Component ], "materials": ["..."],
    "dimensions": Dimensions | null, "energy": EnergyProfile | null,
    "dependencies": [ Dependency ], "sensor_inputs": [ SensorInput ],
    "outputs": [ TwinOutput ],
    "integrations": {}, "cad_refs": [], "hardware_binding": null,   // FWD-COMPAT
    "revision": int, "updated_at": "ISO-8601"
  },
  "last_simulation_id": "?", "last_deliberation_id": "?",
  "created_at": "...", "updated_at": "..."
}

// twin_simulations (Phase 5)
{
  "id": "uuid", "twin_id": "uuid", "revision": int,
  "kind": "blueprint|assembly|resource|failure|timeline|cost",
  "ok": bool, "score": 0..1,
  "findings": ["..."], "warnings": ["..."], "failures": ["..."],
  "metrics": { ... },
  "timeline": [...] | null,    // assembly + timeline only
  "bom": [...] | null,         // resource + cost only
  "created_at": "ISO-8601"
}

// twin_deliberations (Phase 5)
{
  "id": "uuid", "twin_id": "uuid", "simulation_id": "?",
  "voices": [ { "persona": "ajani|minerva|hermes|council", "role": "...", "text": "...", "flags": [...] } ],
  "verdict": "approve|revise|reject|pending",
  "final_text": "...", "created_at": "ISO-8601"
}

// weaver_parts (Phase 6)
{
  "id": "uuid", "name": "...",
  "category": "component|material|fastener|electronic|sensor|actuator|tool|consumable",
  "description": "?", "material": "?", "spec": { ... },
  "unit": "...", "default_cost": float | null, "default_lead_time_days": float | null,
  "suppliers": ["..."], "tags": ["..."],
  "created_at": "...", "updated_at": "..."
}

// weaver_plans (Phase 6)
{
  "id": "uuid", "title": "...", "owner_agent": "...",
  "related_project_id": "?", "description": "?",
  "blueprint": BlueprintInput,
  "parts_extracted": [ ExtractedPart ],
  "twin_id": "uuid",   // Phase-5 twin auto-spawned
  "build_plan":          BuildPlan,
  "manufacturing_plan":  ManufacturingPlan,
  "failure_prediction":  FailurePrediction,
  "council":             CouncilOutcome | null,
  "created_at": "...", "updated_at": "..."
}
```

---

## 3 · Memory schemas (Phase 2)

### 3.1 Categories
| Category | Permanent? | Decays? | Auto-pinned | Producer phases |
|----------|------------|---------|-------------|------------------|
| `user`     | YES | no | yes | architect notes via `POST /api/membank/user` |
| `project`  | YES | no | yes | Phase-1 intake; Phase-5 twin register + sims; Phase-6 plan auto-spawn |
| `blueprint`| YES | no | yes | Phase-1 blueprint generate; Phase-6 every `weaver/plan` |
| `council`  | YES | no | yes | Phase-1 deliberate; Phase-5 twin deliberate (twin sims + verdict) |
| `research` | no  | yes | no | Phase-3 web/pdf/patent; Phase-5 sim outputs tagged `success-memory` / `failure-memory` |
| `lesson`   | no  | yes | no | Phase-1 intake `persist_pipeline` |
| `intake`   | no  | yes | no | Phase-1 intake `persist_pipeline` |
| `chat`     | no  | yes | no | reserved for chat history embeddings |
| `sandbox`  | no  | yes | no | reserved for InteractiveSandbox runs |
| `temporary`| no  | yes | no | scratch space |
| `manual`   | no  | yes | no | default for direct `/store` calls |

### 3.2 Freshness curve
```
freshness(t) = max(MIN_FRESHNESS, base − DECAY_PER_DAY · age_days) + REINFORCEMENT_BUMP × n_reinforce
DECAY_PER_DAY      = 0.05      (≈ 20 days to MIN_FRESHNESS)
REINFORCEMENT_BUMP = 0.20
MIN_FRESHNESS      = 0.05      (never reaches zero)
```
Permanent (pinned=true) rows skip decay entirely.

### 3.3 Search score
```
score = 0.85 · cosine_similarity(query_emb, row_emb)  +  0.15 · freshness_now
default min_score = 0.30  ·  default top_k = 10
```

### 3.4 Embedding providers (per persona)
| Provider | Status | Notes |
|----------|--------|-------|
| `hash` (default) | ✅ | Dependency-free 384-dim feature-hash (blake2b word + char-3gram). Sub-ms, never fails. |
| `ollama` | optional | `nomic-embed-text` via local Ollama server (`OLLAMA_HOST`). Semantic. |
| `emergent` | optional | OpenAI `text-embedding-3-small` via a REAL `OPENAI_API_KEY` (Emergent universal key does NOT cover embeddings). |

`PUT /api/membank/embed-settings` swaps per-persona on the fly.

### 3.5 Graph memory
* Upsert key: `(from_node, to_node, relation)`
* `$inc weight + hits` on repeat assertions
* `GET /api/membank/graph/around?node=X&depth=2` runs BFS, returns `{root, depth, nodes, edges}`

---

## 4 · Knowledge Bank structure (Phase 1)

The Knowledge Bank is the **learning pipeline**'s output, distinct from the Memory Bank:

```
intake (YouTube transcript / text)
        │
        ▼
   knowledge.insert_one()        ← raw transcript + summary
        │
        ▼
   lessons.insert_one()          ← LLM-generated lesson + quiz (Phase 1 personas)
        │
        ▼
   projects.insert_one()         ← LLM-generated project suggestion
        │
        ▼
   memory_bank ×3                ← lesson (decay) + project (permanent) + intake (decay)
   (Phase-2 auto_store)
```

Mastery + study_journal track student progress separately; they are **not** consumed by Phases 5/6.

### Endpoints
| Method | Path | Purpose |
|--------|------|---------|
| POST | `/api/intake/youtube` | YouTube URL → transcript → full pipeline |
| POST | `/api/intake/transcript` | direct text → full pipeline |
| GET  | `/api/knowledge/subjects` | list subjects |
| GET  | `/api/lessons` | list lessons (filter by topic) |
| GET  | `/api/projects` | list projects |
| POST | `/api/quiz/grade` | submit + grade quiz answers |

---

## 5 · Research Pipeline structure (Phase 3)

```
                 ┌────────────────────────┐
                 │  routes/research.py    │
                 │  /web  /pdf  /patent   │
                 └─────────────┬──────────┘
                               │
                ┌──────────────▼───────────────┐
                │  services/research_pipeline  │
                │    research_web()             │
                │    research_pdf()             │
                │    research_patents()         │
                └─┬─────────────┬─────────────┬─┘
                  │             │             │
   ┌──────────────▼──┐  ┌───────▼──────┐  ┌───▼───────────┐
   │ web_scraper.py  │  │ pdf_reader.py│  │ patent_client │
   │ DDG HTML search │  │ pypdf + chunk│  │ G Patents XHR │
   │ httpx+selectolax│  │              │  │ + detail HTML │
   └──────────────┬──┘  └───────┬──────┘  └───┬───────────┘
                  │             │             │
                  ▼             ▼             ▼
   ┌────────────────────────────────────────────────────┐
   │  Hermes summary (web/pdf)  ·  Ajani take (patent)  │
   │  → memory_bank.auto_store(category='research')      │
   │  → tags: [query, source_type]                        │
   └────────────────────────────────────────────────────┘
```

### Endpoints
| Method | Path | Notes |
|--------|------|-------|
| POST | `/api/research/web` | `{query, top_n≤10, summarise}` → list of sources |
| POST | `/api/research/pdf` | multipart `file=<.pdf>` (≤ 12 MB) → chunks + summary |
| POST | `/api/research/patent` | `{query, top_n≤10, deep}` → patents (+ engineer take if `deep`) |
| GET  | `/api/research/recent` | `?source_type=web|pdf|patent` |

### Failure handling
* `ResearchUnreachable` → 503 (DDG/Google Patents may rate-limit a cloud IP)
* PDF: empty → 400, >12 MB → 413, password-protected → 400 clean
* Memory writes are fire-and-forget — never abort the parent call

---

## 6 · Digital Twin structure (Phase 5)

```
┌──────────────────────────────────────────────────────────────────────┐
│                       DIGITAL TWIN STACK                              │
│                                                                      │
│  routes/twins.py                                                     │
│      register · list · categories · /{id} · /state · simulate ·      │
│      simulations · deliberate · delete                               │
│                                                                      │
│  services/digital_twin.py                                            │
│      register_twin()  → memory_bank category=project (permanent)     │
│      run_and_persist_simulation()                                    │
│          ↘ twin_simulator.simulate(twin, kind)                       │
│          ↘ memory_bank category=project                              │
│          ↘ memory_bank category=research (success-/failure-memory)   │
│      deliberate()      asyncio.gather(ajani, minerva, hermes)        │
│          ↘ memory_bank category=council (permanent)                  │
│                                                                      │
│  services/twin_simulator.py    PURE PYTHON, DETERMINISTIC            │
│      blueprint   cycle + reference check                              │
│      assembly    topological sort, step plan                          │
│      resource    BOM + energy budget                                  │
│      failure     fan-out SPOF + sensor gaps + transient power        │
│      timeline    critical-path DP                                     │
│      cost        materials + 20% labour                              │
└──────────────────────────────────────────────────────────────────────┘
```

### Verdict aggregator
```
flag_count = Σ ENGINEERING_FLAG / SCIENCE_FLAG / VALIDATION_FLAG  (over all 3 voices)
flag_count == 0          →  approve
flag_count ≥ 3           →  reject
otherwise                →  revise
any persona unreachable  →  pending
```

### Endpoints (canonical)
| Method | Path | |
|--------|------|---|
| GET | `/api/twins/categories` | enum introspection |
| POST | `/api/twins/register` | spawn |
| GET / DELETE | `/api/twins/{id}` | |
| PUT | `/api/twins/{id}/state` | revision ++ |
| POST | `/api/twins/{id}/simulate` | `{kind}` |
| GET | `/api/twins/{id}/simulations` + `/simulations/{sim_id}` | |
| POST | `/api/twins/{id}/deliberate` | `{simulation_id?}` |

---

## 7 · Weaver structure (Phase 6)

```
┌──────────────────────────────────────────────────────────────────────┐
│                       WEAVER · PHASE 6                                │
│                                                                      │
│  routes/weaver.py                                                    │
│      parts CRUD + search + seed + categories                          │
│      analyze · plan · plans CRUD (?drop_twin=…)                       │
│                                                                      │
│  services/weaver.plan_from_blueprint                                 │
│      1) blueprint_parser.parse()                                      │
│         ├─ structured JSON → _parse_structured()                      │
│         └─ free text       → LLM (Hermes) + regex fallback           │
│      2) match_against_library()                                       │
│      3) digital_twin.register_twin()   ← Phase 5 reuse                │
│      4) run_and_persist_simulation × 4 (assembly·cost·timeline·fail)  │
│      5) _build_plan() / _manufacturing_plan() / _failure_prediction() │
│      6) (optional) digital_twin.deliberate()  ← Phase 5 council       │
│      7) persist to weaver_plans                                       │
│      8) memory_bank category=blueprint (permanent)                    │
│                                                                      │
│  services/parts_db.py    weaver_parts collection                     │
│      25-row idempotent starter seed                                   │
│      match_part(name) → token-overlap + substring score ≥ 0.5         │
└──────────────────────────────────────────────────────────────────────┘
```

### Heuristics
| Aspect | Rule |
|--------|------|
| difficulty | `<60 min·no-electronics→trivial · <240·no-machining→easy · <960→medium · <2880→hard · else→expert` |
| cost | `materials + 20% labour heuristic` |
| risk | `(1 − failure_sim_score) + 0.05·|missing_parts|`, clipped [0,1] |
| tools | union of per-category hints (Soldering iron, Hex key set, Multimeter, …) |

### Endpoints
| Method | Path | |
|--------|------|---|
| POST | `/api/weaver/parts/seed` | idempotent |
| POST/GET/DELETE | `/api/weaver/parts` + `/{id}` | |
| POST | `/api/weaver/analyze` | parse + library match only |
| POST | `/api/weaver/plan` | full pipeline (→ twin + 4 sims + memory) |
| GET / DELETE | `/api/weaver/plans` + `/{id}` | `?drop_twin=true` cascades |

---

## 8 · Data flow between systems

### 8.1 Cross-phase dependency graph

```
                                                    ┌──────────────────┐
                                                    │  Phase 4 Voice   │
                                                    │  HUD voice cmds  │
                                                    └────────┬─────────┘
                                                             │ intent
                                                             ▼
   ┌─────────┐    ┌─────────┐    ┌─────────────┐    ┌────────────────┐
   │  P1     │    │  P3     │    │   P6        │    │   P5           │
   │ Intake  │    │Research │    │  Weaver     │───▶│ Digital Twin   │
   │ + Learn │    │Pipeline │    │ orchestrator│    │ registry + sims│
   └────┬────┘    └────┬────┘    └─────┬───────┘    └────────┬───────┘
        │              │               │                     │
        │ knowledge/   │ research      │ blueprint+plan      │ sim/delib
        │ lesson/      │ rows          │ rows                │ rows
        │ project      ▼               ▼                     ▼
        ▼      ┌───────────────────────────────────────────────────┐
               │            P2  ·  MEMORY BANK + GRAPH              │
               │  memory_bank   ·  graph_triples   ·  atlas_settings│
               │  hash/ollama/emergent embedders, decay+reinforce   │
               └────────────────┬───────────────────────────────────┘
                                │
                                ▼
                          P1 · llm_provider
                          (Emergent / Ollama / LMStudio)
                          for every LLM call, with fallback
```

### 8.2 What writes into memory_bank, by trigger

| Trigger | Category writes |
|---------|-----------------|
| `POST /api/intake/transcript` (Phase 1) | lesson + project + intake |
| `POST /api/council/deliberate` (Phase 1) | council |
| `POST /api/ai/blueprint/generate` (Phase 1) | blueprint |
| `POST /api/research/web/pdf/patent` (Phase 3) | research × N |
| `POST /api/twins/register` (Phase 5) | project |
| `POST /api/twins/{id}/simulate` (Phase 5) | project + research(success/failure) |
| `POST /api/twins/{id}/deliberate` (Phase 5) | council |
| `POST /api/weaver/plan` (Phase 6) | blueprint + (all of the above via auto-spawned twin + sims + optional council) — up to **10 rows per plan** |
| `POST /api/membank/user` | user |

### 8.3 Voice command → action map (Phase 4)

```
"hey atlas, ajani"     →  select-ai  : ajani
"atlas, minerva"        →  select-ai  : minerva
"atlas, projects"       →  open-section : outer/projects
"atlas, lab"            →  open-section : outer/lab
"atlas, memory"         →  open-section : middle/memory
"atlas, encyclopedia"   →  open-section : middle/encyclopedia
"stop / close / cancel" →  close-panel
(11 tile aliases + 4 persona aliases · wake mode requires wake phrase)
```

---

## 9 · Remaining unfinished components

### 9.1 Phase 7 — Robot Control Layer (top priority when spec lands)

The schema is **already plumbed** for it:
* `TwinState.hardware_binding: dict | null` — placeholder, ignored in Phase 5/6
* Weaver respects `hardware_binding` when an architect opts in via plan request
* No collection is missing; binding metadata can be stored directly on the twin

What is missing:
1. Concrete hardware target (ROS2 node? MQTT broker? Modbus/CAN? plain HTTP shim?)
2. Safety envelope policy (what commands are allowed, kill-switch protocol)
3. Telemetry → memory wiring (decay rate for live sensor streams)
4. Authentication and authorization for command-level actions

Until those answers exist, Phase 7 cannot start.

### 9.2 Optional HUD polish (queued, no blocker)

| Item | Effort | Notes |
|------|--------|-------|
| MEMORY tile Recall search → `GET /api/membank/search` | ~1 h | Visuals unchanged |
| Research tabs (Web/PDF/Patent) inside IntakePanel | ~2 h | Hits existing `/api/research/*` |
| "Plan with Weaver" CTA inside BlueprintWorkbench | ~1.5 h | Hits `/api/weaver/plan` |
| Voice intent `"hey atlas, plan: …"` | ~30 min | Already wired backend-side |
| Voice intent `"hey atlas, research …"` | ~30 min | Already wired backend-side |
| Voice intent `"hey atlas, simulate …"` (twin fuzzy-match + TTS verdict) | ~1 h | |

### 9.3 Forward-compat hooks already in code (no work needed until Phase 7+)
* `BlueprintFormat.CAD_EXPORT` / `DIAGRAM` — placeholder formats
* `TwinState.integrations` — for Weaver/IFTTT-like cross-system signals
* `TwinState.cad_refs` — for STL/STEP/glTF asset ids
* `Component.twin_ref` — composes twins recursively (battery_twin used by drone_twin)
* `Part.suppliers` — supplier metadata

---

## 10 · Technical debt & known limitations

### 10.1 Backend
| Item | Severity | Status |
|------|----------|--------|
| Hash embedder is lexical, not semantic (default). | Medium | Architect can swap to Ollama per persona; flagged in PRD. |
| `search_memory` computes cosine in Python (≤ few-thousand rows). | Medium | Migrate to Mongo Atlas Vector Search when rows exceed ~5 k. |
| ElevenLabs cloud-IP block forces OpenAI TTS fallback. | Low | Architect's own ElevenLabs key unblocks; documented. |
| DuckDuckGo HTML / Google Patents may rate-limit the cloud IP. | Low | Surfaced as 503; architect can run locally to bypass. |
| Council deliberation cost ≈ 3 × LLM calls (parallelised). | Low | Mitigated via asyncio.gather (Phase 5 polish). |
| Memory writes are fire-and-forget — silent on failure. | Low | By design (never abort parent pipeline); logged at WARN. |
| No retention cap on `twin_simulations` collection. | Low | Architect can prune; not yet a problem. |
| Blueprint LLM parser depends on Hermes returning valid JSON. | Low | Regex fallback catches obvious "N × Foo" patterns. |

### 10.2 Frontend
| Item | Severity | Status |
|------|----------|--------|
| Agent lint tool flags React-Compiler patterns in 17 files. | Medium | File-level `/* eslint-disable */` applied; CRA `yarn build` succeeds. `DISABLE_ESLINT_PLUGIN=true` in `frontend/.env`. |
| `_legacy/` directory retained per architect directive but excluded from lint. | Low | Documented in `_legacy/README.md`. |
| Wake-word mode auto-restarts every ~60 s — some browsers cut off recognition. | Low | Auto-restart inside `useVoiceRecognition.onend`. |
| No mic-permission graceful UI on denial. | Low | Status field stores `err:not-allowed`; not surfaced visually yet. |

### 10.3 Architectural
| Item | Severity | Status |
|------|----------|--------|
| Two parallel persistence patterns (atlas_core legacy startup-bound vs Phase-2+ lazy). | Low | Both work; lazy pattern is the going-forward default. |
| `atlas_settings` is a single doc with mixed concerns (persona models + embedding models). | Low | Keyed by `_id`; trivially splittable later. |
| Research pipeline writes one memory per chunk for PDFs → many rows for big PDFs. | Low | Architect can throttle via `summarise=false` or chunk size in `pdf_reader.chunk_text`. |
| Phase 1 `knowledge`/`lessons`/`projects` and Phase-2 `memory_bank` overlap conceptually. | Low | By design — Knowledge Bank is the curated learning corpus; Memory Bank is the universal recall layer. |
| No global authn/authz layer. | Medium | Architect is the sole operator; Phase 7 will need this before exposing any command surface. |

### 10.4 What we deliberately did NOT build
* Real CAD parsing (STL/STEP/glTF) — placeholder formats only.
* Real OCR for diagram blueprints — placeholder.
* Real physics solver — Phase 5 sims are deterministic Python heuristics; that was the brief.
* Hardware drivers / GPIO / motor PWM — explicitly out of scope until Phase 7 spec.
* Multi-user / RBAC.

---

## 11 · Quick-start commands

```bash
# Verify health
curl $REACT_APP_BACKEND_URL/api/llm/health
curl $REACT_APP_BACKEND_URL/api/membank/categories
curl $REACT_APP_BACKEND_URL/api/twins/categories
curl $REACT_APP_BACKEND_URL/api/weaver/parts/categories

# Seed the Weaver parts library (idempotent)
curl -X POST $REACT_APP_BACKEND_URL/api/weaver/parts/seed

# Run all backend test suites
cd /app/backend
pytest tests/ -m 'not slow' -v        # fast subset, ~10 s
pytest tests/ -v                       # full incl. LLM-bound, ~3 min

# Build the frontend
cd /app/frontend && yarn build
```

---

## 12 · Files of reference (single-file index)

```
/app/memory/
├── PRD.md                  ← master product requirements + roadmap
├── AUDIT-REPORT.md         ← Phase 0 cleanup audit
├── PHASE2-REPORT.md        ← Memory Bank deep-dive
├── PHASE3-4-REPORT.md      ← Research + Voice
├── PHASE5-REPORT.md        ← Digital Twin Engine
├── PHASE6-REPORT.md        ← Weaver
└── ARCHITECTURE-REPORT.md  ← THIS FILE

/app/backend/
├── server.py               ← FastAPI app + router wiring + atlas_core startup
├── models/
│   ├── twin_models.py      ← Phase 5
│   └── weaver_models.py    ← Phase 6
├── services/
│   ├── llm_provider.py     ← Phase 1
│   ├── memory_bank.py      ← Phase 2  (★ most reused)
│   ├── web_scraper.py      ← Phase 3
│   ├── pdf_reader.py       ← Phase 3
│   ├── patent_client.py    ← Phase 3
│   ├── research_pipeline.py← Phase 3
│   ├── twin_simulator.py   ← Phase 5
│   ├── digital_twin.py     ← Phase 5
│   ├── parts_db.py         ← Phase 6
│   ├── blueprint_parser.py ← Phase 6
│   └── weaver.py           ← Phase 6
├── routes/
│   ├── llm.py · memory.py · research.py · twins.py · weaver.py
│   ├── intake.py · learning.py · council.py · ai_services.py
│   ├── sandbox.py · files.py · chat.py · hud_surfaces.py
│   └── routing/topic_router.py
└── tests/
    ├── test_membank_phase2.py     ← Phase 2 (29 cases)
    ├── test_research_phase3.py    ← Phase 3 (16)
    ├── test_twins_phase5.py       ← Phase 5 (19)
    ├── test_twins_phase5_extras.py← Phase 5 (12)
    ├── test_weaver_phase6.py      ← Phase 6 (13)
    └── test_weaver_phase6_extras.py← Phase 6 (8)
                                       Total: 97 backend tests

/app/frontend/src/
├── components/HUDInterface.js          ← Phase 4 mic toggle wiring
├── components/HUD/*                    ← Luxury HUD reskin (untouched)
├── hooks/
│   ├── useVoiceRecognition.js          ← Phase 4
│   ├── useTTS.js · useAudioFeedback.js · useAudioReactive.js
│   └── useAtlasJob.js
├── utils/voiceCommands.js              ← Phase 4
└── _legacy/                            ← archived per architect directive
```

---

## 13 · Recommended path to Phase 7

When the architect is ready to start Phase 7 Robot Control Layer, please share:

1. **Target platform** — ROS2 / MQTT / HTTP shim / vendor SDK (PX4, Bosch, Tesla bot, etc.)
2. **First robot** — what concrete twin should bind to real hardware first?
3. **Safety policy** — kill-switch protocol, command allow-list, telemetry rate, fail-safe state
4. **Authn/Authz** — who can send commands, how is it gated
5. **Network** — public endpoint, VPN, or local-only?

With those five answers the agent can scaffold Phase 7 in a single iteration:
`services/robot_control.py` (driver-agnostic), `routes/robot.py` (`/api/robot/{bind, status, command}`), telemetry → memory bank wiring (`category='research'` with `temporary` decay), HUD surface inside an existing tile.

Until then, ATLAS is fully operational as a **planning + simulation + research + learning** intelligence — exactly what the brief required.

— ATLAS Lead Architect agent, Feb 2026.
