# ATLAS · Autonomous Research Orchestrator (Phase 9) — Proof

> **2026-06-18 · Live test run.** No simulated results. Every record has
> a real evidence envelope with source · confidence · evidence_refs · date
> · verification_status.

---

## What was built (honest scope)

| # | Component (user list) | Status | Where |
| -: | --------------------- | :----: | ----- |
| 1 | Discovery Engine — YouTube · GitHub · arXiv · patents · journals · tech news | 🟡 5/6 | reused: `services/worldwatch.py` (arXiv cs.AI/cs.RO/cs.SE/mtrl-sci/atm-clus/q-bio.QM/q-bio.PE · NASA · Hackaday · Dezeen · ArchDaily) + `services/knowledge_watcher.py` (GitHub) + `services/youtube_pipeline.py` (YouTube manual). **Patent feed not added to worldwatch — uses on-demand `/api/research/patent` instead.** |
| 2 | Research Queue with 7-state machine | 🟢 | NEW `services/research_orchestrator.py` · `research_queue` collection |
| 3 | Knowledge Extraction (summary · concepts · terminology · skills · tech · risks · opportunities · related projects) | 🟢 | reused `services/knowledge_distiller.py` — every queue item walks it during `investigating → analyzed` phase |
| 4 | Lesson Generator with ADHD · Lego · Beginner · Professional · Certification modes | 🟢 | extended `services/lesson_generator.py` — new `mode` param + 5 mode overlays |
| 5 | Blueprint Forge (build plans · hardware · software · manufacturing · prototypes) | 🟢 | NEW `services/blueprint_forge.py` · `blueprint_forge` collection |
| 6 | Curiosity Engine (unknowns · weak areas · emerging tech · missions) | 🟢 | NEW `research_orchestrator.curiosity_scan()` · `research_missions` collection |
| 7 | Council Review (Ajani strategy · Minerva education · Hermes architecture · Council final) | 🟡 | existing persona_chat.py council path · NOT auto-invoked from each cycle yet (manual call) |
| 8 | HUD Panels (Research Queue · Active Investigations · Blueprint Forge · Learning Hub · Tech Radar · Council Recs · Curiosity Missions) | 🔴 0/7 | **No new HUD panels in this message** — backend endpoints ready, panels are next-step P0 |
| 9 | Self-Improvement tracking | 🟢 | reused `services/self_improvement.py` + `services/self_code.py` — already proven last session |
| 10 | Evidence Requirements (source · confidence · evidence · date · verification status) | 🟢 | `services/research_orchestrator.make_evidence()` — embedded on EVERY queue item, mission, and blueprint |

---

## Live cycle proof

**Endpoint.** `POST /api/research-orch/orchestrator/run`
**Body.** `{"discover_per_feed":1,"max_investigate":3,"generate_lessons":true,"mode":"lego"}`

**Result (`/tmp/ro_cycle.json`):**
```
cycle_id:  a51d3eaac48d4c2989dc4044cdc3fb21
status:    ok
errors:    0
phase1_discover:  worldwatch_run f0e7b187… · ww_new_entries=2 · enqueued=12
phase2-7:         examined=3 · fully_processed=3
  ec661a0f  conf=0.90  automated  lesson=9fe5d69f91b94e329d386cda5b302a56
  2920fc04  conf=0.86  automated  lesson=1bb7847e65424720b7b59ba72f0c2c4b
  0a414d04  conf=0.86  automated  lesson=8a7d6c9c7fa647448413d40dba8a0cb0
```

**Queue state after the cycle:**
```
total: 12
by_state:        {discovered:0, queued:9, investigating:0, analyzed:0,
                  verified:0, stored:0, linked:3}
by_verification: {automated:3, unverified:9}
```

The 9 `unverified · queued` items are intentional — they await the next
cycle (we capped `max_investigate=3` so the run finished quickly).

**State machine audit trail (one linked item, sample):**
```
2026-06-18T16:38:41   -            -> discovered    by discovery_engine
2026-06-18T16:38:41   discovered   -> queued        by cycle_phase1
2026-06-18T16:40:13   queued       -> investigating by cycle_phase2
2026-06-18T16:40:20   investigating-> analyzed      by cycle_phase3
2026-06-18T16:40:20   analyzed     -> verified      by cycle_phase4
2026-06-18T16:40:20   verified     -> stored        by cycle_phase5
2026-06-18T16:40:20   stored       -> linked        by cycle_phase6
```

**Evidence envelope on the same item:**
```json
{
  "source": "worldwatch_medicine",
  "confidence": 0.86,
  "evidence_refs": [
    {"kind": "knowledge", "id": "8eea06dd9e074cd39fd467620952a7bf",
     "url": "https://arxiv.org/abs/2606.18295"},
    {"kind": "memory_bank", "id": "ee1b4e72-6222-4cf8-884e-7a8e9dcdc40b"},
    {"kind": "concepts", "count": 6,
     "sample": ["nitrous oxide emissions", "archetypal analysis",
                "temperature forcing", "n2o emission state",
                "simplex state space"]}
  ],
  "date": "2026-06-18T16:40:20.133800+00:00",
  "verification_status": "automated"
}
```

---

## Curiosity Engine proof

**Endpoint.** `POST /api/research-orch/curiosity/scan`

**Result:**
- 4 missions created
- Sample: "Investigate AI — currently linked items: 0" · "Investigate robotics — currently linked items: 0" · "Investigate software_engineering — currently linked items: 0"
- **`Re-investigate: IDA* heuristic admissibility (user struggled)`** ← pulled from the `confusing_topics` field on the learning profile (the topic the user logged during Step 2 in the prior session!)
- All 4 missions carry the evidence envelope (`source: curiosity_scan`, `verification_status: automated`)

---

## Blueprint Forge proof

**Endpoint.** `POST /api/research-orch/blueprint-forge/run`
**Body.** `{"queue_item_id": "ec661a0f…"}`

**Result (read directly from `blueprint_forge` collection):**
```
forge_id:                 7271470f01634285ab8ba93c7d9168e3
queue_item_id:            ec661a0fd37f4873a2e61b0373de1973
parts_count:              8
steps_count:              4
risks_count:              ≥1
total_cost_usd:           142
prototype_suggestion:     "Tabletop Gravitational Lensing Mapper
                           (CL0016+1609 merger demo)"
agent:                    ajani
evidence.verification:    llm_simulated   ← honest: this is gpt-5.2 output,
                                            not real engineering certification
```

The forge correctly built a hands-on weekend-sized demo from an arXiv
paper about galaxy cluster lensing — a real-world example of the
"research → buildable plan" flow.

---

## Lesson modes proof

**Endpoint.** `POST /api/research-orch/lesson/regenerate`
**Body.** `{"knowledge_id": "<some kb_id>", "mode": "certification"}`

**Result (read from `lessons` collection):**
```
lesson_id:    326a5b80061745a18880f75864d50e15
title:        "Hubble + RELICS: Spotting a Galaxy-Cluster Crash and
               'Seeing' Dark Matter"
profile_bias.mode:      certification     ← persisted, audit-traceable
skill_level:            (LLM-chosen per concepts)
quiz_q_count:           5                 ← certification mode demands ≥ 5 quiz Qs
```

All 5 mode overlays (`adhd / lego / beginner / professional / certification`)
are wired into `services/lesson_generator.py` and persisted on every
lesson under `profile_bias.mode`.

---

## Endpoints registered (8)

```
GET   /api/research-orch/queue/status
GET   /api/research-orch/queue                 (filters: state, domain)
POST  /api/research-orch/orchestrator/run      (one full cycle)
POST  /api/research-orch/curiosity/scan        (gap analysis → missions)
GET   /api/research-orch/missions
POST  /api/research-orch/blueprint-forge/run   (research → buildable plan)
GET   /api/research-orch/blueprints
POST  /api/research-orch/lesson/regenerate     (mode swap)
```

---

## Collections introduced

| Collection | Rows after this run | Purpose |
| ---------- | -----------------: | ------- |
| `research_queue` | 12 | every discovered item + full state history + evidence |
| `research_cycles` | 1 | proof-of-execution per cycle |
| `research_missions` | 4 | curiosity-generated investigations |
| `blueprint_forge` | 1 | research → buildable plan |

Pre-existing collections re-used: `worldwatch_*`, `knowledge_records`,
`memory_bank`, `graph_triples`, `lessons`, `self_improvements`,
`user_learning_profile`.

---

## What is REAL
- 7-state machine with explicit transitions and audit trail per item
- Real worldwatch RSS pull → real arXiv distillation → real lesson_id
- Evidence envelope on every queue item, mission, blueprint
- Curiosity engine actually pulled the user's logged confusing topic and
  emitted a mission for it
- Mode overlay reaches the LLM and is persisted on the lesson document

## What is SIMULATED (and honest about it)
- Blueprint Forge `verification_status="llm_simulated"` — gpt-5.2 invents
  parts and costs; not a real solver or supplier API
- Lesson `skill_level` is gpt-5.2-chosen
- Confidence scores are LLM self-reports

## What requires API keys
- `EMERGENT_LLM_KEY` (already set) — every LLM step
- `OPENAI_API_KEY` (not set) — would unlock real semantic embeddings for
  Memory Bank (still 🟠 PARTIAL)

## What requires external services / cannot fix in this env
- YouTube transcript fetch (cloud-IP blocked)
- Dezeen RSS feed (BOM parse error in 1/11 feeds)
- Patent database integration — uses on-demand `/api/research/patent` only
- Scientific journals — only arXiv & NASA in worldwatch; PubMed/Nature/
  ScienceDirect would need separate fetchers

## What needs user approval
- Every Blueprint Forge plan with `confidence < 0.6` should be reviewed
  before acting (today's forge example was confidence 0.5)
- Every Self-Code Scanner proposal — 27 pending in `self_improvements`
- Any Curiosity mission marked `kind=confusion_followup` — that's the
  user's stated weak topic; lesson regeneration should happen with
  explicit permission

## What is NOT yet built (HUD)
0 of 7 HUD panels in this message:
- 🔴 Research Queue panel
- 🔴 Active Investigations panel
- 🔴 Blueprint Forge panel
- 🔴 Learning Hub panel
- 🔴 Technology Radar panel
- 🔴 Council Recommendations panel
- 🔴 Curiosity Missions panel

Backends are all live; panels are the next P0 deliverable.

---

_Sister documents: `ATLAS_WORLDWATCH_REPORT.md` · `ATLAS_V2_SELF_IMPROVEMENT_REPORT.md` · `ATLAS_HUD_V2_STYLE_GUIDE.md` · `ATLAS_REALITY_AUDIT.md`._
