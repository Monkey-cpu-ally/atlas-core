# Flutter Atlas Voice Core Scaffold

Starter implementation scaffold for:
- voice-first center core,
- council mode sequencing,
- ethereal sigil ring behavior,
- Flutter-to-Unity bridge payload contracts.

This is intentionally a focused scaffold, not a full app.

## Folder layout

- `lib/src/models/voice_core_state.dart`
  - canonical visual/state model
- `lib/src/controllers/voice_core_controller.dart`
  - council timeline + state transitions
- `lib/src/models/voice_core_timing.dart`
  - centralized timing and bounds config for controller/widgets/tests
- `lib/src/bridge/unity_bridge_contract.dart`
  - event names + payload serializers + inbound validator/handler
- `lib/src/widgets/voice_core_layer.dart`
  - composable widget stack (dim + sigil + core + neutral rings)
- `lib/src/widgets/ethereal_sigil_ring.dart`
  - low-opacity sigil renderer
- `test/`
  - baseline behavior tests

## Quick integration

1. Copy this package into your Flutter workspace, or consume it as a path dependency.
2. Provide your Unity core widget as `coreWidget` in `VoiceCoreLayer`.
3. Drive UI using `VoiceCoreController` and call:
   - `enterCouncilActive()`
   - `setCouncilSpeaker(...)`
   - `setCouncilPause()`
   - `completeCouncil()`
4. Emit bridge events with `UnityBridgeEmitter.emitCouncilPhaseChanged(...)`.
5. Apply inbound Unity updates with `UnityBridgeInboundHandler.handleEvent(...)`.
6. Reuse one `VoiceCoreTiming` config instance across controller and `VoiceCoreLayer`.

## Notes

- Rings remain neutral by design in this scaffold.
- Council sigil is Ghost Purple, speaker-invariant, and low opacity (8-15%).
- Optional ultra-slow sigil rotation is available; static is the default.

## TODO integration points

- TODO: Wire voice parser and wake-word engine to call controller transitions.
- TODO: Bind haptic and audio cue services at accent activation sync points.
- TODO: Replace placeholder ring shell with your production HUD implementation.
