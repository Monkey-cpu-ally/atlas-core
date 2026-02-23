# HUD Freeze (Design Lock)

This repo contains a **design-frozen HUD** (dial + rings + voice/council visuals + Appearance Lab).

## What is locked

These paths are treated as **HUD-frozen**:
- `docs/architecture/**`
- `frontend/flutter_atlas_scaffold/**`
- `frontend/flutterflow_app/lib/custom_code/atlas_console/atlas_console_widget.dart`

## Why

To prevent accidental “helpful” redesigns (by AI tools or refactors) that change the look/feel or interaction contracts.

## How to intentionally change the HUD

Any change that touches the locked paths must include an explicit approval marker:
- Add **`[HUD-CHANGE]`** to the PR title, or
- Add **`[HUD-CHANGE]`** to a commit message in the change range.

The CI job **HUD Freeze** will block the change otherwise.

