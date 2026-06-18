# ATLAS · Reality Check Report
_Feb 2026 · brutally honest status — no sugar-coating_

> **Purpose.** Every prior report has been written to celebrate what's working.
> This one names the gaps. For each subsystem: what is **really** in
> production, what is **simulated** (returns plausible output but is a
> heuristic, not the real thing), what is a **placeholder**, what is
> **mocked**, and what is **tested with automated tests** vs. just verified
> by hand.
>
> **Definitions used in this document**
> - 🟢 **WORKING** — real implementation, real production code path
> - 🔵 **TESTED** — automated tests cover the path with named test files
> - 🟡 **SIMULATED** — returns plausible output via heuristic math / LLM call,
>   not the real-world physical/physics process
> - 🟠 **PLACEHOLDER** — stub code, hook that does nothing useful yet
> - 🔴 **MOCKED** — hardcoded data / fake values
> - ⚫ **NOT DONE** — not even a stub
>
> _If a subsystem has both WORKING and SIMULATED parts they are listed
> separately. Nothing is hidden in this document._

---

## 1 · Ajani

| Status | What |
| --- | --- |
| 🟢 WORKING | Voice prompt + persona registry · LLM routing via `services/llm_provider.send('ajani', ...)` · Knowledge-distiller routing on engineering/robotics/manufacturing keywords · Council fan-out voice |
| 🔵 TESTED | `test_persona_chat.py` (9 tests — single-persona chat, multi-turn, MB mirror) · `test_knowledge_ingestion.py` (Ajani-routed distillation) |
| 🟡 SIMULATED | "Personality" is an LLM system prompt — not a learned model. Voice consistency depends entirely on gpt-5.2 holding the prompt. Long answers drift. |
| 🟠 PLACEHOLDER | No tool-use, no self-triggered research, no autonomous behaviour. Ajani only acts when called. |
| 🔴 MOCKED | None |
| ⚫ NOT DONE | No "ask Ajani to build something" surface — Ajani never *plans*, only opines. No HUD identity card linked to chat. |

---

## 2 · Minerva

| Status | What |
| --- | --- |
| 🟢 WORKING | Same plumbing as Ajani (voice prompt, routing, council, chat) |
| 🔵 TESTED | `test_persona_chat.py` (parametrised across all three personas) |
| 🟡 SIMULATED | Same prompt-only personality caveat |
| 🟠 PLACEHOLDER | No experiment-design tool · no literature search · no citation graph. Minerva CONSUMES research handed to her — she does not RUN research. |
| 🔴 MOCKED | None |
| ⚫ NOT DONE | No "Bio-genesis" / "Nano-synthesis" sandboxes (architect-hinted future) · no arXiv-search-then-distill chain (arXiv fetcher exists but must be called with a URL) |

---

## 3 · Hermes

| Status | What |
| --- | --- |
| 🟢 WORKING | Same plumbing · council critique voice |
| 🔵 TESTED | `test_persona_chat.py` · council 3-voice fan-out test in `test_phase8_quad.py::test_ask_council_uses_persona_chat` |
| 🟡 SIMULATED | LLM-generated logic critique — no real formal verification |
| 🟠 PLACEHOLDER | No optimiser primitive · no Pareto-front · no SAT/SMT integration · no code-review pipeline (kbase only ingests GitHub README + metadata via `_fetch_github`, not source files) |
| 🔴 MOCKED | None |
| ⚫ NOT DONE | No `POST /api/hermes/optimize` (proposed in capability report) |

---

## 4 · Council

| Status | What |
| --- | --- |
| 🟢 WORKING | Parallel fan-out to all 3 personas via `asyncio.gather` · synthesis call with sub-voices in context · permanent MemoryBank entry per deliberation · auto-fire from `POST /api/robot/devices/{id}/ask-council` |
| 🔵 TESTED | Council branch in `test_persona_chat.py` · `test_phase8_quad.py::test_ask_council_uses_persona_chat` · iter18 4-row mirror test |
| 🟡 SIMULATED | Single-round deliberation. There is NO back-and-forth rebuttal — sub-voices speak once, then the council synthesises. Architect-spec'd multi-round is NOT implemented. |
| 🟠 PLACEHOLDER | No vote weighting (every voice carries equal weight) · no abstain / "need more data" path · verdict is always synthesised, even when sub-voices disagree heavily |
| 🔴 MOCKED | None |
| ⚫ NOT DONE | Autonomic Council (cron-fire on anomaly without a human click) |

---

## 5 · Knowledge Bank

| Status | What |
| --- | --- |
| 🟢 WORKING | `POST /api/kbase/ingest` · 6 source fetchers (GitHub · YouTube · PDF · Web · Patent · academic incl. arXiv) · LLM persona-voiced distillation · dedup-by-`sha256(normalised_url)` · reinforce-on-revisit · graph triple wiring · Voice "ingest <URL>" intent |
| 🔵 TESTED | `test_knowledge_ingestion.py` (10 tests) · `test_phase8_quad.py::test_arxiv_extract_id_via_full_url` · multi-sentence prompt → citation fix in `_fetch_knowledge` |
| 🟡 SIMULATED | LLM may hallucinate confidence scores on poorly-OCR'd PDFs — no Minerva-specific low-confidence escalation |
| 🟠 PLACEHOLDER | HUD browser — the Cyclopedia tile still shows the LEGACY 22-subject teaching index. The new ingested URL records are reachable only via `/api/kbase/search` |
| 🔴 MOCKED | None |
| ⚫ NOT DONE | Bulk import (CSV / OPML / sitemap) · revision history (re-ingest overwrites the old summary) · image / equation extraction from PDFs · arXiv author back-fill landed but only works on RE-ingest of the same URL |
| ⚠️ Known limitation | YouTube cloud-IP block → 503 with hint; GitHub anonymous quota 60 req/h |

---

## 6 · Memory Bank

| Status | What |
| --- | --- |
| 🟢 WORKING | 11 categories (4 permanent · 7 decaying) · cosine search · freshness decay · reinforce · `auto_store` used by Twin/Weaver/Robot/Knowledge/Research/Persona · REST: store/search/by-tag/reinforce/categories |
| 🔵 TESTED | Covered in iter16/17/18/19 + integration in every robot test |
| 🟡 SIMULATED | **Default 128-dim hash embedding is mostly noise.** Cosine recall on short queries is bad — this is why `by-tag` was added (the testing agent could not find rows via search). Real Ollama / Emergent embeddings work but are NOT the default (cost gate). |
| 🟠 PLACEHOLDER | **No TTL eviction.** Decaying records lose SCORE but never get DELETED. The DB grows monotonically. |
| 🔴 MOCKED | None |
| ⚫ NOT DONE | Cross-category dedup (the same insight can land in `research` AND `project` independently) · vector index for > ~50k records (cosine is full-scan today) |

---

## 7 · Graph Memory

| Status | What |
| --- | --- |
| 🟢 WORKING | `(from_node, to_node, relation, weight, source_id)` triples · `add_triple` · `GET /api/membank/graph/triples` · `GET /api/membank/graph/expand?depth=&min_weight=` BFS · Hebbian weight increment on revisit · auto-wired from Knowledge Ingestion + Robot device registration |
| 🔵 TESTED | 4 graph tests in `test_phase8_quad.py` (BFS shape · depth growth · min_weight filter · unknown-node fallback) |
| 🟡 SIMULATED | Relations are TEMPLATE-driven (concept↔tag, project↔concept, agent↔concept). The system does NOT extract relations from prose — every triple comes from a code path that explicitly creates it. |
| 🟠 PLACEHOLDER | **No HUD visualisation.** The data is ready for vis-network / sigma.js, but there is no UI yet. JSON only. |
| 🔴 MOCKED | None |
| ⚫ NOT DONE | Path-finding (shortest-path between two nodes) · cycle detection · graph-aware queries used by Council reasoning (Council currently uses cosine memory pull, not graph traversal) |

---

## 8 · Research Pipeline

| Status | What |
| --- | --- |
| 🟢 WORKING | DuckDuckGo web search (no key) · Google Patents scraper (selectolax) · `pypdf` PDF reader (URL or base64) · arXiv Atom API · unified `source_fetchers.fetch(url)` dispatcher · auto-store into `memory_bank` category `research` (decaying) |
| 🔵 TESTED | Via `test_knowledge_ingestion.py` + `test_phase8_quad.py::test_arxiv_extract_id_via_full_url` |
| 🟡 SIMULATED | None — real network calls |
| 🟠 PLACEHOLDER | "academic" classifier just routes non-arXiv hosts to the generic page scrape — no PubMed / Nature / ScienceDirect-specific extraction |
| 🔴 MOCKED | None |
| ⚫ NOT DONE | Image / figure / table extraction · incremental crawl (one-shot only) · arXiv full PDF body (we use the Atom abstract only) · JavaScript-rendered pages (selectolax is HTML-only) |
| ⚠️ Known limitation | **YouTube cloud-IP block** (architect-acknowledged) — 503 with hint; **DuckDuckGo** rate-limits aggressive bursts |

---

## 9 · Voice

| Status | What |
| --- | --- |
| 🟢 WORKING | `useVoiceRecognition.js` 3 modes (off / push-to-talk / wake-word) · `parseVoiceCommand` intents (select-ai · open-section · close-panel · ingest-url) · voice transcript ribbon · Web Speech API for STT |
| 🔵 TESTED | 10/10 voice-parser unit tests (`tests/voice_parser_iter16.cjs`) |
| 🟡 SIMULATED | **Wake-word detection is text-match on already-transcribed audio.** There is NO actual on-device hot-word model. The browser hears everything; we filter strings. |
| 🟠 PLACEHOLDER | TTS persona-specific voice selection (one default voice per provider — Ajani / Minerva / Hermes all sound identical when spoken) · no multi-turn dialog context for voice queries |
| 🔴 MOCKED | None |
| ⚫ NOT DONE | Offline STT (whisper.cpp local provider proposed but not built) · streaming STT (Web Speech API one-shot only) · voice → persona chat panel auto-open |
| ⚠️ Known limitation | **ElevenLabs free tier blocks cloud container IP.** Currently falls back to OpenAI TTS via `emergentintegrations` — a REAL fallback, not a mock. ElevenLabs will activate on non-blocked deployments. |

---

## 10 · HUD (Atlas Core Luxury reskin)

| Status | What |
| --- | --- |
| 🟢 WORKING | 3-ring drag-to-rotate · 50+ tiles · mic toggle · voice transcript bar · AI face dock · Atlas Sentinel ribbon · Persona Chat Panel (double-click face) · Robot Control panel embedded in SYSTEMS tile · Knowledge / Research / Twins / Weaver / Diagnostics tiles wired to live APIs |
| 🔵 TESTED | Smoke screenshots iter15-19 · Sentinel anomaly chip test in iter19 · Persona panel rendering verified via Playwright screenshot |
| 🟡 SIMULATED | None on the UI itself |
| 🟠 PLACEHOLDER | **Several tiles in `AtlasSidePanel.js` lines ~88-99 surface HARDCODED content lists** — e.g. 'Connected Devices': ['Primary Display', 'Audio Interface', 'Input Controller', 'External Sensors'] and 'Blueprint Gallery': ['System Architecture v3.2', 'Data Flow Model v2.1', …]. These are MOCKED display strings, not real data. The replaced/extended tiles (Memory · Research · Twins · Weaver · Cyclopedia · Diagnostics · Robot Control) are real. |
| 🔴 MOCKED | The `AtlasSidePanel` legacy-content map (above) · the AI face avatars are static PNGs · the central plasma sphere is a CSS animation with no live signal binding |
| ⚫ NOT DONE | Mobile / touch layout · tile search · graph viz tile · theme switcher |
| ⚠️ Known limitation | CSS-heavy: ~120 transformed elements stutter on low-end GPUs · `window.confirm()` in clear-safe-state flow is outside the Luxury aesthetic |

---

## 11 · Digital Twin

| Status | What |
| --- | --- |
| 🟢 WORKING | Registry · state revisions · 6 simulator engines · council deliberation · auto-spawn project + research memories per simulation · `bind-twin` from Robot Control · `state.safety_history` patch on Clear Safe State |
| 🔵 TESTED | `test_twins_phase5.py` · used by every robot pipeline test (sim_score check) |
| 🟡 SIMULATED | **ALL 6 SIMULATORS ARE HEURISTIC SCORE FORMULAS.** They are NOT real physics. No FEA, no CFD, no SPICE, no Monte Carlo. They return 0-1 floats via rule-of-thumb math (e.g. mechanical = function of mass + tolerance; failure = composition of subscores). Useful for RELATIVE ranking, useless for absolute engineering validation. **Anything labelled "sim_score" in Robot Control is one of these heuristics.** |
| 🟠 PLACEHOLDER | No 3D model preview · no twin templates / starter library (every register must specify state from scratch) |
| 🔴 MOCKED | None — heuristics are deterministic, not random fakes |
| ⚫ NOT DONE | Connection to a real solver (OpenFOAM / FEniCS / ngspice / etc.) |

---

## 12 · Weaver

| Status | What |
| --- | --- |
| 🟢 WORKING | Blueprint parse (natural-language tolerant) · parts enrich · twin spawn · 4-sim sweep (mechanical · thermal · failure · cost-sensitivity) · build/manufacturing/failure plans · optional council fire · plans persist in `weaver_plans` + MemoryBank `project` category |
| 🔵 TESTED | `test_weaver_phase6.py` (15 tests) |
| 🟡 SIMULATED | Sim sweep inherits the Digital Twin's heuristic caveat (#11). Parts library is 25 ROWS — anything beyond that gets LLM-imagined costs. |
| 🟠 PLACEHOLDER | No CAD / STL import (text blueprints only) · no live BOM editor in HUD (read-only display) · currency conversion (USD assumed) |
| 🔴 MOCKED | **Parts library `vendor` field is free-text** — no real supplier integration (no Digi-Key / Mouser API). Lead-times are starter-library guesses. |
| ⚫ NOT DONE | Parts auto-enrichment from Knowledge Bank when a blueprint references an unknown part (proposed) |

---

## 13 · Robot Control

| Status | What |
| --- | --- |
| 🟢 WORKING | Device registry · telemetry store · simulation-first command pipeline (`authorise → device_lookup → simulate → validate → execute`) · roles (owner / council / ajani / minerva / hermes / guest) · `X-Atlas-Role` header gate · EMERGENCY_STOP → SAFE_STATE · CLEAR_SAFE_STATE (owner + name-confirm + must-be-in-safe-state) · MQTT publish (best-effort, dormant w/o broker) · mTLS cert issuance · full audit trail in `robot_commands` + MemoryBank council category |
| 🔵 TESTED | 33 tests across `test_robot_phase7.py` (10) + `test_robot_clear_safe_state.py` (7) + `test_phase8_quad.py` (anomaly + mqtt-dormant) + `test_mtls_phase8f.py` (7) + `test_robot_membank_wiring.py` (3) |
| 🟡 SIMULATED | **The "execute" step writes a Command record + publishes to MQTT (if configured) + writes to the inbox.** It DOES NOT make any actuator move because no real device polls this inbox in the current deployment. The pipeline_log says "executed" — meaning Atlas considers itself to have dispatched the command, NOT that a physical actuator turned. The first time a real ESP32 polls the inbox, this changes from simulated to actually-physical. |
| 🟠 PLACEHOLDER | `firmware_update` CommandKind exists in the enum + role gate, but the delivery channel is a stub (no signed-bin pipeline) |
| 🔴 MOCKED | None on the backend. The HUD Robot Control panel uses real device data. |
| ⚫ NOT DONE | Real MQTT broker deployment (path exists, dormant) · ROS2 adapter · mTLS server-side enforcement (issuance works, `MTLS_ENFORCE=true` flips on the verify path — that path needs the FastAPI client-cert verification dependency wired) |
| ⚠️ Known limitation | Soft role gate via header — fine for local LAN, must be JWT for internet · ephemeral test devices accumulate in `robot_devices` (~5/run) — no cleanup script · inbox `delivered` flag is in-process — won't scale across replicas |

---

## 14 · Sentinel (Atlas Sentinel ribbon + Anomaly)

| Status | What |
| --- | --- |
| 🟢 WORKING | Bottom ribbon polling `/api/robot/devices` + telemetry every 12s · 3 chips (WATER / AIR / SOIL) with status colour + twin-bound badge · click → popover · Welford rolling mean+stddev per (device, telemetry-key) with 10-sample warmup · |z| ≥ 3.0 trips amber `is-anomaly` state · popover shows drifting keys + z-scores · "ask the council" button → `/api/robot/devices/{id}/ask-council` → `/api/persona/council/chat` → reply renders inline · localStorage-persisted dismiss |
| 🔵 TESTED | 4 anomaly tests in `test_phase8_quad.py` (warmup → outlier · envelope reset owner-only · ask-council shape · MQTT-dormant regression) · iter19 HUD smoke confirms amber state visible |
| 🟡 SIMULATED | The **telemetry being scored is whatever a test or curl call pushes**. No real sensor is feeding the seed devices in this env. The anomaly detection itself is real Welford math — but the data it learns from is currently synthetic. |
| 🟠 PLACEHOLDER | **Autonomic firing is NOT wired.** A human must click "ask the council" — the architect-proposed 60-second cron that auto-fires on every newly-tripped anomaly DOES NOT EXIST yet. |
| 🔴 MOCKED | None |
| ⚫ NOT DONE | Sparkline / historical-chart popovers · per-device threshold UI (sigma is configurable via `state.anomaly_sigma` but no UI to set it) · chip → drill-down to bound Digital Twin |

---

## 15 · ESP32 Integration

| Status | What |
| --- | --- |
| 🟢 WORKING | **Source code only.** `/app/firmware/esp32/atlas_device.ino` is real, complete Arduino sketch — Wi-Fi · HTTP-poll telemetry + inbox · all CommandKind handlers · local SAFE_STATE enforcement (refuses ACTUATE while safe_state==true) · optional MQTT subscribe behind `-DATLAS_ENABLE_MQTT` · optional mTLS constants. README documents the full flash workflow + safety contract table + per-target swaps. |
| 🔵 TESTED | **Nothing.** No real ESP32 has ever flashed this code. No automated tests. No verified Wi-Fi connection. No verified telemetry round-trip from real silicon. |
| 🟡 SIMULATED | **`read_sensors()` returns synthetic values** based on `millis()`-derived noise around plausible ranges. **`actuate()` is `Serial.print` only.** `actuate_safe()` is `Serial.print` only. To get real sensor reads / real actuation, the architect must replace these hooks with the actual sensor library calls (BME280, SCD40, DS18B20, etc.) and digital-write pins. |
| 🟠 PLACEHOLDER | `firmware_update` command handler logs "stub" and does nothing — real OTA needs a signed-bin download channel + `Update.begin/.write/.end()` calls. **`safe_state` does NOT persist across reboot** — every power-cycle resets it to `false` (architect flagged this). Persistence requires `Preferences` (NVS) — proposed but not implemented. |
| 🔴 MOCKED | The placeholder `read_sensors` reads ARE mocked synthetic values. |
| ⚫ NOT DONE | **Never flashed onto real hardware.** No mTLS PEM strings have ever been pasted into the constants. No MQTT broker has ever connected. No device has ever appeared in the Sentinel ribbon from a real ESP32. Currently the Sentinel shows seed devices that exist as DB rows only. |

---

## Aggregate honesty score

| Subsystem | Honest one-liner |
| --- | --- |
| Ajani / Minerva / Hermes | Prompt-driven LLM voices. They sound like personas because gpt-5.2 plays along. They have no autonomous behaviour. |
| Council | Real parallel fan-out, single-round only, no rebuttals. |
| Knowledge Bank | Fully real, but the HUD doesn't surface ingested records — still shows the legacy 22-subject index. |
| Memory Bank | Real, but **default embedding is noise**. By-tag is the reliable lookup; cosine recall on short queries is poor. |
| Graph Memory | Real triples, real BFS. **No visualisation.** Council does not yet use it for reasoning. |
| Research Pipeline | Real network calls. YouTube blocked by cloud IP. arXiv = Atom abstract only, no PDF body. |
| Voice | Real STT via Web Speech API + real OpenAI TTS fallback. **Wake-word is string-match, not a hot-word model.** ElevenLabs blocked by cloud IP. |
| HUD | Real, polished, locked geometry. **Several side-panel content lists are hardcoded display strings** (Connected Devices, Blueprint Gallery — `AtlasSidePanel.js` lines 88-99). |
| Digital Twin | **All 6 simulators are heuristic score formulas. There is no real physics in this system.** Sim scores are meaningful for ranking, not for engineering certification. |
| Weaver | Real pipeline. 25-row parts library; everything beyond gets LLM-imagined costs. |
| Robot Control | Real backend pipeline. **"Executed" means the inbox row was written — no real actuator has ever moved.** mTLS issuance works; enforcement is dormant. |
| Sentinel | Real Welford. **Data being scored is synthetic** (no real sensor feed). Autonomic firing is NOT wired — human click required. |
| ESP32 | **Real source code. Zero hardware contact.** Sensor reads + actuator drives are placeholders. Never flashed, never tested. |

---

## What "passing tests" actually means in this codebase

The 44/44 passing test count covers:
- **Backend API contracts** — every documented endpoint returns the documented shape and respects its role gate.
- **Pipeline orchestration** — Twin → Sim → Validate → Execute fires in the right order with the right side-effects.
- **Persistence integrity** — Memory Bank rows are written with the right category + tags · graph triples link correctly · sessions persist correctly.
- **Safety contracts** — Emergency Stop locks the device · Clear Safe State requires the exact device-name confirmation · cross-role boundaries are enforced.

It does NOT cover:
- Real hardware behaviour (no ESP32 has ever connected)
- Real sensor data (Sentinel sees only synthetic / pushed telemetry)
- Real physics (twin simulators are heuristics)
- Real-world reliability of LLM persona voices (gpt-5.2 may drift over long conversations)
- Real MQTT broker delivery (dormant — no broker deployed)
- Real mTLS enforcement (issuance only — `MTLS_ENFORCE=false` in v1)
- End-to-end from "I speak a sentence" → "actuator turns" (the chain is built but no one has walked it on real silicon)

---

## The shortest path from "tested" to "real"

1. **Flash one ESP32** with `atlas_device.ino`, point at the preview URL, replace `read_sensors()` with one real sensor read (BME280 is simplest). 30 minutes once the board is in hand.
2. **Verify Sentinel sees it.** That single observation moves ESP32 Integration from 🟠 PLACEHOLDER to 🟢 WORKING.
3. **Stand up an MQTT broker** (any Mosquitto in a Docker container). Set `MQTT_BROKER_HOST=<ip>` on the backend, set `MQTT_HOST` in the sketch with `-DATLAS_ENABLE_MQTT`. Verify push delivery via the chip's serial log.
4. **Set `MTLS_ENFORCE=true`** after pasting the issued PEMs into the sketch. Confirm the device still posts; confirm an un-certed curl gets 403.
5. **Hook a real actuator** — one solenoid valve, one relay, one stepper. The instant `actuate()` turns a thing, Robot Control moves from 🟡 SIMULATED-execute to 🟢 WORKING-execute.

After those 5 steps the only subsystems still genuinely simulated are the Digital Twin engines themselves (which are heuristic by design — real physics is a wholly different project).

---

_End of reality check. This document is the most accurate single description
of where ATLAS actually is in Feb 2026. Every prior phase report is true but
written with the optimism of "the path is built". This one is written with
the discipline of "the path has not yet been walked on real silicon"._
