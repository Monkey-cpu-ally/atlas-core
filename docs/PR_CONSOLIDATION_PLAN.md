# ATLAS Open-PR Consolidation Plan

Purpose: prevent multiple architecture-changing branches from being merged out of order or from silently overwriting one another.

## Merge gate

No architecture/HUD PR should be marked ready until:

1. It is rebased or refreshed against current `main`.
2. Backend startup succeeds in CI.
3. Relevant tests pass.
4. Persona contracts remain aligned with `docs/PERSONA_CONTRACTS.md`.
5. It does not duplicate changes already landed through another consolidation PR.

## Current sequence

### 1. Foundation / CI stabilization

Consolidation branch: `atlas/fix-red-foundation`

Contains:
- permission-safe upload storage initialization
- regression tests for CI/container filesystem permissions
- persona-role documentation aligned to the executable runtime
- verification that first-class persona chat and persistent persona memory already exist on `main`

This branch should land before the larger visual/integration branches are refreshed.

### 2. Engineering integration stack — PR #96

Keep draft until refreshed against the stabilized `main`. Validate Docker/Compose, Qdrant, OpenCV, CadQuery, KiCad and observability dependencies independently. Do not merge placeholder/external runtime assumptions without CI or explicit optional-dependency behavior.

### 3. Tool Bus persistent event work — PR #105

Keep draft until refreshed. Its in-memory event log is useful but not yet restart-persistent. Merge only after its event contract is reconciled with any newer visual/event infrastructure.

### 4. Visual ecosystem — PR #106

Keep draft. Refresh after Tool Bus/event contracts are stable. Connect backend services to publish visual events automatically before treating the WebSocket layer as production integration.

### 5. HUD redesign — PR #144

Keep draft and merge last. The HUD must consume stable backend contracts; it must not define competing business logic or duplicate service state.

### 6. CI upload fix — PR #150

The functional changes from this PR are being incorporated into `atlas/fix-red-foundation`. Once that consolidation PR is merged, #150 should be closed as superseded rather than merged separately.

## Rule

Backend truth first, integration contracts second, event transport third, HUD presentation last.
