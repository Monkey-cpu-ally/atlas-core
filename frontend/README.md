# Frontend

Frontend app lives here.

## Target layout (Atlas Command Center)

- Left panel: Projects list + project selector
- Center panel: Chat/command input
- Right panel: stacked agent panels
  - Ajani (Blueprint)
  - Minerva (Teach-back)
  - Hermes (Validation)
- Pipeline tracker: Blueprint -> Build -> Modify

## Backend integration

Use `src/client/atlasClient.ts` to call:

- `POST /atlas/orchestrate`
- `GET /atlas/projects`
- `GET /atlas/projects/{project}/memory`
- `POST /atlas/projects/{project}/reset`
