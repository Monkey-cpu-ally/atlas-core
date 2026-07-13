# ATLAS Visual Ecosystem

## Purpose

ATLAS has one brain and multiple visual bodies. The backend, memory bank, agents,
digital twins, Weaver, and robot-control services remain authoritative. Visual
clients subscribe to the same event contract and render the state differently.

## Official visual modules

| Module | Technology | Role |
|---|---|---|
| ATLAS Vision | React + React Three Fiber | Everyday web HUD and lightweight 3D core |
| ATLAS Desktop | Tauri | Installed wrapper for ATLAS Vision |
| ATLAS Console | Godot | Dedicated touchscreen and command-center client |
| ATLAS Pulse | TouchDesigner | Audio-reactive particles and large-display effects |
| ATLAS Chamber | Unreal Engine | High-end digital twins and immersive demonstrations |
| ATLAS Motion | Rive | AI faces, logos, icons, and state-machine animation |
| ATLAS Studio | Spline/Blender | Shared 3D asset and scene production |

Unity is reserved for a future XR client only when it provides a feature that the
Godot or Unreal clients cannot provide efficiently.

## Design rule

No visual client may own core memory, safety decisions, robot authorization, or
project truth. Clients are replaceable views over ATLAS Core.

## Shared flow

```text
ATLAS Core / FastAPI
        |
        +-- REST: commands, history, project data
        +-- WebSocket: live visual events
                |
                +-- React HUD
                +-- Godot Console
                +-- TouchDesigner Pulse
                +-- Unreal Chamber
```

## Event envelope

All live visual messages use the same envelope:

```json
{
  "version": "1.0",
  "event": "ai.state.changed",
  "timestamp": "2026-07-13T18:00:00Z",
  "source": "atlas-core",
  "correlation_id": "optional-request-id",
  "payload": {}
}
```

The canonical schema lives at `shared/protocols/atlas-visual-event.schema.json`.

## Initial implementation order

1. Shared event contract and client registry.
2. React event bridge and 3D HUD scene.
3. Rive state mapping for Ajani, Minerva, Hermes, and Council.
4. Tauri desktop packaging.
5. Godot command-console client.
6. TouchDesigner bridge using WebSocket or OSC.
7. Unreal chamber and digital-twin visualization.

## Visual identity

- Ajani: crimson; strategy, defense, execution.
- Minerva: teal; knowledge, biology, nature, teaching.
- Hermes: warm off-white/gold; architecture, engineering, construction.
- Council: purple; multi-agent deliberation.
- Explore Mode: transparent orange; discovery and ingestion.

Rings rotate slowly, respond to state, and return to their home alignment after
an interaction. AI face panels remain outside the central ring assembly.
