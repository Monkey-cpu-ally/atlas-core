# ATLAS Data Folder

This folder defines the local development data convention for ATLAS.

## Mission

Give ATLAS a clean local home for persisted records during Phase 5 development.

## Important Rule

Runtime data files should generally not be committed unless they are safe examples or fixtures.

## Folder Convention

```text
atlas-data/
├── README.md
├── examples/
├── memory/
├── knowledge/
├── sources/
├── tasks/
├── events/
├── diagnostics/
├── projects/
└── backups/
```

## Current Persistence Mode

ATLAS currently supports JSON-backed persistence for:

```text
Memory records
Source passports
Knowledge entries
Tasks
Events
```

## Future Storage Modes

```text
SQLite for structured local data
Graph database for relationships
Vector database for semantic search
Object storage for files, images, CAD, audio, and documents
```

## Developer Note

For local testing, prefer using temporary folders or `atlas-data/local/`.

Do not commit private user data, secrets, raw conversation logs, or sensitive project files.
