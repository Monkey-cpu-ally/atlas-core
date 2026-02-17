# Backend

FastAPI backend entrypoint is `backend/main.py`.

## Atlas Orchestrator endpoints

- `POST /route` (primary MVP route endpoint)
- `POST /atlas/orchestrate`
- `POST /atlas/route`
- `GET /atlas/projects`
- `GET /atlas/projects/{project}/memory`
- `POST /atlas/projects/{project}/reset`
- `GET /atlas/vision`
- `GET /atlas/domains`
- `GET /atlas/prototypes/active`
- `GET /atlas/project-registry`
- `GET /atlas/project-registry/search?q=...`
- `GET /atlas/project-registry/{project_id}`
- `GET /atlas/capability-matrix`
- `GET /atlas/teaching-framework`
- `GET /atlas/academic-integration-plan`
- `GET /atlas/operational-rules`
- `GET /atlas/doctrine`

These routes implement the command-center flow:
1. Intake
2. Intent classification
3. Ordered routing (Ajani -> Minerva -> Hermes)
4. Combined output with validation status and project-scoped memory

Blueprint/Build/Modify stage outputs are structured and include:
- measurable objectives and constraints
- risk and test protocol
- version tag discipline
- teaching-oriented Minerva breakdowns
- Hermes approval status and safety enforcement
