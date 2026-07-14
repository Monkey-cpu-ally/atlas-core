# ATLAS Visual Ecosystem

## Purpose

ATLAS has one brain and multiple visual bodies. The backend, memory bank, agents,
digital twins, Weaver, and robot-control services remain authoritative. Visual
clients subscribe to the same event contract and render the state differently.

## Official visual modules

| Module | Technology | Role | Current connection state |
|---|---|---|---|
| ATLAS Vision | React | Primary Genesis Hub and everyday HUD | Active development; connected to visual WebSocket bridge |
| ATLAS Desktop | Tauri + Rust | Installed wrapper for ATLAS Vision | Project shell and Rust bridge are in GitHub; requires successful desktop build |
| ATLAS Console | Godot | Dedicated touchscreen and command-center client | Project, scene, and live event script are in GitHub |
| ATLAS Pulse | TouchDesigner | Audio-reactive particles and large-display effects | Python bridge is in GitHub; requires TouchDesigner installed to run |
| ATLAS Chamber | Unreal Engine | High-end digital twins and immersive demonstrations | C++ bridge component is in GitHub; requires an Unreal project build and editor installation |
| ATLAS Motion | Rive | AI faces, logos, icons, and state-machine animation | State mapping is in GitHub; real `.riv` portrait assets still need to be created and connected |
| ATLAS Studio | Spline/Blender | Shared 3D asset and scene production | Asset workflow planned; editors and source assets are external tools |

Unity is reserved for a future XR client only when it provides a feature that the
Godot or Unreal clients cannot provide efficiently.

## Connection truth

Being present in GitHub means the project files, bridges, configuration, and source
code are stored with ATLAS. It does **not** mean Unreal Engine, TouchDesigner, Rive,
Godot, Blender, or other desktop applications are installed on a device.

A module is considered fully operational only after:

1. Its source files are in GitHub.
2. Its required application or runtime is installed.
3. The project builds successfully.
4. It connects to the ATLAS visual WebSocket or command API.
5. Real ATLAS events have been tested in that client.

## Design rule

No visual client may own core memory, safety decisions, robot authorization, or
project truth. Clients are replaceable views over ATLAS Core.

Every client must follow the Genesis Design Bible:

- voice first,
- quiet idle state,
- one AI face at a time,
- all three faces only for Council or an explicit group request,
- Constellation Wheel rather than the retired ring HUD,
- real capabilities only,
- project artwork as the visual focus,
- and no decorative interface elements without a purpose.

## Shared flow

```text
ATLAS Core / FastAPI
        |
        +-- REST: commands, history, project data
        +-- WebSocket: live visual events
                |
                +-- React Genesis Hub
                +-- Tauri Desktop
                +-- Godot Console
                +-- TouchDesigner Pulse
                +-- Unreal Chamber
                +-- Rive Motion state adapters
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

## Genesis implementation order

1. Stabilize CI, backend event validation, and the shared client registry.
2. Complete the React Genesis Hub state system.
3. Build the working Constellation Wheel and real capability registry.
4. Add one-face portrait presence and Council exceptions.
5. Add Rive state mapping and real portrait assets for Ajani, Minerva, and Hermes.
6. Package the approved React Hub through Tauri.
7. Mirror approved Hub states in Godot.
8. Connect TouchDesigner for ambient particles and audio-reactive effects.
9. Build Unreal Chamber scenes only after the lightweight clients are stable.
10. Establish the Blender/Spline asset pipeline for shared project art and 3D models.

## Visual identity

- Ajani: deep crimson, burgundy, bronze; strategy, leadership, defense, and execution.
- Minerva: teal, sage, living green; knowledge, biology, nature, teaching, and care.
- Hermes: warm off-white, gold, silver; architecture, engineering, invention, and construction.
- Council: royal purple and indigo; multi-agent deliberation.
- Explore Mode: transparent orange; discovery and ingestion.

The retired multi-ring HUD is no longer the active design. The official navigation
system is the circular **Constellation Wheel**, modeled after the approved reference:
illustrated nodes arranged on a curved wheel, a selected node enlarged, adjacent
nodes still visible, large project artwork at center, and contextual details beside it.
