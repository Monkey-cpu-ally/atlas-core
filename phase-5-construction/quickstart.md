# Phase 5 Quickstart

This quickstart explains the current implementation scaffold.

## What Exists Now

```text
atlas-core-runtime/src/atlas_core_runtime/
atlas-events/src/atlas_events/
atlas-tasks/src/atlas_tasks/
atlas-memory-engine/src/atlas_memory_engine/
atlas-knowledge-engine/src/atlas_knowledge_engine/
atlas-agent-runtime/src/atlas_agent_runtime/
```

## First Python Contracts Added

```text
AtlasService
HealthReport
ServiceRegistry
AtlasEvent
AtlasTask
MemoryRecord
SourcePassport
KnowledgeEntry
AgentIdentity
```

## Current Status

These are not full services yet. They are the first code contracts for ATLAS Core.

## Next Build Step

Create actual service implementations:

```text
ConfigService
EventBusService
TaskService
MemoryService
KnowledgeService
AgentRuntimeService
DiagnosticsService
```

## Rule

Do not add advanced features until the service foundation can start, register, report health, and shut down cleanly.
