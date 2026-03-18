# AGENTS.md

## Cursor Cloud specific instructions

### Overview

Atlas Core is a FastAPI-based AI persona educational assistant (codename ATLAS-PRIME). It has a Python backend, a PWA frontend served as static files, and a Three.js 3D Blueprint Viewer.

### Running the dev server

```bash
export PATH="$HOME/.local/bin:$PATH"
export DATABASE_URL="postgresql://atlas:atlas@localhost:5432/atlas_core"
export OPENAI_API_KEY="sk-placeholder-for-dev"
export OPENAI_BASE_URL="https://api.openai.com/v1"
uvicorn atlas_core_new.main:app --host 0.0.0.0 --port 8000 --reload
```

### Key gotchas

- **Missing external packages**: The app imports `umojaforge`, `doctrine`, `uws_workshop`, and `pre_reality_engine` at the top level in `main.py`. These packages do not exist on PyPI and must be present as stub directories at the workspace root with FastAPI `APIRouter` exports. The stub packages are created during setup and committed to the repo.
- **OpenAI API key required at import time**: The `ResponsePipeline` class instantiates an `OpenAI` client during module initialization. The app will crash on startup if `OPENAI_API_KEY` is not set. Use `sk-placeholder-for-dev` for local dev when you don't need actual AI responses.
- **Undeclared pip dependencies**: `trafilatura`, `reportlab`, `itsdangerous`, and `requests` are used in code but not listed in `pyproject.toml`. They must be installed separately.
- **PostgreSQL required**: The app needs a running PostgreSQL instance. The `DATABASE_URL` env var must be set. Without it, `SessionLocal` is `None` and DB-backed endpoints return fallback responses, but the app still starts.
- **No test suite**: There are no automated tests in the repository.
- **Lint**: No lint config is bundled. Use `ruff check atlas_core_new/` for quick linting. Critical-only: `ruff check atlas_core_new/ --select E9,F63,F7,F82`.
- **PostgreSQL startup**: Run `sudo pg_ctlcluster 16 main start` before starting the app.
- **PATH**: `pip install --user` puts binaries in `~/.local/bin`, which may not be on PATH. Export it: `export PATH="$HOME/.local/bin:$PATH"`.

### Endpoints for quick verification

- `GET /health` — health check
- `GET /api` — system info
- `GET /identity` — system identity and principles
- `GET /forge/templates` — list robot templates
- `POST /forge/build/ant` — build an ant robot (no AI key needed)
- `GET /lessons/{persona}/fields` — list lesson fields
- `GET /lego-lessons` — list LEGO-style lessons
- `GET /viewer/index` — 3D Blueprint Viewer (browser)
