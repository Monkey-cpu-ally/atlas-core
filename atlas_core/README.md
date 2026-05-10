# ATLAS Core v1

A modular cognitive backend, completely separate from the HUD frontend in
`/app/frontend` and from the legacy `/app/backend`. Only Python is shipped
here.

## Folder structure

```
atlas-core/
├── app/
│   └── main.py           # FastAPI entry — wires every engine under /atlas/*
├── cores/
│   ├── base_core.py      # AICore base class (think + mental_simulate)
│   ├── titan_core.py     # Ajani — strategy / engineering / kinetics
│   ├── gaia_core.py      # Minerva — culture / ethics / life sciences
│   └── mercury_core.py   # Hermes — math / patterns / validation
├── council/
│   └── router.py         # routes lead/support/critic; assembles council answer
├── teaching_engine/
│   └── teaching.py       # 4-band depth (seed → shape → substance → shadows)
├── blueprint_engine/
│   └── blueprint.py      # parallel mental simulation + 5-phase plan
├── archive_engine/
│   └── parser.py         # PDF/ZIP scan + classify + summarize + route
├── shield_core/
│   └── shield.py         # injection defense, quarantine, gates, identity
├── memory/
│   └── memory.py         # in-memory store w/ DB-shaped interface
├── requirements.txt
├── .env                  # EMERGENT_LLM_KEY, CORS_ORIGINS
└── README.md
```

## Running it

```bash
cd /app/atlas-core
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload
```

Browse `http://localhost:8002/docs` for the interactive OpenAPI UI.

## Endpoints

All endpoints are under `/atlas/...`.

| Method | Path                              | Purpose                                       |
| -----: | --------------------------------- | --------------------------------------------- |
| GET    | `/atlas/status`                   | Full subsystem health snapshot                |
| POST   | `/atlas/cores/{core_key}/think`   | Talk to one core directly                     |
| GET    | `/atlas/cores/{core_key}/history` | Retrieve conversation log for a session       |
| POST   | `/atlas/council/preview`          | Fast routing decision only (no LLM)           |
| POST   | `/atlas/council/route`            | Full council assembly (3 LLM calls)           |
| POST   | `/atlas/teach`                    | 4-band lesson at PhD depth / 6th-grade clarity|
| POST   | `/atlas/blueprint`                | Parallel mental sim + 5-phase plan            |
| POST   | `/atlas/archive/upload`           | Upload PDF / ZIP / TXT; auto-classify & route |
| GET    | `/atlas/archive/list`             | List archived entries (optional core filter)  |
| GET    | `/atlas/shield/status`            | Shield config + permissions                   |
| POST   | `/atlas/shield/permission`        | Flip a capability gate                        |
| GET    | `/atlas/events`                   | Recent audit log                              |

## Design notes

- **No persistence yet.** `memory/memory.py` is in-memory but exposes a
  clean interface ready for a DB-backed swap (MongoDB / Postgres) without
  changing any caller.
- **Identity hard rules live with the core**, not with the router. Each
  core's `system_prompt()` composes its identity + its own rules + a
  shared `BASE_RULES` block.
- **Shield runs at every trust boundary.** `sanitize_text()` is called
  before storage, before LLM calls, and on archive extraction.
- **Council is heuristic.** `route()` is keyword-based and instant; the
  full `assemble()` flow does 3 LLM calls (lead answer, critique, next
  step). The heuristic can be swapped for a learned classifier without
  changing callers.

## Integration with the HUD

The HUD frontend in `/app/frontend` and the legacy `/app/backend` API are
**not touched** by this build. ATLAS Core runs on its own port (`8002`).
When you are ready to surface it in the HUD, mount `atlas_router` onto the
existing FastAPI app:

```python
from atlas_core.app.main import atlas_router  # noqa
app.include_router(atlas_router)
```

…or keep the two stacks separate and have the frontend call the new
service directly with its own base URL.
