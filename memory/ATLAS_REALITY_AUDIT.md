# ATLAS · Reality Audit

> **2026-06-18 · Updated to include Watcher Systems + Self-Improvement.**
> Every subsystem is classified using exactly the five labels the user
> requested. Evidence per row is a file path + line range, OR a test/run ID
> from the verification suite or live test, OR a verbatim log/curl response.

| Symbol | Label | Definition |
| ------ | ----- | ---------- |
| 🟢 | **REAL** | Real implementation, real production code path, exercised by an automated or live test with persisted IDs. |
| 🟠 | **PARTIAL** | The path is wired end-to-end, but some leg is dormant / behind a flag / missing a glue step. |
| 🟡 | **SIMULATED** | Returns plausible output via heuristic math or LLM call. Not a fake — but not the real-world physical/physics process. |
| 🔴 | **PLACEHOLDER** | Stub. Code present but does nothing useful yet, or returns hardcoded values. |
| ⚫ | **UNTESTED** | Not exercised by automated tests, AND not manually verified in this environment. May still be REAL in production. |

---

## Index — 22 subsystems

| # | Subsystem | Primary label |
| -: | --------- | ------------- |
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
| 12 | Weaver | 🟡 SIMULATED |
| 13 | Robot Control backend | 🟠 PARTIAL |
| 14 | Sentinel ribbon | 🟢 REAL |
| 15 | ESP32 firmware | ⚫ UNTESTED |
| 16 | MQTT bridge | 🔴 PLACEHOLDER |
| 17 | mTLS | 🟠 PARTIAL |
| 18 | Sentinel Autonomic Watcher | 🟢 REAL |
| 19 | ElevenLabs TTS | 🔴 PLACEHOLDER |
| 20 | YouTube transcript ingestion | 🔴 PLACEHOLDER |
| **21** | **GitHub Knowledge Watcher (new)** | **🟢 REAL** |
| **22** | **Self-Improvement Watcher (new)** | **🟢 REAL** |

**Roll-up**
| Label | Count | Subsystems |
| ----- | :---: | ---------- |
| 🟢 REAL | **8** | Council · Knowledge Bank · Graph Memory · Research Pipeline · Sentinel ribbon · Sentinel Autonomic Watcher · **GitHub Knowledge Watcher** · **Self-Improvement Watcher** |
| 🟡 SIMULATED | 5 | Ajani · Minerva · Hermes · Digital Twin · Weaver |
| 🟠 PARTIAL | 5 | Memory Bank · Voice · HUD · Robot Control · mTLS |
| 🔴 PLACEHOLDER | 3 | MQTT bridge · ElevenLabs TTS · YouTube transcript |
| ⚫ UNTESTED | 1 | ESP32 firmware |

---

## Section A · subsystems 1–20 (unchanged from `ATLAS_TRUTH_REPORT.md`)

> The audit for subsystems 1–20 is verbatim from `ATLAS_TRUTH_REPORT.md`
> (same evidence, same primary labels). Cross-reference that file for the
> full per-row tables. Summarised here so the audit is self-contained.

### 1–3 · Personas (Ajani, Minerva, Hermes) — 🟡 SIMULATED
- **Real plumbing.** `services/llm_provider.send(persona, ...)` → gpt-5.2 via Emergent universal key.
- **Why simulated.** The "personality" is a system prompt; gpt-5.2 plays along but no learned model exists.
- **Evidence.** `test_03_persona_chat_voice_differentiation` — `all_3_replies_distinct: True`, `model_used: gpt-5.2`, distinct `cited_memory_ids` per persona (`/tmp/atlas_verify.log` lines 67-99).

### 4 · Council — 🟢 REAL
- **Evidence.** `test_09_sentinel_anomaly_and_council` — `watcher_fire-now.fired: 1`, `autonomic_council_memory_count: 1` (`/tmp/atlas_verify.log` lines 233-255).
- **Caveat.** Single-round only (no rebuttals), uses cosine pull not graph BFS. Caveats live as 🔴 PLACEHOLDER sub-features in `REALITY_CHECK_REPORT.md` §4.

### 5 · Knowledge Bank — 🟢 REAL
- **Evidence.** `test_02_knowledge_ingestion_github` — full GitHub ingest, `reinforce_count: 11`, `graph_edges_around_root: 16`, distinct concepts list (`/tmp/atlas_verify.log` lines 21-62).
- **Caveat.** HUD Cyclopedia tile still shows the legacy 22-subject index — ingested records reachable only via `/api/kbase/search`.

### 6 · Memory Bank — 🟠 PARTIAL
- **Evidence.** `test_01_memory_persistence_across_restart` — round-trip via by-tag PASSES (`/tmp/atlas_verify.log` lines 9-20).
- **Why PARTIAL.** Default embedder is the 128-dim hash backend in `services/memory_bank.py` lines 150-177 — cosine recall on short queries is noisy. **Ollama install attempted in this session but the binary was wiped from `/usr/local/bin/ollama` between bash sessions twice in a row** (cloud container behaviour), so `ATLAS_EMBED_PROVIDER=ollama` remains a P2 toggle. `OPENAI_API_KEY` is unset, so the `emergent` real-embedding path is also unreachable.
- **TTL eviction NOT implemented** — decaying rows lose score but never get DELETED.

### 7 · Graph Memory — 🟢 REAL
- **Evidence.** `test_04_graph_traversal_depth_3` — `node_count: 7, edge_count: 15, depth-3 reached verify-c: True` (`/tmp/atlas_verify.log` lines 100-123). After the watcher run, total `graph_triples=1316`.

### 8 · Research Pipeline — 🟢 REAL
- **Evidence.** `test_05_research_pipeline_arxiv` — full arXiv fetch with `source_author: Alec Radford, Jong Wook Kim, Tao Xu, Greg Brockman, Christine McLeavey, Ilya Sutskever`, 21 concepts extracted (`/tmp/atlas_verify.log` lines 125-159).

### 9 · Voice — 🟠 PARTIAL
- **Real.** Web Speech API STT, OpenAI TTS fallback active.
- **Wake-word is string-match on transcribed audio** — not a hot-word model. Persona-specific TTS voices not differentiated.

### 10 · HUD — 🟠 PARTIAL
- **Evidence.** `test_10_hud_panels_read_live_apis` — every panel `status=200, live=true` (`/tmp/atlas_verify.log` lines 256-302).
- **PARTIAL.** `AtlasSidePanel.js` lines ~88-99 still carry HARDCODED legacy lists (`Connected Devices`, `Blueprint Gallery`). Replacement is a deferred P2 item from the previous "Proceed with all P2 tasks" message — moved aside when the user redirected to Watcher Systems.

### 11 · Digital Twin — 🟡 SIMULATED
- **Evidence verdict line.** `test_06_digital_twin_lifecycle` — `VERDICT: 🟡 SIMULATED — heuristic simulator engine, not real physics` (`/tmp/atlas_verify.log` line 185).

### 12 · Weaver — 🟡 SIMULATED
- **Evidence verdict line.** `test_07_weaver_plan_from_twin` — `VERDICT: 🟡 SIMULATED — heuristic costs/lead-times for unknown parts (25-row library)`, `parts_sample (first 3): [null, null, null]` (`/tmp/atlas_verify.log` lines 187-205).

### 13 · Robot Control — 🟠 PARTIAL
- **Evidence.** `test_08_robot_safety_full_chain` — full guest-reject → owner-execute → e-stop → clear pipeline PASS (`/tmp/atlas_verify.log` lines 206-232).
- **PARTIAL.** `execute` step is dispatch-only; no real actuator polls the inbox.

### 14 · Sentinel ribbon — 🟢 REAL
- **Evidence.** `test_09` Welford `z_scores.co2: 36115.029` trips on outlier (`/tmp/atlas_verify.log` lines 238-250).

### 15 · ESP32 firmware — ⚫ UNTESTED
- Real source code at `/app/firmware/esp32/atlas_device.ino`. **Zero hardware contact.** `read_sensors()` returns synthetic values; `actuate()` is `Serial.print`.

### 16 · MQTT bridge — 🔴 PLACEHOLDER
- Code path exists, `paho-mqtt` installed, but no broker deployed. Falls back gracefully (`test_phase8_quad.py` MQTT-dormant regression).

### 17 · mTLS — 🟠 PARTIAL
- Issuance works (`test_mtls_phase8f.py` 7/7). Server-side request verification requires `MTLS_ENFORCE=true` which is unset.

### 18 · Sentinel Autonomic Watcher — 🟢 REAL
- **Evidence.** `test_09` — `watcher_fire-now.examined: 9, fired: 1` (`/tmp/atlas_verify.log` lines 251-254). 60s in-process cron task in `services/sentinel_watcher.py`.

### 19 · ElevenLabs TTS — 🔴 PLACEHOLDER
- Cloud-IP block on free tier. OpenAI TTS fallback active.

### 20 · YouTube transcript — 🔴 PLACEHOLDER
- Cloud-IP block. Returns graceful 503. Channel/playlist URLs don't have transcripts at all — see new self-improvement proposal `410a020f…` for the fix path.

---

## Section B · NEW subsystems (built in this session)

### 21 · GitHub Knowledge Watcher — 🟢 REAL

| Aspect | Status | Evidence |
| ------ | ------ | -------- |
| Source registry (`watchers` collection, idempotent by sha256 URL hash) | 🟢 REAL | source_id `a2f334e53c8f49a3bbbdb4e1e3b28611`, source_hash `4218d71a2ac9c0142ac72366`. Second `register` call returned `run_count: 3` (proves idempotency) |
| README fetch (60 KB cap) via existing `_fetch_github` | 🟢 REAL | `proof.files_scanned[0]: {filename: 'README', chars: 57799}` |
| URL regex extraction + markdown-heading category lookup | 🟢 REAL | 15 URLs with 4 distinct categories (`Personal Favorites:`, `YouTube Channels & Other Resources`, etc.) |
| Per-URL `kbase.ingest_url` pipeline | 🟢 REAL | run_id `705e6a1c30cd45adbbebaf3f41009680` → `knowledge_ids_created_or_reused: 15`, `memory_ids_created_or_reused: 15` |
| Auto-wired graph triples (concept → tag, agent → concept, project → concept) | 🟢 REAL | `graph_edges_created: 24` in this run; **total `graph_triples: 1316` after test** |
| TRANSCRIPT_UNAVAILABLE stub recording (URL + category only, **no copyrighted body text**) | 🟢 REAL | 14 rows in `knowledge_records` with `transcript_status='TRANSCRIPT_UNAVAILABLE'`; 14 matching tagged rows in `memory_bank`. Verified by Mongo `count_documents`. |
| Lesson generation via gpt-5.2 — real LLM call, persisted | 🟢 REAL | lesson_id `671582b765b04d9e8f37191d720eb0c5` · `model_used: gpt-5.2` · `provider_used: emergent` · 4 quiz questions, 5 vocabulary terms, 3 hands-on steps |
| Proof endpoint returns the full run verbatim | 🟢 REAL | `GET /api/watchers/proof/a2f334e53c8f49a3bbbdb4e1e3b28611` → JSON contains `run_id`, `summary`, `files_scanned`, `ingest_results[15]`, `lessons_created[1]`, `errors: []` |
| Sub-features that are 🟡 SIMULATED inside this REAL system | | gpt-5.2 self-reports lesson `confidence_score` and `skill_level` (heuristic) |
| Sub-features that are ⚫ NOT DONE | | (a) No GitHub-push webhook auto-run (manual `/run` only) (b) No content-aware diff vs last commit — `last_commit_sha` is a placeholder hash of the first line (c) No YouTube channel-RSS resolver — see proposal `410a020f…` |

**Why 🟢 REAL is primary.** Every claim is exercised by a real curl call
with a persisted Mongo row carrying a real ID. Three runs of the same source
produced `run_count=3` in `watchers`, three documents in `watcher_runs`, and
seven lessons in `lessons` (one per run × multiple runs). The TRANSCRIPT_UNAVAILABLE
rule is enforced — verified that no full transcript body was stored, only
URL + category metadata.

### 22 · Self-Improvement Watcher — 🟢 REAL

| Aspect | Status | Evidence |
| ------ | ------ | -------- |
| Proposal creation with strict category + risk validation | 🟢 REAL | proposal `410a020f53e34e3997c96e70664eda24` accepted with `category=research_source, risk_level=low` |
| Approval/rejection lifecycle | 🟢 REAL | Status transitioned `pending → approved` via `POST /api/self-improve/approve/410a020f…` with `decision_note: 'approved — channel-resolver is a sensible upgrade'` persisted |
| Approval gating logic | 🟢 REAL | Code path in `services/self_improvement.py` lines 49-52: `approval_required = risk_level in {medium,high} or category in {code_architecture, agent_personality}`. The low-risk research_source proposal correctly returned `approval_required: false`. |
| Weekly report (deterministic, no cron) | 🟢 REAL | `GET /api/self-improve/weekly-report` returned `{total_proposals: 1, by_category: {research_source: 1}, by_status: {approved: 1}}` |
| History audit trail | 🟢 REAL | `GET /api/self-improve/history` returned the full record with timestamps and decision_note |
| **Strict "never silently rewrite" contract** | 🟢 REAL | The service has NO code path that writes to anything but the `self_improvements` collection. Status changes are only via the route layer's explicit approve/reject endpoints. Code architecture proposals are forced `approval_required: true` by category gating. |
| Sub-features that are ⚫ NOT DONE | | (a) No automatic proposal generation (currently only created via explicit POST) (b) No "applied" automation — even an approved proposal must be implemented by a human or main agent (c) No diff-aware tracking of user corrections — `evidence` is whatever the proposer supplies |

**Why 🟢 REAL is primary.** Every lifecycle transition was exercised with
real curl calls and persisted with real IDs. The "never silently rewrite"
rule is structurally enforced by code organisation — the service module has
no `update_*` functions touching anything outside its own collection.

---

## Section C · changes since `ATLAS_TRUTH_REPORT.md`

| Subsystem | Before | After | Why |
| --------- | ------ | ----- | --- |
| Memory Bank Ollama path | 🟠 PARTIAL (Ollama configured but not default) | 🟠 PARTIAL (unchanged — install attempted, **binary wiped between bash sessions**, sentence-transformers attempt cut off by environment instability) | Cloud container cleanup behaviour |
| HUD legacy hardcoded tiles | 🟠 PARTIAL | 🟠 PARTIAL (still TODO — deferred when user redirected to Watcher build) | User redirected task mid-execution |
| **NEW: GitHub Knowledge Watcher** | — | 🟢 REAL | Built + tested live this session |
| **NEW: Self-Improvement Watcher** | — | 🟢 REAL | Built + tested live this session |

---

## Section D · the "what's blocking 🟢 REAL across the board" list

The same list from `ATLAS_TRUTH_REPORT.md` Section "What '🟢 REAL across the
board' would require" applies, with the following updates:

| Step | Current status |
| ---- | -------------- |
| Flash one ESP32 with `atlas_device.ino` | ⚫ Still untouched |
| Stand up a Mosquitto broker | 🔴 Still dormant |
| Set `MTLS_ENFORCE=true` | 🟠 Still issuance-only |
| Wire one real actuator | 🟡 Still simulated-execute |
| Switch `ATLAS_EMBED_PROVIDER=ollama` (or get OPENAI_API_KEY) | 🟠 **BLOCKED in this env — Ollama binary keeps getting wiped from `/usr/local/bin` between bash sessions; sentence-transformers install also interrupted by env instability** |
| Build HUD graph-viz tile | 🟠 Still TODO (deferred during this session) |
| Move ElevenLabs to non-blocked deployment | 🔴 Out-of-env fix |
| YouTube channel-RSS resolver | 🟠 **NEW PROPOSAL `410a020f…` approved — implementation pending** |
| YouTube transcript cloud-IP unblock | 🔴 Out-of-env fix |

---

## Section E · honesty caveats specific to this session

1. **Ollama install attempt did NOT succeed.** Despite two retries with full
   `zstd` extraction (38 MB binary visibly placed at `/usr/local/bin/ollama`
   within the install bash session), the binary was empirically gone in the
   next bash session. This is documented because it directly bears on the
   Memory Bank PARTIAL classification — the upgrade path the truth report
   identified is **not feasible in this cloud container**.
2. **`sentence-transformers` fallback was started** (pip install kicked off
   in a previous step) but the bash gateway dropped repeatedly mid-install.
   The package is NOT currently installed (verified by `pip show` returning
   `Package(s) not found`).
3. **HUD legacy-tile replacement and graph-viz panel** from the P2 list were
   NOT implemented in this session because the user redirected mid-task to
   the Watcher Systems build. Both remain TODO.
4. **The new Watcher Systems are the only NEW work that flipped a label to
   🟢 REAL in this session.** Every other primary label is unchanged from
   `ATLAS_TRUTH_REPORT.md`.

---

_Sister documents:_
- `/app/memory/ATLAS_VERIFICATION_RESULTS.md` — raw 11-test pytest log
- `/app/memory/ATLAS_INTEGRATION_PLAN.md` — 5 macro flows
- `/app/memory/ATLAS_DATA_FLOW.md` — collection-level data flow
- `/app/memory/ATLAS_TRUTH_REPORT.md` — prior 20-subsystem truth report
- `/app/memory/ATLAS_WATCHER_SYSTEM_REPORT.md` — full proof-of-life for the 2 new watchers (this session)
- `/app/memory/REALITY_CHECK_REPORT.md` — Feb 2026 brutally honest companion
