# ATLAS · Verification Results (Raw)

> **Source.** `/app/backend/tests/test_atlas_verification_suite.py`
> **Run log.** `/tmp/atlas_verify.log` (verbatim, copied here)
> **Run date.** 2026-06-18 03:47 UTC
> **Suite result.** `11 passed in 57.68s`
> **Legend used by suite.** `PASS · FAIL · PARTIAL · 🟡 SIMULATED · 🟠 PLACEHOLDER`
>
> This document is the **raw evidence** — no commentary, no summarization. Every
> `PASS`, `FAIL`, `WARNING`, `🟡 SIMULATED`, `🟠 PLACEHOLDER`, and `UNTESTED`
> item is listed below exactly as it appeared in the log.

---

## Suite roll-up

```
============================= test session starts ==============================
platform linux -- Python 3.11.15, pytest-9.0.3, pluggy-1.6.0
rootdir: /app/backend
configfile: pytest.ini
plugins: anyio-4.13.0
collecting ... collected 11 items
============================= 11 passed in 57.68s ==============================
```

| # | Test | pytest status | Verdict line (verbatim) |
| - | ---- | ------------- | ----------------------- |
| 01 | `test_01_memory_persistence_across_restart` | PASSED | `VERDICT: PASS — write + read round-trip via by-tag` |
| 02 | `test_02_knowledge_ingestion_github` | PASSED | `VERDICT: PASS — KB→Memory→Graph triple-write verified` |
| 03 | `test_03_persona_chat_voice_differentiation` | PASSED | `VERDICT: PASS — distinct voices + all 3 mirrors written` |
| 04 | `test_04_graph_traversal_depth_3` | PASSED | `VERDICT: PASS` |
| 05 | `test_05_research_pipeline_arxiv` | PASSED | `VERDICT: PASS` |
| 06 | `test_06_digital_twin_lifecycle` | PASSED | `VERDICT: 🟡 SIMULATED — heuristic simulator engine, not real physics` |
| 07 | `test_07_weaver_plan_from_twin` | PASSED | `VERDICT: 🟡 SIMULATED — heuristic costs/lead-times for unknown parts (25-row library)` |
| 08 | `test_08_robot_safety_full_chain` | PASSED | `VERDICT: PASS — guest rejected · owner executed · e-stop locked · clear unlocked · audit complete (execute is SIMULATED — no real actuator wired)` |
| 09 | `test_09_sentinel_anomaly_and_council` | PASSED | `VERDICT: PASS` |
| 10 | `test_10_hud_panels_read_live_apis` | PASSED | `VERDICT: PASS — every HUD panel endpoint returns live data` |
| 99 | `test_99_final_roll_up` | PASSED | `VERIFICATION SUITE COMPLETE — see per-test VERDICT lines above` |

---

## TEST 01 · MEMORY PERSISTENCE

```
· memory_id: 7b70a70a-6c26-4025-b57f-e683a59f57c6
· category: user
· persona: system
· retrieved_id: 7b70a70a-6c26-4025-b57f-e683a59f57c6
· stored_content_excerpt: Verification-suite memory carrying token VERIFY-MEM-5a05f5cf1e.
· db_collection: memory_bank
· VERDICT: PASS — write + read round-trip via by-tag
```

**Status flags raised:** PASS

---

## TEST 02 · KNOWLEDGE INGESTION (GitHub URL)

```
· source_url: https://github.com/openai/whisper
· source_type: github
· knowledge_entry_id: 691fa4b64ae84bd1a94754a3800feb54
· memory_entry_id (mirror): 6b777c5b-1a37-49eb-9936-5e7ea6162cde
· reinforce_count: 11
· concepts: [
    "multitask token prompting",
    "model variants",
    "transformer encoder-decoder",
    "transformer-seq2seq",
    "multitask learning",
    "model size tradeoffs",
    "model sizes",
    "transformer seq2seq model",
    "dependency toolchain",
    "multitask tokens",
    "installation dependencies",
    "model-scaling",
    "audio preprocessing",
    "language identification",
    "speech translation",
    "inference requirements",
    "multitask training",
    "command-line interface",
    "whisper-model",
    "transformer seq2seq",
    "dependency stack",
    "sequence-to-sequence transformer",
    "whisper model",
    "multitask..."
  ]
· related_agents: ["hermes"]
· graph_root_node: multitask token prompting
· graph_edges_around_root: 16
· search_q=whisper hits: 1
· VERDICT: PASS — KB→Memory→Graph triple-write verified
```

**Status flags raised:** PASS

---

## TEST 03 · PERSONA CHAT (3 voices, 1 question)

```
· [ajani] session_id: ba05e222f0e544f5b0ef2698e9865ac4
· [ajani] message_id: a4ea7cc9f9f34684abfc38a0cbd048b8
· [ajani] model_used: gpt-5.2
· [ajani] cited_memory_ids: [
    "16389a07-545c-4002-a2fa-40ee94cd4334",
    "903ef8d0-9d1d-431d-88d2-f9223eede62c"
  ]
· [ajani] cited_knowledge_ids: []
· [ajani] reply (first 140): I build and break down real-world engineered systems—mechanisms, tolerances, supply chains, and failure modes—so you know what can be built

· [minerva] session_id: 0f964d37411a49e3be4b25bed0ec2631
· [minerva] message_id: 95c8e89824f34bb1b7d1f7bd469ac8dc
· [minerva] model_used: gpt-5.2
· [minerva] cited_memory_ids: [
    "6e39e847-0624-49fe-b447-3769b2359356",
    "d9c1f722-c777-4580-ba5a-9a470044a63a"
  ]
· [minerva] cited_knowledge_ids: []
· [minerva] reply (first 140): I focus on rigorous, evidence-based engineering judgment for system architecture and reliability—what’s true, reproducible, and supported by

· [hermes] session_id: dadfece7e4fc41beaa8bc559ca1bb0d8
· [hermes] message_id: d0cc77fc3e564540b07d5ba3dbdd8af4
· [hermes] model_used: gpt-5.2
· [hermes] cited_memory_ids: [
    "302d5446-684f-48ea-bdee-a535cf23438a",
    "7d573b69-d8af-44c9-9b5d-89dd91ad0143"
  ]
· [hermes] cited_knowledge_ids: []
· [hermes] reply (first 140): I hunt patterns and failure modes to deliver optimal, stress-tested engineering decisions with explicit assumptions and trade-offs.

· all_3_replies_distinct: True
· [ajani] memory rows mirrored: 1
· [minerva] memory rows mirrored: 1
· [hermes] memory rows mirrored: 1
· VERDICT: PASS — distinct voices + all 3 mirrors written
```

**Status flags raised:** PASS

---

## TEST 04 · GRAPH TRAVERSAL (depth=3)

```
· root: verify-root-5b4335
· depth_requested: 3
· node_count: 7
· edge_count: 15
· nodes (first 10): [
    "verify-a",
    "verify-b",
    "verify-c",
    "verify-root-2a7f3f",
    "verify-root-5b4335",
    "verify-root-69e612",
    "verify-x"
  ]
· relation_types_present: ["depends_on", "implements", "relates_to"]
· depth-3 reached verify-c: True
· VERDICT: PASS
```

**Status flags raised:** PASS

---

## TEST 05 · RESEARCH PIPELINE (arXiv)

```
· source_url: https://arxiv.org/abs/2212.04356
· source_type: academic
· source_author: Alec Radford, Jong Wook Kim, Tao Xu, Greg Brockman,
                 Christine McLeavey, Ilya Sutskever
· title: Robust Speech Recognition via Large-Scale Weak Supervision
· summary (excerpt): The paper evaluates speech models trained by predicting
  transcripts from large quantities of internet audio, relying on weakly
  curated supervision rather than tightly controlled labels. Scaling this a...
· concepts: [
    "weakly-supervised training",
    "robust speech recognition",
    "weakly supervised training",
    "robust speech processing",
    "robust generalization",
    "multilingual asr",
    "weak supervision",
    "speech processing",
    "multilingual ASR",
    "zero-shot transfer",
    "large-scale training data",
    "multitask multilingual supervision",
    "multilingual dataset",
    "multilingual data",
    "multilingual speech recognition",
    "benchmark generalization",
    "model release",
    "transcript prediction objective",
    "benchmark evaluation",
    "large-scale audio corpus",
    "multitask multilingual dataset"
  ]
· citations_url_kept: True
· graph_edges_for_first_concept: 19
· VERDICT: PASS
```

**Status flags raised:** PASS

---

## TEST 06 · DIGITAL TWIN LIFECYCLE

```
· twin_id: 611b563aae984a8fa6efa92adf53ad98
· state_before: {
    "status": "simulated",
    "components": [],
    "materials": [],
    "dimensions": null,
    "energy": null,
    "dependencies": [],
    "sensor_inputs": [],
    "outputs": [],
    "integrations": {},
    "cad_refs": [],
    "hardware_binding": null,
    "revision": 3,
    "updated_at": "2026-06-18T03:45:25.959220+00:00"
  }
· sim_kind: failure
· sim_score: 0.6
· sim_id: e92b3a9f43dc4becb231af5d3743f5ac
· state_after.readings: None
· memory_entries_for_twin: 0
· VERDICT: 🟡 SIMULATED — heuristic simulator engine, not real physics
```

**Status flags raised:** 🟡 SIMULATED (test passed structurally, but the underlying simulator is heuristic — not real physics)

---

## TEST 07 · WEAVER PLAN GENERATION

```
· plan_id: 88d9ffb3227440aca786d179cace1add
· twin_id (spawned): 66c0c7cf0035432ba2f888683c3e49d7
· parts_count: 10
· parts_sample (first 3): [null, null, null]
· build_plan_steps: 10
· risks_count: 0
· total_cost: 26.28
· critical_path_days: 9.0
· memory_rows_for_plan: 0
· VERDICT: 🟡 SIMULATED — heuristic costs/lead-times for unknown parts (25-row library)
```

**Status flags raised:**
- 🟡 SIMULATED — heuristic costs/lead-times for unknown parts (25-row library)
- ⚠️ `parts_sample (first 3)` returned `[null, null, null]` — first 3 enriched
  parts have no `vendor`/`sku` metadata (free-text parts library, no Digi-Key /
  Mouser API)
- ⚠️ `memory_rows_for_plan: 0` — plan was created but no row landed in MemoryBank
  filtered by this plan_id at the moment of check (plan persists in
  `weaver_plans` collection regardless)

---

## TEST 08 · ROBOT SAFETY CHAIN (guest reject → owner exec → e-stop → clear)

```
· device_id: e12b868b01c84cfba114f5a63b810c84
· guest_actuate.status: rejected
· guest_actuate.reason: command 'actuate' is owner-only (got role=guest)
· owner_ping.status: executed
· owner_ping.pipeline_steps: ["authorise", "validate", "execute"]
· e-stop.status: safe_state
· actuate_in_safe_state.status: rejected
· actuate_in_safe_state.reason: device is in SAFE_STATE — clear it first via owner
· clear.status_code: 200
· clear.body.device.status: registered
· audit_command_count: 4
· audit_kinds: ["clear_safe_state", "actuate", "ping", "actuate"]
· VERDICT: PASS — guest rejected · owner executed · e-stop locked · clear unlocked · audit complete (execute is SIMULATED — no real actuator wired)
```

**Status flags raised:**
- PASS — all four safety contracts honoured
- 🟡 SIMULATED — execute step is dispatch-only (no real actuator is wired in
  this environment; the pipeline_log says "executed" meaning Atlas considers
  itself to have dispatched the command, NOT that a physical actuator turned)

---

## TEST 09 · SENTINEL ANOMALY → AUTONOMIC COUNCIL

```
· device_id: c3d7640a78324eb0a3ce2666218930ff
· envelope.n_after_warmup: 12
· envelope.anomaly_before_outlier: None
· envelope.anomaly_after_outlier: {
    "drifting_keys": ["co2"],
    "since": "2026-06-18T03:47:35.883602+00:00",
    "z_scores": {"co2": 36115.029},
    "sigma_threshold": 3.0,
    "last_seen": "2026-06-18T03:47:35.883620+00:00"
  }
· watcher_fire-now.examined: 9
· watcher_fire-now.fired: 1
· autonomic_council_memory_count: 1
· VERDICT: PASS
```

**Status flags raised:** PASS
*(implicit caveat from REALITY_CHECK_REPORT §14: telemetry being scored is
synthetic — Welford math is real, but in this run the data feeding it was
pushed by the test itself, not a physical sensor.)*

---

## TEST 10 · HUD LIVE-DATA WIRING

```
· PersonaPanel   /persona/list                      status=200 live=true size=2152
· MemoryPanel    /membank/search?q=robot&limit=5    status=200 live=true size=6203
· KnowledgePanel /kbase/search?q=whisper&limit=5    status=200 live=true size=2781
· TwinPanel      /twins/list                        status=200 live=true size=10987
· RobotPanel     /robot/devices?limit=10            status=200 live=true size=7402
· SentinelPanel  /robot/devices?limit=10            status=200 live=true size=7402
· SentinelPanel  /robot/devices/<id>/telemetry      status=200 live=true size=190
· VERDICT: PASS — every HUD panel endpoint returns live data
```

**Status flags raised:** PASS — every HUD panel endpoint returns live data

---

## TEST 99 · FINAL ROLL-UP

```
==============================================================================
  VERIFICATION SUITE COMPLETE — see per-test VERDICT lines above
==============================================================================

  legend: PASS · FAIL · PARTIAL · 🟡 SIMULATED · 🟠 PLACEHOLDER
```

**Status flags raised:** PASS

---

## FAIL items

> **None.** No test in this suite produced a `FAIL` verdict.

---

## WARNING / atypical observations within passing tests

| Test | Observation |
| ---- | ----------- |
| 06 | `state_after.readings: None` — twin state is registered but no live readings have ever been pushed for this twin |
| 06 | `memory_entries_for_twin: 0` — twin lifecycle ran, but no MemoryBank row was tagged with this specific twin_id at the moment of check |
| 07 | `parts_sample (first 3): [null, null, null]` — enriched parts have no vendor/SKU; LLM-imagined for unknown parts |
| 07 | `risks_count: 0` — plan generated zero risks; Weaver risk-enumerator is conservative on a simple blueprint |
| 07 | `memory_rows_for_plan: 0` — plan persisted in `weaver_plans`, but no MB row keyed to this plan_id at check time |
| 09 | `envelope.anomaly_after_outlier.z_scores.co2: 36115.029` — extreme z-score because warmup mean/stddev was tiny; real-world sensors will produce far smaller magnitudes |

These are **observations**, not failures — the test contract still passes
because the verdict criteria (PASS/SIMULATED) were met. They are listed here
so nothing is hidden.

---

## 🟡 SIMULATED items (from VERDICT lines)

| Test | Item |
| ---- | ---- |
| 06 | Digital Twin simulator engine — heuristic only, no real physics (no FEA, no CFD, no SPICE) |
| 07 | Weaver costs/lead-times for unknown parts — LLM-imagined when not in the 25-row starter library |
| 08 | Robot `execute` step — writes Command row + MQTT publish + inbox row, but no real actuator polls the inbox in this deployment |

## 🟠 PLACEHOLDER items (from VERDICT lines)

> **None.** No test verdict line raised the 🟠 PLACEHOLDER flag in this run.

*Cross-reference:* `REALITY_CHECK_REPORT.md` documents additional 🟠
PLACEHOLDER items at the **subsystem** level (e.g. HUD legacy tile content,
Sentinel autonomic-firing UI absence pre-watcher, ESP32 OTA stub) that are
outside the scope of these 11 automated tests.

## UNTESTED surfaces (not covered by this 11-test suite)

| Surface | Why it's UNTESTED here |
| ------- | ---------------------- |
| ESP32 firmware (`/app/firmware/esp32/atlas_device.ino`) | No real hardware has flashed it. Suite cannot test it. |
| ElevenLabs TTS provider | Cloud-IP block on free tier — falls back to OpenAI TTS |
| YouTube Transcript ingestion | Cloud-IP block — endpoint returns graceful 503 |
| Real MQTT broker delivery | No broker deployed — code path is dormant |
| mTLS *enforcement* (request verification) | `MTLS_ENFORCE=false` — only issuance is exercised |
| Sentinel autonomic firing on **real** sensor data | All sensor data in this run was pushed synthetically by the test |
| Voice STT/TTS round-trip from browser | Requires Web Speech API in a real browser — out of pytest scope |
| Cross-replica inbox `delivered` flag | Single-process test — multi-replica behaviour unknown |

---

_End of raw results. Cross-references: `ATLAS_VERIFICATION_SUITE.md` for the
suite contract, `REALITY_CHECK_REPORT.md` for subsystem-level honesty,
`ATLAS_TRUTH_REPORT.md` (companion document) for the REAL/SIMULATED/PARTIAL/
PLACEHOLDER/UNTESTED classification across all 15 subsystems._
