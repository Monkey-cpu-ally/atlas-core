# Phase 7 — Robot Control Layer · Completion Report
_Feb 2026 · ATLAS Core HUD_

## Goal
Bring Atlas Core into the physical world: an MQTT-style HTTP bridge for local
hardware (ESP32 / Raspberry Pi), with strict **Simulation-First** safety and
role-based access. Three architect-spec seed targets must come online on first
boot, each bound to its own Phase-5 Digital Twin: **POSEIDON-BUOY**,
**AETHER-STATION**, **SOIL-WATCH**.

## Hard Constraints (architect spec)
1. **Simulation-first** — every non-trivial command flows
   `Twin → Simulate → Validate → Execute`. No bypass.
2. **Owner-locked** — `actuate`, `motion`, `bind_twin`, `firmware_update`,
   `emergency_stop` require role `owner`.
3. **Allow-list** — every command kind must be on `ALLOWED_COMMANDS`.
4. **Full audit trail** — every device action writes a Phase-2 Memory Bank
   record (project/council/research category per type).
5. **Local LAN only** — soft role gate via `X-Atlas-Role` header for v1
   (no JWT until deployment moves off the architect's network).

## Files
| File | Purpose |
| --- | --- |
| `backend/models/robot_models.py` | Pydantic v2 models + enums (Role, DeviceKind, DeviceStatus, CommandKind, CommandStatus) + `OWNER_ONLY_COMMANDS` set |
| `backend/services/robot.py` | Registry, telemetry, sim-first command pipeline, idempotent 3-device seed, twin auto-spawn + auto-bind |
| `backend/routes/robot.py` | REST surface at `/api/robot/*` |
| `backend/tests/test_robot_phase7.py` | 10 smoke tests (run via pytest) |
| `backend/tests/test_robot_membank_wiring.py` | 3 Memory-Bank wiring tests (added by testing agent) |
| `frontend/src/components/HUD/RobotPanel.js` | Embedded UI panel inside SYSTEMS tile |

## REST surface
```
GET    /api/robot/roles
POST   /api/robot/seed
GET    /api/robot/devices                              ?status=&kind=&limit=
POST   /api/robot/devices                              X-Atlas-Role: owner
GET    /api/robot/devices/{id}
POST   /api/robot/devices/{id}/bind-twin               X-Atlas-Role: owner
POST   /api/robot/devices/{id}/telemetry               device-side push (no role)
GET    /api/robot/devices/{id}/telemetry               ?limit=
POST   /api/robot/devices/{id}/command                 X-Atlas-Role: <role>
GET    /api/robot/devices/{id}/commands                ?limit=
GET    /api/robot/devices/{id}/commands/inbox          device-side poll (delivered-once)
GET    /api/robot/commands/{id}
POST   /api/robot/devices/{id}/emergency-stop          X-Atlas-Role: owner
```

## Command pipeline
```
                          ┌───────────────┐
                          │  submit_cmd   │
                          └──────┬────────┘
                                 ▼
   1. authorise(role, kind) ──► REJECT if owner-only & not owner
                                 │
                                 ▼
   2. device_lookup           ──► REJECT if device not found
                                 │
                                 ▼
   3. simulate via Phase-5 twin (skipped for ping/read_telemetry)
        sim = dt.run_and_persist_simulation(twin_id, FAILURE)
        cmd.sim_score = sim.score
                                 │
                                 ▼
   4. validate (score ≥ 0.50)  ──► REJECT with sub-threshold reason
                                 │
                                 ▼
   5. execute → MQTT-style HTTP bridge (poll on inbox)
        REJECT if device.status == SAFE_STATE & cmd ≠ ping/e-stop
                                 │
                                 ▼
   6. memory log (Phase-2 mb.auto_store, category=project)
```

## Seed data
On startup `_seed_phase7_devices()` runs `services.robot.seed_if_needed()`:

| Device | Kind | Sensors | Auto-twin (`TwinCategory.ENVIRONMENT`) |
| --- | --- | --- | --- |
| POSEIDON-BUOY | sensor | water_temperature, ph, turbidity | "POSEIDON-BUOY twin" |
| AETHER-STATION | sensor | co2, pm2_5, voc, temperature | "AETHER-STATION twin" |
| SOIL-WATCH | sensor | soil_moisture, soil_temperature, nutrient_level | "SOIL-WATCH twin" |

All three devices are twin-bound out of the box — required so the Simulation-
First gate can run an actual sim on any non-trivial command.

## Roles
```
owner   → full control (devices, binding, actuate, motion, firmware, e-stop)
council → may issue read-only / configure recommendations
ajani   → engineer voice (read-only + recommend)
minerva → scientist voice (read-only + recommend)
hermes  → validator voice (read-only + recommend)
guest   → read-only
```
Role is parsed from `X-Atlas-Role` header (case-insensitive; unknown → guest).

## Frontend (HUD wire-up)
Embedded inside `DiagnosticsPanel.js` (the SYSTEMS middle-ring tile) — no ring
geometry changes. The new `RobotPanel.js` shows:
- Role selector (owner / council / ajani / minerva / hermes / guest)
- Device list with status dot, kind, status, `twin-bound` badge
- PING / ACTUATE / E-STOP buttons (issue against selected device)
- Last-command card with status colour, sim_score, rejection_reason
- Telemetry history (last 5)
- Command log (last 8, status-coloured)

## Verification
- **Local pytest:** 10/10 in `tests/test_robot_phase7.py` (~1.5s)
- **Testing agent (iteration_15.json):** 13/13 (10 + 3 memory-bank wiring) on
  the external preview URL. All architect-spec items pass:
  - roles enum + owner_only_commands surfaced
  - seed idempotent, all 3 devices twin-bound
  - device registration owner-only (guest → 403, owner → 200)
  - telemetry roundtrip + ONLINE status flip + history
  - sim-first pipeline (sim_score populated on owner ACTUATE against twin)
  - guest ACTUATE → REJECTED with "owner-only" reason
  - owner PING on non-twin device → EXECUTED
  - inbox delivers-once (second poll empty)
  - EMERGENCY_STOP gate + SAFE_STATE blocks subsequent actuate
  - Phase-2 Memory Bank auto-store wired for device/telemetry/command

## Known v1 limitations
- HTTP-poll MQTT bridge (no broker). To slot in a real broker, re-implement
  `_publish_command()` against `paho-mqtt`; API surface stays unchanged.
- Soft role gate (header-based). JWT comes in when the deployment leaves the
  local LAN.
- ROS2 compatibility via future adapter only.
