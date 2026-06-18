# ATLAS · Truth Report

> **Feb 2026 · No sugar-coating · No optimism bias**
>
> Every subsystem is classified into exactly ONE primary status (the most
> honest single label) and may carry secondary callouts. **Evidence** for each
> classification is a file path + line range OR a verification-suite test ID
> OR a verbatim log line.
>
> **Classifications used in this document**
> | Symbol | Meaning |
> | ------ | ------- |
> | 🟢 **REAL** | Real implementation. Real production code path. Hits real systems (real network, real Mongo, real LLM). Tested. |
> | 🟡 **SIMULATED** | Returns plausible output via heuristic math or LLM call. NOT a fake — but NOT the real-world physical/physics process. |
> | 🟠 **PARTIAL** | The path is wired end-to-end, but some leg is dormant / behind a flag / missing a glue step. |
> | 🔴 **PLACEHOLDER** | Stub. The code is present but does nothing useful yet. Or returns hardcoded values. |
> | ⚫ **UNTESTED** | Not exercised by automated tests, AND not manually verified in this environment. May still be REAL in production. |
>
> Primary status is the one the architect / user would care about MOST.

---

## Index

| # | Subsystem | Primary status |
| - | --------- | -------------- |
| 1 | Ajani | 🟡 SIMULATED |
| 2 | Minerva | 🟡 SIMULATED |
| 3 | Hermes | 🟡 SIMULATED |
| 4 | Council | 🟢 REAL |
| 5 | Knowledge Bank | 🟢 REAL |
| 6 | Memory Bank | 🟠 PARTIAL |
| 7 | Graph Memory | 🟢 REAL |
| 8 | Research Pipeline | 🟢 REAL |
| 9 | Voice (STT + TTS + wake-word) | 🟠 PARTIAL |
| 10 | HUD (Atlas Core) | 🟠 PARTIAL |
| 11 | Digital Twin | 🟡 SIMULATED |
| 12 | Weaver (Build Planning) | 🟡 SIMULATED |
| 13 | Robot Control backend | 🟠 PARTIAL |
| 14 | Sentinel (anomaly ribbon) | 🟢 REAL |
| 15 | ESP32 firmware integration | ⚫ UNTESTED |
| 16 | MQTT bridge | 🔴 PLACEHOLDER (dormant) |
| 17 | mTLS | 🟠 PARTIAL (issuance-only) |
| 18 | Sentinel Autonomic Watcher | 🟢 REAL |
| 19 | ElevenLabs TTS | 🔴 PLACEHOLDER (cloud-IP blocked → fallback) |
| 20 | YouTube transcript ingestion | 🔴 PLACEHOLDER (cloud-IP blocked) |

---

## 1 · Ajani

**Primary: 🟡 SIMULATED**

| Aspect | Status | Evidence |
| ------ | ------ | -------- |
| LLM routing via `services/llm_provider.send('ajani', ...)` | 🟢 REAL | `test_03_persona_chat_voice_differentiation` (`[ajani] model_used: gpt-5.2`, `cited_memory_ids: [16389a07-…, 903ef8d0-…]`) |
| Persona "personality" | 🟡 SIMULATED | System prompt only. Not a learned model. `reply (first 140): "I build and break down real-world engineered systems—mechanisms, tolerances, supply chains, and failure modes…"` — gpt-5.2 is playing along, not a fine-tuned Ajani. |
| Knowledge-distiller routing on engineering keywords | 🟢 REAL | `test_02_knowledge_ingestion_github` (`related_agents: ["hermes"]` for whisper repo — router classified it correctly; would route engineering URLs to ajani) |
| Autonomous behaviour | 🔴 PLACEHOLDER | No tool-use, no self-triggered research. Ajani only acts when called. (`REALITY_CHECK_REPORT.md` §1) |
| HUD identity card linked to chat | ⚫ UNTESTED | Persona chat panel exists; identity card linkage not exercised in this suite |

**Why SIMULATED is primary.** The most important thing about Ajani — "the
voice" — is gpt-5.2 following a prompt. It is not a learned persona. It works
beautifully but it is not what a layperson would assume when told "we have an
AI named Ajani".

---

## 2 · Minerva

**Primary: 🟡 SIMULATED**

| Aspect | Status | Evidence |
| ------ | ------ | -------- |
| LLM routing + persona prompt | 🟢 REAL | `test_03` (`[minerva] model_used: gpt-5.2`, distinct reply confirmed by `all_3_replies_distinct: True`) |
| Persona personality | 🟡 SIMULATED | Same prompt-only caveat as Ajani. `reply (first 140): "I focus on rigorous, evidence-based engineering judgment for system architecture and reliability…"` |
| Experiment design tools | 🔴 PLACEHOLDER | None implemented (`REALITY_CHECK_REPORT.md` §2) |
| arXiv-search-then-distill chain | 🟠 PARTIAL | arXiv fetcher works (`test_05_research_pipeline_arxiv`), but must be called with a URL; no "search arXiv for X" flow yet |
| Literature search / citation graph | 🔴 PLACEHOLDER | None |
| Bio-genesis / Nano-synthesis sandboxes (architect-hinted) | ⚫ NOT DONE | Out of scope for Phase 8 |

---

## 3 · Hermes

**Primary: 🟡 SIMULATED**

| Aspect | Status | Evidence |
| ------ | ------ | -------- |
| LLM routing + persona prompt | 🟢 REAL | `test_03` (`[hermes] model_used: gpt-5.2`, distinct reply confirmed) |
| Council critique voice | 🟢 REAL | `test_phase8_quad.py::test_ask_council_uses_persona_chat` (sibling suite) |
| Logic critique | 🟡 SIMULATED | LLM-generated, not formal verification. No SAT/SMT integration. |
| Optimiser primitive / Pareto-front | 🔴 PLACEHOLDER | None (`REALITY_CHECK_REPORT.md` §3) |
| Code review pipeline | 🔴 PLACEHOLDER | `kbase` only ingests GitHub README + metadata via `_fetch_github`, not source files |
| `POST /api/hermes/optimize` | ⚫ NOT DONE | Proposed in capability report; not implemented |

---

## 4 · Council

**Primary: 🟢 REAL**

| Aspect | Status | Evidence |
| ------ | ------ | -------- |
| Parallel fan-out to 3 personas via `asyncio.gather` | 🟢 REAL | `services/persona_chat.py` Council branch. Each sub-voice produces a distinct reply. |
| Synthesis call | 🟢 REAL | Sub-voices passed into synthesis prompt context |
| Permanent MB entry per deliberation | 🟢 REAL | `test_09_sentinel_anomaly_and_council` (`autonomic_council_memory_count: 1`) |
| Auto-fire from `/api/robot/devices/{id}/ask-council` | 🟢 REAL | `test_09` (`watcher_fire-now.fired: 1`) |
| Multi-round rebuttal | 🟡 SIMULATED | Single-round only. No back-and-forth. (`REALITY_CHECK_REPORT.md` §4) |
| Vote weighting | 🔴 PLACEHOLDER | Every voice carries equal weight; no abstain path |
| Council uses Graph Memory for reasoning | 🔴 PLACEHOLDER | Council uses cosine pull, NOT BFS traversal |

**Why REAL is primary.** The mechanism (fan-out, synthesis, persistence,
auto-fire) is all real production code that ran successfully in the
verification suite. The "single-round" limitation is a SCOPE limitation, not
a fake.

---

## 5 · Knowledge Bank

**Primary: 🟢 REAL**

| Aspect | Status | Evidence |
| ------ | ------ | -------- |
| `POST /api/kbase/ingest` | 🟢 REAL | `test_02` (full GitHub ingest produced `knowledge_entry_id: 691fa4b6…`) |
| 6 source fetchers (GitHub · YouTube · PDF · Web · Patent · academic incl. arXiv) | 🟢 REAL | GitHub (`test_02`), arXiv (`test_05`) — both verified |
| LLM persona-voiced distillation | 🟢 REAL | `test_02` produced 24+ concepts including domain-correct terms ("transformer encoder-decoder", "multitask training", …) |
| Dedup-by-`sha256(normalised_url)` | 🟢 REAL | `test_02` `reinforce_count: 11` — same URL revisited, no dup row |
| Reinforce-on-revisit | 🟢 REAL | `reinforce_count: 11` proves revisits worked |
| Graph triple wiring | 🟢 REAL | `test_02` `graph_edges_around_root: 16`; `test_05` `graph_edges_for_first_concept: 19` |
| Voice "ingest <URL>" intent | 🟢 REAL | `tests/voice_parser_iter16.cjs` 10/10 |
| HUD browser surfacing of ingested records | 🔴 PLACEHOLDER | Cyclopedia tile still shows the LEGACY 22-subject teaching index; ingested records reachable only via `/api/kbase/search` |
| YouTube fetcher | 🔴 PLACEHOLDER on cloud IP | Cloud-IP block → graceful 503 with hint (`REALITY_CHECK_REPORT.md` §5) |

---

## 6 · Memory Bank

**Primary: 🟠 PARTIAL**

| Aspect | Status | Evidence |
| ------ | ------ | -------- |
| 11 categories (4 permanent · 7 decaying) | 🟢 REAL | `services/memory.py` |
| Write/read round-trip | 🟢 REAL | `test_01_memory_persistence_across_restart` (`VERDICT: PASS — write + read round-trip via by-tag`) |
| `auto_store` used by Twin/Weaver/Robot/Knowledge/Research/Persona | 🟢 REAL | Every other test wrote MB rows as side effect |
| REST: store/search/by-tag/reinforce/categories | 🟢 REAL | `test_01` retrieved by-tag successfully |
| **Default 128-dim hash embedding** | 🟡 SIMULATED | "Mostly noise" — cosine recall on short queries is bad. This is why `by-tag` was added (the testing agent could not find rows via search). |
| Ollama / Emergent embedding fallback | 🟠 PARTIAL | Code path exists; not the default (cost gate). `ATLAS_EMBED_PROVIDER=ollama` is a P2 toggle. |
| TTL eviction for decaying categories | 🔴 PLACEHOLDER | Score decays but rows are never DELETED. DB grows monotonically. |
| Cross-category dedup | 🔴 PLACEHOLDER | Same insight can land in `research` AND `project` independently |
| Vector index for > ~50k records | ⚫ NOT DONE | Cosine is full-scan today |

**Why PARTIAL is primary.** The "fundamental thing" — write to MB and read it
back — is REAL and tested. BUT the default embedding is so noisy that
cosine retrieval is the user-facing weak link. Users see a "memory bank that
forgets" because cosine doesn't match short queries, even though the data is
there (by-tag finds it instantly).

---

## 7 · Graph Memory

**Primary: 🟢 REAL**

| Aspect | Status | Evidence |
| ------ | ------ | -------- |
| Triple model `(from, to, relation, weight, source_id)` | 🟢 REAL | `services/graph.py` |
| `GET /api/membank/graph/triples` | 🟢 REAL | `test_04_graph_traversal_depth_3` returned `edge_count: 15` |
| `GET /api/membank/graph/expand?depth=&min_weight=` BFS | 🟢 REAL | `test_04` `depth-3 reached verify-c: True` |
| Hebbian weight increment on revisit | 🟢 REAL | Implemented in `add_triple`; reinforced via kbase reinforce path |
| Auto-wired from Knowledge Ingestion | 🟢 REAL | `test_02` graph_edges_around_root: 16 |
| Auto-wired from Robot device registration | 🟢 REAL | `services/robot.py` `_register_device_in_graph` |
| Relation extraction from prose | 🔴 PLACEHOLDER | All triples come from code paths that EXPLICITLY create them. No NER/RE. |
| HUD visualisation | 🔴 PLACEHOLDER | Data ready; no UI yet. JSON only. |
| Path-finding (shortest-path) | ⚫ NOT DONE | |
| Council uses graph for reasoning | 🔴 PLACEHOLDER | Council currently uses cosine pull |

---

## 8 · Research Pipeline

**Primary: 🟢 REAL**

| Aspect | Status | Evidence |
| ------ | ------ | -------- |
| DuckDuckGo web search (no key) | 🟢 REAL | `services/source_fetchers.py` |
| Google Patents scraper (selectolax) | 🟢 REAL | Implemented; tested in iter15 |
| `pypdf` PDF reader (URL or base64) | 🟢 REAL | Implemented |
| arXiv Atom API | 🟢 REAL | `test_05` (`source_type: academic`, full author list "Alec Radford, Jong Wook Kim, Tao Xu, Greg Brockman, Christine McLeavey, Ilya Sutskever") |
| Auto-store into `memory_bank` category=`research` | 🟢 REAL | Mirror created in `test_02` |
| YouTube transcript | 🔴 PLACEHOLDER | Cloud-IP blocked → 503 with hint |
| "academic" classifier for non-arXiv hosts | 🟠 PARTIAL | Routes to generic page scrape, no PubMed/Nature/ScienceDirect specifics |
| arXiv full PDF body | ⚫ NOT DONE | Atom abstract only |
| JS-rendered pages | ⚫ NOT DONE | selectolax is HTML-only |
| Incremental crawl | ⚫ NOT DONE | One-shot only |

---

## 9 · Voice (STT + TTS + wake-word)

**Primary: 🟠 PARTIAL**

| Aspect | Status | Evidence |
| ------ | ------ | -------- |
| `useVoiceRecognition.js` 3 modes (off / push-to-talk / wake-word) | 🟢 REAL | Implemented |
| Voice intent parser (select-ai · open-section · close-panel · ingest-url) | 🟢 REAL | `tests/voice_parser_iter16.cjs` 10/10 |
| Web Speech API STT | 🟢 REAL | Browser-native |
| OpenAI TTS via `emergentintegrations` | 🟢 REAL | Active fallback (not a mock) |
| **Wake-word detection** | 🟡 SIMULATED | Text-match on already-transcribed audio. NO actual on-device hot-word model. Browser hears everything; we filter strings. |
| Persona-specific TTS voices (Ajani/Minerva/Hermes sound distinct when spoken) | 🔴 PLACEHOLDER | One default voice per provider — all 3 sound identical |
| ElevenLabs TTS | 🔴 PLACEHOLDER (cloud-IP blocked) | Free tier blocks cloud container IP; falls back to OpenAI TTS |
| Offline STT (whisper.cpp local) | ⚫ NOT DONE | Proposed |
| Streaming STT | ⚫ NOT DONE | Web Speech API one-shot only |

**Why PARTIAL is primary.** STT + TTS + intent parsing all work. But wake-word
is a string-match (not a hot-word model), and persona-specific voices don't
actually sound different. The user-facing experience is partial.

---

## 10 · HUD (Atlas Core Luxury reskin)

**Primary: 🟠 PARTIAL**

| Aspect | Status | Evidence |
| ------ | ------ | -------- |
| 3-ring drag-to-rotate | 🟢 REAL | Implemented; iter15-19 screenshots |
| 50+ tiles | 🟢 REAL | |
| Voice transcript bar | 🟢 REAL | |
| AI face dock + Persona Chat Panel (double-click face) | 🟢 REAL | iter19 Playwright |
| Atlas Sentinel ribbon | 🟢 REAL | `test_10` Sentinel endpoints live |
| Knowledge / Research / Twins / Weaver / Diagnostics tiles | 🟢 REAL | `test_10` — every panel endpoint returns `status: 200, live: true` |
| Robot Control panel embedded in SYSTEMS tile | 🟢 REAL | `test_10` (`RobotPanel /robot/devices?limit=10 status=200 live=true size=7402`) |
| **Several tiles in `AtlasSidePanel.js` lines ~88-99** | 🔴 PLACEHOLDER | HARDCODED display strings: `'Connected Devices': ['Primary Display', 'Audio Interface', 'Input Controller', 'External Sensors']`, `'Blueprint Gallery': ['System Architecture v3.2', 'Data Flow Model v2.1', …]` |
| AI face avatars | 🔴 PLACEHOLDER | Static PNGs (no live state binding) |
| Central plasma sphere | 🔴 PLACEHOLDER | CSS animation with no live signal binding |
| Mobile / touch layout | ⚫ NOT DONE | |
| Graph viz tile | ⚫ NOT DONE | Data ready, UI not built |

---

## 11 · Digital Twin

**Primary: 🟡 SIMULATED**

| Aspect | Status | Evidence |
| ------ | ------ | -------- |
| Registry + state revisions | 🟢 REAL | `test_06_digital_twin_lifecycle` (`twin_id: 611b563a…, revision: 3`) |
| **All 6 simulator engines** | 🟡 SIMULATED | `test_06` `VERDICT: 🟡 SIMULATED — heuristic simulator engine, not real physics`. **NO FEA, no CFD, no SPICE, no Monte Carlo.** Returns 0-1 floats via rule-of-thumb math. Useful for ranking, useless for absolute engineering validation. |
| Council deliberation per simulation | 🟢 REAL | (uses Council, see §4) |
| Auto-spawn project + research memories per simulation | 🟢 REAL | `services/twin.py` writes MB rows |
| `bind-twin` from Robot Control | 🟢 REAL | `test_robot_phase7.py` |
| `state.safety_history` patch on Clear Safe State | 🟢 REAL | `test_08` `clear.status_code: 200` |
| 3D model preview | 🔴 PLACEHOLDER | |
| Twin templates / starter library | 🔴 PLACEHOLDER | Every register must specify state from scratch |
| Connection to real solver (OpenFOAM / FEniCS / ngspice) | ⚫ NOT DONE | |

**Why SIMULATED is primary.** The verdict line says it: "heuristic simulator
engine, not real physics". Every twin sim score is rule-of-thumb math. The
PIPELINE around the simulator is real, but the simulator itself is heuristic
by design.

---

## 12 · Weaver (Build Planning)

**Primary: 🟡 SIMULATED**

| Aspect | Status | Evidence |
| ------ | ------ | -------- |
| Blueprint parse (NL-tolerant) | 🟢 REAL | `test_07_weaver_plan_from_twin` produced 10-step plan |
| Twin spawn from blueprint | 🟢 REAL | `test_07` `twin_id (spawned): 66c0c7cf…` |
| 4-sim sweep (mechanical · thermal · failure · cost-sensitivity) | 🟢 REAL pipeline, 🟡 SIMULATED math | Inherits Twin's heuristic caveat |
| Build / manufacturing / failure plan synthesis | 🟢 REAL | `test_07` `build_plan_steps: 10` |
| Plan persistence in `weaver_plans` | 🟢 REAL | `test_07` `plan_id: 88d9ffb3…` |
| MB `project` category mirror | 🟠 PARTIAL | `test_07` `memory_rows_for_plan: 0` — plan persisted in `weaver_plans` but no row keyed to this plan_id in MB at check time. Other tests in `test_weaver_phase6.py` show this normally fires; this run's specific tag query missed it. |
| **25-row parts library** | 🟡 SIMULATED | Anything beyond gets LLM-imagined costs. `test_07` `parts_sample (first 3): [null, null, null]` proves unknown parts get null vendor/SKU. |
| **Risk count** | ⚠️ Observation | `test_07` `risks_count: 0` — simple blueprint produced zero risks |
| CAD / STL import | 🔴 PLACEHOLDER | Text blueprints only |
| Live BOM editor in HUD | 🔴 PLACEHOLDER | Read-only display |
| Digi-Key / Mouser API | 🔴 PLACEHOLDER | Vendor field is free-text |
| Currency conversion | 🔴 PLACEHOLDER | USD assumed |

**Why SIMULATED is primary.** The verdict line says it: "heuristic
costs/lead-times for unknown parts (25-row library)". Until a real parts API
is wired, Weaver's outputs ARE plausible-sounding heuristics for the
out-of-library parts.

---

## 13 · Robot Control backend

**Primary: 🟠 PARTIAL**

| Aspect | Status | Evidence |
| ------ | ------ | -------- |
| Device registry | 🟢 REAL | `test_08` `device_id: e12b868b…` |
| Telemetry store | 🟢 REAL | `test_10` `/telemetry status=200 live=true` |
| Simulation-first command pipeline (`authorise → device_lookup → simulate → validate → execute`) | 🟢 REAL | `test_08` `owner_ping.pipeline_steps: ["authorise", "validate", "execute"]` |
| Role gate via `X-Atlas-Role` header | 🟢 REAL | `test_08` `guest_actuate.status: rejected, reason: "command 'actuate' is owner-only (got role=guest)"` |
| EMERGENCY_STOP → SAFE_STATE | 🟢 REAL | `test_08` `e-stop.status: safe_state` |
| Actuate refused in SAFE_STATE | 🟢 REAL | `test_08` `actuate_in_safe_state.status: rejected, reason: "device is in SAFE_STATE — clear it first via owner"` |
| CLEAR_SAFE_STATE (owner + name-confirm) | 🟢 REAL | `test_08` `clear.status_code: 200` |
| Full audit trail | 🟢 REAL | `test_08` `audit_command_count: 4, audit_kinds: ["clear_safe_state", "actuate", "ping", "actuate"]` |
| **`execute` step writes to inbox** | 🟡 SIMULATED | `test_08` verdict notes "execute is SIMULATED — no real actuator wired". The pipeline considers the command DISPATCHED — but no real device polls the inbox in this deployment. The first time a real ESP32 polls the inbox, this flips to REAL. |
| `firmware_update` CommandKind | 🔴 PLACEHOLDER | Enum + role gate exist; delivery channel is a stub (no signed-bin pipeline) |
| MQTT publish | 🔴 PLACEHOLDER (dormant) | Best-effort if `MQTT_BROKER_HOST` set; no broker deployed |
| mTLS server-side verify | 🟠 PARTIAL | Issuance works; verify path is dormant (`MTLS_ENFORCE=false`) |
| ROS2 adapter | ⚫ NOT DONE | |
| Inbox `delivered` flag | ⚠️ in-process only | Won't scale across replicas |
| Ephemeral test-device cleanup | ⚠️ partial | Manual script exists |

**Why PARTIAL is primary.** Every safety contract is REAL and tested. But
the headline action — "the robot does the thing" — is SIMULATED because no
real device is wired. The instant one ESP32 polls the inbox, this flips to
REAL.

---

## 14 · Sentinel (Atlas Sentinel ribbon)

**Primary: 🟢 REAL**

| Aspect | Status | Evidence |
| ------ | ------ | -------- |
| Bottom ribbon polling `/api/robot/devices` + telemetry every 12s | 🟢 REAL | `test_10` SentinelPanel `/robot/devices status=200 live=true` |
| 3 chips (WATER / AIR / SOIL) | 🟢 REAL | iter19 HUD smoke |
| Welford rolling mean+stddev per (device, key) with 10-sample warmup | 🟢 REAL | `test_09` `envelope.n_after_warmup: 12, anomaly_before_outlier: None` |
| |z| ≥ 3.0 trips anomaly | 🟢 REAL | `test_09` `z_scores: {"co2": 36115.029}, sigma_threshold: 3.0` |
| Popover shows drifting keys + z-scores | 🟢 REAL | iter19 |
| "Ask the council" button | 🟢 REAL | `test_09` autonomic path also fires this same route |
| Council reply rendered inline | 🟢 REAL | `test_09` `autonomic_council_memory_count: 1` |
| localStorage-persisted dismiss | 🟢 REAL | |
| **Telemetry data being scored** | 🟡 SIMULATED | Welford math is real; data in this run was test-pushed, not from a physical sensor |
| Sparkline / historical chart popovers | 🔴 PLACEHOLDER | |
| Per-device threshold UI | 🔴 PLACEHOLDER | `state.anomaly_sigma` configurable via API but no UI |
| Chip → drill-down to bound twin | ⚫ NOT DONE | |

---

## 15 · ESP32 firmware integration

**Primary: ⚫ UNTESTED**

| Aspect | Status | Evidence |
| ------ | ------ | -------- |
| `/app/firmware/esp32/atlas_device.ino` (full Arduino sketch) | 🟢 REAL **source code** | File exists, compiles in theory |
| Wi-Fi connect, HTTP-poll telemetry + inbox | 🟢 REAL source | (not executed) |
| All CommandKind handlers | 🟢 REAL source | (not executed) |
| Local SAFE_STATE enforcement | 🟢 REAL source | (not executed) |
| Optional MQTT subscribe behind `-DATLAS_ENABLE_MQTT` | 🟢 REAL source | (not executed) |
| Optional mTLS constants | 🟢 REAL source | (not executed) |
| README with flash workflow, safety contract table, per-target swaps | 🟢 REAL | `/app/firmware/esp32/README.md` |
| **`read_sensors()`** | 🔴 PLACEHOLDER | Returns synthetic values based on `millis()`-derived noise. To get real reads, replace hooks with sensor library calls (BME280, SCD40, DS18B20, …). |
| **`actuate()` / `actuate_safe()`** | 🔴 PLACEHOLDER | `Serial.print` only. To turn a thing, wire `digitalWrite` to a pin. |
| `firmware_update` command handler | 🔴 PLACEHOLDER | Logs "stub" and does nothing |
| `safe_state` persistence across reboot | 🔴 PLACEHOLDER | Every power-cycle resets to false. Requires `Preferences` (NVS). |
| **Has any real ESP32 ever flashed this?** | ⚫ UNTESTED | **No.** Zero hardware contact. No verified Wi-Fi, no verified round-trip. |

**Why UNTESTED is primary.** The source code is real and complete. But no
real silicon has ever run it. Until one does, this is the single biggest
"believed-real-but-actually-unproven" surface in ATLAS.

---

## 16 · MQTT bridge

**Primary: 🔴 PLACEHOLDER (dormant)**

| Aspect | Status | Evidence |
| ------ | ------ | -------- |
| `paho-mqtt` adapter (`services/mqtt_bridge.py`) | 🟢 REAL source | |
| Best-effort publish on every robot command | 🟢 REAL source | |
| Broker subscribe for telemetry ingest | 🟢 REAL source | |
| Falls back gracefully if `MQTT_BROKER_HOST` not set | 🟢 REAL | `test_phase8_quad.py` regression (MQTT-dormant) |
| **Real broker deployed in this environment** | ⚫ NOT DONE | Code path is dormant |
| **Real device subscribed** | ⚫ NOT DONE | |

---

## 17 · mTLS

**Primary: 🟠 PARTIAL (issuance-only)**

| Aspect | Status | Evidence |
| ------ | ------ | -------- |
| `cryptography`-based CA + cert issuance | 🟢 REAL | `services/mtls.py`, `test_mtls_phase8f.py` (7 tests) |
| Cert persisted in `mtls_certificates` | 🟢 REAL | |
| **Server-side request verification** | 🟠 PARTIAL | Code path exists; only enforced when `MTLS_ENFORCE=true`. In this env it's false. Issuance is exercised; verify is dormant. |
| **Revocation list** | ⚫ NOT DONE | No CRL/OCSP |
| **Cert paste into ESP32** | ⚫ UNTESTED | Constants exist in firmware; no device has pasted real PEMs |

---

## 18 · Sentinel Autonomic Watcher

**Primary: 🟢 REAL**

| Aspect | Status | Evidence |
| ------ | ------ | -------- |
| 60s cron task (`services/sentinel_watcher.py`) | 🟢 REAL | `test_09` `watcher_fire-now.examined: 9, fired: 1` |
| Examines `hardware_devices.state.anomaly_envelope` | 🟢 REAL | `test_09` |
| Auto-fires `/api/robot/devices/{id}/ask-council` on new envelope | 🟢 REAL | `test_09` `autonomic_council_memory_count: 1` |
| De-duplication on already-fired envelope | 🟢 REAL | (sibling test in `test_sentinel_watcher.py`) |
| **Production cron driver** | 🟠 PARTIAL | Implemented as a periodic task within the FastAPI process; in-process scheduler. Survives restart but not horizontally scaled. |

---

## 19 · ElevenLabs TTS

**Primary: 🔴 PLACEHOLDER (cloud-IP blocked → fallback active)**

| Aspect | Status | Evidence |
| ------ | ------ | -------- |
| ElevenLabs SDK integration | 🟢 REAL source | |
| **Cloud-container IP is blocked by ElevenLabs free tier** | 🔴 BLOCKED | Known limitation |
| Fallback to OpenAI TTS via `emergentintegrations` | 🟢 REAL | Active in this deployment — this is a REAL fallback, not a mock |
| **Will activate on non-blocked deployment** | ⚫ UNTESTED | No proof in current env |

---

## 20 · YouTube transcript ingestion

**Primary: 🔴 PLACEHOLDER (cloud-IP blocked)**

| Aspect | Status | Evidence |
| ------ | ------ | -------- |
| `youtube_transcript_api` integration | 🟢 REAL source | |
| **Cloud-container IP is blocked by YouTube** | 🔴 BLOCKED | Known limitation |
| Graceful error → 503 with hint | 🟢 REAL | Endpoint returns user-facing warning, not silent failure |

---

## Aggregate truth table

| Status | Count | Subsystems |
| ------ | ----- | ---------- |
| 🟢 REAL | 6 | Council, Knowledge Bank, Graph Memory, Research Pipeline, Sentinel ribbon, Sentinel Watcher |
| 🟡 SIMULATED | 5 | Ajani, Minerva, Hermes, Digital Twin, Weaver |
| 🟠 PARTIAL | 4 | Memory Bank, Voice, HUD, Robot Control, mTLS |
| 🔴 PLACEHOLDER | 3 | MQTT bridge, ElevenLabs TTS, YouTube ingestion |
| ⚫ UNTESTED | 1 | ESP32 firmware integration |

*(Note: a subsystem can be 🟢 REAL primarily and still have 🔴 PLACEHOLDER /
🟡 SIMULATED **sub-features** — see the detailed tables above. The roll-up
here counts the PRIMARY label only.)*

---

## What "🟢 REAL across the board" would require

The shortest path from current state to "every primary label is 🟢 REAL":

1. **Flash one ESP32 with `atlas_device.ino`** pointed at the preview URL.
   Replace `read_sensors()` with a single real sensor read (BME280 is
   simplest). Verify Sentinel sees it. → flips ESP32 from ⚫ to 🟢.
2. **Stand up a Mosquitto broker** anywhere reachable. Set
   `MQTT_BROKER_HOST=<ip>` on backend and `-DATLAS_ENABLE_MQTT` on the
   sketch. → flips MQTT from 🔴 to 🟢.
3. **Set `MTLS_ENFORCE=true`** after pasting issued PEMs. Confirm an
   un-certed curl gets 403. → flips mTLS from 🟠 to 🟢.
4. **Wire one solenoid valve OR one relay OR one stepper** to the ESP32.
   The instant `actuate()` turns a real thing, Robot Control execute step
   flips from 🟡 to 🟢, which flips Robot Control primary from 🟠 to 🟢.
5. **Switch `ATLAS_EMBED_PROVIDER=ollama`** (or paid Emergent embeddings).
   Memory Bank cosine recall becomes useful → flips Memory Bank from 🟠 to
   either 🟢 or stays 🟠 pending TTL eviction implementation.
6. **Build the HUD graph-viz tile** + delete `AtlasSidePanel.js` legacy
   hardcoded lists → flips HUD from 🟠 to 🟢.
7. **Move ElevenLabs to a deployment whose IP is not blocked** → flips
   ElevenLabs from 🔴 to 🟢. (Or accept OpenAI TTS as the production voice.)
8. **YouTube ingestion** cannot be flipped to 🟢 in any cloud container —
   YouTube blocks ALL cloud IPs. Either route through a residential proxy or
   classify this as PERMANENTLY 🔴 by design.

The 🟡 SIMULATED items (Personas, Twin, Weaver) are 🟡 BY DESIGN. Personas
need a different model architecture (fine-tune or RAG-only) to become 🟢.
Twin/Weaver need real solvers (FEniCS / OpenFOAM / Digi-Key API) which are a
separate project entirely.

---

_End of truth report. Sister documents:_
- `/app/memory/ATLAS_VERIFICATION_RESULTS.md` (raw test evidence)
- `/app/memory/ATLAS_INTEGRATION_PLAN.md` (5 macro flows)
- `/app/memory/ATLAS_DATA_FLOW.md` (collection-level data movement)
- `/app/memory/REALITY_CHECK_REPORT.md` (Feb 2026 honest status — companion)
