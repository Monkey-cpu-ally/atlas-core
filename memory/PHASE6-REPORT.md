# Phase 6 — Weaver · Completion Report

> Status: ✅ **COMPLETE** · Feb 2026 · 81/81 backend tests passing (`iteration_14.json`)
> Owner: ATLAS Lead Architect · Built on top of Phase 5 (Digital Twin Engine)

---

## 1 · Goals

Build ATLAS's **manufacturing and assembly planning intelligence**:

* Read blueprints (structured JSON now; text/CAD/diagram placeholders ready)
* Match parts against a reusable library
* Spawn a Digital Twin per plan (Phase-5 reuse, not duplication)
* Produce four artefacts per plan:
  - **Build plan** — assembly order, tools, difficulty, total minutes
  - **Manufacturing plan** — cost (materials + 20% labour), timeline, BOM, longest-lead part
  - **Failure prediction** — risk score, missing parts, SPOFs, weak designs
  - **Council outcome** (optional) — Ajani/Minerva/Hermes voices + verdict
* Persist every plan + write a permanent **blueprint memory** in Phase-2 Memory Bank
* Hard constraint: **planning + simulation only**; no hardware control

---

## 2 · Architecture

```
┌──────────────────────────────────────────────────────────────────────────┐
│                              WEAVER · PHASE 6                             │
│                                                                          │
│   routes/weaver.py                                                       │
│       ├─ /api/weaver/parts          CRUD + search + seed + categories    │
│       ├─ /api/weaver/analyze        parse+enrich a blueprint (no twin)   │
│       └─ /api/weaver/plan           full pipeline → WeaverPlan           │
│                                                                          │
│   services/weaver.plan_from_blueprint                                    │
│       │                                                                  │
│       ▼ 1) blueprint_parser.parse()                                      │
│           ├─ structured JSON  → _parse_structured()                      │
│           └─ free text        → LLM (Hermes) + regex fallback            │
│       ▼ 2) match_against_library()                                       │
│       ▼ 3) digital_twin.register_twin()  ← Phase 5                       │
│       ▼ 4) digital_twin.run_and_persist_simulation() × 4                 │
│           assembly · cost · timeline · failure                           │
│       ▼ 5) _build_plan() / _manufacturing_plan() / _failure_prediction() │
│       ▼ 6) (optional) digital_twin.deliberate()  ← Phase 5 council       │
│       ▼ 7) Persist to weaver_plans                                       │
│       ▼ 8) memory_bank.auto_store(category='blueprint')                  │
│                                                                          │
│   services/parts_db.py                                                   │
│       weaver_parts collection (Mongo) · 25-row starter seed              │
│       match_part(name)  →  token-overlap + substring score ≥ 0.5         │
│                                                                          │
│   services/blueprint_parser.py                                           │
│       LLM via llm_provider.send('hermes', system, prompt)                │
│       regex fallback catches "N × Foo" patterns                          │
└──────────────────────────────────────────────────────────────────────────┘
```

### MongoDB collections (new in Phase 6)
| Collection | Purpose |
|------------|---------|
| `weaver_parts` | reusable parts library — categories, cost, lead-time, suppliers, tags |
| `weaver_plans` | one row per WeaverPlan; cross-links `twin_id` (Phase 5) |

---

## 3 · API surface

### Parts library
| Method | Path | Notes |
|--------|------|-------|
| POST | `/api/weaver/parts/seed` | idempotent starter seed (25 parts) |
| GET  | `/api/weaver/parts/categories` | enum introspection |
| POST | `/api/weaver/parts` | add a Part |
| GET  | `/api/weaver/parts` | `?category=&q=&limit=` |
| GET  | `/api/weaver/parts/{id}` | fetch one |
| DELETE | `/api/weaver/parts/{id}` | remove one |

### Blueprint pipeline
| Method | Path | Notes |
|--------|------|-------|
| POST | `/api/weaver/analyze` | parse + library-match only; no twin / no sims |
| POST | `/api/weaver/plan` | **full pipeline**; spawns twin + runs sims |
| GET  | `/api/weaver/plans` | `?owner_agent=&project_id=&limit=` |
| GET  | `/api/weaver/plans/{id}` | one plan |
| DELETE | `/api/weaver/plans/{id}` | `?drop_twin=true` to cascade |

### Pydantic shapes (canonical)
```python
class BlueprintInput:
    format: BlueprintFormat       # text | json | cad_export | diagram
    title: str | None
    description: str | None
    text: str | None
    parts: list[dict]
    relations: list[BlueprintRelation]

class WeaverPlan:
    id: str
    title: str
    owner_agent: str
    related_project_id: str | None
    blueprint: BlueprintInput
    parts_extracted: list[ExtractedPart]
    twin_id: str                  # Phase-5 twin auto-spawned
    build_plan: BuildPlan
    manufacturing_plan: ManufacturingPlan
    failure_prediction: FailurePrediction
    council: CouncilOutcome | None
    created_at: str
    updated_at: str

class BuildPlan:
    assembly_order: list[AssemblyStep]   # step, description, tools, minutes, cautions
    tools_required: list[str]
    materials_required: list[dict]
    difficulty: Difficulty               # trivial|easy|medium|hard|expert
    total_estimated_minutes: float

class ManufacturingPlan:
    total_cost: float
    materials_cost: float
    labour_cost: float                    # 20% of materials_cost
    critical_path_days: float             # from Phase-5 timeline sim
    longest_lead_part: str | None
    bom: list[dict]
    resource_notes: list[str]

class FailurePrediction:
    risk_score: float                     # 0..1; (1 - sim_score) + 0.05·missing_count
    missing_parts: list[str]              # not in the library
    weak_designs: list[str]               # warnings from failure sim
    single_points_of_failure: list[str]
    notes: list[str]
```

---

## 4 · Heuristics

### Difficulty curve (build_plan.difficulty)
```
total_minutes < 60   and no electronics   →  TRIVIAL
total_minutes < 240  and no machining     →  EASY
total_minutes < 960                       →  MEDIUM
total_minutes < 2880                      →  HARD
otherwise                                 →  EXPERT
```

### Per-category assembly minutes (per unit)
```
fastener      1.5 min
material      8.0 min
electronic   12.0 min
sensor        8.0 min
actuator     10.0 min
component     6.0 min
consumable    1.0 min
tool          0.0 min   (not assembled)
```

### Risk score
```
risk_score = clip( (1 - failure_sim_score) + 0.05 * |missing_parts|, 0, 1 )
```

### Tools required
Union of category-keyed tool hints:
* Fastener → "Hex key set M2-M6", "Screwdriver set"
* Electronic / Sensor → "Soldering iron", "Multimeter"
* Actuator → "Hex key set M2-M6", "Multimeter"
* Material → "3D printer 200x200", "Cutting tool"

---

## 5 · Starter parts library (25 entries)

| Category | Examples |
|----------|----------|
| material | PLA, PETG, Al-6061 sheet, CFRP plate |
| consumable | Solder 60/40 |
| fastener | M3 cap screw 10mm, M3 hex nut, M5 cap screw 16mm |
| electronic | ATmega328P, ESP32-S3, STM32F4, Buck converter, LiPo 1S |
| sensor | MPU6050 IMU, BME280, VL53L1X ToF, OV2640 camera |
| actuator | SG90 servo, MG996R, 2204 brushless, N20 gearmotor |
| tool | Soldering iron, Hex key set, 3D printer, Multimeter |

`POST /api/weaver/parts/seed` is idempotent — calling it twice returns `{seeded: 0}` the second time.

---

## 6 · Memory wiring

| Event | Memory write |
|-------|--------------|
| `POST /api/weaver/plan` | `category='blueprint'` (PERMANENT) tagged `[weaver, <twin_category>]` · source_id = `plan.id` |
| Auto-spawned twin (Phase 5) | `category='project'` (PERMANENT) tagged `[<twin_category>, twin]` |
| 4 sims per plan | `category='project'` + `category='research'` rows (`success-memory` / `failure-memory`) — same as native twin sims |
| Optional council deliberation | `category='council'` (PERMANENT) tagged `[<twin_category>, twin, <verdict>]` |

A single plan with council deliberation produces **10 memory rows** — one anchoring blueprint memory + one twin-registration memory + 4 × (project+research) sim memories + 1 council memory. All are queryable via Phase-2 `/api/membank/search` and `/api/membank/graph/*`.

---

## 7 · Agent roles

Reused verbatim from Phase 5:

* **Ajani** (engineering, manufacturing, risk) — primary critic when owner_agent is unset; default owner of weaver plans
* **Minerva** (material science, environmental impact) — flags non-recyclable materials and energy assumptions
* **Hermes** (validation, optimisation, consistency) — the only persona used by the blueprint LLM parser (pattern hunter is the right fit)
* **Council** — aggregates the three voices; verdict ∈ {approve, revise, reject, pending}

---

## 8 · Future compatibility (already in place)

| Field | Phase | Will hold |
|-------|-------|-----------|
| `BlueprintFormat.CAD_EXPORT` | future | STEP/STL/glTF ingest |
| `BlueprintFormat.DIAGRAM` | future | image/PDF OCR |
| `ExtractedPart.library_part_id` | now | already used for matching |
| `WeaverPlan.related_project_id` | now | links a plan to a learning project (Phase 1/2) |
| Twin's `state.integrations` / `state.hardware_binding` | Phase 7 | when the Robot Control Layer wants to bind a Weaver-spawned twin to a real device |

The architect can extend without schema migration: free-text blueprints already work via the Hermes LLM parser; CAD/diagram formats currently fall through to the text path on the `description` field, so a Phase-future CAD parser can be slotted in without changing the API.

---

## 9 · Worked example — Pan/tilt camera rig

Input:
```json
{
  "title": "2-arm pan/tilt camera rig v1",
  "owner_agent": "ajani",
  "deliberate": false,
  "blueprint": {
    "format": "json",
    "parts": [
      {"name":"ESP32-S3 module","category":"electronic","quantity":1},
      {"name":"MPU6050 IMU","category":"sensor","quantity":1},
      {"name":"SG90 micro servo","category":"actuator","quantity":2},
      {"name":"PLA filament 1.75mm","category":"material","quantity":0.2,"unit":"kg"},
      {"name":"M3 cap screw 10mm","category":"fastener","quantity":8},
      {"name":"Custom carbon arm","category":"component","quantity":2}
    ],
    "relations": [
      {"from_part":"ESP32-S3 module","to_part":"SG90 micro servo","relation":"signals"},
      {"from_part":"ESP32-S3 module","to_part":"MPU6050 IMU","relation":"signals"},
      {"from_part":"Custom carbon arm","to_part":"SG90 micro servo","relation":"mounts"}
    ]
  }
}
```

Output (abridged):
```
plan_id = 033cad5da803...
twin_id = ee9ce63ace25...
build_plan      : difficulty=medium · 6 steps · 72 min
                  tools = ['Soldering iron', 'Multimeter', 'Hex key set M2-M6',
                          'Screwdriver set', '3D printer 200x200', 'Cutting tool']
manufacturing   : materials=$19.24, labour=$3.85, total=$23.09
                  critical_path_days=9 (longest_lead = ESP32-S3 module)
failure         : risk=0.65
                  missing = ['Custom carbon arm']
                  SPOF    = ['ESP32-S3 module (fan-out ≥ 2)']
```

---

## 10 · Test coverage

* `/app/backend/tests/test_weaver_phase6.py` — 13 cases (12 fast + 1 slow LLM-bound)
* `/app/backend/tests/test_weaver_phase6_extras.py` — 8 cases (extra review-request assertions)
* `/app/backend/pytest.ini` — registers the `slow` marker

Run fast suite (`< 5 s`):
```
cd /app/backend && pytest tests/test_weaver_phase6*.py -m 'not slow' -v
```

Full suite (`< 50 s` including 1 council deliberation):
```
cd /app/backend && pytest tests/test_weaver_phase6*.py -v
```

---

## 11 · Roadmap update

```
Phase 0 — Audit / Cleanup             ✅
Phase 1 — Real LLM Integration        ✅
Phase 2 — Memory Bank                  ✅
Phase 3 — Research Pipeline            ✅
Phase 4 — Voice System                 ✅
Phase 5 — Digital Twin Engine          ✅
Phase 6 — Weaver                       ✅  ← THIS PHASE
Phase 7 — Robot Control Layer          ⏳  awaits target hardware spec
```

---

## 12 · Recommended next steps (when architect is ready)

1. **HUD tile for Weaver** — `BlueprintWorkbench` already exists as a HUD panel; add a "Plan with Weaver" CTA that POSTs the panel's current blueprint to `/api/weaver/plan` and surfaces the cost/timeline/risk cards inline. ~1.5 h, no aesthetic change.
2. **Free-text blueprint via voice** — wire `"hey atlas, plan: <description>"` to send the transcript as `{format: "text", text}` into `/api/weaver/plan`. Already supported by the LLM parser; just one new voice intent. ~30 min.
3. **CAD ingest stub** — add a `services/cad_ingest.py` placeholder that turns an STL/STEP into a list of named meshes; route them into `BlueprintInput.parts`. ~2 h.
4. **Phase 7 Robot Control bridge** — keep `TwinState.hardware_binding` filled by Weaver when an architect explicitly opts in via plan request. Pre-empts re-work when Robot Control lands. ~30 min.
