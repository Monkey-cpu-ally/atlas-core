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



### Live functional tiles (Feb 2026)
- [x] **MANUAL** → `/api/manual/sections` — 5 collapsible sections (Hard Rules, Personas, Rings, Lab, Voice)
- [x] **CYCLOPEDIA** → `/api/knowledge/subjects` — searchable chip grid + per-subject detail
- [x] **MEMORY** → `/api/memory/feed` — live event feed (atlas_events collection), auto-refresh every 8s
- [x] **CUSTOMIZATION** → `/api/settings` GET/PUT — TTS provider, default language, accent theme, voice toggle (persisted to MongoDB `atlas_settings`)
- [x] **ARCHIVE** → tabbed browser (`Atlas memory` / `Uploaded files`) reading `atlas_archive` + `/api/files/list`
- [x] **EXPLORE / INTAKE** → `/api/intake/youtube` + `/api/intake/transcript` — YouTube URL with paste-transcript fallback, builds AI-routed lesson + 5-question quiz, persists to atlas_archive
- [x] **COUNCIL** → `/api/council/route` + `/api/council/deliberate` — keyword routing (AJANI · MINERVA · HERMES · COUNCIL) + tri-AI deliberation in voice (gpt-5.2)
- [x] Topic router (`/app/backend/routing/topic_router.py`) — first-match scan: AJANI → MINERVA → HERMES → COUNCIL fallback

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
