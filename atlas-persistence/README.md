# ATLAS Persistence

## Mission

Persist ATLAS records so events, tasks, memory, knowledge, and agent state can survive beyond one runtime session.

## Phase 5 Persistence Strategy

Start simple, then grow.

```text
Step 1: Repository interfaces
Step 2: JSON file persistence for local development
Step 3: SQLite persistence for structured records
Step 4: Graph database adapter interface
Step 5: Vector database adapter interface
```

## Why Start With JSON?

JSON persistence is not the final storage layer. It is a simple local development foundation that makes the first ATLAS services easier to test, inspect, and debug.

## Future Storage Layers

```text
JSON files: local development
SQLite: local structured records
Graph database: relationships and knowledge graph
Vector database: semantic search
Object storage: files, images, documents, CAD, audio
```

## Status

Scaffold created. Interfaces and JSON store pending.
