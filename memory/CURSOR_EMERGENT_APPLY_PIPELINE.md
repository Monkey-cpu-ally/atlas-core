# Cursor/Emergent Apply Instructions

Merge this packet into atlas-core.

## Tasks
1. Add a backend route for `/api/dev/pipeline/status` or adapt to existing route style.
2. Add a service that aggregates current system status.
3. Wire the route into the backend app/server.
4. Add the frontend Engineering Console component.
5. Add a basic HUD link/panel only if safe; do not clutter the main HUD.
6. Run tests.
7. Do not delete existing routes.
8. Commit to a feature branch after tests pass.

## Safety
- Non-destructive merge only.
- Preserve existing endpoint names.
- Add aliases only when needed.
- If a route already exists, extend it instead of duplicating logic.
