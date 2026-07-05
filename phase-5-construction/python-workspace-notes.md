# Python Workspace Notes

The first Phase 5 implementation uses separate service folders with `src/` layouts.

## Current Packages

```text
atlas-core-runtime/src/atlas_core_runtime
atlas-events/src/atlas_events
atlas-tasks/src/atlas_tasks
atlas-memory-engine/src/atlas_memory_engine
atlas-knowledge-engine/src/atlas_knowledge_engine
atlas-agent-runtime/src/atlas_agent_runtime
atlas-diagnostics/src/atlas_diagnostics
```

## Temporary Local Run Idea

Until packaging is finalized, set `PYTHONPATH` to include each `src` folder.

Example concept:

```bash
export PYTHONPATH="atlas-core-runtime/src:atlas-events/src:atlas-tasks/src:atlas-memory-engine/src:atlas-knowledge-engine/src:atlas-agent-runtime/src:atlas-diagnostics/src"
python phase-5-construction/bootstrap_demo.py
```

## Test Concept

```bash
export PYTHONPATH="atlas-core-runtime/src:atlas-events/src:atlas-tasks/src:atlas-memory-engine/src:atlas-knowledge-engine/src:atlas-agent-runtime/src:atlas-diagnostics/src"
pytest atlas-tests/tests
```

## Next Packaging Step

Create a root workspace strategy:

```text
Option A: Python monorepo with pyproject workspaces
Option B: One installable atlas-core package with internal modules
Option C: Multiple installable packages
```

Recommended next step: start simple with one root `pyproject.toml` and keep packages importable for tests.
