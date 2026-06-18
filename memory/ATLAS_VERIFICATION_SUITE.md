# ATLAS Verification Suite

> **Purpose.** Prove that ATLAS subsystems are actually connected and working —
> not mocked, hardcoded, or visually present. Every test prints structured
> evidence (IDs, DB records, scores, API responses) and ends with one of:
> **PASS · FAIL · PARTIAL · 🟡 SIMULATED · 🟠 PLACEHOLDER**.
>
> **Runnable counterpart:** `/app/backend/tests/test_atlas_verification_suite.py`
> **Last-run results:** `/app/memory/ATLAS_VERIFICATION_RESULTS.md`

## Rules of evidence
- No fake success messages.
- No static/mock data unless clearly marked **MOCK**.
- Every test must surface real IDs, real DB collection names, real LLM model strings.
- If a subsystem is simulated (heuristic, not real-world), the VERDICT must say so.
- If a subsystem is placeholder, the VERDICT must say so.

## How to run

```bash
cd /app/backend
python -m pytest tests/test_atlas_verification_suite.py -v -s | tee /tmp/atlas_verify.log
```

The `-s` flag is important — it lets the structured evidence print
through pytest's capture. Each test prints a boxed header, the labelled
evidence lines, and a single `VERDICT:` line.

## The 10 tests

| # | Test | What it proves | Subsystem(s) touched |
| --- | --- | --- | --- |
| 01 | Memory Persistence | Write a tagged memory → retrieve it by exact tag. Survives across requests; the by-tag endpoint bypasses cosine similarity entirely. | Memory Bank · MongoDB |
| 02 | Knowledge Ingestion (GitHub) | Ingest `github.com/openai/whisper` → confirm KnowledgeRecord id + MemoryBank mirror id + graph edges around the distilled concepts. | Knowledge Bank · Research Pipeline · Memory Bank · Graph Memory |
| 03 | Persona Chat (3 voices) | Send identical question to Ajani · Minerva · Hermes; verify distinct replies, the model used, cited memories, and a persisted MB mirror per persona (queried via `/api/membank/by-tag?tag=<session_id>`). | Persona Chat · LLM Provider · Memory Bank |
| 04 | Graph Traversal (depth=3) | Seed a known subgraph (4 triples), expand via `/graph/expand?depth=3`, confirm depth-3 hop reached the leaf. | Graph Memory |
| 05 | Research Pipeline (arXiv) | Ingest a real arXiv URL → confirm source_type=academic + source_author parsed from Atom feed + summary non-trivial + graph edges from the distilled concepts. | Research Pipeline · Knowledge Bank · Memory Bank · Graph Memory |
| 06 | Digital Twin Lifecycle | Update bound twin's state · run a `failure` simulation · confirm sim_score · confirm memory rows tagged with twin_id. **Marked 🟡 SIMULATED**: simulator engines are heuristic, not real physics. | Digital Twin · Memory Bank |
| 07 | Weaver Plan Generation | Submit a blueprint → confirm BOM count > 0 · build steps > 0 · risks list · total_cost · critical_path_days. **Marked 🟡 SIMULATED**: costs / lead-times for parts outside the 25-row library are LLM-imagined. | Weaver · Digital Twin · Memory Bank |
| 08 | Robot Safety Chain | Guest ACTUATE → REJECTED. Owner PING → EXECUTED. EMERGENCY_STOP → safe_state. ACTUATE in safe_state → REJECTED. CLEAR_SAFE_STATE → registered. Full audit chain in `robot_commands`. **Marked SIMULATED for execute**: no real actuator wired. | Robot Control · Digital Twin · Memory Bank |
| 09 | Sentinel Anomaly → Council | 12 normal readings + 1 outlier → anomaly trips. `fire-now` runs the watcher → autonomic council Memory Bank entry created (`category=council`, tag=`autonomic_council`). | Sentinel · Persona Chat (Council) · Memory Bank |
| 10 | HUD Live-Data Wiring | Probe the exact endpoints the HUD components call (`/persona/list`, `/membank/search`, `/kbase/search`, `/twins/list`, `/robot/devices`, telemetry). Each returns real data with real IDs. | HUD ↔ all APIs |

## Evidence schema per test

Each `_print_evidence(label, value)` line surfaces one piece of proof:
- `memory_id`, `session_id`, `device_id`, `twin_id`, `plan_id`, `command_id` — real UUIDs from MongoDB
- `model_used`, `provider_used` — the exact LLM string returned by `llm_provider.send`
- `cited_memory_ids`, `cited_knowledge_ids` — the rows the persona actually grounded itself in
- `pipeline_log` / `pipeline_steps` — the ordered list of steps the robot command went through
- `sim_score` — the heuristic float the Digital Twin returned (0–1)
- `concepts` / `tags` — the canonical slugs written into Graph Memory
- `VERDICT` — final status string

## What "PASS" does NOT imply

- It does **not** imply that any real-world physical action took place. Robot Control's "executed" step writes to the inbox; no actuator has ever moved.
- It does **not** imply that Digital Twin scores match real engineering certification — they are heuristics.
- It does **not** imply that Weaver costs are accurate — parts outside the 25-row library get LLM-imagined values.
- It does **not** imply that an ESP32 ever connected. The Sentinel sees pushed telemetry only.

## What "PASS" DOES imply

- The API contracts are real.
- The MongoDB persistence is real (rows are written and retrievable).
- The cross-system wiring is real (KB writes to MB writes to Graph writes to per-persona memory).
- The role gates are real (guest is rejected, owner is allowed).
- The safety contracts are real (emergency stop locks the device, clear-safe-state requires confirmation).
- The autonomic loop is real (Sentinel anomaly → Watcher tick → Council Memory Bank row).
