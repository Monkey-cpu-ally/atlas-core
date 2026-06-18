# ATLAS · Data Flow

> **Purpose.** Shows where every byte of data originates, where it is stored,
> what mutates it, and which subsystems read it. Companion to
> `ATLAS_INTEGRATION_PLAN.md` (which describes the 5 macro flows) — this
> document tracks the **collections, schemas, and write/read fan-out**.

---

## 1 · Collection map (Mongo)

| Collection | Owners (write) | Readers | Lifetime |
| ---------- | -------------- | ------- | -------- |
| `memory_bank` | `services/memory.py`, `kbase`, `persona_chat`, `robot`, `weaver`, `twin`, `research`, `sentinel_watcher` | persona chat (cosine), `/api/membank/*` | mixed: 4 permanent + 7 decaying categories |
| `knowledge` | `services/kbase.py` (`ingest`) | `/api/kbase/search`, persona chat | permanent · dedup by `sha256(normalised_url)` |
| `graph_triples` | `services/graph.py` via kbase + robot register | `/api/membank/graph/*` (BFS) | permanent · Hebbian weight increment |
| `persona_chat_sessions` | `services/persona_chat.py` | session history endpoint | per-user · multi-turn |
| `persona_chat_messages` | `services/persona_chat.py` | session history endpoint | persisted with `cited_memory_ids` + `cited_knowledge_ids` |
| `twin_registry` | `services/twin.py` | `/api/twins/*`, robot bind | permanent · revisioned |
| `twin_simulations` | `services/twin.py` (simulate) | `/api/twins/{id}/simulations` | append-only |
| `weaver_plans` | `services/weaver.py` | `/api/weaver/plans` | append-only |
| `hardware_devices` | `services/robot.py` (register) | Sentinel ribbon, RobotPanel | mutable · `safe_state` flag, `state.anomaly_envelope` |
| `hardware_commands` | `services/robot.py` (pipeline) | audit trail, `/api/robot/devices/{id}/commands` | append-only |
| `hardware_telemetry` | `services/robot.py` (POST /telemetry) | Welford anomaly, SentinelPanel | rolling window |
| `mtls_certificates` | `services/mtls.py` (issue) | (future) request verification when `MTLS_ENFORCE=true` | permanent |

---

## 2 · Field-level data flow per macro flow

### Flow 1 · Research → Knowledge

```
URL (voice intent or HTTP) ─┐
                            ▼
              source_fetchers.fetch(url) → fetched_payload
              { source_type, title, body, author, citations, … }
                            │
                            ├──► LLM distill (persona-routed) ─► distilled
                            │    { summary, concepts[], related_agents[], confidence }
                            │
                            ├──► knowledge.insert_one({
                            │      _id: sha256(normalised_url),
                            │      source_url, source_type, source_author,
                            │      title, summary, concepts, related_agents,
                            │      reinforce_count: 1,           ← incremented on revisit
                            │      created_at, updated_at
                            │    })
                            │
                            ├──► memory_bank.insert_one({
                            │      id: uuid,
                            │      category: "research",
                            │      tags: ["kbase:<knowledge_id>", *concepts],
                            │      content: title + " — " + summary,
                            │      meta: { source_url, persona }
                            │    })
                            │
                            └──► graph_triples.insert_many([
                                   {from: concept_i, to: concept_j, relation: "relates_to", weight: 1.0, source_id: knowledge_id},
                                   {from: concept_i, to: tag_k,     relation: "implements",  weight: 1.0, source_id: knowledge_id},
                                   …
                                 ])
```

### Flow 2 · Persona Chat → Graph

```
HTTP body: { message, session_id?, role? }
                            │
                            ▼
       memory_bank.find(category in preferred_categories[persona])
                            │
                       cosine top-K → cited_memories[]
                            │
       knowledge.find(related_agents contains persona)
                            │
                       cosine top-K → cited_knowledge[]
                            │
                            ▼
              llm_provider.send(persona, prompt_with_cites)
                            │
                            ▼
       persona_chat_sessions.insert_or_update({
         session_id, persona, started_at, turn_count++
       })
       persona_chat_messages.insert_one({
         message_id, session_id, role, content,
         cited_memory_ids, cited_knowledge_ids, model_used: "gpt-5.2"
       })
       memory_bank.insert_one({
         category: persona=="council" ? "council" : "user",
         tags: ["persona:<persona>", "session:<session_id>"],
         content: question + " ⇨ " + reply
       })
```

### Flow 3 · Digital Twin → Weaver Plan

```
POST /api/twins/register      ── ► twin_registry.insert_one({ twin_id, state })
POST /api/twins/{id}/simulate ── ► twin_simulations.insert_one({
                                       sim_id, twin_id, kind, score, inputs, outputs
                                   })

POST /api/weaver/plan { blueprint } ─► weaver.parse_blueprint(blueprint)
                                    ─► weaver.enrich_parts(parts)         ← 25-row library + LLM
                                    ─► weaver.spawn_twin()                 ← writes twin_registry
                                    ─► weaver.run_sim_sweep()              ← writes twin_simulations × 4
                                    ─► weaver.build_plan()                 ← steps[], risks[]
                                    ─► weaver_plans.insert_one({
                                         plan_id, twin_id, parts[],
                                         build_plan, manufacturing_plan,
                                         failure_plan, total_cost,
                                         critical_path_days
                                       })
                                    ─► memory_bank.insert_one({
                                         category: "project",
                                         tags: ["plan:<plan_id>", "twin:<twin_id>"]
                                       })
```

### Flow 4 · Robot → Sentinel → Council

```
ESP32 / curl: POST /api/robot/devices/{id}/telemetry
              body: { readings: {co2: 580, temp_c: 22.1, …} }
                            │
                            ▼
       hardware_telemetry.insert_one({device_id, readings, ts})
       hardware_devices.find_one(device_id)
                  └─► state.anomaly_envelope (Welford):
                      for each key:
                        n++
                        delta  = x - mean
                        mean  += delta / n
                        delta2 = x - mean
                        M2    += delta * delta2
                        if n > 10:           ← warmup
                          stddev = sqrt(M2 / (n-1))
                          z      = abs(x - mean) / stddev
                          if z >= sigma_threshold(3.0):
                            drifting_keys.add(key)
                            z_scores[key] = z
                            since = now()
                            last_seen = now()
                            hardware_devices.update_one(state.anomaly_envelope)
                            │
                            ▼
       sentinel_watcher (60s cron):
         for dev in devices where state.anomaly_envelope.drifting_keys:
           if not already_fired_for_envelope:
             POST /api/robot/devices/{id}/ask-council  (internal call)
               └─► POST /api/persona/council/chat
                     └─► memory_bank.insert_one(category="council",
                                                tags=["device:<id>", "anomaly", *drifting_keys])
                     └─► hardware_commands.insert_one(kind="ask_council",
                                                       pipeline_log=[...])

       Safety chain (orthogonal):
         POST /api/robot/devices/{id}/command
           role check → simulate (twin) → validate → execute
           kind == "emergency_stop"     ─► state.safe_state = true
           kind in OWNER_ONLY ∧ safe_state ─► REJECT
           kind == "clear_safe_state" ∧ name_match ─► state.safe_state = false
```

### Flow 5 · HUD → Live APIs

```
React component mount / tile click
       │
       ▼
useEffect(() => {
  fetch(`${REACT_APP_BACKEND_URL}/api/<resource>`)
    .then(r => r.json())
    .then(setState);
}, []);
       │
       ▼
FastAPI route under /api/ (no auth on read, role-header on writes)
       │
       ▼
Mongo collection (see §1)
       │
       ▼
JSON body → React state
       │
       ▼
panel renders <li>, <Card>, <Sparkline>, popover …
```

---

## 3 · Cross-flow shared writes

These are the **rendezvous points** where multiple flows write to the same
collection. They are the highest-value indices for verifying integration:

| Collection | Writers from Flow… | Why it matters |
| ---------- | ------------------ | --------------- |
| `memory_bank` | 1 (research), 2 (user/council), 3 (project), 4 (council/sentinel), 5 (none — read-only) | Single source-of-truth for persona recall |
| `graph_triples` | 1 (kbase), 4 (robot register adds device↔role triples) | Graph reasoning surface |
| `hardware_commands` | 4 (every command in the pipeline) | Audit trail for safety review |
| `twin_simulations` | 3 (Weaver sim sweep), 4 (robot bind-twin sims) | Sim-first safety enforcement |

---

## 4 · Bytes that **leave** Atlas

| Egress | Destination | Triggered by |
| ------ | ----------- | ------------ |
| LLM prompts | OpenAI / Anthropic / Gemini via `emergentintegrations` | every persona chat, every kbase distill, every council call |
| HTTP fetches | `github.com`, `arxiv.org`, `youtube.com` (blocked), DDG, Google Patents | every kbase ingest |
| MQTT publish (best-effort) | `MQTT_BROKER_HOST` if set | every robot command (dormant if no broker) |
| OpenAI TTS audio | OpenAI | `/api/voice/speak` |
| (planned) Webhook to user | not implemented | — |

---

## 5 · Bytes that **enter** Atlas

| Ingress | Source | Mediator |
| ------- | ------ | -------- |
| Voice transcript | Web Speech API (browser) | `useVoiceRecognition.js` → intent parser → HTTP |
| URL ingest text | HTTP POST `/api/kbase/ingest` | `source_fetchers.fetch` |
| Telemetry envelopes | HTTP POST `/api/robot/devices/{id}/telemetry` (test-pushed today; ESP32-pushed when flashed) | Welford |
| Persona chat | HTTP POST `/api/persona/{persona}/chat` | `persona_chat.py` |
| (planned) MQTT telemetry | broker subscribe | dormant until broker deployed |

---

## 6 · Data lifecycle / retention

| Type | Lifecycle | Eviction |
| ---- | --------- | -------- |
| Permanent memories (`user`, `project`, `council`, `agent`) | forever | none |
| Decaying memories (`research`, `recent`, `transient`, `prompt`, `feedback`, `error`, `task`) | freshness score decays daily | **🟠 no TTL eviction yet** — score drops but row stays |
| Knowledge | forever (dedup + reinforce) | none |
| Graph triples | forever; weight Hebbian-incremented on revisit | none |
| Persona chat | forever (history endpoint reads it back) | none |
| Hardware commands | forever (audit) | none |
| Hardware telemetry | rolling window per device (configurable, default last 200) | trimmed on insert |
| mTLS certs | until revoked (revocation list not implemented) | manual |

---

## 7 · Where this data flow is **honest**

| Honesty point | Explanation |
| ------------- | ----------- |
| `memory_bank` default embedding is a 128-dim hash | Cosine recall on short queries is noisy — `by-tag` is the reliable lookup. Real embeddings require Ollama or paid Emergent embeddings. |
| `twin_simulations.score` is a heuristic | No FEA / CFD / SPICE — just rule-of-thumb math. Useful for ranking, not certification. |
| `hardware_commands.pipeline_log[-1] == "executed"` | Means dispatched, NOT physically actuated. No real actuator is wired in this deployment. |
| Sentinel anomaly envelope `z_scores` | Welford math is real. Data feeding it in this run was synthetic / test-pushed. |
| `kbase` YouTube fetch | Cloud-IP blocked. Returns graceful 503 with hint, NOT silent failure. |

---

_End of data flow document. For per-test evidence see
`ATLAS_VERIFICATION_RESULTS.md`. For per-subsystem honesty grading see
`ATLAS_TRUTH_REPORT.md`._
