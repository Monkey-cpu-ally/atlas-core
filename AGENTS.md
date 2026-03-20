# Atlas Core — Development Guide

## Cursor Cloud specific instructions

### Architecture

Atlas Core is a monolithic Python/FastAPI application (`atlas_core_new/main.py`) with a PostgreSQL database and a static PWA frontend. It uses three AI personas (Ajani, Minerva, Hermes) for an educational assistant system.

### Running the dev server

```bash
export PATH="$HOME/.local/bin:$PATH"
export DATABASE_URL="postgresql://ubuntu:atlas@localhost/atlas_core"
uvicorn atlas_core_new.main:app --host 0.0.0.0 --port 8000 --reload
```

PostgreSQL must be running first: `sudo pg_ctlcluster 16 main start`

### External stub packages

The app imports four external packages (`umojaforge`, `doctrine`, `uws_workshop`, `pre_reality_engine`) that are not published to PyPI. Stub packages providing empty FastAPI routers exist at the workspace root. These stubs allow the app to start; the corresponding features (simulator, doctrine system, UWS workshop, pre-reality engine) will return no routes until the real packages are provided.

### Key gotchas

- **`design_engine` uses raw psycopg2 connection pools** (not SQLAlchemy). It reads `DATABASE_URL` directly and requires a password in the connection string — peer auth without a password will fail.
- **Implicit dependencies** not listed in `pyproject.toml` but required at import time: `trafilatura`, `itsdangerous`, `requests`, `reportlab`.
- **Database is optional for many endpoints.** If `DATABASE_URL` is unset, `SessionLocal` is `None` and DB-backed endpoints return fallback responses. Non-DB endpoints (health, identity, forge, research, lessons, bots, pipeline) work without a database.
- **AI features (chat, generate) require `AI_INTEGRATIONS_OPENAI_API_KEY` and `AI_INTEGRATIONS_OPENAI_BASE_URL`** env vars. Without them, those endpoints will fail at runtime but the server still starts.
- **No existing linter configuration.** Use `ruff check atlas_core_new/` for linting; the codebase has many pre-existing lint warnings (line length, unused imports).
- **No automated test suite exists** in the repository.

### Useful test endpoints (no external API keys needed)

- `GET /health` — server health
- `GET /api` — API info
- `GET /identity` — system identity
- `GET /bots` — list robot profiles
- `POST /forge/build/{template}` — build a forge template (ant, crab, octopus, etc.)
- `GET /research` — list all persona research
- `GET /lessons/{persona}/fields` — list lesson fields
- `GET /lego-lessons` — list LEGO-style lessons
- `GET /progress?user_id=default_user` — DB-backed user progress
