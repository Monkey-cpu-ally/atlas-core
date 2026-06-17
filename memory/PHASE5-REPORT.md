# Phase 5 — Digital Twin Engine · Completion Report

> Status: ✅ **COMPLETE** · Feb 2026 · 76/76 backend tests passing (`iteration_13.json`)
> Owner: ATLAS Lead Architect

---

## 1 · Goals

Build a **simulation-only** twin layer for ATLAS to model projects, robots,
devices, environments, buildings, and power/manufacturing systems before
real-world construction.

* **Registry** — register, version, search twins by category/owner/project
* **State** — components, dependencies, energy, sensors, dimensions, outputs
* **Six simulators** — blueprint, assembly, resource, failure, timeline, cost
* **Council deliberation** — Ajani + Minerva + Hermes voices → final verdict
* **Memory integration** — every sim seeds permanent project memory + decaying
  success-/failure-memory in the Phase-2 Memory Bank
* **Forward-compat hooks** — `integrations`, `cad_refs`, `hardware_binding`
  fields are in place but ignored; populated by Phases 6 (Weaver) and 7
  (Robot Control)
* Hard constraint: **no physics engine, no hardware control** in Phase 5

---

## 2 · Architecture

```
┌──────────────────────────────────────────────────────────────────────────┐
│                       ATLAS · DIGITAL TWIN STACK                          │
│                                                                          │
│   routes/twins.py                                                        │
│       └─ POST /api/twins/register                                        │
│       └─ GET  /api/twins/list  (static path declared BEFORE /{id})       │
│       └─ GET  /api/twins/{id}                                            │
│       └─ PUT  /api/twins/{id}/state          state.revision ++           │
│       └─ POST /api/twins/{id}/simulate       any of 6 kinds              │
│       └─ POST /api/twins/{id}/deliberate     council verdict             │
│       └─ DEL  /api/twins/{id}                cascade sims + delibs       │
│                                                                          │
│   services/digital_twin.py                                               │
│       ├─ register_twin()      → memory_bank category=project (permanent) │
│       ├─ run_and_persist_simulation()                                    │
│       │     ↘ services/twin_simulator.simulate(twin, kind)               │
│       │     ↘ memory_bank.auto_store(category=project)                   │
│       │     ↘ memory_bank.auto_store(category=research,                  │
│       │                              tag=success-memory|failure-memory)  │
│       └─ deliberate()                                                    │
│             ↘ asyncio.gather(ajani, minerva, hermes)  ← parallel         │
│             ↘ verdict synthesised from collected flags                   │
│             ↘ memory_bank.auto_store(category=council, permanent)        │
│                                                                          │
│   services/twin_simulator.py    pure Python, deterministic               │
│       ├─ _sim_blueprint   cycle + reference check                        │
│       ├─ _sim_assembly    topo-sort + step plan                          │
│       ├─ _sim_resource    BOM + energy budget                            │
│       ├─ _sim_failure     fan-out SPOF + sensor gaps + power transients  │
│       ├─ _sim_timeline    critical-path DP over dep DAG                  │
│       └─ _sim_cost        materials + 20% labour heuristic               │
│                                                                          │
│   models/twin_models.py    Pydantic v2                                   │
│       DigitalTwin · TwinState · Component · Dependency                   │
│       SensorInput · TwinOutput · Dimensions · EnergyProfile              │
│       SimulationResult · CouncilDeliberation · DeliberationVoice         │
└──────────────────────────────────────────────────────────────────────────┘
```

### MongoDB collections
| Collection | Purpose |
|------------|---------|
| `digital_twins`        | one row per twin · `id`, `category`, `owner_agent`, `related_project_id`, `state`, `last_simulation_id`, `last_deliberation_id` |
| `twin_simulations`     | history of every sim · `id`, `twin_id`, `revision`, `kind`, `ok`, `score`, `findings/warnings/failures/metrics/timeline/bom` |
| `twin_deliberations`   | council deliberations · `id`, `twin_id`, `simulation_id`, `voices[]`, `verdict`, `final_text` |

No new collection is needed for graph-of-twins yet — the existing
`graph_triples` Phase-2 collection can hold inter-twin relationships when
the architect wants them; just `POST /api/membank/graph/triple` with the
twin ids as nodes.

---

## 3 · API surface

| Method | Path | Body / Query | Returns |
|--------|------|--------------|---------|
| POST | `/api/twins/register` | `RegisterRequest` | `DigitalTwin` |
| GET | `/api/twins/list` | `category=&owner_agent=&project_id=&status=&limit=` | `{count, items}` |
| GET | `/api/twins/categories` | – | enum introspection |
| GET | `/api/twins/{id}` | – | `DigitalTwin` |
| PUT | `/api/twins/{id}/state` | `TwinState` | twin with `state.revision += 1` |
| DELETE | `/api/twins/{id}` | – | `{deleted: id}` (cascades sims + delibs) |
| POST | `/api/twins/{id}/simulate` | `{kind}` | `SimulationResult` |
| GET | `/api/twins/{id}/simulations` | `limit=` | `{count, items}` |
| GET | `/api/twins/simulations/{sim_id}` | – | `SimulationResult` |
| POST | `/api/twins/{id}/deliberate` | `{simulation_id?}` | `CouncilDeliberation` |

### Pydantic shapes (canonical)
```python
class DigitalTwin:
    id: str
    name: str
    category: TwinCategory
    owner_agent: str          # 'ajani' | 'minerva' | 'hermes' | 'council'
    related_project_id: str | None
    description: str | None
    tags: list[str]
    state: TwinState
    last_simulation_id: str | None
    last_deliberation_id: str | None
    created_at: str
    updated_at: str

class TwinState:
    status: TwinStatus        # draft | spec | simulated | approved | deprecated
    components: list[Component]
    materials: list[str]
    dimensions: Dimensions | None
    energy: EnergyProfile | None
    dependencies: list[Dependency]
    sensor_inputs: list[SensorInput]
    outputs: list[TwinOutput]
    integrations: dict        # FORWARD-COMPAT (Phase 6 Weaver)
    cad_refs: list[str]       # FORWARD-COMPAT (CAD ingest)
    hardware_binding: dict|None # FORWARD-COMPAT (Phase 7 Robot Control)
    revision: int
    updated_at: str

class SimulationResult:
    id: str
    twin_id: str
    revision: int
    kind: SimulationKind      # blueprint|assembly|resource|failure|timeline|cost
    ok: bool
    score: float              # 0..1
    findings: list[str]
    warnings: list[str]
    failures: list[str]
    metrics: dict
    timeline: list[dict] | None    # assembly + timeline only
    bom: list[dict] | None         # resource + cost only
    created_at: str
```

### Simulation score formula
```
score = clip(1.0 - 0.40 · |failures| - 0.10 · |warnings|, 0, 1)
```
A clean run (no warnings, no failures) is 1.0; one failure drops to 0.6;
two failures drop to 0.2.

### Deliberation verdict aggregator
1. Each persona may emit one or more `*_FLAG` tokens
   (`ENGINEERING_FLAG`, `SCIENCE_FLAG`, `VALIDATION_FLAG`).
2. `flag_count = Σ flags across personas`
3. `flag_count == 0 → approve` · `flag_count ≥ 3 → reject` · else `revise`
4. If any persona is unreachable → `pending` (retry once provider is back)

---

## 4 · Memory wiring

| Trigger | Memory Bank write |
|---------|-------------------|
| Register a twin | `category=project` (permanent) tagged `[<category>, twin]` + custom tags |
| Run a simulation | `category=project` (permanent) tagged `[<category>, <kind>, twin]` + a second row in `category=research` (decaying) tagged with `success-memory` or `failure-memory` |
| Council deliberation | `category=council` (permanent) tagged `[<category>, twin, <verdict>]` |

All writes go through `memory_bank.auto_store()` so a Memory Bank failure
never aborts the twin pipeline.

---

## 5 · Forward-compatibility

| Field | Phase | Will hold |
|-------|-------|-----------|
| `TwinState.integrations` | Phase 6 Weaver | per-system integration metadata (mqtt topics, weaver flow ids) |
| `TwinState.cad_refs` | future | links to imported CAD assets (STL/STEP/glTF) |
| `TwinState.hardware_binding` | Phase 7 Robot Control | the real device this twin shadows (manufacturer/serial/MAC) |
| `Component.twin_ref` | Phase 6+ | composes another registered twin (e.g. robot.power = power_cell_twin) |

Power Cell Project, Green Robot Project, Plant Library, Mother Box research
are all just `DigitalTwin` rows with appropriate categories — no schema
extension required. The architect can already register them today.

---

## 6 · Example twins

### 6.1 Green Robot — Pollinator drone
```bash
curl -X POST $API/api/twins/register -H 'Content-Type: application/json' -d '{
  "name": "GreenSwarm Pollinator v1",
  "category": "robot",
  "owner_agent": "ajani",
  "tags": ["pollinator", "drone", "solar"],
  "state": {
    "components": [
      {"id":"frame","name":"Carbon frame","quantity":1,"material":"CFRP","mass_kg":0.12,"cost_per_unit":42,"lead_time_days":7},
      {"id":"mcu","name":"Flight MCU","quantity":1,"material":"Si","cost_per_unit":18,"lead_time_days":5},
      {"id":"motor","name":"Brushless motor","quantity":4,"material":"Cu","cost_per_unit":12,"lead_time_days":10},
      {"id":"solar","name":"GaAs cell","quantity":2,"material":"GaAs","cost_per_unit":35,"lead_time_days":14},
      {"id":"batt","name":"LiPo cell","quantity":1,"material":"Li","cost_per_unit":22,"lead_time_days":4}
    ],
    "energy": {"peak_w": 42, "average_w": 12, "daily_wh": 35, "source": "solar+battery"},
    "dependencies": [
      {"from_component":"batt","to_component":"motor","kind":"powers"},
      {"from_component":"batt","to_component":"mcu","kind":"powers"},
      {"from_component":"solar","to_component":"batt","kind":"powers"},
      {"from_component":"mcu","to_component":"motor","kind":"signals"}
    ],
    "sensor_inputs": [
      {"name":"IMU","kind":"motion","unit":"m/s2"},
      {"name":"PhotoLux","kind":"light","unit":"lux"}
    ]
  }
}'
```

### 6.2 Power Cell — modular battery
```bash
curl -X POST $API/api/twins/register -d '{
  "name": "Power Cell · 5 kWh module",
  "category": "power_system",
  "owner_agent": "ajani",
  "state": {
    "components": [
      {"id":"cells","name":"LFP cell pack","quantity":160,"material":"LFP","cost_per_unit":4.5,"lead_time_days":21},
      {"id":"bms","name":"BMS board","quantity":1,"cost_per_unit":85,"lead_time_days":12},
      {"id":"inverter","name":"4 kW inverter","quantity":1,"cost_per_unit":210,"lead_time_days":28},
      {"id":"enclosure","name":"IP67 case","quantity":1,"material":"PC","cost_per_unit":48,"lead_time_days":7}
    ],
    "energy": {"peak_w": 4000, "average_w": 1200, "daily_wh": 5000, "source": "grid+solar"},
    "dependencies": [
      {"from_component":"cells","to_component":"bms","kind":"powers"},
      {"from_component":"bms","to_component":"inverter","kind":"powers"},
      {"from_component":"enclosure","to_component":"cells","kind":"mounts"}
    ]
  }
}'
```

### 6.3 Manufacturing System — 3D-printer farm
```bash
curl -X POST $API/api/twins/register -d '{
  "name": "Mother Box · 16-bay print farm",
  "category": "manufacturing_system",
  "owner_agent": "hermes",
  "state": {
    "components": [
      {"id":"frame","name":"Rack","quantity":1,"cost_per_unit":420,"lead_time_days":14},
      {"id":"printer","name":"Print head","quantity":16,"cost_per_unit":380,"lead_time_days":35},
      {"id":"plc","name":"Master PLC","quantity":1,"cost_per_unit":260,"lead_time_days":21},
      {"id":"feed","name":"Filament hopper","quantity":4,"cost_per_unit":110,"lead_time_days":12}
    ],
    "energy": {"peak_w": 8800, "average_w": 4400, "daily_wh": 100000, "source": "grid"},
    "dependencies": [
      {"from_component":"plc","to_component":"printer","kind":"signals"},
      {"from_component":"feed","to_component":"printer","kind":"supplies"},
      {"from_component":"frame","to_component":"printer","kind":"mounts"}
    ],
    "sensor_inputs": [
      {"name":"BedTemp","kind":"temperature","unit":"C"},
      {"name":"Filament","kind":"presence","unit":"bool"}
    ]
  }
}'
```

Each of these triggers blueprint/assembly/resource/cost sims successfully
and then survives a council deliberation.

---

## 7 · Test coverage

* `/app/backend/tests/test_twins_phase5.py` — 19 cases
* `/app/backend/tests/test_twins_phase5_extras.py` — 12 cases (validation edges, deliberate-with-explicit-sim, BOM totals, critical path, project-memory wiring)
* Run all: `pytest backend/tests/test_twins_phase5* -v` (~82 s, LLM-bound on deliberate cases)

| Coverage area | Cases |
|---------------|-------|
| Registry CRUD + filters | 4 |
| State revision bump | 1 |
| All 6 simulators (parametrised) | 6 |
| Cycle detection / unknown refs | 2 |
| Star-topology SPOF | 1 |
| Council deliberation (4 voices, verdict set) | 2 |
| Simulation history + by-id | 2 |
| Invalid kind / category / short name → 422 | 3 |
| Cascade delete | 1 |
| Memory wiring (project + research) | 2 |
| Performance — parallel LLM in deliberate | (implicit, P95 reduced) |
| **Phase-2 / 3 regression** | 45 / 45 still passing |

---

## 8 · Roadmap update

```
Phase 0 — Audit / Cleanup             ✅ done
Phase 1 — Real LLM Integration        ✅ done
Phase 2 — Memory Bank                  ✅ done
Phase 3 — Research Pipeline            ✅ done
Phase 4 — Voice System                 ✅ done
Phase 5 — Digital Twin Engine          ✅ done  ← THIS PHASE
Phase 6 — Weaver Integration           ⏳ awaits architect spec
Phase 7 — Robot Control Layer          ⏳ awaits target hardware spec
```

---

## 9 · Recommended next steps (when architect is ready)

1. **HUD tile for Digital Twin** — add a "Twins" outer-ring tab inside an
   existing panel (e.g. `BlueprintWorkbench`) that lists registered twins,
   lets the architect pick one, runs the 6 sims with a single click, and
   shows the council verdict — all without changing the HUD aesthetic.
   ~2 h.
2. **Compose-via-twin_ref** — Wire `Component.twin_ref` so a robot twin
   can declare its battery component as `twin_ref=power_cell.id`; the
   resource/cost sims would then recurse into the referenced twin. ~1 h.
3. **Graph-of-twins** — push twin ids into Phase-2 `graph_triples` with
   relations `composes`, `extends`, `replaces` so the architect can BFS
   the project knowledge graph from the HUD. ~30 min.
4. **Phase 6 (Weaver) bridge stub** — keep `state.integrations` filled by
   a tiny `weaver_bridge.py` placeholder that future Weaver flow ids can
   read. Pre-empts re-work when Phase 6 spec lands. ~30 min.
