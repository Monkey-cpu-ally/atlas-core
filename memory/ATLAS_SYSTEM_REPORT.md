# ATLAS · System Report

> **Generated:** Feb 2026 · supersedes ARCHITECTURE-REPORT.md for executive overview
> **Owner-of-record:** the architect
> **Repo:** `/app` · **Stack:** FastAPI + Motor + MongoDB · React (CRA) + Luxury HUD reskin
> **Phases complete:** 0–7 + Knowledge Ingestion + Voice "Ingest <URL>" + Atlas Sentinel + Clear Safe State
> **Total tests passing:** 111/111 (most recent green run: `iteration_16.json` + 17/17 in `test_robot_clear_safe_state.py` + `test_robot_phase7.py`)

---

## 1 · Completed Phases

| # | Phase | Status | Headline artefact |
| --- | --- | --- | --- |
| 0 | Architecture Audit & Cleanup | ✅ | `AUDIT-REPORT.md`; `_legacy/`; clean route prefixes |
| 1 | Real LLM Integration | ✅ | `services/llm_provider.py` — Emergent / Ollama / LMStudio with per-persona overrides in `atlas_settings._id="persona_models"` |
| 2 | Memory Bank · Vector · Graph | ✅ | 11 categories (4 permanent · 7 decaying), hash embedding + reinforcement decay, graph triples |
| 3 | Research Pipeline | ✅ | Web (DuckDuckGo) · PDF (`pypdf`) · Patent (Google Patents) · auto-store into `research` category |
| 4 | Voice System & ATLAS HUD | ✅ | `useVoiceRecognition.js` (off / push-to-talk / wake-word) · `voiceCommands.js` (persona, tile, **ingest-url** intents) |
| 5 | Digital Twin Engine | ✅ | 6 simulator engines · twin registry · parallel council deliberation · auto-spawned project/research memories |
| 6 | Weaver (Build Planner) | ✅ | Blueprint → parts enrich → twin spawn → 4-sim sweep → build/manufacturing/failure plans → council |
| K | Knowledge Ingestion | ✅ | GitHub · YouTube · PDF · Web · Patent · Academic URLs → LLM distillation → dedup-by-URL → reinforce-on-revisit → graph triples |
| 7 | Robot Control Layer | ✅ | MQTT-style HTTP bridge · sim-first command pipeline · owner-locked actuators · seeds POSEIDON-BUOY · AETHER-STATION · SOIL-WATCH |
| 7a | Voice "Ingest <URL>" | ✅ | Voice → /api/kbase/ingest → Knowledge Bank → Memory Bank → Graph Memory closed loop |
| 7b | Atlas Sentinel | ✅ | Bottom HUD ribbon: WATER · AIR · SOIL live telemetry · click → popover · localStorage-persisted dismiss |
| 7c | Clear Safe State | ✅ | Owner-only release of SAFE_STATE · confirm=device-name · cannot bypass an active e-stop · twin + memory + command audit |

---

## 2 · Database Schemas

All collections live in `${DB_NAME}`. ID strategy: every doc carries a string `id` (uuid4 hex); MongoDB `_id` is opaque and never returned to clients.

### Core (Phases 0–2)
| Collection | Purpose | Indexed fields |
| --- | --- | --- |
| `atlas_settings` | Singleton-style configs (e.g. `persona_models`) keyed by `_id` (string slug) | `_id` |
| `memory_bank` | Phase-2 records: every persisted insight (research, project, council, weaver, robot…) | `id`, `category`, `persona`, `tags`, `created_at` |
| `graph_triples` | (subject, relation, object) edges sourced from MemoryBank + Knowledge ingestion | `id`, `subject`, `object`, `relation` |
| `knowledge` | Legacy 22-subject teaching index (predates the Knowledge Ingestion System) | `id`, `subject` |

### Research (Phase 3)
| Collection | Purpose |
| --- | --- |
| `web_results` | DuckDuckGo result snapshots (URL, text, fetched_at) |
| `patent_results` | Google-Patents scrape snapshots |
| `pdf_extractions` | per-PDF text + metadata (page count, chunk hashes) |

### Digital Twin (Phase 5)
| Collection | Purpose |
| --- | --- |
| `digital_twins` | `{id, name, category, state, hardware_binding?, safety_history?, updated_at, …}` |
| `twin_simulations` | Each simulator run: `{id, twin_id, kind, score, output, started_at}` |

### Weaver (Phase 6)
| Collection | Purpose |
| --- | --- |
| `weaver_parts` | Starter library (25 rows seeded) + ingested parts |
| `weaver_plans` | One per blueprint parse: bom + manufacturing/build/failure plans |

### Knowledge Ingestion
| Collection | Purpose |
| --- | --- |
| `knowledge_records` | Distilled `KnowledgeRecord` per source URL (dedup-by-`sha256(normalised_url)`) |

### Robot Control (Phase 7)
| Collection | Purpose |
| --- | --- |
| `robot_devices` | Device registry with status, twin binding, hardware profile |
| `robot_telemetry` | Append-only telemetry stream (decaying — also mirrored into Memory Bank) |
| `robot_commands` | Every issued Command + its full pipeline_log |

---

## 3 · API Surface

All routes are prefixed `/api/…` (Kubernetes ingress routes `/api/*` → backend:8001).

### Memory Bank
```
POST   /api/membank/store
GET    /api/membank/search?q=&category=&limit=
GET    /api/membank/by-tag?tag=
POST   /api/membank/reinforce/{id}
GET    /api/membank/graph/triples?subject=&relation=
POST   /api/membank/graph/triple
DELETE /api/membank/{id}
```

### Research
```
POST   /api/research/web      { query, limit }
POST   /api/research/pdf      { url | base64, name? }
POST   /api/research/patent   { query, limit }
```

### Digital Twin
```
POST   /api/twins/register      { name, category, state }
GET    /api/twins/list
GET    /api/twins/categories
GET    /api/twins/{id}
PUT    /api/twins/{id}/state
DELETE /api/twins/{id}
POST   /api/twins/{id}/simulate     { kind }
GET    /api/twins/{id}/simulations
POST   /api/twins/deliberate        { twin_id, agents[] }
GET    /api/twins/simulations/{sim_id}
```

### Weaver
```
POST   /api/weaver/plan           { blueprint, options? }
GET    /api/weaver/plans
GET    /api/weaver/plans/{id}
GET    /api/weaver/parts          ?q=&category=
POST   /api/weaver/parts          (owner only)
```

### Knowledge Ingestion
```
POST   /api/kbase/ingest          { url, project_id?, force_agent?, extra_tags? }
GET    /api/kbase/search?q=&tag=
GET    /api/kbase/by-url?url=
GET    /api/kbase/classify?url=
GET    /api/kbase/agents/route?text=
GET    /api/kbase/{id}
DELETE /api/kbase/{id}
```

### Robot Control (Phase 7)
```
GET    /api/robot/roles                              → enum + owner_only_commands
POST   /api/robot/seed                               → idempotent re-seed
GET    /api/robot/devices                            ?status=&kind=&limit=
POST   /api/robot/devices                            X-Atlas-Role: owner
GET    /api/robot/devices/{id}
POST   /api/robot/devices/{id}/bind-twin             owner; { twin_id }
POST   /api/robot/devices/{id}/telemetry             device push (no role)
GET    /api/robot/devices/{id}/telemetry             ?limit=
POST   /api/robot/devices/{id}/command               X-Atlas-Role: <role>; { kind, payload }
GET    /api/robot/devices/{id}/commands              ?limit=
GET    /api/robot/devices/{id}/commands/inbox        device-side poll (delivered-once)
GET    /api/robot/commands/{id}
POST   /api/robot/devices/{id}/emergency-stop        owner
POST   /api/robot/devices/{id}/clear-safe-state      owner; { confirm: <device_name> }
```

### LLM Provider
```
POST   /api/llm/complete         { messages, persona?, model? }
GET    /api/llm/personas
POST   /api/llm/persona-model    { persona, model }   (admin)
```

---

## 4 · Memory Schemas

### `MemoryRecord` (collection: `memory_bank`)
```python
class MemoryRecord(BaseModel):
    id: str                          # uuid4 hex
    content: str                     # human-readable insight
    category: MemoryCategory         # see enum below
    persona: str                     # ajani | minerva | hermes | council | system | research
    source_type: str                 # robot_command | robot_telemetry | research | weaver_plan | …
    source_id: Optional[str]         # FK into the originating collection
    tags: List[str]
    embedding: List[float]           # 128-dim by default (hash); Ollama/Emergent optional
    confidence: float                # 0.0–1.0
    reinforce_count: int = 0
    last_reinforced_at: Optional[datetime]
    created_at: datetime
```

### `MemoryCategory`
| Category | Decay | Notes |
| --- | --- | --- |
| `system` | **permanent** | Boot config, persona model overrides |
| `project` | **permanent** | Anything tied to a `project_id` (weaver, twin, robot) |
| `council` | **permanent** | Safety actions: emergency_stop · clear_safe_state · deliberations |
| `agent`  | **permanent** | Agent-personal long-term lessons |
| `research` | decaying | Web/PDF/patent/youtube/github; reinforce on revisit |
| `telemetry` | decaying | Robot telemetry bursts |
| `chat` | decaying | Per-session conversation history |
| `weaver_draft` | decaying | Plan intermediates pre-publish |
| `twin_state` | decaying | Twin state revisions |
| `simulation` | decaying | Simulator outputs |
| `ephemeral` | decaying (fast) | Scratch space; reaped weekly |

### `GraphTriple` (collection: `graph_triples`)
```python
class GraphTriple(BaseModel):
    id: str
    subject: str          # canonical concept slug
    relation: str         # relates_to | implements | depends_on | belongs_to_project | owned_by_agent | …
    object: str           # concept | tag | project_id | persona name
    weight: float = 1.0   # Hebbian-style — incremented on revisit
    source_memory_id: Optional[str]
    created_at: datetime
```

---

## 5 · Knowledge Schemas

### `KnowledgeRecord` (collection: `knowledge_records`)
```python
class KnowledgeRecord(BaseModel):
    id: str
    title: str
    summary: str                       # 2-4 sentence persona-voiced distillation
    key_points: List[str]              # 3-8 bullets
    concepts: List[str]                # canonical slugs for graph wiring
    tags: List[str]
    source_url: str
    source_hash: str                   # sha256(normalised_url) — dedup key
    source_type: SourceType            # github | youtube | pdf | web | patent | academic
    source_author: Optional[str]
    confidence_score: float            # 0.0–1.0 (LLM self-rated)
    related_agents: List[str]          # ajani | minerva | hermes | council
    related_projects: List[str]
    memory_bank_id: str                # FK into memory_bank (every record is also a MemoryRecord)
    reinforce_count: int = 0
    created_at: datetime
    last_reinforced_at: Optional[datetime]
```

### `IngestRequest`
```python
class IngestRequest(BaseModel):
    url: str
    project_id: Optional[str]          # if set → MemoryCategory.PROJECT (permanent)
    force_agent: Optional[str]         # bypass keyword router
    extra_tags: List[str] = []
```

---

## 6 · Research Pipeline Flow

```
                 ┌────────────────────────┐
                 │   POST /api/research/* │
                 │   or /api/kbase/ingest │
                 └────────────┬───────────┘
                              ▼
            ┌────────────────────────────────┐
            │    Source dispatcher           │
            │    services/source_fetchers.py │
            └─────┬───────┬────────┬─────────┘
                  │       │        │
   ┌──────────────┘   ┌───┘    ┌───┴──────────┐
   ▼                  ▼        ▼              ▼
GitHub API     YouTube       PDF (pypdf)    Web/Patent/Academic
(no token)     transcript    blob or URL    scraper
   │                  │        │              │
   └──────────────────┴────────┴──────────────┘
                              │ raw text + metadata
                              ▼
            ┌────────────────────────────────┐
            │  knowledge_distiller.py        │
            │  • keyword-density agent route │
            │  • persona-voiced LLM call     │
            │  • strict JSON schema          │
            │  • anti-copyright system prompt│
            └────────────┬───────────────────┘
                         │ Distillation(summary, key_points, …)
                         ▼
            ┌────────────────────────────────┐
            │ knowledge_ingestion.py          │
            │  dedup by sha256(url) →         │
            │  reinforce OR persist new       │
            │  + graph triple wiring          │
            └────────────┬───────────────────┘
                         ▼
                ┌────────────────────┐
                │  knowledge_records │
                │  + memory_bank     │
                │  + graph_triples   │
                └────────────────────┘
```

---

## 7 · Digital Twin Flow

```
   POST /api/twins/register       ┌──────────────────┐
   ───────────────────────────►   │  digital_twins   │  twin doc {id, state, …}
                                  └─────────┬────────┘
                                            ▼
                          PUT /api/twins/{id}/state
                          (or auto-patch from Phase 7 bind-twin /
                           clear-safe-state)
                                            │
                                            ▼
                          POST /api/twins/{id}/simulate
                          (kind ∈ MECHANICAL | THERMAL | ELECTRICAL |
                                  CHEMICAL | OPTICAL | FAILURE)
                                            │
                          ┌─────────────────┴─────────────────┐
                          ▼                                   ▼
                   twin_simulator.py                    persist
                   (6 engines)                          twin_simulations
                          │                                   │
                          ▼                                   ▼
                   sim.score, sim.output                 mb.auto_store(category=simulation)
                                            │
                                            ▼
                          POST /api/twins/deliberate
                          (agents in parallel: ajani / minerva / hermes /
                           council) — produces a `consensus` MemoryRecord
                           in category=council (permanent)
```

Phase 6 (Weaver) and Phase 7 (Robot Control) both consume this surface — Weaver to score blueprints, Robot Control to validate every actuator command before execution.

---

## 8 · Weaver Flow

```
POST /api/weaver/plan { blueprint } 
   ↓
blueprint_parser.py  →  parts list (each enriched against `weaver_parts`)
   ↓
parts_db.py          →  cost · vendor · lead-time enrichment (25-row starter library)
   ↓
weaver.py            →  spawns a Digital Twin (category=manufacturing)
   ↓
4 simulator passes   →  mechanical · thermal · failure · cost-sensitivity
   ↓
plan synthesis       →  build_plan · manufacturing_plan · failure_plan
   ↓
(optional)           →  /api/twins/deliberate for council sign-off
   ↓
persist              →  weaver_plans + mb.auto_store(category=project)
```

---

## 9 · Robot Control Flow

```
            POST /api/robot/devices/{id}/command
            { kind, payload }   header: X-Atlas-Role
                       │
                       ▼
   ┌────────────────────────────────────────────┐
   │ 1. authorise(role, kind)                    │
   │    OWNER_ONLY = {actuate, motion, bind_twin,│
   │     firmware_update, clear_safe_state}      │
   │    → REJECT on miss                         │
   └────────────────────┬───────────────────────┘
                       ▼
   ┌────────────────────────────────────────────┐
   │ 2. device_lookup → REJECT if not found     │
   │    REJECT if device.status == SAFE_STATE   │
   │    AND kind ∉ {ping, emergency_stop}       │
   │    ↑↑ — Emergency Stop remains highest     │
   │       priority gate, even above clear      │
   └────────────────────┬───────────────────────┘
                       ▼
   ┌────────────────────────────────────────────┐
   │ 3. simulate via Phase-5 twin (FAILURE kind)│
   │    skipped for ping/read_telemetry         │
   │    cmd.sim_score = sim.score               │
   └────────────────────┬───────────────────────┘
                       ▼
   ┌────────────────────────────────────────────┐
   │ 4. validate (sim_score ≥ 0.50)              │
   │    → REJECT with reason on fail            │
   └────────────────────┬───────────────────────┘
                       ▼
   ┌────────────────────────────────────────────┐
   │ 5. execute → publish to MQTT-style HTTP    │
   │    inbox (device polls /commands/inbox)    │
   │    side-effect: emergency_stop flips device│
   │    side-effect: clear_safe_state patches   │
   │      twin.state.safety_history + flips     │
   │      device back to REGISTERED             │
   └────────────────────┬───────────────────────┘
                       ▼
   ┌────────────────────────────────────────────┐
   │ 6. log: insert robot_commands +             │
   │    mb.auto_store(category=council|project) │
   └────────────────────────────────────────────┘
```

### Safety state machine
```
                            ┌──────────────┐
                  register  │ REGISTERED   │
                ───────────►│              │
                            └──┬────────▲──┘
                  telemetry    │        │  clear_safe_state
                               ▼        │  (owner + confirm + must be in SAFE)
                            ┌──────────────┐
                            │   ONLINE     │
                            └──┬───────────┘
                  emergency_   │
                  stop (owner) │
                               ▼
                            ┌──────────────┐
                            │  SAFE_STATE  │   ← Emergency Stop remains
                            └──────────────┘     highest priority
```

Three architect-spec seed devices come up on first boot, each auto-bound to an `ENVIRONMENT` Digital Twin:

| Device | Sensors | Twin |
| --- | --- | --- |
| POSEIDON-BUOY | water_temperature, ph, turbidity | POSEIDON-BUOY twin |
| AETHER-STATION | co2, pm2_5, voc, temperature | AETHER-STATION twin |
| SOIL-WATCH | soil_moisture, soil_temperature, nutrient_level | SOIL-WATCH twin |

The HUD surfaces them via the **Atlas Sentinel** bottom ribbon (live polling every 12s) and the **Robot Control** panel inside the SYSTEMS tile.

---

## 10 · Remaining Work

### P1 — Recommended next
- **MQTT broker** — slot a real `paho-mqtt` adapter into `_publish_command()`; HTTP-poll remains the fallback.
- **Sentinel → Twin drill-down** — click a Sentinel chip → auto-load that device's Twin + most-recent simulations in the SYSTEMS panel.
- **Clear-safe-state UI confirmation modal** — replace the browser-native `window.confirm` with the same Luxury-HUD modal style used elsewhere.

### P2 — Polish
- `/api/robot/devices/{id}` PATCH for tag/notes edits (currently registration is the only write).
- Bulk seed loader for ESP32/Pi hardware profiles (currently 5 kinds in the enum, 3 seeded).
- WebSocket telemetry channel (the HUD currently polls).

### P3 — Hardening
- JWT auth in place of `X-Atlas-Role` once the deployment leaves local LAN.
- Per-device rate limiter (currently no throttle on telemetry intake).
- Outbox-pattern for command publish (current in-memory `delivered` flag is sufficient for one Atlas instance, won't scale across replicas).

---

## 11 · Known Limitations

| Area | Limitation | Mitigation |
| --- | --- | --- |
| **ElevenLabs TTS** | Free tier blocks the cloud container IP | Fallback to OpenAI TTS via `emergentintegrations` is wired and reliable |
| **YouTube transcript API** | Native YT cloud-IP block | Endpoint returns 503 with a clear message; user can rerun from a residential proxy |
| **Auth** | `X-Atlas-Role` is a soft header gate (local LAN only) | JWT migration is a 1-day swap once needed |
| **Vector search** | Default hash embedding (128-dim) is identity-poor — keyword search outranks it for short queries | Set `ATLAS_EMBED_PROVIDER=ollama` (or `emergent`) to upgrade |
| **Concurrency** | Single FastAPI worker, single MongoDB | Move to gunicorn + replica set if the architect wants > 1 rps sustained |
| **Robot bridge** | HTTP-poll (devices GET `/commands/inbox`) — latency ≈ poll-interval / 2 | Drop in `paho-mqtt` when a broker is available |
| **Clear safe state** | No automatic "after N minutes" auto-clear — by design (operator must explicitly release) | None — this is the safety contract |
| **Memory Bank search** | Some Phase-7 entries (council/permanent) score below the default similarity threshold | Lower threshold via `?score=0.1` or query by tag (`/api/membank/by-tag?tag=clear_safe_state`) |

---

## 12 · Recommended Phase 8 Roadmap

### Theme: **Real-world deployment + autonomy**

```
                                    Phase 8
                              "Hardware Reality"
                                       │
       ┌───────────────────────────────┼───────────────────────────────┐
       ▼                               ▼                               ▼
   8A: Field MQTT              8B: Atlas Voice 2          8C: Autonomous Council
   - paho-mqtt broker           - Wake-word offline       - Council deliberation
   - Real ESP32 firmware          (Whisper.cpp local)       triggers on telemetry
     reference impl             - TTS persona voices         anomalies
   - mTLS device certs          - Streaming STT/TTS       - Auto-fire E-STOP on
   - OTA firmware update          via WebSocket             agreed-safe-violation
   - Topic-level ACL            - Multi-turn context       - Owner override flow

       ▼                               ▼                               ▼
       └───────────────────────────────┼───────────────────────────────┘
                                       ▼
                              Phase 8 deliverables:
                              • Real outdoor POSEIDON-BUOY (water sensor)
                              • Real outdoor AETHER-STATION (air sensor)
                              • Real outdoor SOIL-WATCH (soil sensor)
                              • Atlas can ingest knowledge, plan a build,
                                manufacture, deploy, and respond — by voice
```

### Concrete v1 milestones
1. **`paho-mqtt` adapter** — replace HTTP poll; keep the public REST surface unchanged.
2. **ESP32 reference firmware** — minimal C++ sketch that posts telemetry + polls inbox + obeys SAFE_STATE.
3. **Local STT/TTS** — `whisper.cpp` + Coqui-TTS pinned per persona, behind an LMStudio-style local provider so Emergent LLM key stays optional.
4. **Anomaly-triggered council** — a cron-like watcher on `robot_telemetry` that spawns a `/api/twins/deliberate` when readings exceed a learned envelope.
5. **mTLS device certs** — paired-key issuance during `POST /api/robot/devices`.
6. **OTA firmware** — new owner-only command `firmware_update` with explicit `confirm=` (same anti-fat-finger pattern as clear-safe-state).
7. **Field deployment** — one of each seed device wired up at the architect's chosen site.

### Optional adjuncts (parallel tracks)
- **Atlas Sentinel v2** — historical chart popovers (sparklines) instead of last-value text.
- **Knowledge Bank UI** — Cyclopedia panel currently shows the seed teaching subjects; surface the ingested URL records too.
- **Council reasoning transparency** — show the per-agent vote chain when a council action fires.

---

## Appendix · File index for Phase 7

| File | Role |
| --- | --- |
| `backend/models/robot_models.py` | Pydantic enums + `Device`, `Command`, `TelemetryRecord`, `HardwareProfile`. `CommandKind.CLEAR_SAFE_STATE` (owner-only) added Feb 2026. |
| `backend/services/robot.py` | Registry · telemetry · sim-first pipeline · `emergency_stop` · `clear_safe_state` · `seed_if_needed` |
| `backend/routes/robot.py` | REST surface under `/api/robot/*`; `clear-safe-state` endpoint added Feb 2026. |
| `backend/tests/test_robot_phase7.py` | 10/10 — original Phase 7 spec |
| `backend/tests/test_robot_membank_wiring.py` | 3/3 — Phase-2 memory wiring |
| `backend/tests/test_robot_clear_safe_state.py` | 7/7 — clear safe state hard-guarantees |
| `backend/tests/test_iter16_voice_ingest_sentinel.py` | 4/4 — voice ingest + Sentinel + permissions |
| `frontend/src/components/HUD/RobotPanel.js` | Inside SYSTEMS tile · PING / ACTUATE / E-STOP / **CLEAR SAFE STATE** |
| `frontend/src/components/HUD/AtlasSentinel.js` | Optional bottom ribbon · WATER · AIR · SOIL |
| `frontend/src/utils/voiceCommands.js` | `ingest-url` intent + persona/tile aliases |
| `frontend/src/components/HUDInterface.js` | `executeVoiceIntent` ingest-url branch + Sentinel mount |

---

_End of report. For per-phase deep dives see `PHASE2-REPORT.md`, `PHASE3-4-REPORT.md`, `PHASE5-REPORT.md`, `PHASE6-REPORT.md`, `PHASE7-REPORT.md`, `KNOWLEDGE-INGESTION-REPORT.md`._
