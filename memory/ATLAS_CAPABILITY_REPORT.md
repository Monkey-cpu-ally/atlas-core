# ATLAS · Capability Report
_Generated Feb 2026 · companion to `ATLAS_SYSTEM_REPORT.md`_

> **Scope.** Per-system snapshot of what's actually wired, what's stubbed, what's planned. Each system is graded **Implemented · Partially · Planned**, with current capabilities, gaps, known limitations and the recommended next step.
>
> **Legend** ✅ Implemented · 🟡 Partially implemented · ⏳ Planned

---

## 1 · Ajani — Engineer / Builder persona

**Status:** 🟡 **Partially implemented**

### Current capabilities ✅
- Routed automatically by `services/knowledge_distiller.py::route_agent()` for engineering / robotics / manufacturing / blueprint / failure-mode tokens (keyword-density scoring).
- Persona-voiced LLM distillation prompt ("Zulu warrior-engineer. Focus on what can be BUILT and what FAILS.") via Phase-1 `llm_provider`.
- Default model override registered in `atlas_settings._id="persona_models"` → Emergent `gpt-5.2` (configurable per persona).
- Participates in Phase-5 council deliberations (`POST /api/twins/{id}/deliberate`) producing a per-persona `DeliberationVoice`.
- Memory tags every ingested record with `related_agents: ['ajani', …]` for Graph-Memory queries.

### Missing capabilities
- No dedicated `/api/ajani/*` chat surface — the persona is invoked only **inside** other flows (kbase distillation, council deliberation). There is no first-class "talk to Ajani" REST endpoint.
- No long-term persona memory pivot — Ajani-tagged memories are queryable but the persona itself does not yet **read its own memory** before answering.
- No HUD "speak as Ajani" panel — the persona is text-only; the AI face / mic chip surfaces Ajani as the active AI but no per-persona conversation thread exists.

### Known limitations
- Persona routing is keyword-density only; an ambiguous phrase like *"build a bioreactor"* will pick Ajani over Minerva even though the science context outweighs the build.
- Council voices are single-turn — Ajani cannot rebut Minerva mid-deliberation.

### Recommended next step
Wire `POST /api/persona/{ajani|minerva|hermes}/chat` that (a) retrieves the persona's tagged memories (top-k by similarity + freshness), (b) prepends them as system context, (c) calls `llm_provider` with the persona prompt, (d) writes the reply back to the Memory Bank tagged with the persona. Single endpoint unblocks dedicated HUD persona panels.

---

## 2 · Minerva — Scientist / Researcher persona

**Status:** 🟡 **Partially implemented**

### Current capabilities ✅
- Persona prompt active ("scholar of nature. Focus on what is TRUE and what is REPRODUCIBLE.").
- Routed for science / biology / chemistry / agriculture / medicine / education / research / patent keywords.
- Drives the dominant share of Knowledge-Ingestion records (PDFs, academic, patents → typically Minerva).
- Voice in council deliberation: "evidence quality + reproducibility" lens.
- Tags downstream Memory entries with `related_agents: ['minerva']` for graph traversal.

### Missing capabilities
- No literature-search agent — Minerva cannot **search the Research Pipeline herself**; she only distils what is handed to her.
- No experiment-design tool — there is no equivalent of Weaver for science (the user has hinted at a future *"Bio-genesis"* / *"Nano-synthesis"* sandbox).
- No citation graph — ingested papers carry `source_url` but the graph_triples don't yet model "cites" / "extends" relations between two papers.

### Known limitations
- Same single-turn limit as Ajani in council mode.
- LLM distillation may hallucinate confidence on PDFs that returned poor OCR — there is no Minerva-specific "low confidence → request human review" branch.

### Recommended next step
A `POST /api/minerva/search?query=` that chains `services/research_pipeline.web → services/source_fetchers.fetch → services/knowledge_distiller.distill` end-to-end, returning the top 5 distilled records and storing them as research-memory in one call. This turns Minerva from a downstream consumer into an active researcher.

---

## 3 · Hermes — Validator / Logician persona

**Status:** 🟡 **Partially implemented**

### Current capabilities ✅
- Persona prompt active ("messenger of clarity. Focus on what is LOGICAL and what is OPTIMAL.").
- Routes math / logic / validation / optimisation / software / algorithm / code-review tokens.
- Default reviewer voice in Phase-5 council deliberations — surfaces logical contradictions in Ajani/Minerva's recommendations.
- Tagged in graph triples as `relates_to` source for any concept where Hermes was the routing winner.

### Missing capabilities
- No formal-verification surface — Hermes cannot run actual SAT/SMT or unit-test sweeps; the persona produces logical critique in natural language only.
- No optimisation-loop primitive — there is no `POST /api/hermes/optimize` that takes a Weaver plan and returns a Pareto-front (cost vs failure-rate vs lead-time).
- No code-review pipeline — Hermes does not yet read a GitHub repo's source files (kbase only ingests README/metadata via `_fetch_github`).

### Known limitations
- "Logic" check is LLM-generated, so it inherits LLM hallucinations.
- Hermes does not enforce constraints — he only flags them.

### Recommended next step
Add `services/optimiser.py` exposing `optimise(plan, objective)` that (a) parameter-sweeps a Weaver plan via Phase-5 simulator, (b) computes a Pareto front, (c) returns top-3 trade-offs. Wire as `POST /api/hermes/optimize`. Gives Hermes a concrete decision-support role beyond critique.

---

## 4 · Council — Multi-persona deliberation

**Status:** ✅ **Implemented**

### Current capabilities ✅
- `POST /api/twins/{twin_id}/deliberate { agents: [...] }` — parallel agent voices (Ajani · Minerva · Hermes), each invoked with the twin's latest simulation as context.
- Final synthesised verdict appended as `DeliberationVoice(persona="council", role="verdict")`.
- Permanent council Memory Bank entry on every deliberation (category=council, never decays).
- Readable deliberation text duplicated into research-memory for retrieval / chat.
- Council voice automatically fires inside Phase 6 Weaver when a plan crosses a risk threshold.
- Council voice is **also** automatically fired by Phase-7 robot safety actions (`emergency_stop`, `clear_safe_state`) — the council never "votes" on these, but they are logged in the council category as audit trail.

### Missing capabilities
- No agent-vs-agent back-and-forth — current deliberation is one round of parallel voices then a single synthesis. No rebuttals.
- No vote weighting — every agent's voice carries equal influence in the verdict.
- No abstention or "request more data" path — verdict is always synthesised, even when agents disagree heavily.

### Known limitations
- Parallel calls inflate token spend on the Emergent LLM key (≥3 calls per deliberation).
- Synthesis quality depends on the model — sometimes the verdict glosses over a disagreement instead of surfacing it.

### Recommended next step
Add a `rounds: int = 1` parameter to `deliberate()` that loops rebuttals (Ajani sees Minerva's voice in round 2, etc.) and tracks a confidence-delta per round to early-exit when consensus stabilises. Implements actual multi-turn deliberation without changing the public API shape.

---

## 5 · Knowledge Bank

**Status:** ✅ **Implemented**

### Current capabilities ✅
- `POST /api/kbase/ingest` accepts a URL or PDF blob; dispatches to GitHub / YouTube / PDF / Web / Patent / Academic fetcher.
- LLM persona-voiced distillation (`services/knowledge_distiller.py`) with strict JSON schema and anti-copyright system prompt (no >15 consecutive verbatim words).
- Dedup-by-`sha256(normalised_url)` → reinforce-on-revisit (merges tags · concepts · agents · projects).
- Every record written to BOTH `knowledge_records` (specialised schema) AND `memory_bank` (general MemoryRecord) — single source of truth for cross-system queries.
- Graph triple wiring on persist: concept↔tag · project↔concept · agent↔concept.
- Voice command "*ingest <URL>*" wired (`utils/voiceCommands.js`) — the HUD's mic chip now feeds the Knowledge Bank directly.
- Endpoints: `ingest · search · by-url · classify · agents/route · {id} · DELETE {id}`.

### Missing capabilities
- No HUD browser yet — the Cyclopedia tile still shows the legacy 22-subject teaching index; the new ingested URL records aren't surfaced.
- No bulk import — a user must ingest one URL at a time (no CSV / OPML / sitemap loader).
- No revision history — re-ingesting the same URL merges, but the old summary is overwritten with no diff log.

### Known limitations
- YouTube transcripts: native cloud-IP block → graceful 503 with proxy hint.
- GitHub: anonymous API quota (60 req/h per IP).
- PDFs: text-only extraction; figures and equations are lost.
- LLM distillation cost scales linearly with ingestion volume (Emergent LLM key budget).

### Recommended next step
Surface ingested records in the HUD's Cyclopedia panel — a small "Recent Ingests" section showing the latest 10 KnowledgeRecord titles linked to their source URLs, with the existing 22-subject teaching index above. Zero-risk additive UI change that closes the user-facing loop.

---

## 6 · Memory Bank

**Status:** ✅ **Implemented**

### Current capabilities ✅
- 11 memory categories — 4 permanent (system · project · council · agent), 7 decaying (research · telemetry · chat · weaver_draft · twin_state · simulation · ephemeral).
- Vector field per record (128-dim hash embedding by default; Ollama / Emergent providers selectable via `ATLAS_EMBED_PROVIDER`).
- Freshness decay + Hebbian-style reinforcement (`reinforce_count`, `last_reinforced_at`).
- `auto_store(content, persona, category, source_type, source_id, tags)` — single ingress used by Twin, Weaver, Robot, Knowledge, Research subsystems.
- Full REST surface: `store · search · by-category · by-tag · reinforce · {id} · DELETE`.
- Wired as the **audit trail** for every safety-relevant Phase-7 action (emergency_stop, clear_safe_state, owner-only commands).

### Missing capabilities
- No public `GET /api/membank/by-tag?tag=...` route — the testing agent had to fall back to `/list?category=council` to verify tag persistence; the by-tag query exists in service but isn't routed.
- No TTL eviction — decaying records age in score, but the documents themselves stay in MongoDB forever (manual `DELETE` only).
- No cross-category dedup — the same insight can land in both `research` and `project` categories without merge.

### Known limitations
- Default hash embedding has poor recall for short queries (3-5 word search misses semantically-related records). Upgrading to Ollama or Emergent embeddings is one env-flag away but costs tokens.
- Vector search uses cosine over `numpy.dot`; with > ~50k records you'll want an actual index (e.g. Atlas Search or a Mongo `$vectorSearch`).

### Recommended next step
Two trivial fixes: (1) expose `GET /api/membank/by-tag?tag=...` (the service method exists — just needs a route). (2) Add a daily TTL-eviction cron that drops `category in {ephemeral, telemetry}` records older than 7 days. Both are <1h.

---

## 7 · Graph Memory

**Status:** 🟡 **Partially implemented**

### Current capabilities ✅
- `graph_triples` collection with `(subject, relation, object, weight, source_memory_id)`.
- Auto-wiring on Knowledge Ingestion: concept↔tag, project↔concept, agent↔concept.
- Auto-wiring on Robot device registration: device-name↔twin_id (`bound_to`).
- Hebbian weight increment on revisit (the more often a triple is reinforced, the higher its weight).
- REST: `POST /api/membank/graph/triple · GET /api/membank/graph/triples?subject=&relation=`.

### Missing capabilities
- No graph traversal endpoint — querying "all concepts within 2 hops of `solar-panel`" requires multiple round trips.
- No path-finding — there is no "shortest concept-path between Ajani's domain and Minerva's domain" surface.
- No HUD visualisation — the graph exists but the user can only see it as JSON arrays.
- No automatic relation extraction from text — relations are template-driven (concept↔tag), not learned from prose.

### Known limitations
- Linear scan: queries are not indexed beyond `(subject, object, relation)` — a 10k-edge graph already takes ~30ms per traversal.
- No cycle detection — long-lived triple chains can self-reinforce indefinitely.

### Recommended next step
Add `GET /api/membank/graph/expand?subject=&depth=N&min_weight=W` that returns a BFS-bounded neighbourhood as `{nodes, edges}` ready for a force-directed layout (vis-network / sigma.js). Same endpoint serves the future HUD visualiser.

---

## 8 · Research Pipeline

**Status:** ✅ **Implemented**

### Current capabilities ✅
- DuckDuckGo web search (no key).
- Google Patents scraper (no key, `selectolax` based).
- PDF reader (`pypdf`) — accepts URL or base64 blob.
- Unified dispatcher `services/source_fetchers.fetch(url)` with type sniffing (`SourceType` enum).
- Every result auto-stored into MemoryBank category `research` (decaying).
- 503-with-hint behaviour on YouTube transcript cloud-IP block.
- Composable with the Knowledge Ingestion System — same fetchers, two consumers.

### Missing capabilities
- No academic API integration (arXiv, PubMed) — current "academic" classifier just routes to the web fetcher.
- No image / figure extraction from PDFs.
- No structured table extraction from web pages.
- No incremental crawl — every fetch is one-shot; there is no scheduler.

### Known limitations
- YouTube blocked on the cloud IP (graceful failure but real limitation).
- DuckDuckGo rate-limits aggressive bursts.
- Web scrapes don't render JavaScript (selectolax is HTML-only).

### Recommended next step
Wire arXiv's free API (`http://export.arxiv.org/api/query?…`) as a first-class `_fetch_arxiv` in `source_fetchers.py`. Direct quality bump for Minerva's domain. Two-hour task.

---

## 9 · Voice System

**Status:** ✅ **Implemented** (with one external dependency limitation)

### Current capabilities ✅
- `hooks/useVoiceRecognition.js` — 3 modes via the HUD mic chip: **off · push-to-talk · wake-word**.
- Wake phrases: `hey atlas`, `atlas`, `okay atlas`, `ok atlas`, plus persona names.
- `utils/voiceCommands.js::parseVoiceCommand()` — intents: `select-ai`, `open-section`, `close-panel`, **`ingest-url`**, `noop`.
- TTS surface: `/api/ai/voices` returns active provider; ElevenLabs preferred; OpenAI TTS fallback via `emergentintegrations`.
- Voice command "*ingest <URL>*" feeds the Knowledge Bank end-to-end with live transcript feedback in the HUD.

### Missing capabilities
- No streaming STT — recognition is one transcript at a time (browser Web Speech API limitation).
- No offline mode — Web Speech API needs network; we don't yet bundle `whisper.cpp`.
- No persona-specific voice selection — TTS uses one default voice per provider.
- No multi-turn dialog — every transcript is parsed in isolation, no chat context.

### Known limitations
- **ElevenLabs free tier blocks the cloud container IP** → currently using OpenAI TTS reliably as fallback. Real ElevenLabs voice will activate when deployed to a non-blocked IP / paid tier.
- Browser Web Speech API quality varies (Chrome > Safari > Firefox).
- Wake-word detection is text-match on already-transcribed audio — no actual on-device hot-word model.

### Recommended next step
Add an offline STT path using `whisper.cpp` exposed via a local provider (parallel to LMStudio in `llm_provider.py`). Same architecture, new "transcribe" verb. Unblocks the architect's eventual deployment to a no-internet site.

---

## 10 · HUD (Luxury Atlas Core interface)

**Status:** ✅ **Implemented**

### Current capabilities ✅
- 3 concentric drag-to-rotate rings (`AtlasCore.js`, `DialRing.js`).
- 50+ tiles across inner/middle/outer rings — all geometric positions locked per the architect's spec.
- Live functional tiles: Memory · Research · Twins · Weaver · Cyclopedia · Diagnostics (now hosts the Robot Control panel) · IntakePanel · Lessons · Quizzes · ArchiveBrowser · …
- Voice transcript ribbon (`.atlas-voice-transcript`) with live ingest feedback.
- AI face dock (bottom-centre) cycling through Ajani · Minerva · Hermes (selectable + voice-targetable).
- Mic toggle (top-right) cycling off → push-to-talk → wake-word.
- **Atlas Sentinel** ribbon (bottom-anchored, optional via localStorage) — WATER · AIR · SOIL chips with live telemetry every 12s + click-to-popover + SAFE_STATE red-pulse animation.
- Robot Control panel embedded inside SYSTEMS tile — role dropdown, device list with twin-bound badge, PING / ACTUATE / E-STOP / **CLEAR SAFE STATE** buttons.

### Missing capabilities
- No mobile / touch optimisation — desktop only.
- No drag-to-reorganise — tile positions are locked.
- No theme switcher — Luxury reskin is the only theme.
- No tile search — to find a specific tile you must remember which ring it lives in.
- Clear-safe-state confirmation uses `window.confirm()` (functional but outside the Luxury aesthetic).

### Known limitations
- Heavy CSS — the rings render ~120 transformed elements; on low-end GPUs this stutters.
- Some component lint warnings have been silenced rather than fixed (legacy CRA strict-mode issues).
- HUD geometry is locked per the architect — adding new top-level functionality means wiring into existing tiles (which is exactly what Phase-7 Robot Control + Sentinel did).

### Recommended next step
Replace `window.confirm()` in `RobotPanel.js`'s clear-safe-state flow with a glass-morphism Luxury-style modal (reuse the existing `.bp-synth-block` styling). One file, ~40 lines, closes the only visual inconsistency in Phase 7.

---

## 11 · Digital Twin

**Status:** ✅ **Implemented**

### Current capabilities ✅
- Registry: `POST /api/twins/register · GET /list · GET /{id} · PUT /{id}/state · DELETE /{id}`.
- 6 simulator engines: MECHANICAL · THERMAL · ELECTRICAL · CHEMICAL · OPTICAL · FAILURE (`services/twin_simulator.py`).
- Council deliberation: `POST /{id}/deliberate { agents: [...] }` — parallel agent voices + synthesised verdict.
- Auto-spawned project + research memories on every simulation.
- State revisions: arbitrary JSON state; Phase-7 Clear Safe State now patches `state.safety_history` directly.
- Used as the safety surface by Weaver (plan-time) AND Robot Control (run-time).

### Missing capabilities
- Simulators are heuristic / score-based — no actual physics solver (no FEA, no CFD, no SPICE).
- No HUD twin visualiser — twins are JSON only; no 3D model preview.
- No twin templates / library — every register call must specify state from scratch.

### Known limitations
- Simulator scores are 0–1 floats based on rule-of-thumb formulae; useful for relative ranking, not for absolute engineering validation.
- Failure simulator output drives Robot-Control's "validate ≥ 0.50" gate — tuning that threshold is currently manual.

### Recommended next step
Add a small twin template registry — 5–10 canned starting states ("solar buoy", "indoor greenhouse", "soil sensor", "drone arm", …) selectable on register. Cuts boilerplate and gives the HUD's IntakePanel a meaningful "Spawn Twin" dropdown.

---

## 12 · Weaver

**Status:** ✅ **Implemented**

### Current capabilities ✅
- `POST /api/weaver/plan { blueprint }` — full pipeline: parse → parts-enrich → twin-spawn → 4-simulator sweep (mechanical · thermal · failure · cost-sensitivity) → build/manufacturing/failure plans → optional council.
- Parts library: 25-row starter (`services/parts_db.py`); enriched on every plan with cost · vendor · lead-time.
- Blueprint parser tolerates natural-language and structured input.
- Outputs persist in `weaver_plans` collection + every plan auto-stored in MemoryBank `project` (permanent).
- Council voice fires automatically when the plan's twin failure score exceeds threshold.

### Missing capabilities
- No CAD / STL import — blueprints are text only.
- No live BOM editing in HUD — the Weaver tile shows plans but you cannot drag-and-drop parts.
- No supplier integration — `vendor` field is a free-text string, not a real catalog link.
- No cost-rollup currency conversion — assumes USD.

### Known limitations
- The starter parts library is small (25 rows) — exotic components fall back to LLM-imagined costs.
- The 4-simulator sweep is sequential — wall-clock ~6-12s per plan.

### Recommended next step
Add parts auto-enrichment from the Knowledge Bank — when a blueprint references an unknown part, the system would auto-ingest its product page (web fetcher) and add it to the parts library. Closes the loop between Knowledge Bank and Weaver.

---

## 13 · Robot Control

**Status:** ✅ **Implemented** (architect's hard spec met; broker swap planned)

### Current capabilities ✅
- Device registry, telemetry store, command pipeline at `/api/robot/*`.
- Roles: owner / council / ajani / minerva / hermes / guest via `X-Atlas-Role` header.
- Owner-only commands: actuate · motion · bind_twin · firmware_update · emergency_stop · **clear_safe_state**.
- **Simulation-first** command pipeline: authorise → device_lookup → simulate (Phase-5 twin) → validate (sim_score ≥ 0.50) → execute (MQTT-style HTTP bridge) → audit (Memory Bank).
- Idempotent seed of POSEIDON-BUOY · AETHER-STATION · SOIL-WATCH on startup, each auto-bound to its own `ENVIRONMENT` Digital Twin.
- Inbox poll endpoint with delivered-once semantics.
- Emergency Stop → SAFE_STATE; subsequent non-trivial commands blocked until cleared.
- **Clear Safe State** (owner-only, body.confirm=device.name, must-already-be-in-safe-state guard) → device flip + twin state.safety_history patch + permanent council Memory Bank entry.
- Full audit trail in `robot_commands` collection (every command, every pipeline step, with timestamps).
- HUD surface in two places: Robot Control panel (inside SYSTEMS tile) + Atlas Sentinel ribbon (live telemetry).
- 17/17 backend tests passing (10 Phase 7 + 7 Clear Safe State, plus 3 testing-agent extras and 3 membank wiring = 23 total robot tests passing).

### Missing capabilities
- HTTP-poll MQTT bridge — no real MQTT broker yet (`paho-mqtt` adapter planned).
- No ROS2 compatibility.
- No mTLS — devices authenticate by knowing their device-id, not by certificate.
- No OTA firmware mechanism — `firmware_update` is on the enum but the actual delivery channel is stubbed.
- No anomaly detection — telemetry just streams; nothing yet flips a chip amber when readings drift.

### Known limitations
- Soft role gate via header — fine for local LAN, must move to JWT for any internet deployment.
- Test runs accumulate ephemeral devices in `robot_devices` collection (no auto-cleanup).
- Inbox `delivered` flag is in-process — won't scale across multiple Atlas replicas (outbox-pattern needed).

### Recommended next step
Drop in `paho-mqtt` behind `services/robot._publish_command()` while keeping the REST surface identical. ESP32 firmware then becomes the more interesting deliverable — a 200-line C++ sketch that mirrors the inbox-poll protocol over MQTT.

---

## Summary table

| System | Status | Test coverage | Biggest gap |
| --- | --- | --- | --- |
| Ajani | 🟡 | distillation + council | No dedicated chat surface |
| Minerva | 🟡 | distillation + council | Cannot self-trigger research |
| Hermes | 🟡 | distillation + council | No optimiser primitive |
| Council | ✅ | full deliberate + verdict | Single-round only |
| Knowledge Bank | ✅ | 10/10 (`test_knowledge_ingestion.py`) | No HUD browser |
| Memory Bank | ✅ | regression + Phase-7 wiring | by-tag route missing |
| Graph Memory | 🟡 | embedded in kbase tests | No traversal endpoint |
| Research Pipeline | ✅ | covered via kbase | No arXiv API |
| Voice | ✅ | 10/10 parser + 4/4 e2e | ElevenLabs IP-blocked (OpenAI fallback works) |
| HUD | ✅ | smoke + Sentinel iter16 | `window.confirm()` outside aesthetic |
| Digital Twin | ✅ | `test_twins_phase5.py` | Heuristic sims, no real physics |
| Weaver | ✅ | `test_weaver_phase6.py` (15/15) | No CAD import |
| Robot Control | ✅ | 23/23 across 4 test files | No real MQTT broker |

---

## Top 5 next moves (cross-system priority)

1. **`POST /api/persona/{ajani|minerva|hermes}/chat`** — unblocks dedicated persona panels in the HUD; foundational for all three persona enhancements.
2. **`paho-mqtt` adapter** for Robot Control — turns Atlas from a simulator into a real-world bridge.
3. **`GET /api/membank/graph/expand?subject=&depth=N`** — unlocks future graph visualisation and is one of the most-requested traversal patterns across Council + Weaver + Knowledge use cases.
4. **arXiv fetcher in Research Pipeline** — direct quality bump for Minerva-tagged Knowledge Bank entries.
5. **Sentinel anomaly detection** — promote the bottom ribbon from passive ticker to a proactive guardian; ties together Robot Control, Memory Bank (envelope learning) and Council (auto-deliberate on drift).

---

_End of capability report. For implementation detail per system see the matching phase report under `/app/memory/`._
