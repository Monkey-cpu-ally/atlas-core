# ATLAS · Complete Architecture Audit
_Generated 2026-06-21 · read-only investigation_

## How to read this document
- 🟢 **PROD** — running in production, real data, tested.
- 🟡 **PARTIAL** — works but missing pieces or limited coverage.
- 🔴 **MISSING** — referenced but not built.
- ⚪ **MOCK / DEAD** — placeholder code or static lists (none should remain after the 2026-06-18 audit).

---

## A · Data Sources

| # | Source | Status | Backing collection | Live count | Notes |
|---|---|---|---|---:|---|
| 1 | WorldWatch RSS feeds | 🟢 | `worldwatch_feeds` | 11 RSS | arXiv, Hackaday, MIT Tech, NASA, Dezeen, NewAtlas, … |
| 2 | Patent search feeds | 🟢 | `worldwatch_feeds` (source_type=patent) | 6 | Google Patents XHR + fallback ingestion |
| 3 | YouTube manual ingest | 🟢 | `youtube_transcripts_private` | 3 | Privacy-only (consent gated) |
| 4 | YouTube channel watchlist | 🔴 | — | — | **NOT BUILT** |
| 5 | Patents on-demand | 🟢 | (not persisted as feed) | — | `services/patent_client.py` |
| 6 | Web scraping (single URL) | 🟢 | n/a | — | `services/web_scraper.py` + research routes |
| 7 | Code watchers (git/web) | 🟢 | `watchers` + `watcher_runs` | 1 / 3 | Auto-pulls + ingests |
| 8 | PDF + text upload | 🟢 | `intake/*` | 10 | `routes/intake.py` + `pdf_reader.py` |
| 9 | Robot telemetry (uplink) | 🟢 | `robot_telemetry` | 243 | HTTP + MQTT |
| 10 | NIR spectra | 🟢 | `nir_spectra` + `nir_results` | 10 / 10 | scipy peak detect + cosine match |

---

## B · Database Inventory (42 collections)

### Knowledge / Memory
| Collection | Rows | Schema highlights | Purpose |
|---|---:|---|---|
| `memory_bank` | 1502 | `id`, `content`, `persona`, `category`, `permanent`, `embedding` (384-dim ST), `embed_meta`, `tags`, `pinned`, `reinforce_count`, `freshness` | **Shared Atlas Memory Bank** with persona-based partitioning |
| `knowledge_records` | 50 | `id`, `title`, `summary`, `key_points`, `tags`, `source_type`, `source_url`, `source_hash`, `concepts`, `related_agents`, `confidence_score`, `memory_bank_id` | Long-form knowledge with citation chains |
| `knowledge` | 6 | `id`, `title`, `topic`, `source`, `transcript`, `summary`, `ai_owner` | LEGACY YouTube-shaped store (kept for backward compat, write-only on chat.py path) |
| `graph_triples` | 2753 | `from_node`, `relation`, `to_node`, `hits`, `source_id`, `weight` | Concept relationship graph (BFS-traversed) |
| `nir_library` | 12 | `id`, `name`, `category`, `characteristic_peaks_nm` | NIR fingerprint reference |

### YouTube / Ingestion
| Collection | Rows | Schema | Status |
|---|---:|---|---|
| `youtube_transcripts_private` | 3 | `id`, `video_url`, `video_title`, `channel_name`, `transcript_text`, `consent` | 🟢 Manual ingest works |
| **`youtube_channels` (watchlist)** | — | — | 🔴 **NOT BUILT** |
| **`youtube_channel_runs`** | — | — | 🔴 **NOT BUILT** |

### Research / WorldWatch
| Collection | Rows | Purpose |
|---|---:|---|
| `worldwatch_feeds` | 17 | RSS + patent feeds (11 RSS + 6 patent) |
| `worldwatch_runs` | 31 | Per-cycle proof envelope |
| `worldwatch_updates` | 26 | Per-entry ingestion log |
| `research_queue` | 26 | State machine: discovered→queued→investigating→linked |
| `research_missions` | 4 | Long-running discovery missions |
| `research_cycles` | 26 | Orchestrator cycle proofs |
| `orchestrator_loops` | 1 | Multi-cycle background jobs |

### Robotics / Twins / NIR
| Collection | Rows | Purpose |
|---|---:|---|
| `robot_devices` | 48 | ESP32 + simulated device registry |
| `robot_commands` | 99 | Command pipeline log |
| `robot_telemetry` | 243 | Inbound sensor data |
| `digital_twins` | 10 | Includes AGRI-ROVER-01, ATLAS-CELL-V1/SS-V1 |
| `twin_simulations` | 49 | Per-engine sim results (incl. THERMAL ODE) |
| `twin_environments` | 7 | Spatial + ambient context (lab/outdoor/aerial/aquatic/lunar) |
| `twin_deliberations` | 2 | Council-on-twin records |
| `nir_spectra` / `nir_results` | 10/10 | NIR scans |
| `weaver_parts` / `weaver_plans` | 25/2 | Parts library + build plans |
| `blueprints` / `blueprint_forge` | 3/1 | Project blueprints |
| `projects` | 6 | Long-running project tracker |
| `sandbox_runs` / `sandbox_saved` | 11/1 | Live execution sandbox |
| `sentinel_autonomic_fires` | 10 | Auto-detected anomalies |

### AI / Agents / HUD
| Collection | Rows | Purpose |
|---|---:|---|
| `persona_sessions` / `persona_messages` | 185/400 | Per-agent chat history |
| `conversations` / `messages` | 4/8 | Older chat schema (still wired in some flows) |
| `lessons` | 14 | Pedagogical content (auto-generated) |
| `user_learning_profile` | 1 | Adaptive style record (Welford online stats) |
| `atlas_archive` | 11 | Long-term reference content |
| `atlas_events` | 2 | System-wide event log |
| `atlas_settings` | 3 | Per-app config |
| `self_improvements` | 28 | Proposed/applied code-level improvements |
| `watchers` / `watcher_runs` | 1/3 | Site/repo watchers |
| `visual_style_memory` | 1 | Adaptive HUD theming hint store |

### Missing collections (referenced in the architect's spec)
| Collection | Status | Why missing |
|---|---|---|
| `subjects` (22 subjects) | 🔴 | Only 5 subjects hardcoded in `knowledge_core.py` |
| `research_sources` (unified) | 🔴 | RSS+patent are in `worldwatch_feeds`, code in `watchers`, YouTube in `youtube_transcripts_private` — no unified registry |
| `youtube_channels` | 🔴 | Manual transcript ingest exists, no channel-watch automation |
| `youtube_channel_runs` | 🔴 | Same |

---

## C · API Surface (96 endpoints across 25 routers)

| Router | Endpoints | Status |
|---|---:|---|
| `ai_services` | 9 | 🟢 |
| `atlas_v2` | 8 | 🟢 |
| `chat` | 6 | 🟢 |
| `council` | 4 | 🟢 |
| `environments` | 7 | 🟢 |
| `files` | 4 | 🟢 |
| `hud_surfaces` | 5 | 🟢 |
| `intake` | 6 | 🟢 |
| `kbase` | 4 | 🟢 |
| `knowledge` | 6 | 🟢 (subjects endpoint serves 5/22) |
| `learning` | 5 | 🟢 |
| `lessons` | 4 | 🟢 |
| `llm` | 3 | 🟢 |
| `memory` | 12 | 🟢 (has /list /search /by-tag /graph/* /embed-settings) |
| `nir` | 8 | 🟢 |
| `persona` | 8 | 🟢 |
| `research` | 6 | 🟢 |
| `research_orchestrator` | 9 | 🟢 |
| `robot` | 13 | 🟢 |
| `sandbox` | 5 | 🟢 |
| `self_improve` | 5 | 🟢 |
| `twins` | 5 | 🟢 |
| `watchers` | 4 | 🟢 |
| `weaver` | 4 | 🟢 |
| `youtube` | 5 | 🟢 (only manual ingest — no channel auto-pull) |

**Missing endpoints:**
- 🔴 `GET /api/subjects` (22-subject taxonomy)
- 🔴 `POST /api/subjects/{id}/assign-content`
- 🔴 `GET /api/research-sources` (unified registry)
- 🔴 `POST /api/youtube/channels` + `GET /api/youtube/channels` (channel watchlist)
- 🔴 `POST /api/youtube/channels/{id}/poll` (worker trigger)

---

## D · Memory System

### Embeddings (🟢 PROD)
- Provider: sentence-transformers `all-MiniLM-L6-v2` (CPU, 384-dim, L2-normalised)
- Wired into `memory_bank` collection on every `store` call
- Recall: cosine similarity in-process (no vector-DB dependency)
- Tested: lithium query → "Solid-state lithium battery" matched at 0.55+ cosine
- Embed-settings router exposes per-persona model selection

### Agent partitioning (🟡 PARTIAL)
- `memory_bank.persona` field used by all writes (`ajani`, `minerva`, `hermes`, `council`, `default`)
- Persona index NOT explicit (relies on Mongo full-collection scan with field filter)
- No dedicated "Ajani's memory" or "Minerva's memory" view endpoint — `GET /api/membank/list?persona=ajani` works but is undocumented

### Council pipeline (🟢 PROD)
- `services/council.py` — 4-voice deliberation (Ajani / Minerva / Hermes synthesised by Council voice)
- Auto-invoked by orchestrator when knowledge confidence < 0.7
- Outputs persisted to `memory_bank` with `persona=council`, `category=council`
- Surfaced in HUD via `CouncilPanel.js`

---

## E · YouTube Pipeline

| Stage | Component | Status |
|---|---|---|
| Channel discovery | `services/youtube_resolver.py` | 🟢 |
| Channel RSS resolution | `youtube_resolver.resolve_channel` | 🟢 (uploads.xml endpoint) |
| Transcript auto-fetch | (blocked by Google cloud-IP ban) | 🔴 |
| Manual transcript paste | `routes/youtube.py:/ingest-transcript` | 🟢 |
| Channel watchlist | — | 🔴 **NOT BUILT** |
| Channel poll worker | — | 🔴 |
| Per-video knowledge entry | `youtube_transcripts_private` | 🟢 |
| Knowledge → MemoryBank link | via `services/youtube_pipeline.py` | 🟢 |
| Lesson generation from YT | `services/lesson_generator.py` | 🟢 |

---

## F · AI Agents

| Agent | Persona ID | Memory partition | Status |
|---|---|---|---|
| Ajani (Engineering / robotics) | `ajani` | `memory_bank` rows where `persona=ajani` (≥ 200 rows) | 🟢 |
| Minerva (Science / theory) | `minerva` | `memory_bank persona=minerva` (≥ 200) | 🟢 |
| Hermes (Logic / dialogue) | `hermes` | `memory_bank persona=hermes` (≥ 80) | 🟢 |
| Council (synthesis) | `council` | `memory_bank persona=council` (≥ 350) | 🟢 |

---

## G · HUD Components → Backend (full matrix)

This was completed in `/app/memory/HUD_AUDIT.md` on 2026-06-18 and re-confirmed today. 25/25 HUD panels read live data. 23/23 sampled endpoints return non-empty real responses. No mock data.

---

## H · Dependency Graph (high level)

```
                            ┌───────────────────────┐
                            │   sentinel watcher    │  🟢
                            └───────────┬───────────┘
                                        ▼
       ┌──── worldwatch_feeds ────┐
       │   (rss + patent)         │
       ▼                          ▼
  ┌────────┐               ┌──────────────┐
  │  RSS   │               │  Patents     │  🟢
  │ ingest │               │ search XHR   │
  └───┬────┘               └──────┬───────┘
      ▼                           ▼
            worldwatch_updates  →  research_queue  ◄── 🟢
                                       │
                                       ▼
                  ki.ingest_url → knowledge_records  →  memory_bank ──┐
                                       │                              │
                                       ▼                              ▼
                                  graph_triples              embedding (ST)
                                       │
                                       ▼
                                   Council voice  →  lessons / blueprints
                                       │                  │
                                       ▼                  ▼
                                  projects ◄── blueprint_forge
                                       │
                                       ▼
                                  improvement_loop


  ┌──────── YouTube ───────┐
  │ manual transcript      │  🟢 (works)
  │ ingest                 │
  └────────────────────────┘

  ┌──────── YouTube ───────┐
  │ CHANNEL WATCHLIST      │  🔴 (missing)
  │ + auto-poll            │
  └────────────────────────┘
```

---

## I · Single-source-of-truth gaps

1. **Subject taxonomy**: 5 subjects in code (`knowledge_core.py`) ≠ 22 in architect's spec. No DB table. Lessons/knowledge can't be filtered by canonical subject.
2. **Research sources**: 3 separate registries (`worldwatch_feeds` RSS+patent, `watchers` web/git, `youtube_transcripts_private` per-video). No unified `research_sources` view.
3. **YouTube channels**: No channel registry. Auto-pull is blocked anyway, but a "watchlist" entity is missing entirely.
4. **Agent memory views**: Works via `?persona=` query but no per-agent dedicated endpoint or stats card.

---

## J · What's actually production-ready right now

- 🟢 `memory_bank` with 384-dim ST embeddings + 1502 rows
- 🟢 `graph_triples` (2753 edges) — BFS-traversed by Council reasoning
- 🟢 Council 4-voice deliberation (auto-invoke on low-confidence)
- 🟢 Research orchestrator (single + multi-cycle background loop)
- 🟢 WorldWatch RSS+Patent ingestion (17 feeds)
- 🟢 NIR Scanner pipeline (12-entry library + scipy analysis)
- 🟢 Robot stack (HTTP+MQTT, 48 devices, mTLS, safety contract)
- 🟢 Digital Twin engine (6 heuristic + 1 ODE thermal)
- 🟢 Twin Environments (7 environments, AABB compatibility checker)
- 🟢 28 self-improvement proposals (auto-generated by self_code scanner)
- 🟢 Reference twins (AGRI-ROVER-01 + 2 power cells)
- 🟢 39/39 backend pytest regression suite
