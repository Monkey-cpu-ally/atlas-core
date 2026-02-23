# Atlas Core
Safety-first environmental robotics framework with an AI persona-based assistant system.

## What’s in this repo

- **Backend (FastAPI)**: `atlas_core_new/`
- **PWA UI (served by backend)**: `atlas_core_new/static/`
- **Flutter app (FlutterFlow export)**: `frontend/flutterflow_app/`
- **HUD dial + rings + voice/council scaffold**: `frontend/flutter_atlas_scaffold/`
- **HUD specs (design-frozen)**: `docs/architecture/`

## Run the backend (local dev)

From repo root:

```bash
bash scripts/dev_backend.sh
```

Then open:
- `http://127.0.0.1:8000/` (PWA UI)
- `http://127.0.0.1:8000/health` (health check)

Optional config:
- Copy `.env.example` to `.env` and set `OPENAI_API_KEY` and/or `DATABASE_URL` as needed.

## Run the Flutter app

Prerequisite: install Flutter on your machine.

```bash
cd frontend/flutterflow_app
flutter pub get
flutter run
```

In the app console, set **Atlas Base URL**:
- **Android emulator**: `http://10.0.2.2:8000`
- **iOS simulator**: `http://127.0.0.1:8000`
- **Physical device**: `http://<your-lan-ip>:8000`

## HUD design lock

The HUD is protected from accidental redesigns.
See `docs/HUD_FREEZE.md` (and use `[HUD-CHANGE]` only when you intentionally want HUD edits).
