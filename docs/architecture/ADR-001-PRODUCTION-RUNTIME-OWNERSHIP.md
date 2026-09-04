# ADR-001: Production Runtime Ownership

**Status:** Accepted for the production-hardening stream
**Date:** 2026-09-04

## Context

ATLAS contains a broad application backend, a standalone `atlas_core` package, several `atlas-*-runtime` packages, a React HUD, and a Unity HUD project. These layers preserve valuable work, but their overlapping names and responsibilities make it unsafe to infer which implementation owns production behavior.

## Decision

For HUD Intelligence Loop V1:

- `backend/server.py` is the current production composition root.
- `backend/services/persona_chat.py` owns persona orchestration until the versioned Intelligence API replaces its public role.
- `backend/services/llm_provider.py`, `memory_bank.py`, and `knowledge_ingestion.py` remain the current model, memory, and knowledge adapters.
- `contracts/personas.v1.json` is the only authoritative persona identity contract.
- `frontend/src/components/HUDInterface.js` is the first production HUD consumer.
- The Unity HUD is an adapter target and must adopt the same versioned contracts; it does not define a second intelligence runtime.
- `atlas_core/` and the standalone runtime packages remain supported modules/scaffolds until a separate migration ADR moves a responsibility into them.

## Consequences

- New V1 behavior enters through `/api/v1/intelligence`, not another parallel chat route.
- Existing routes remain behind compatibility adapters during migration.
- Code movement is incremental and test-gated.
- A module is not deleted merely because it is not authoritative for V1.
- Runtime ownership changes require a new ADR and release-manifest update.
