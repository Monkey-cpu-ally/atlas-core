# Backend

FastAPI backend entrypoint is `backend/main.py`.

## Atlas Orchestrator endpoints

- `POST /route` (primary MVP route endpoint)
- `POST /atlas/orchestrate`
- `POST /atlas/route`
- `GET /atlas/projects`
- `GET /atlas/projects/{project}/memory`
- `POST /atlas/projects/{project}/reset`

These routes implement the command-center flow:
1. Intake
2. Intent classification
3. Ordered routing (Ajani -> Minerva -> Hermes)
4. Combined output with validation status and project-scoped memory
