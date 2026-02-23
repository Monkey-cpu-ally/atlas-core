# FlutterFlow App (Monorepo Mirror)

This folder (`frontend/flutterflow_app/`) is a **mirror import** of the FlutterFlow export
that lives on the GitHub branch:

- `flutterflow`

We keep it here so the monorepo branch (`cursor/three-js-library-import-ed42`) can include:
- the FastAPI backend (`atlas_core_new/`, `backend/`)
- docs/specs (`docs/`)
- shared contracts
**and** the Flutter UI code in one place.

## How this folder is updated

We re-import from the `flutterflow` branch using:

```bash
git fetch origin flutterflow
rm -rf frontend/flutterflow_app
mkdir -p frontend/flutterflow_app
git archive origin/flutterflow | tar -x -C frontend/flutterflow_app
```

## Why this exists (FlutterFlow limitation)

FlutterFlow expects a Flutter project at the **repo root**.
This repo is a monorepo, so the `flutterflow` branch stays Flutter-rooted, while the
working branch stays monorepo-rooted.

## Local .gitignore

The `.gitignore` inside this folder is Flutter/Dart-focused so we do not accidentally commit:
- `.dart_tool/`
- plugin registrants
- build outputs

## Next integration steps

- Add a path dependency on `../flutter_atlas_scaffold`
- Wire backend calls (`/suggest`, `/validate`, `/chat`) to the FastAPI service
- Connect council state machine + Unity bridge events
