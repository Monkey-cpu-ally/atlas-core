# Phase 2 — Memory Bank · Completion Report

> Status: ✅ **COMPLETE** · 29/29 backend tests passed · Feb 2026
> Owner: ATLAS Lead Architect
> Reviewed by: testing_agent_v3_fork iteration_11

---

## 1 · Goals (from the architect brief)

Build a Knowledge + Memory layer for ATLAS that supports:
1. Vector search (semantic / lexical recall across all persona outputs)
2. Graph memory (entity–relation triples that reinforce with use)
3. Six memory categories with different persistence policies
4. Zero external infrastructure (MongoDB-internal — option C the architect chose)
5. Auto-population from existing pipelines (lesson, intake, council, blueprint, project)

All five are now live and tested.

---

## 2 · Architecture

```
┌──────────────────────────────────────────────────────────────────────────┐
│                         ATLAS COGNITIVE ARCH                              │
│                                                                          │
│   Lesson          Intake          Council         Blueprint              │
│   (decay)         (decay)         (permanent)     (permanent)            │
│       │             │                 │               │                  │
│       ▼             ▼                 ▼               ▼                  │
│   ┌──────────────────────────────────────────────────────────────┐       │
│   │  services/memory_bank.py · auto_store(category, persona, …)  │       │
│   └────────────────────┬────────────────────┬────────────────────┘       │
│                        │                    │                            │
│            ┌───────────▼────────┐  ┌────────▼─────────┐                  │
│            │   memory_bank      │  │  graph_triples   │                  │
│            │  (MongoDB col)     │  │  (MongoDB col)   │                  │
│            │                    │  │                  │                  │
│            │  id, content,      │  │  from_node,      │                  │
│            │  persona,          │  │  to_node,        │                  │
│            │  category,         │  │  relation,       │                  │
│            │  permanent,        │  │  weight, hits,   │                  │
│            │  pinned,           │  │  updated_at      │                  │
│            │  freshness,        │  │                  │                  │
│            │  reinforce_count,  │  └──────────────────┘                  │
│            │  last_referenced,  │                                        │
│            │  embedding[384],   │  ┌──────────────────┐                  │
│            │  embed_meta,       │  │ atlas_settings   │                  │
│            │  tags,             │  │ _id: embedding_  │                  │
│            │  source_type,      │  │      models      │                  │
│            │  source_id,        │  │ (per-persona)    │                  │
│            │  created_at        │  └──────────────────┘                  │
│            └────────────────────┘                                        │
└──────────────────────────────────────────────────────────────────────────┘
```

Embedding stack (per-persona, swappable):
* **`hash`** (default) — deterministic blake2b feature-hash over word + char-3-gram
  tokens, L2-normalised, 384 dims. Zero dependencies, sub-millisecond.
* **`ollama`** — POST `${OLLAMA_HOST}/api/embeddings` (`nomic-embed-text` default).
* **`emergent`** — OpenAI `text-embedding-3-small` via a real `OPENAI_API_KEY`
  (the Emergent universal key does NOT cover the embeddings endpoint).

Fallback chain: `<requested provider>` → on any error → `hash` (never blocks).

---

## 3 · API endpoints

All under `/api/membank/*`.

### Memory CRUD
| Method | Path | Notes |
|--------|------|-------|
| POST | `/api/membank/store` | full-control store; honours `category` + `pinned` |
| GET  | `/api/membank/search` | `?q=…&persona=&category=&top_k=10&min_score=0.30` |
| GET  | `/api/membank/list`   | `?persona=&category=&limit=40&include_decayed=false` |
| POST | `/api/membank/reinforce/{id}` | +0.20 freshness, +1 reinforce_count |
| DELETE | `/api/membank/{id}` | hard delete |
| GET  | `/api/membank/categories` | static introspection — permanent/decay lists |

### Shortcut endpoints
| Method | Path | Behaviour |
|--------|------|-----------|
| POST | `/api/membank/user`     | category=`user`, pinned=true, persona=council |
| GET  | `/api/membank/user`     | list architect notes (always include_decayed) |
| POST | `/api/membank/research` | category=`research`, decaying, persona=hermes by default |

### Graph triples
| Method | Path | Notes |
|--------|------|-------|
| POST | `/api/membank/graph/triple` | upsert on (from, to, relation); $inc weight + hits |
| GET  | `/api/membank/graph/list`   | `?node=&relation=&limit=100` |
| GET  | `/api/membank/graph/around` | BFS `?node=…&depth=1..3&limit_per_layer=12` |

### Embed-provider settings
| Method | Path | Notes |
|--------|------|-------|
| GET | `/api/membank/embed-settings` | per-persona provider/model + available providers |
| PUT | `/api/membank/embed-settings` | `{updates: {ajani: {provider: "ollama", model: "nomic-embed-text"}}}` |

---

## 4 · Memory category schema

| Category   | Permanent? | Decay? | Auto-pinned | Source pipelines |
|------------|------------|--------|-------------|------------------|
| `user`     | YES        | no     | yes         | `POST /api/membank/user` (architect notes) |
| `project`  | YES        | no     | yes         | `routes/learning.py::persist_pipeline` |
| `blueprint`| YES        | no     | yes         | `routes/ai_services.py::generate_blueprint` |
| `council`  | YES        | no     | yes         | `routes/council.py::deliberate` |
| `research` | no         | yes    | no          | `POST /api/membank/research` (Phase 3 intake) |
| `temporary`| no         | yes    | no          | manual / scratch |
| `lesson`   | no         | yes    | no          | `routes/learning.py::persist_pipeline` |
| `intake`   | no         | yes    | no          | `routes/intake.py` via persist_pipeline |
| `chat`     | no         | yes    | no          | reserved for chat history embeddings |
| `sandbox`  | no         | yes    | no          | reserved for InteractiveSandbox runs |
| `manual`   | no         | yes    | no          | default for direct `/store` calls |

### Freshness curve

```
freshness(t) = max(MIN_FRESHNESS, base − DECAY_PER_DAY · age_days)
              + REINFORCEMENT_BUMP per /reinforce call (capped at 1.0)

DECAY_PER_DAY      = 0.05   (≈ 20 days to MIN_FRESHNESS)
REINFORCEMENT_BUMP = 0.20
MIN_FRESHNESS      = 0.05   (never hits 0 — old memory always remains searchable)
```

Permanent rows have `pinned=true` and bypass decay entirely.

### Search score
```
score = 0.85 · cosine_similarity + 0.15 · freshness_now
```
Default min_score = 0.30. Decayed memories surface less unless reinforced.

---

## 5 · Auto-wired pipelines (Phase 2 deliverable)

| Pipeline | File | Lines | Memory writes |
|----------|------|-------|---------------|
| **Intake → Lesson → Project** | `routes/learning.py::persist_pipeline` | 220-260 | 1× lesson (decay), 1× project (permanent), 1× intake (decay) — all via `asyncio.gather` |
| **Council deliberation** | `routes/council.py::deliberate` | 107-125 | 1× council (permanent), persona = lead voice |
| **Blueprint Engine** | `routes/ai_services.py::generate_blueprint` | 410-440 | 1× blueprint (permanent), persona = ajani |
| **User memory** | `routes/memory.py::store_user_memory` | n/a | architect-driven, 1× user (permanent) |
| **Research memory** | `routes/memory.py::store_research_memory` | n/a | Phase 3 entry point, 1× research (decay) |

All writes go through `services.memory_bank.auto_store(...)` which:
1. Validates content (≥3 chars) — silently skips if too short.
2. Runs the persona's preferred embedder; falls back to `hash` on failure.
3. Inserts the row into `memory_bank` with `permanent` flag derived from category.
4. NEVER raises — wraps the entire flow in try/except so a failed embedding
   can never abort the parent pipeline (intake / council / blueprint).

---

## 6 · MongoDB schemas

### `memory_bank`
```jsonc
{
  "id": "uuid4",                     // primary key (string, not _id)
  "content": "text up to 8000 chars",
  "persona": "ajani|minerva|hermes|council",
  "category": "user|project|blueprint|council|research|temporary|lesson|intake|chat|sandbox|manual",
  "permanent": true,                  // derived from category
  "pinned": true,                     // bypasses decay when true
  "source_type": "user|project|blueprint|council|research|lesson|intake|chat|sandbox|manual",
  "source_id": "uuid4 of upstream row (lesson_id, project_id, …)",
  "tags": ["string", "..."],
  "freshness": 1.0,                   // 0..1, stored
  "reinforce_count": 0,
  "created_at": "ISO-8601 UTC",
  "last_referenced": "ISO-8601 UTC",
  "embedding": [384 floats],          // not echoed in API responses
  "embed_meta": {
    "persona": "ajani",
    "provider_requested": "hash|ollama|emergent",
    "provider_used": "hash|ollama|emergent",
    "model": "atlas-hash-v1|nomic-embed-text|text-embedding-3-small",
    "fallback_reason": "string (optional)"
  }
}
```

### `graph_triples`
```jsonc
{
  "from_node": "string",
  "to_node": "string",
  "relation": "lowercase string",
  "source_id": "uuid4 (optional)",
  "weight": 1.5,                      // $inc on repeat
  "hits": 3,                          // $inc on repeat
  "updated_at": "ISO-8601 UTC"
}
// unique upsert key: (from_node, to_node, relation)
```

### `atlas_settings._id: "embedding_models"`
```jsonc
{
  "_id": "embedding_models",
  "ajani":   {"provider": "hash",    "model": "atlas-hash-v1"},
  "minerva": {"provider": "hash",    "model": "atlas-hash-v1"},
  "hermes":  {"provider": "ollama",  "model": "nomic-embed-text"},
  "council": {"provider": "hash",    "model": "atlas-hash-v1"}
}
```

---

## 7 · Test coverage

`pytest` file: `/app/backend/tests/test_membank_phase2.py`
Report: `/app/test_reports/iteration_11.json`

```
29 / 29 PASSED in 99s
─ store / search / list / reinforce / delete / categories       8 cases
─ user + research shortcut endpoints                            4 cases
─ graph triples (upsert / list / around BFS)                    5 cases
─ embed-settings GET/PUT, invalid-provider rejection            3 cases
─ category filter on search + list                              2 cases
─ freshness decay + min_score filter                            2 cases
─ wiring: intake → lesson + project + intake memories           1 case
─ wiring: council → permanent council memory                    1 case
─ wiring: blueprint → permanent blueprint memory                1 case
─ score formula validation (0.85·sim + 0.15·freshness)          1 case
─ BFS depth correctness                                         1 case
```

---

## 8 · Roadmap update

```
Phase 0 — Audit / Cleanup                  ✅ done
Phase 1 — Real LLM Integration             ✅ done
Phase 2 — Knowledge / Memory Bank          ✅ done  ← THIS PHASE
Phase 3 — Research Pipeline                ⏭ next
Phase 4 — Voice System & ATLAS HUD         ⏳ pending
Phase 5 — Digital Twin Engine              ⏳ pending (needs spec)
Phase 6 — Weaver Integration               ⏳ pending (needs spec)
Phase 7 — Robot Control Layer              ⏳ pending (needs hw spec)
```

---

## 9 · Recommended Phase 3 plan — Research Pipeline

Phase 3 turns ATLAS from a learner into a **researcher**. It should pull
external knowledge, distil it through the Hermes critic, and persist into
the `research` category of the Memory Bank we just shipped.

### 9.1 Surfaces to build
1. **Web research** — given a query, fetch top-N results, scrape page text,
   chunk + embed + summarise via Hermes (pattern hunter persona).
2. **PDF analysis** — accept an upload (`pypdf` is already in
   `requirements.txt`), extract per-page text, summarise + auto-tag.
3. **Patent analysis** — search USPTO / Google Patents API (free), pull
   claims + abstract, hand to Ajani (engineer persona) for build-feasibility
   commentary.

### 9.2 Backend surface
```
/app/backend/
├── services/
│   ├── research_pipeline.py            ← orchestrator (web/pdf/patent)
│   ├── web_scraper.py                  ← httpx + selectolax (lightweight)
│   ├── pdf_reader.py                   ← pypdf + chunker
│   └── patent_client.py                ← Google Patents / USPTO REST
└── routes/
    └── research.py
        ├── POST /api/research/web         { query, top_n=5 }
        ├── POST /api/research/pdf         multipart upload
        ├── POST /api/research/patent      { query }
        └── GET  /api/research/jobs/{id}   poll for async results
```

### 9.3 Memory wiring (already in place)
Every successful research artefact writes through `auto_store(category="research")`
with `source_type` ∈ {`web`, `pdf`, `patent`} and `source_id` = the artefact's UUID.
This is the **same path** the architect uses today via
`POST /api/membank/research` — Phase 3 just automates the call.

### 9.4 Deps to add (small, additive)
* `selectolax` — fast HTML extraction (≈4 MB)
* `tldextract` — domain normalisation for source provenance
* (`pypdf` and `httpx` are already installed)

### 9.5 Council integration
Long research jobs (>15s) should reuse the existing `useAtlasJob` polling
pattern (`/api/atlas/jobs/{id}` queue from Phase 0). New job-types added:
`research:web`, `research:pdf`, `research:patent`.

### 9.6 HUD surface
The OUTER world ring already has an **EXPLORE / INTAKE** tile —
extend its panel with two new tabs:
* "Web"   — query + top-N preview cards
* "PDF"   — drag-drop area + chunk summary
The "Patent" tab can ship later once the architect picks a patent provider.

> **Hard rule observed**: visuals untouched — new functionality goes inside
> the existing INTAKE panel; no new outer-ring tile, no geometry change.

### 9.7 Estimated effort
* Service layer + routes: ~3 hours
* Memory wiring: trivial (already in place)
* HUD tab additions inside IntakePanel: ~1.5 hours
* Tests (web with respx mocks + pdf with a fixture PDF): ~1 hour
* **Total: ~5-6 hours of agent work, single iteration.**

---

## 10 · Hand-off note for the next iteration

* Phase 2 is fully tested, lint-clean, and wired into the four upstream
  pipelines as described above.
* `services/memory_bank.py` is the single source of truth for any new
  memory writes — never insert directly into `memory_bank`; always go
  through `store_memory(...)` or `auto_store(...)`.
* When the architect says "go", proceed with Phase 3 §9 above. Begin by
  scaffolding `services/research_pipeline.py` and `routes/research.py`,
  then add the Web tab inside `IntakePanel.js` (HUD aesthetic preserved).
