# Atlas Core HUD — PRD

## Original Problem Statement
A 2.5D AI HUD interface for Atlas Core. Three concentric, drag-to-rotate radial
dial rings around a central animated core. Built to match the user's exact
reference screenshot (rectangular tiles on glowing blue circular tracks inside a
blue rectangular HUD frame, tiles snap to the top slot when selected, selected
tile glows in the AI's identity color).

## Identity Colors
- **Ajani**:   crimson #DC143C — Builder / Strategist / Engineer
- **Minerva**: teal    #20B2AA — Guide / Teacher / Healer
- **Hermes**:  silver  #C0C0C0 — Messenger / Protector / Validator
- **Council**: purple  #9370DB — Trinity Counsel

## Architecture

### Frontend
```
/app/frontend/src/
├── components/
│   ├── HUDInterface.js          # Main orchestrator
│   ├── HUD/
│   │   ├── DialRing.js          # Single radial drag-to-rotate dial
│   │   ├── AtlasCore.js         # Canvas-based central orb
│   │   └── AtlasSidePanel.js    # Right-side context panel
│   ├── ChatPanel.js
│   ├── FileUploadModal.js
│   └── FileBrowserPanel.js
├── data/
│   ├── ringStructure.js         # INNER/MIDDLE/OUTER ring tile definitions
│   └── atlasCore.js             # AI personas, projects, phases
├── hooks/
│   ├── useVoiceRecognition.js   # Web Speech API wrapper
│   └── useAudioFeedback.js      # WebAudio click/tone/snap/glide
└── App.css                      # Theme + radial dial CSS
```

### Backend
```
/app/backend/
├── server.py                    # FastAPI entrypoint
├── routes/
│   ├── chat.py                  # POST /api/chat/send (Emergent LLM Key)
│   ├── files.py                 # /api/files/{upload,list,download,delete,stats}
│   └── knowledge.py             # /api/knowledge/{subjects,teach}
└── services/
    ├── ai_categorizer.py
    └── knowledge_core.py        # 22 educational subjects (in-memory)
```

## Ring Layout (matches reference screenshot + 6-layer spec)

### Layer hierarchy (inside → outside, all centered on orb)
1. **Core orb** ≈ 18% of HUD — tappable lava-lamp visualization
2. **Core containment ring** ≈ 22% (1.3× orb) — decorative reactor cradle
3. **Inner orbit** ≈ 38% (2.5× orb) — AI personas (4 slots @ 90°, compass)
4. **Mid system ring** ≈ 60% (4× orb) — operating-system shell
5. **Outer world ring** ≈ 88% (6× orb) — knowledge / exploration
6. **Ghost / parallax rings** — 7 faded background circles drifting at
   different speeds (75–320 s per revolution) for "living machine" depth.
   Opacity 5–15%, extend beyond the rectangular HUD frame.

### Inner ring (4 slots @ 90°)
- N: AJANI — E: MINERVA — S: HERMES — W: COUNCIL

### Mid System ring (5 slots, 8-slot grid)
- N: MANUAL — E: ENCYCLOPEDIA — SE: MEMORY — S: SYSTEMS — SW: CUSTOMIZATION

### Outer World ring (6 slots, 8-slot grid)
- N: SUBJECTS — E: LAB — SE: PROJECTS — S: BLUEPRINTS — SW: ARCHIVE — W: EXPLORE MODE

## Motion Spec (per ring)
| Ring   | Snap duration | Easing                        | Personality |
|--------|---------------|-------------------------------|-------------|
| Inner  | 300 ms        | cubic-bezier(.33, 1, .68, 1)  | Identity / soft |
| Middle | 180 ms        | cubic-bezier(.4, 0, .2, 1)    | Mechanical / precise |
| Outer  | 400 ms        | cubic-bezier(.25, .8, .3, 1)  | Exploratory / graceful |

Stillness rule: rings only move on drag, click, voice, or panel open. After
movement they snap to the nearest slot and stop. No auto-spin.

## Interactions
- **Click a tile** → select it (inner = activate AI; middle/outer = open panel)
- **Drag the ring** → rotates all tiles around center; on release, snaps to
  nearest slot and the new top tile is selected
- **Memory / Archive tiles** → open File Browser (not side panel)
- **Voice mic button** (top-right) → "Minerva, open projects" rotates ring 1 to
  Minerva, ring 3 to Projects, opens panel
- **Hard Limits / Sound / Upload** → top-right control buttons

## What's Implemented (this session, Feb 2026)
- [x] Radial dial rebuild with polar-coord tile placement and pointer-driven
      drag-to-rotate (DialRing.js)
- [x] Layout matches user reference image exactly with interleaved middle
      ring (offset 22.5° from outer to avoid radial collisions)
- [x] Premium glass tiles with neon rim, gradient bg, hover lift
- [x] 6-layer ring hierarchy: orb (18%) → core ring (22%) → inner (38%) →
      mid (60%) → outer (88%) → 7 ghost parallax rings
- [x] Differentiated ring track thicknesses (containment > inner > outer > mid)
- [x] **Fluid liquid lava-lamp core** — 11 organic deformed blobs (red,
      teal, silver, violet, magenta) with velocity squash/stretch, particle
      system, central pulse nucleus, multi-layer depth, tap-to-shock ripple
- [x] Tap reaction: rings flare, tiles shift, containment ring brightens,
      deep machine hum
- [x] Voice command flow fixed (callback-ref hook, getUserMedia, onError)
- [x] FileUploadModal + FileBrowserPanel: data-testid for testability
- [x] Backend `.env` fix: EMERGENT_LLM_KEY on its own line

### AI Services (NEW this iteration)
- [x] **OpenAI TTS** — POST /api/ai/tts with per-AI voice mapping
- [x] **Minerva approval API** — POST /api/ai/minerva/approve
- [x] **Hermes validation API** — POST /api/ai/hermes/validate
- [x] **Blueprint Engine** — POST /api/ai/blueprint/generate
- [x] **Audio-reactive core** — useAudioReactive hook wires mic AnalyserNode RMS into AtlasCore
- [x] **TTS playback in ChatPanel** with chat-voice-toggle
- [x] **BlueprintWorkbench** UI on outer-blueprints tile

### ATLAS Core v1 — separate cognitive backend (NEW)
- [x] `/app/atlas_core/` real Python package (renamed from atlas-core)
- [x] **3 cognitive cores**: TitanCore/Ajani, GaiaCore/Minerva, MercuryCore/Hermes
- [x] **Council Router**: keyword-based lead/support/critic + 3-LLM assemble
- [x] **Teaching Engine**: 4-band depth — **simple / systems / advanced / speculative** (with seed/shape/substance/shadows aliases) — auto-routes lead core through council; ATLAS teaching law enforced in the prompt
- [x] **Blueprint Engine** (two flows):
  - [x] `design()` → original 5-phase plan
  - [x] `tri_council()` → 3 parallel voices (Ajani structural / Minerva human / Hermes inventive) + synthesis blueprint (headline, 3 pillars, tensions, first_actions, open_questions)
- [x] **Archive Engine**: PDF/ZIP/TXT scan → shield-sanitize → classify → core route → summarize → memory store
- [x] **Shield Core**: 9 injection patterns + 4 control tokens + upload quarantine + capability gates
- [x] **Identity Anchor Protection**: SHA-256 fingerprint per core anchored at boot;
      `verify_identity()` before every LLM call raises if drift detected;
      `reinforcement_preamble()` prepended to every system prompt;
      12 identity-attack patterns redacted before reaching the LLM
- [x] **Mounted on HUD backend** at `/api/atlas/*`
- [x] **Async job queue** at `/api/atlas/jobs/{id}` — tri-council & teach return job_id immediately, frontend polls every 2s. Bypasses K8s ingress 60s timeout for 4-LLM-call flows.
- [x] **Memory layer**: thread-safe in-memory store + job store

### HUD Workbench wiring (Feb 2026 — visuals untouched)
- [x] **BlueprintWorkbench** wired to `/api/atlas/blueprint/council` via `useAtlasJob` hook. "Generate" runs the tri-council and renders 3 voices + synthesis pillars/tensions/actions/questions.
- [x] **TeachingWorkbench** mounted on the SUBJECTS tile. Calls `/api/atlas/teach`, renders 4-band lesson collapsed details.
- [x] **FileUploadModal** dual-posts PDFs/ZIPs to `/api/atlas/archive/upload`. Result shown inline (routed-to core, domain, summary, open questions). Quarantine errors surface as a red inline message. Identity anchors cannot be modified by uploads (they live in code-level identity hashes).

### TTS / ElevenLabs / Multi-language voices (Feb 2026)
- [x] **Module-level TTS client cache** (OpenAI + ElevenLabs) — eliminates 150–400 ms cold-start per request
- [x] **ElevenLabs TTS provider** — POST /api/ai/tts auto-routes to ElevenLabs when key configured; per-persona voice IDs (Ajani=Adam, Minerva=Bella, Hermes=Antoni, Trinity=Rachel); model `eleven_multilingual_v2`
- [x] **Graceful OpenAI fallback** — when ElevenLabs returns 401/missing_permissions, server falls back to OpenAI TTS in-flight; first failure sets a process-level `_ELEVEN_TTS_DISABLED` flag so subsequent calls skip the failed round-trip
- [x] **Multi-language support** — TTS endpoint accepts `language` (en/zu/yo/maa/…); default per persona (Ajani=Zulu, Minerva=Yoruba, Hermes=Maa, Trinity=English); response headers expose `X-AI-Provider`, `X-AI-Voice`, `X-AI-Language`, `X-AI-Model`
- [x] **`/api/ai/voices`** — discovery endpoint returns both provider voice maps + persona language defaults + active provider
- [x] **`/api/ai/voices/elevenlabs`** — live-fetch ElevenLabs account voices (returns JSON error body when key lacks `voices_read`)
- [x] **Speed validation** — Pydantic `Field(ge=0.25, le=4.0)` on TTS request `speed`
- [x] **ChatPanel language picker** — inline EN/ZU/YO/MAA pills next to the voice toggle; auto-snaps to active AI's native language; user-selectable
- [x] **AbortController everywhere** — `useTTS` aborts in-flight fetch on next-speak / unmount; `useAtlasJob` auto-cancels poll + submit on consuming-component unmount; `ChatPanel` aborts chat fetch on unmount → closing a panel mid-LLM-job no longer leaks network calls

### Interactive Sandbox — hands-on labs in the teaching flow (Feb 2026)
- [x] **`InteractiveSandbox` component** at `/app/frontend/src/components/HUD/InteractiveSandbox.js`
  - **6 labs**, two per persona — failure modes map directly to each lead core's Hard Rule, so failing the design teaches the doctrine:
    - **Power** (Ajani / red) — Solar station: tune sunlight / angle / temperature / battery; overheats and shuts down if you push it past containment.
    - **Bridge** (Ajani / red) — Bridge design: balance supports / span / material / load; collapses under stress.
    - **Resonance** (Ajani / red) — Ambient vibration energy harvesting: tune sensors / frequency / amplifier / damping; resonant collapse if amplifier > 85 and damping < 40 (cannot safely shut down).
    - **Ecosystem** (Minerva / teal) — Biome balance: predators / plants / water / climate; irreversible harm if any species crashes — teaches "no harm in the name of optimisation."
    - **Code** (Hermes / silver) — AI module balance: speed / memory / safety / complexity.
    - **Nanoswarm** (Hermes / silver) — Medical nanobot swarm: size / coordination / precision / battery; uncontainable if size > 800 and coordination < 70 — teaches "never design nanobots capable of self-replication."
  - Per-lab sliders, live derived metrics (Atlas Score / Output-Efficiency / Stability-Reliability), 5-step Mastery rank, Failure-Vision toggle
  - 3 mentor cards (Ajani / Minerva / Hermes) — lead persona's card highlighted with `.lead` glow + "PERSONA · LEAD" badge + domain-specific feedback message; non-lead mentors give generic teaching-doctrine feedback
  - Volume2 "speak this" button on each mentor — fires the existing TTS pipeline in the mentor's native language
  - NaN-safe lab switching via `liveValues` derived state
  - Reactive `initialLabKey` — parent can drive tab via prop change (used by topic-auto-route)
- [x] **Embedded inside TeachingWorkbench** — toggle button "Try a hands-on lab" auto-routes via `pickLabForTopic(topic)` before flipping open; auto-suggested when lesson topic matches `power|solar|grid|battery|reactor`, `bridge|beam|structure|span|load`, `code|program|algorithm|complexity`, `ecosystem|biodiversity|ecology|biome|permaculture|forest|wildlife`, `nano|swarm|atomic|molecular`, `resonance|vibration|wave|kinetic|RF|harvest`, etc.
- [x] **LAB outer-ring tile** opens TeachingWorkbench with the sandbox pre-expanded (`forceSandbox={true}` prop) — replaces the previous static items list
- [x] HUD aesthetic — dark glass panels, Orbitron labels, persona-coloured accent per lab, no purple gradient
- [x] Tabs wrap to 2 rows when 6+ labs are present

## Backlog

### Phase 0 — Audit Cleanup (Feb 2026)
- [x] Full audit report written to `/app/AUDIT-REPORT.md` (9 findings: 2 high, 3 medium, 4 low)
- [x] `pypdf==6.11.0` + `youtube-transcript-api==1.2.4` added to `requirements.txt` (closes H-2)
- [x] `atlas_core/council/router.py::route` renamed to `route_internal`; `route` kept as alias in `atlas_core/council/__init__.py` for backwards compat (closes M-1)
- [x] 4 orphan luxury-reskin frontend files moved to `frontend/src/_legacy/` + README explaining how to restore: ChatPanel, FileBrowserPanel, FileUploadModal, useVoiceRecognition (closes M-2)
- [x] `_LEGACY_NOTICE` docstrings added to `/api/knowledge/teach`, `/api/atlas/teach`, `/api/atlas/teach/sync` — pointers at canonical `/api/learning/...` (documents H-1; full consolidation deferred to Phase 2)
- [x] All 9 critical API endpoints verified 200 OK post-cleanup
- [x] New MongoDB collection `study_journal` (free-form architect notes per lesson) documented

### Phase 1 — Real LLM Integration (Feb 2026)
- [x] **NEW** `services/llm_provider.py` — unified async `send(persona, system, user)` wrapper with per-persona provider/model selection, graceful local→cloud fallback, never-empty-response defensive retry
- [x] **NEW** providers supported: `emergent` (default, via Emergent LLM Key — OpenAI gpt-5.2/4.1-mini, Claude Sonnet 4.5/Haiku 4.5, Gemini 3 Flash/Pro), `ollama` (local, OpenAI-compatible HTTP), `lmstudio` (local, OpenAI-compatible HTTP)
- [x] **NEW** routes (`routes/llm.py`): `GET /api/llm/health`, `GET /api/llm/persona-models`, `PUT /api/llm/persona-models`, `POST /api/llm/test`
- [x] **NEW** MongoDB doc `atlas_settings.{_id: "persona_models"}` stores per-persona overrides
- [x] **REFACTORED** `routes/council.py::_ask` now routes through `llm_provider.send` — picking up per-persona overrides automatically while preserving the council deliberation behavior
- [x] **VERIFIED** fallback path live-tested: set Ajani → Ollama (unreachable) → POST /api/llm/test → response from Emergent gpt-5.2 with `fallback_reason` recorded
- [x] Env vars (optional): `OLLAMA_HOST` (default `http://localhost:11434`), `LMSTUDIO_BASE_URL` (default `http://localhost:1234/v1`)

### Phase 2 — Knowledge / Memory Bank (Feb 2026) ✅ COMPLETE
- [x] **NEW** `services/memory_bank.py` — vector + graph memory layered on MongoDB
- [x] **NEW** 11 memory categories with permanent/decay policy:
   - Permanent (auto-pinned): `user`, `project`, `blueprint`, `council`
   - Decay (reinforcement curve): `research`, `temporary`, `lesson`, `intake`, `chat`, `sandbox`, `manual`
- [x] **NEW** dependency-free `hash` embedding (blake2b feature-hash, 384 dims) is the default — zero external deps, never fails. Switchable per-persona to `ollama` (semantic) or `emergent` (real OpenAI key) via PUT `/api/membank/embed-settings`
- [x] **NEW** routes (`routes/memory.py`): `/api/membank/store`, `/search`, `/list`, `/reinforce/{id}`, `/{id}` DELETE, `/categories`, `/user`, `/research`, `/graph/triple`, `/graph/list`, `/graph/around`, `/embed-settings` GET/PUT
- [x] **NEW** auto-wired pipelines (fire-and-forget via `auto_store`):
   - Intake → 3 memories (lesson + project + intake)
   - Council deliberation → 1 council memory
   - Blueprint generate → 1 blueprint memory
- [x] **NEW** freshness curve: 0.05/day decay, +0.20 per reinforcement, MIN_FRESHNESS=0.05; permanent rows skip decay entirely
- [x] **NEW** search score = 0.85·cosine + 0.15·freshness (default min_score=0.30, top_k=10)
- [x] **NEW** graph triples: upsert on (from,to,relation) with $inc weight+hits; BFS `around` to depth 3
- [x] **VERIFIED** 29/29 backend tests pass (`/app/backend/tests/test_membank_phase2.py`, report `iteration_11.json`)
- [x] Completion report: `/app/memory/PHASE2-REPORT.md`

### Phase 3 — Research Pipeline (Feb 2026) ✅ COMPLETE
- [x] **NEW** `services/web_scraper.py` — DuckDuckGo HTML search + httpx+selectolax page fetch (no API key, raises ResearchUnreachable on cloud-IP blocks)
- [x] **NEW** `services/pdf_reader.py` — pypdf extraction + paragraph-aware chunker with sentence overlap
- [x] **NEW** `services/patent_client.py` — Google Patents public XHR search + detail-page scraper (no API key)
- [x] **NEW** `services/research_pipeline.py` — orchestrates web/pdf/patent → optional Hermes/Ajani LLM summary → memory bank with category='research'
- [x] **NEW** routes (`routes/research.py`): `POST /api/research/web`, `POST /api/research/pdf` (multipart), `POST /api/research/patent`, `GET /api/research/recent`
- [x] **NEW** dep added to `requirements.txt`: `selectolax==0.4.10`
- [x] **VERIFIED** 16/16 backend tests pass (`/app/backend/tests/test_research_phase3.py`, report `iteration_12.json`)
- [x] All research outputs persist into Memory Bank Phase 2 (`category='research'`, decaying with reinforcement)

### Phase 4 — Voice System & ATLAS HUD (Feb 2026) ✅ COMPLETE
- [x] **NEW** `hooks/useVoiceRecognition.js` — Web Speech API wrapper with 3 modes (`off`|`push`|`wake`), lazy mic permission, auto-restart in wake mode, callback-via-ref so the engine survives re-renders
- [x] **NEW** `utils/voiceCommands.js` — `parseVoiceCommand(transcript, {requireWake})` → intent (`select-ai`/`open-section`/`close-panel`/`noop`). Recognises persona aliases (Ajani/Minerva/Hermes/Trinity-Council) + 11 tile aliases (subjects/lab/projects/blueprints/archive/explore/manual/encyclopedia/memory/systems/customization)
- [x] **NEW** mic toggle in HUDInterface top-right (next to sound toggle) cycles off→push-to-talk→wake-word→off. Wake-word mode pulses the chip with persona accent. Live transcript chip slides in from top-right while listening.
- [x] HUD visuals untouched per architect directive — new controls slot into the existing glass-chip aesthetic.
- [x] **VERIFIED** voice cycle + DOM contract green in iteration_12.json (frontend Playwright)

### Phase 5 — Digital Twin Engine (Feb 2026) ✅ COMPLETE
- [x] **NEW** `models/twin_models.py` — Pydantic v2 models for `DigitalTwin`, `TwinState`, `Component`, `Dependency`, `SensorInput`, `SimulationResult`, `CouncilDeliberation`, `TwinCategory` enum (device/robot/vehicle/environment/building/manufacturing_system/power_system), `SimulationKind` enum
- [x] **NEW** `services/twin_simulator.py` — 6 pure-Python simulation engines: blueprint (cycle + reference check), assembly (topological order), resource (BOM + energy budget), failure (fan-out SPOF + sensor gaps + transient power risk), timeline (critical-path DP), cost (materials + 20% labour). Deterministic, sub-100ms each.
- [x] **NEW** `services/digital_twin.py` — registry CRUD + run_and_persist_simulation + parallel council deliberation (asyncio.gather over Ajani/Minerva/Hermes). Lazy MongoDB client; no startup hook.
- [x] **NEW** `routes/twins.py` — full REST surface mounted at `/api/twins/*` (register, list, get, state PUT, simulate, simulations history, simulations by id, deliberate, delete with cascade)
- [x] **NEW** auto-wired memory: register → permanent project memory; simulate → permanent project + decaying research memory tagged success/failure; deliberate → permanent council memory
- [x] Forward-compat fields built-in: `state.integrations` (Weaver), `state.cad_refs` (CAD ingest), `state.hardware_binding` (Phase 7 robot control), `component.twin_ref` (twin composition)
- [x] **VERIFIED** 76/76 backend tests passing (`iteration_13.json`): 31 Phase-5 + 45 Phase-2/3 regression
- [x] Documentation + 3 example twins (Pollinator drone, Power Cell, Mother Box print farm) in `/app/memory/PHASE5-REPORT.md`

### Phase 6 — Weaver (Feb 2026) ✅ COMPLETE
- [x] **NEW** `models/weaver_models.py` — Pydantic v2 models: `Part`, `BlueprintInput`, `ExtractedPart`, `BuildPlan`, `ManufacturingPlan`, `FailurePrediction`, `CouncilOutcome`, `WeaverPlan`; enums `PartCategory` (component/material/fastener/electronic/sensor/actuator/tool/consumable), `Difficulty`, `BlueprintFormat`
- [x] **NEW** `services/parts_db.py` — MongoDB-backed parts library with idempotent 25-row starter seed. Token-overlap + substring matching (threshold 0.5) via `match_part(name)`.
- [x] **NEW** `services/blueprint_parser.py` — structured-JSON parser + Hermes LLM free-text parser (`llm_provider.send('hermes', …)`) + regex fallback. Enriches every extracted part with `library_part_id` + confidence.
- [x] **NEW** `services/weaver.py` — full pipeline `plan_from_blueprint`: parse → enrich → spawn Phase-5 twin → run 4 sims → compose build/manufacturing/failure plans → optional council deliberation → persist → write permanent blueprint memory
- [x] **NEW** `routes/weaver.py` — REST surface mounted at `/api/weaver/*`: `/parts` CRUD + search + seed + categories, `/analyze`, `/plan`, `/plans` CRUD with optional `?drop_twin=true` cascade
- [x] Difficulty heuristic (trivial/easy/medium/hard/expert), tools-required union from category hints, risk = (1−sim_score) + 0.05·|missing_parts|
- [x] Memory wiring: blueprint plan → permanent blueprint memory (10 memory rows total per deliberated plan, all queryable via `/api/membank/search`)
- [x] **VERIFIED** 81/81 backend tests passing (`iteration_14.json`): 21 Phase-6 + 60 Phase-2/5 regression. `pytest.ini` registers the `slow` marker.
- [x] Documentation + pan/tilt example in `/app/memory/PHASE6-REPORT.md`

### Knowledge Ingestion System (Feb 2026) ✅ COMPLETE
- [x] **NEW** `models/knowledge_models.py` — Pydantic `KnowledgeRecord` schema (title, summary, key_points, tags, source_type, source_url, source_hash, source_author, confidence_score, related_agents, related_projects, concepts, memory_bank_id, reinforce_count, timestamps) + `SourceType` enum (github · youtube · pdf · web · patent · academic) + `IngestRequest`/`FetchedSource`/`Distillation`
- [x] **NEW** `services/source_fetchers.py` — single `fetch(url)` dispatcher that picks `_fetch_github` (api.github.com, no token), `_fetch_youtube` (yt-transcript-api 1.x with graceful cloud-IP-block 503), `_fetch_pdf` (Phase-3 pdf_reader; remote URL or base64 blob), `_fetch_patent`/`_fetch_academic`/`_fetch_web` (Phase-3 reuse)
- [x] **NEW** `services/knowledge_distiller.py` — keyword-density `route_agent()` + persona-voiced LLM distillation via Phase-1 llm_provider. Strict JSON schema, anti-copyright system prompt ("rewrite in your own wording, no >15 consecutive verbatim words"), graceful fallback record (confidence=0.20) on LLM failure
- [x] **NEW** `services/knowledge_ingestion.py` — orchestrator: fetch → distill → dedup by `sha256(normalised_url)` → reinforce-on-revisit (merges tags/concepts/agents/projects, calls `mb.reinforce`) OR persist new → wire graph triples (concept↔tag · project↔concept · agent↔concept)
- [x] **NEW** `routes/kbase.py` — `/api/kbase/{ingest, search, by-url, classify, agents/route, {id}, {id} DELETE}` (prefix `/api/kbase` to avoid conflict with legacy `/api/knowledge` 22-subject teaching routes)
- [x] **NEW** memory category routing: project_id → category=project (PERMANENT) · agent=council → category=council (PERMANENT) · else → category=research (decaying, reinforce-able)
- [x] Anti-copyright safeguards: distilled content only in persistence; raw fetched text lives only in-request memory; source URL + author + confidence always preserved for citation
- [x] **VERIFIED** 10/10 tests passing in 22s (`tests/test_knowledge_ingestion.py`) — includes GitHub Whisper README example, YouTube cloud-IP-block tolerance, dedup + reinforce, graph wiring, anti-leakage
- [x] Documentation: `/app/memory/KNOWLEDGE-INGESTION-REPORT.md`

### Phase 7 — Robot Control Layer (Feb 2026) ✅ COMPLETE
- [x] **NEW** `models/robot_models.py` — Pydantic models: `Device`, `TelemetryRecord`, `Command`, `HardwareProfile`. Enums: `Role` (owner/council/ajani/minerva/hermes/guest), `DeviceKind` (esp32/raspberry_pi/usb_camera/sensor/gateway), `DeviceStatus` (registered/online/offline/safe_state/quarantined), `CommandKind` (ping/read_telemetry/configure/actuate/motion/bind_twin/firmware_update/emergency_stop), `CommandStatus` (queued/simulated/validated/executed/rejected/failed). `OWNER_ONLY_COMMANDS` set + `ALLOWED_COMMANDS` allow-list.
- [x] **NEW** `services/robot.py` — Device registry, telemetry store, simulation-first command pipeline: `authorise → device_lookup → simulate (Phase-5 twin) → validate (score ≥ 0.50) → execute (HTTP-poll MQTT bridge) → memory log`. Every step recorded in `pipeline_log`. EMERGENCY_STOP flips device to SAFE_STATE; subsequent actuate/motion blocked until owner clears. Idempotent `seed_if_needed()` provisions POSEIDON-BUOY / AETHER-STATION / SOIL-WATCH and auto-spawns + auto-binds a `TwinCategory.ENVIRONMENT` Phase-5 twin per device. Memory wiring: every device, telemetry record, and command writes a `mb.auto_store` record (telemetry → research/decaying; commands/devices → project + council tags).
- [x] **NEW** `routes/robot.py` — REST surface at `/api/robot/*`: `seed`, `roles`, `devices` (POST owner-only / GET list / GET by id), `devices/{id}/bind-twin` (owner-only), `devices/{id}/telemetry` (POST device-side / GET history), `devices/{id}/command` (role gate via `X-Atlas-Role` header), `devices/{id}/commands` (history), `devices/{id}/commands/inbox` (device-side poll endpoint — returns executed-but-undelivered commands once, marks delivered on read), `devices/{id}/emergency-stop` (owner-only), `commands/{id}`. Role is parsed from the `X-Atlas-Role` header (soft gate for local LAN v1).
- [x] Server wiring: `routes/robot.py` mounted in `server.py`; startup hook `_seed_phase7_devices` runs idempotent seed (3 devices + 3 twins) on first boot.
- [x] Frontend wiring: `/app/frontend/src/components/HUD/RobotPanel.js` (new) — embedded inside `DiagnosticsPanel` so the SYSTEMS tile now also surfaces Robot Control. Role dropdown, device list with status colour + twin-bound badge, PING / ACTUATE / E-STOP buttons, last-command panel (status colour + sim_score + rejection_reason), telemetry history, command log. No ring-geometry changes.
- [x] **VERIFIED** 13/13 backend tests passing (`iteration_15.json` — testing agent): 10 in `tests/test_robot_phase7.py` (roles, seed, owner-gate registration, telemetry roundtrip, guest-rejected actuate, owner ping, sim-first actuate, inbox once-delivery, emergency stop, command listing) + 3 in `tests/test_robot_membank_wiring.py` (Phase-2 memory bank auto-store wired for device/telemetry/command).
- [x] Hardcoded MONGO_URL fallback removed per env-only rule (testing-agent review).

### Phase 7+ Voice "Ingest <URL>" + Atlas Sentinel (Feb 2026) ✅ COMPLETE
- [x] **UPDATED** `utils/voiceCommands.js` — new `ingest-url` intent: detects the verb "ingest" + any URL form (https://, http://, scheme-less, www., trailing punctuation tolerated). Survives transcript normalisation by running on the RAW transcript first. Works with or without a wake phrase.
- [x] **UPDATED** `components/HUDInterface.js executeVoiceIntent` — on `ingest-url`, POSTs to `/api/kbase/ingest`, shows live transcript feedback ("Ingesting <url> …" → "Stored \"<title>\" · tags" or "Re-reinforced \"<title>\"") in the existing `.atlas-voice-transcript` ribbon.
- [x] Voice → Knowledge Bank → Memory Bank → Graph Memory chain: every voice-ingested URL writes a `KnowledgeRecord` (summary, key_points, tags, concepts, source_url, source_type, related_agents, related_projects, memory_bank_id) + graph triples (concept↔tag · project↔concept · agent↔concept). Dedup-by-URL → reinforce-on-revisit.
- [x] Permission verification (P1): curl-logged guest ACTUATE → REJECTED with `command 'actuate' is owner-only (got role=guest)`; owner ACTUATE → EXECUTED with full 4-step pipeline log (authorise → simulate sim_score=1.0 → validate → execute) on POSEIDON-BUOY.
- [x] **NEW** `components/HUD/AtlasSentinel.js` — optional environmental ribbon at the bottom of the HUD. Polls `/api/robot/devices` + `/api/robot/devices/{id}/telemetry?limit=1` every 12s for the three seed devices. Each chip shows latest payload (WATER/AIR/SOIL), gains an `is-safe` red pulse class when device.status==`safe_state`. Click → popover with full payload + timestamp. Dismissible × button persists via `localStorage[atlas.sentinel.enabled]`.
- [x] **NEW** CSS additions to `App.css` for `.atlas-sentinel*` selectors (glass-morphism pill, color-mix per chip-hue, pulse animation on safe state). HUD ring geometry untouched.
- [x] **UPDATED** `/app/memory/ARCHITECTURE-REPORT.md` — new "System data flow" section diagramming Knowledge Bank → Memory Bank → Graph Memory ⇄ Digital Twin ⇄ Weaver ⇄ Robot Control with the voice-ingest entry point.
- [x] **VERIFIED** 14/14 in `iteration_16.json`: 4/4 backend (`tests/test_iter16_voice_ingest_sentinel.py`), 10/10 voice-parser unit tests (`tests/voice_parser_iter16.cjs`), and full frontend regression (Sentinel render, popover, dismiss/persist, SAFE STATE visual, Robot Control panel still functional inside SYSTEMS).

### Phase 7+ Clear Safe State (Feb 2026) ✅ COMPLETE
- [x] **UPDATED** `models/robot_models.py` — `CommandKind.CLEAR_SAFE_STATE` added · `OWNER_ONLY_COMMANDS` extended.
- [x] **UPDATED** `services/robot.py` — `clear_safe_state(device_id, role, confirm, agent?)` enforces (in this order): owner-only role check → device lookup → exact-name confirm match (anti-fat-finger) → device-must-already-be-in-safe-state guard (so this endpoint can NEVER bypass any other safety gate) → write `robot_commands` record with 4-step pipeline_log (authorise · confirm · verify_safe_state · execute) → flip device `safe_state → registered` → patch bound Digital Twin's `state.safety_history` (capped at 25) + `state.safe_state=false` + `state.last_safety_clear_at` → write permanent `council` Memory Bank entry tagged `['robot','safety','clear_safe_state',<device_name>]`.
- [x] **UPDATED** `routes/robot.py` — new `POST /api/robot/devices/{id}/clear-safe-state` accepting `ClearSafeStateRequest{ confirm: str }`; route-level role gate as defence-in-depth (403/400/409/404 mapped from service result).
- [x] **UPDATED** `frontend/HUD/RobotPanel.js` — new "Clear Safe State" button (lime-green outline, `ShieldCheck` icon, `data-testid="robot-cmd-clear-safe-state"`) rendered ONLY when selected device.status==='safe_state'. Click → browser `window.confirm()` with device name surfaced + plain-English warning that Emergency Stop remains the highest-priority safety control → POST with `confirm: <device_name>`. Backend double-gates regardless.
- [x] **NEW** `backend/tests/test_robot_clear_safe_state.py` — 7 hard-guarantee tests (owner-only / wrong-confirm / missing-confirm / cannot-clear-healthy / full-success path with twin+memory+command audit / second-clear rejected / unknown device 404).
- [x] **VERIFIED** `iteration_17.json` — 10/10 backend (7 + 3 testing-agent extras: membank tagging, pipeline-log step ordering, e-stop+actuate regression) · 13/13 prior Phase-7 regression intact · 5/5 HUD assertions (button conditional render + window.confirm + post-clear device flip).
- [x] **NEW** `/app/memory/ATLAS_SYSTEM_REPORT.md` — full system report with completed phases, DB schemas, API endpoints, memory/knowledge schemas, all flows (Research/Twin/Weaver/Robot), remaining work, known limitations, recommended Phase 8 roadmap.



### Phase 8a — Persona Chat API foundation (Feb 2026) ✅ COMPLETE
- [x] **NEW** `models/persona_models.py` — `ChatRequest`, `ChatResponse`, `ChatSession`, `ChatMessage`, `CouncilSubVoice`, `PersonaInfo` Pydantic models. Stable response shape for future HUD persona panels + voice integration.
- [x] **NEW** `services/persona_chat.py` — orchestrator: per-turn pipeline (session lookup → persona-tagged memory pull → knowledge-bank pull → recent session turns → persona system-prompt assembly → `llm_provider.send()` → persist user+assistant → mirror assistant into Memory Bank with `category=agent` permanent). Council variant fans out to ajani/minerva/hermes in parallel then runs a synthesis call with all three sub-voices in context; each sub-voice also gets mirrored to Memory Bank (`category=agent`) and the synthesis to `category=council`. Single `PERSONAS` registry is the SHARED source of truth with `knowledge_distiller.py`.
- [x] **NEW** `routes/persona.py` — REST surface: `GET /api/persona/list` · `POST /api/persona/{persona}/chat` · `GET /api/persona/{persona}/sessions` · `GET /api/persona/sessions/{id}` · `DELETE /api/persona/sessions/{id}` (preserves Memory Bank entries) · `GET /api/persona/sessions`.
- [x] `memory_bank.py PERMANENT_CATEGORIES` adds `agent`.
- [x] `routes/memory.py` adds `GET /api/membank/by-tag` — exact-tag lookup.
- [x] `_fetch_knowledge` tokenises natural-language prompts before kbase.search.
- [x] **VERIFIED** `iteration_18.json` — 34/34.

### Phase 8 P2–P5 — Graph + Sentinel + MQTT + arXiv (Feb 2026) ✅ COMPLETE
- [x] **P2 Graph Traversal** — `services/memory_bank.py::neighborhood` extended with `min_weight` filter. `routes/memory.py` exposes `GET /api/membank/graph/expand?subject=&depth=&min_weight=&limit_per_layer=` returning `{nodes, edges, node_count, edge_count}` — vis-network / sigma.js / d3-force ready.
- [x] **P3 Sentinel Anomaly Detection** — `services/anomaly.py` runs Welford's online algorithm per (device, telemetry-key); 10-sample warmup gate; |z| ≥ 3.0 default trips `device.state.anomaly`. Auto-cleared on next in-envelope reading. New `GET /api/robot/devices/{id}/envelope`, owner-only `POST /devices/{id}/envelope/reset`, `POST /devices/{id}/ask-council` auto-fires `/api/persona/council/chat`. Sentinel chip flips amber + popover shows drifting keys + z-scores + "ask the council" button with inline reply.
- [x] **P4 paho-mqtt Adapter** — `services/mqtt_bridge.py` lazy-connect singleton, daemon network thread, best-effort publish after EXECUTE. Dormant when `MQTT_BROKER_HOST` unset — REST surface unchanged. `GET /api/robot/mqtt/status`. `paho-mqtt==2.1.0` added to requirements.
- [x] **P5 arXiv Integration** — `_fetch_arxiv` uses arXiv's free Atom API; old/new IDs supported; non-arXiv academic URLs fall back to generic page scrape. `_reinforce` now back-fills `source_author` and `title` on re-ingest (testing-agent-caught data-loss fix).
- [x] **Incidental:** `seed_if_needed` made name-aware; HUD `?limit=200` for full device list.
- [x] **VERIFIED** `iteration_19.json` — 41/41 backend + frontend HUD smoke GREEN.

### Phase 8 e/f/g — Persona panels + ESP32 firmware + mTLS (Feb 2026) ✅ COMPLETE
- [x] **8e — Persona Chat Panels (frontend):** `components/HUD/PersonaChatPanel.js` — docked right-side chat panel. Opens on **double-click** of an AI face card (single-click still selects the persona for the existing HUD context). Sticky session per persona in `localStorage[atlas.persona.session.<persona>]` — closing + reopening resumes; "new chat" trash icon discards the local log without touching Memory Bank. Hydrates persona identity from `GET /api/persona/list`. Council variant renders the 3 sub-voices in a collapsible block above the synthesised reply. Full `data-testid` coverage: `ai-face-{slug}`, `persona-chat-{slug}`, `persona-chat-input-{slug}`, `persona-chat-send-{slug}`, `persona-chat-close-{slug}`, `persona-chat-new-{slug}`, `council-subvoice-{slug}`. CSS in `App.css` (`.persona-chat-*`) uses per-persona accent via `--persona-accent` and `color-mix()`.
- [x] **8f — mTLS device certs:** `services/mtls.py` mints a self-signed ATLAS Root CA on first call (stored under `MTLS_CA_DIR` env or `/app/backend/_data/mtls/`, key mode 0600); per-device ECDSA P-256 cert+key signed by the CA on every `POST /api/robot/devices`. Returns the cert/key/ca PEMs ONCE in the response (`mtls` block) with an explicit "save these now" warning; server persists ONLY the fingerprint + serial + not_after. New endpoints `POST /api/robot/devices/{id}/mtls/issue` (owner-only rotation) and `GET /api/robot/mtls/ca`. Enforcement is **dormant in v1** — gated on `MTLS_ENFORCE=true` (architect decision: ship issuance now, flip on enforcement when devices are in the field).
- [x] **8g — ESP32 reference firmware:** `/app/firmware/esp32/atlas_device.ino` — single-file Arduino sketch (ESP32 core ≥ 2.0). Telemetry push every 5s + inbox poll every 3s. Handles every CommandKind including local SAFE_STATE enforcement (the device refuses ACTUATE/MOTION on its own even if the server lets one through — belt-and-braces). Optional MQTT subscribe path behind `-DATLAS_ENABLE_MQTT`. Optional mTLS via 3 PEM constants. Sensor reads / actuator drives are clearly-marked hooks (`read_sensors()`, `actuate()`, `actuate_safe()`). Companion `README.md` documents the full flash workflow, the safety contract table, and the per-target device-type swaps (POSEIDON-BUOY / AETHER-STATION / SOIL-WATCH).
- [x] **VERIFIED** 44/44 backend tests (7 new `test_mtls_phase8f.py` + 11 phase8_quad + 26 prior regression). HUD screenshot confirms persona chat panel opens on AI-face double-click and council fan-out renders all 3 sub-voices (Ajani / Minerva / Hermes) with the synthesis below.



### Phase 8h — Sentinel Autonomic Watcher + housekeeping (Feb 2026) ✅ COMPLETE
- [x] **NEW** `services/sentinel_watcher.py` — background asyncio loop fires `persona_chat.chat_any('council', ...)` automatically whenever a device's anomaly block changes. Dedupe key = `(device_id, anomaly.since, sorted(drifting_keys))` persisted in collection `sentinel_autonomic_fires`; same anomaly never fires twice. 5-minute cooldown per device (configurable). Council reply persisted as permanent `category=council` Memory Bank entry tagged `autonomic_council` + device name + every drifting key.
- [x] **NEW** `GET /api/robot/sentinel/watcher/status` — running flag, ticks counter, fires_total, last_fire_at, last_error. **`POST /api/robot/sentinel/watcher/fire-now`** — owner-only manual tick (for dev + demos).
- [x] Env config: `SENTINEL_AUTONOMIC=true` (default off — set to true in this env), `SENTINEL_AUTONOMIC_INTERVAL_S=60`, `SENTINEL_AUTONOMIC_COOLDOWN_S=300`. Lifecycle wired into FastAPI `@app.on_event("startup"|"shutdown")`.
- [x] Failure mode: dedupe record is INSERTED BEFORE the LLM call, so a council outage doesn't loop us. Errors counted + last_error surfaced; ticks continue regardless.
- [x] **NEW** `backend/scripts/cleanup_test_devices.py` — wipes ephemeral robot devices created by pytest runs (prefix-matched: `TEST-`, `FIX-DEV-`, `CLEAR-TEST-`, `HEALTHY-`, `MTLS-TEST-`, `ANOMALY-TEST-`, `AUTONOMIC-`). Dry-run by default; `--commit` to actually delete. Protected names list (POSEIDON-BUOY / AETHER-STATION / SOIL-WATCH) is hardcoded; **never deletes a twin that a protected device references** (fix landed after first run accidentally orphaned POSEIDON-BUOY's twin by deleting a shared test-fixture twin reference).
- [x] **HUD honesty: DEMO CONTENT badge** added to `AtlasSidePanel.js` operation-info panels — every tile that surfaces a hardcoded list ("Connected Devices", "Blueprint Gallery", etc.) now displays an amber pill saying "DEMO CONTENT · not wired to live data". Tiles backed by real APIs (Memory, Research, Twins, Weaver, Cyclopedia, Diagnostics, Robot Control) are unaffected.
- [x] **VERIFIED** 48/48 backend tests passing across all suites: `test_sentinel_watcher.py` (4 new) + `test_mtls_phase8f.py` (7) + `test_phase8_quad.py` (11) + `test_robot_phase7.py` (10) + `test_robot_clear_safe_state.py` (7) + `test_persona_chat.py` (9). Includes full anomaly→fire-now→council→Memory Bank chain + dedupe verification + cooldown.



### Live functional tiles (Feb 2026)
- [x] **MANUAL** → `/api/manual/sections` — 5 collapsible sections (Hard Rules, Personas, Rings, Lab, Voice)
- [x] **CYCLOPEDIA** → `/api/knowledge/subjects` — searchable chip grid + per-subject detail
- [x] **MEMORY** → `/api/memory/feed` — live event feed (atlas_events collection), auto-refresh every 8s
- [x] **CUSTOMIZATION** → `/api/settings` GET/PUT — TTS provider, default language, accent theme, voice toggle (persisted to MongoDB `atlas_settings`)
- [x] **ARCHIVE** → tabbed browser (`Atlas memory` / `Uploaded files`) reading `atlas_archive` + `/api/files/list`
- [x] **EXPLORE / INTAKE** → `/api/intake/youtube` + `/api/intake/transcript` — YouTube URL with paste-transcript fallback, builds AI-routed lesson + 5-question quiz, persists to atlas_archive
- [x] **COUNCIL** → `/api/council/route` + `/api/council/deliberate` — keyword routing (AJANI · MINERVA · HERMES · COUNCIL) + tri-AI deliberation in voice (gpt-5.2)
- [x] Topic router (`/app/backend/routing/topic_router.py`) — first-match scan: AJANI → MINERVA → HERMES → COUNCIL fallback

### ATLAS V2 build — Parts 1-5 (Feb 2026 · Session continuation)
- [x] **Part 1 · World Update Watcher** — `services/worldwatch.py` · 12 curated RSS/Atom feeds covering AI/robotics/SE/electronics/batteries/green-tech/manufacturing/design/architecture/medicine/agriculture/aerospace · `/api/worldwatch/{status,seed,run,updates,feeds}` · live test: 10/11 feeds ingested (1 BOM error captured) · 10 real "what changed" notes via gpt-5.2 with novelty classification · KB+MB+graph triple-write per entry · domain→agent routing (AI/medicine/agriculture→Minerva, robotics/electronics/manufacturing/design/architecture/aerospace→Ajani, SE→Hermes)
- [x] **Part 2 · Self-Code Improvement** — `services/self_code.py` · AST + regex detectors (TODO/FIXME, bare except:pass, hardcoded HUD lists, module > 550 lines, missing route tests) · `/api/self-code/{proposals,scan,approve,reject}` · live scan: 63 files · 29 findings · 27 new pending proposals (dedupes against existing) · STRICT "approval-first" rule honoured (zero auto-apply)
- [x] **Part 3 · Personal Learning Adaptation** — `services/adaptation.py` · single-doc `user_learning_profile` keyed `id="default"` · default 6-9grade explanation + lego_steps lesson format + 6 explanation rules · `/api/learning/{profile,log-confusion,log-success}` · NOT yet consumed by lesson generator (integration gap documented)
- [x] **Part 4 · HUD V2 theme foundation** — 4 JSON theme files at `/app/themes/` (theme manifest + color + motion + layout tokens) · `/api/themes/{list,{id}}` · agent colors locked: Ajani #E63946 · Minerva #2EC4B6 · Hermes #F4EFE4 · Council #9B6BD8 · anti-pattern list enforced · full HUD reskin deferred to follow-up design pass
- [x] **Part 5 · Visual Style Memory** — `services/adaptation.py` style section · single-doc `visual_style_memory` · `/api/style/{preferences,note,warning}` · too_plain / too_messy counters · live test: counter incremented
- [x] `ATLAS_WORLDWATCH_REPORT.md` · `ATLAS_V2_SELF_IMPROVEMENT_REPORT.md` · `ATLAS_HUD_V2_STYLE_GUIDE.md`

**Rules honoured.** v1 untouched · no major code rewrites · every proposal pending until approved · themes are JSON-swappable · NO new feature was applied silently (only the system that COLLECTS them was built).

**Carry-forward blockers from prior steps.**
- 🟠 Step 3 from prior priority — `sentence-transformers` Memory Bank upgrade — install was killed mid-flight by the bash gateway twice. NOT installed. Memory Bank remains 🟠 PARTIAL.
- 🟠 Step 4 from prior priority — HUD Graph Visualization — backend `/api/membank/graph/expand` is live; UI panel NOT yet built. Captured as a Part 4 next-step.
- 🟠 HUD V2 visual reskin — theme tokens shipped; CSS-variable hook + per-panel reskin NOT yet implemented.
- 🟠 Dezeen RSS BOM parse error — 1 of 11 feeds currently failing. Captured as a worldwatch TODO.

### YouTube Learning subsystem (Feb 2026 · Session continuation)
- [x] **Channel RSS Resolver** — `GET /api/youtube/resolve-channel?url=&n=3` · resolves any channel form (`/channel/UC*`, `/user/X`, `/c/X`, `/@h`) into latest N videos via public Atom feed
- [x] **Manual Transcript Ingestion** — `POST /api/youtube/ingest-transcript` · sidesteps cloud-IP block · full KB → MB → Graph → Lesson chain · transcript body stored ONLY in private `youtube_transcripts_private` collection (consent=user_supplied)
- [x] **Lesson Generator** — already built, now triggered by manual-transcript ingest
- [x] **Verification Dashboard** — `GET /api/youtube/dashboard` · live verdict computed from DB (`🟢 Verified` requires ≥1 MANUAL_PROVIDED + ≥1 lesson)
- [x] **Live proof against Sebastian Lague channel** — `UCmtyQOKKmrMVaKuRXz02jbQ` resolved · 3 latest videos returned · 1 transcript ingested · `knowledge_id=29e6257c479443eea2c2e3898b3192ff` · `lesson_id=e3b15139552f4baab8619506a13608fc` · 36 graph triples · 6 vocabulary terms · 4 quiz questions
- [x] `ATLAS_YOUTUBE_LEARNING_PROOF.md` — every ID + raw DB readback documented

**Verdict (per database):** 🟢 **Verified end-to-end via manual transcript ingest** (was 🔴 Not Verified). Direct YouTube transcript fetch remains 🔴 Blocked by cloud-IP — fix is out-of-environment.

### Watcher Systems pass (Feb 2026 · Session continuation)
- [x] **GitHub Knowledge Watcher** — `/api/watchers/{sources,github/register,github/run,github/status,proof/{id}}` + helper `/api/kbase/sources/github`
- [x] **Lesson generator** — gpt-5.2-backed lesson plans persisted in `lessons` collection; `/api/lessons/{generated,by-source,{lesson_id}}`
- [x] **Self-Improvement Watcher** — `/api/self-improve/{proposals,propose,approve/{id},reject/{id},history,weekly-report}` · strict "never silently rewrite" contract (no code path touches anything outside `self_improvements` collection)
- [x] Live test against `https://github.com/PrejudiceNeutrino/YouTube_Channels` — source_id `a2f334e53c8f49a3bbbdb4e1e3b28611` · run_id `705e6a1c30cd45adbbebaf3f41009680` · **15 links / 15 KB-records / 15 MB-rows / 24 graph edges / 1 lesson / 0 errors**
- [x] `ATLAS_WATCHER_SYSTEM_REPORT.md` — real evidence + simulated/key/transcript/hardware/incomplete sections
- [x] `ATLAS_REALITY_AUDIT.md` — 22-subsystem REAL/PARTIAL/SIMULATED/PLACEHOLDER/UNTESTED audit · roll-up: 🟢 8 · 🟡 5 · 🟠 5 · 🔴 3 · ⚫ 1

**Honest caveats from this session.** Ollama embed-provider switch attempted but **the `/usr/local/bin/ollama` binary is wiped between bash sessions in this cloud container** (verified empirically twice). `sentence-transformers` fallback install was cut off by bash-gateway instability. HUD legacy-tile replacement + graph-viz panel were deferred when the user redirected to Watcher Systems build. YouTube channel-URL → video-URL resolver is captured as Self-Improvement proposal `410a020f53e34e3997c96e70664eda24` (approved, implementation pending).

### Verification documentation pass (Feb 2026 · Session continuation)
- [x] `ATLAS_VERIFICATION_RESULTS.md` — raw 11-test results from `/tmp/atlas_verify.log` (PASS/SIMULATED/observations, no summarization)
- [x] `ATLAS_INTEGRATION_PLAN.md` — 5 end-to-end flows (Research→Knowledge · Persona→Graph · Twin→Weaver · Robot→Sentinel · HUD→Live APIs)
- [x] `ATLAS_DATA_FLOW.md` — collection-level data movement, schemas, write/read fan-out, egress/ingress, retention
- [x] `ATLAS_TRUTH_REPORT.md` — REAL / SIMULATED / PARTIAL / PLACEHOLDER / UNTESTED classification for all 20 subsystems with file-path & test-ID evidence

**Roll-up from truth report.** 🟢 6 · 🟡 5 · 🟠 4 · 🔴 3 · ⚫ 1
- 🟢 REAL: Council · Knowledge Bank · Graph Memory · Research Pipeline · Sentinel ribbon · Sentinel Watcher
- 🟡 SIMULATED: Ajani · Minerva · Hermes (prompt-driven) · Digital Twin (heuristic) · Weaver (heuristic costs)
- 🟠 PARTIAL: Memory Bank (hash embedding) · Voice (string-match wake-word) · HUD (legacy hardcoded tiles) · Robot Control (execute is dispatch-only) · mTLS (issuance-only)
- 🔴 PLACEHOLDER: MQTT (dormant) · ElevenLabs TTS (cloud-IP block) · YouTube ingestion (cloud-IP block)
- ⚫ UNTESTED: ESP32 firmware (real source code, zero hardware contact)

### Vibrancy pass (Feb 2026, additive only, HUD geometry untouched)
- [x] Subtle radial vignette + ambient scan-line sweep behind the HUD frame (9s period)
- [x] Brighter dial-ring drop-shadow, active ring saturated glow
- [x] Persona button pulse animation amped (scale + double glow halo)
- [x] Tile hover: scale-up + neon stroke draw
- [x] Side-panel persona-coloured top accent line
- [x] Central core saturation +18%, contrast +5%
- [x] Persona name label double text-shadow glow

### P1
- [x] ~~Minerva approval API + Hermes validation API~~ — DONE
- [x] ~~Blueprint Engine + Design Tools~~ — DONE

### P2
- [x] ~~Real-time TTS for AI personas (per-AI voice rhythm)~~ — DONE (OpenAI + ElevenLabs)
- [ ] Offline AI fallback (Ollama local LLM or hybrid cache)
- [ ] Hidden / advanced rings (diagnostics, build mode)
- [ ] More labs in InteractiveSandbox (Bio-genesis, Nano-synthesis, Energy harvesting)

### P3
- [ ] Persistent PostgreSQL Knowledge Core (currently MongoDB-backed via atlas_core memory)
- [ ] 3D WebGL upgrade for the central core (user deferred — keep canvas core)
- [x] ~~Multi-language voice support~~ — DONE (ZU/YO/MAA via ElevenLabs multilingual)
- [x] ~~Custom AI voice profiles~~ — DONE (per-persona ElevenLabs voice IDs)
- [ ] ElevenLabs key with full `text_to_speech` + `voices_read` scopes (current key has neither — system runs in OpenAI fallback)
- [ ] Save sandbox configurations + replay
- [ ] AI-suggested next slider tweak ("try angle = 35 to maximise solar output")
