# ATLAS Level 8 Upgrade Roadmap

## Objective

Move ATLAS from an advanced agentic AI platform to a reliable, embodied engineering/research system capable of long-running autonomous missions, verified tool use, simulation-backed design work, persistent memory, and hardware-in-the-loop execution.

## Level 8 Definition

ATLAS reaches Level 8 when the following are all true:

1. One production-grade runtime unifies personas, memory, knowledge, tools, events, jobs, HUD, simulation, and robot-control contracts.
2. Ajani, Minerva, Hermes, and Council can run multi-step missions with explicit planning, execution, verification, recovery, and durable state.
3. Semantic memory and graph memory operate continuously with source provenance and compatibility-safe embeddings.
4. Tool Bus execution is persistent, auditable, approval-aware, and recoverable across restarts.
5. Research output is source-grounded and can feed engineering workflows without bypassing evidence or safety gates.
6. Digital Twin uses a real physics/geometry backend for at least one supported engineering domain.
7. Robot Control supports hardware-in-the-loop command acknowledgement, telemetry validation, emergency-stop semantics, and simulation fallback.
8. Weaver can execute a constrained validated task through the same mission architecture, first in simulation and then against authorized hardware.
9. CI verifies the full mission path and blocks regressions before merge.
10. Main is protected by required checks and release criteria.

## Upgrade Sequence

### Gate 1 — Stabilized Main

- Refresh and integrate runtime integrity fixes from PR #169.
- Preserve upload portability, MQTT lifecycle correctness, vector compatibility guards, and Robot Control state-integrity fixes.
- Remove superseded foundation/upload PRs after equivalent fixes are proven on main.
- Enable required checks/branch protection on main after workflows are confirmed stable.

Exit criteria:
- backend starts in CI and supported deployment targets
- runtime inspector reports Memory/LLM/MQTT readiness
- all current backend regression tests pass
- no known phantom robot/twin bindings

### Gate 2 — Persistent Intelligence Layer

- Refresh engineering/memory work from PR #96 against stabilized main.
- Run MongoDB as source of truth.
- Run Qdrant as semantic retrieval keyed to canonical memory IDs.
- Add embedding model/version metadata and migration/reindex strategy.
- Connect graph memory and provenance to semantic retrieval.

Exit criteria:
- semantic retrieval survives restart
- incompatible vectors cannot be mixed
- persona memories remain isolated while shared knowledge is retrievable
- retrieval quality tests pass against a fixed evaluation set

### Gate 3 — Durable Tool Bus + Event Fabric

- Refresh PR #105 and replace in-memory-only event persistence with SQLite/PostgreSQL or equivalent durable storage.
- Define canonical mission/job/event envelopes.
- Add idempotency keys, retry classes, cancellation, timeout, and recovery semantics.
- Refresh visual event contracts from PR #106 only after backend event contracts stabilize.

Exit criteria:
- job/event history survives restart
- failed jobs can resume or terminate deterministically
- duplicate commands do not duplicate physical actions
- HUD and other clients consume one event contract

### Gate 4 — Knowledge Bank V1 Consolidation

- Consolidate overlapping PRs #170, #172, and #184 rather than merging divergent histories blindly.
- Use the finalized 48-subject taxonomy.
- Preserve source authority tiers, licensing/storage policy, cross-listing, ingestion, retrieval, citation readiness, and usable-knowledge metrics.
- Prove end-to-end ingestion -> distillation -> memory/graph -> retrieval -> cited response.

Exit criteria:
- all 48 subjects validate
- catalog coverage is never reported as ingestion/expert readiness
- citation provenance is preserved end-to-end
- Knowledge Bookshelf uses only real backend data

### Gate 5 — Autonomous Mission Engine

Implement a mission state machine:

PLAN -> APPROVE -> EXECUTE -> OBSERVE -> VERIFY -> REVISE -> COMPLETE/FAIL

Required capabilities:
- task decomposition
- tool selection
- dependency graph
- checkpoints
- budget/time limits
- failure classification
- retry/replan
- human approval boundaries
- artifact/result verification
- durable mission memory

Persona verification roles:
- Ajani: strategy, objective integrity, risk, priorities
- Minerva: evidence, research quality, citations, domain assumptions
- Hermes: engineering correctness, code, systems, simulation, implementation validation
- Council: final cross-check for high-impact missions

Exit criteria:
- ATLAS completes a 30–60 minute software/research mission without manual step-by-step prompting
- interrupted missions can resume from durable checkpoints
- ATLAS cannot mark completion when required verification gates fail

### Gate 6 — Engineering Execution Stack

- Integrate OpenCV inspection.
- Integrate CadQuery CAD generation.
- Integrate KiCad ERC/DRC validation.
- Add controlled local artifact workspace.
- Add simulation adapters under Tool Bus contracts.
- Add deterministic engineering test fixtures.

Exit criteria:
- ATLAS can research -> design -> generate artifact -> validate -> revise -> report
- engineering outputs carry provenance, tool logs, and verification status

### Gate 7 — Real Digital Twin

Replace rule-only claims with a real simulation backend for an initial supported domain.

Minimum viable Level-8 twin:
- geometry model
- physical parameters and units
- deterministic solver integration
- scenario/config versioning
- telemetry/state synchronization
- simulation-vs-real comparison hooks

Preferred first domain:
- robot mechanism or electromechanical assembly where CAD + motion/loads + telemetry can be verified.

Exit criteria:
- identical inputs reproduce simulation results within tolerance
- ATLAS can detect invalid parameters and solver failures
- mission engine consumes simulation results as evidence rather than prose

### Gate 8 — Hardware-in-the-Loop Robot Control

- Device identity and registration
- authenticated command channel
- command acknowledgement
- telemetry sequence validation
- watchdog/heartbeat
- emergency stop
- command deduplication/idempotency
- simulation fallback
- hardware/simulation mode clearly distinguished

Exit criteria:
- a registered test device acknowledges authorized commands
- ATLAS records command -> acknowledgement -> telemetry result
- loss of communication fails safe
- no software path can claim physical success without acknowledgement

### Gate 9 — Weaver Constrained Autonomy

Start with one narrow, testable Weaver capability.

Example progression:
1. simulate pick/place trajectory
2. validate workspace/collision constraints
3. send approved command to test hardware
4. receive acknowledgement and telemetry
5. visually inspect result
6. revise/retry within limits
7. archive mission evidence

Exit criteria:
- constrained Weaver task passes repeatedly in simulation
- same task passes on authorized hardware with evidence
- failure paths terminate safely

### Gate 10 — Level 8 Certification Suite

Create a fixed ATLAS benchmark suite covering:
- persona contract integrity
- memory persistence
- semantic retrieval
- research provenance
- tool execution
- autonomous mission recovery
- software engineering task
- CAD/electronics task
- Digital Twin task
- robot-control simulation task
- hardware-in-the-loop task where hardware is available
- HUD/event synchronization
- safety/authorization checks

A Level 8 release must not be based on feature presence. It requires repeatable passing evidence.

## Initial Integration Priority

1. PR #169 runtime stabilization
2. PR #96 engineering + Qdrant refresh
3. PR #105 durable Tool Bus/events refresh
4. Knowledge Bank consolidation (#170/#172/#184)
5. PR #106 event-driven visual ecosystem refresh
6. PR #144 HUD redesign refresh
7. Mission engine
8. real Digital Twin
9. hardware-in-the-loop Robot Control
10. Weaver constrained autonomy

## Current Rule

Do not add major new feature branches until the current integration debt is reduced. Prefer one canonical implementation per capability, one event contract, one mission state model, and one measurable definition of done.
