# CHANGELOG_DEV

Development change log for cleanup/performance/UI passes.

Format:
- Date
- Area
- Summary
- Risk
- Rollback

---

## 2026-02-17

### Area: Safety Net / Process
- Summary: Initialized `CHANGELOG_DEV.md` for reversible staged changes (cleanup, performance, UI polish) with risk and rollback notes per change.
- Risk: None (documentation only).
- Rollback: Revert commit that introduces this file.

### Area: Branching
- Summary: Repository is operating on managed branch `cursor/three-js-library-import-ed42`; staged pass commits are recorded on this branch.
- Risk: Low (process note only).
- Rollback: N/A.

### Area: Pass 1 Audit
- Summary: Added cleanup audit report at `docs/pass1_cleanup_audit.md` documenting dead-weight scan outcomes and no-behavior-change constraints.
- Risk: None (documentation only).
- Rollback: Revert commit that adds the pass-1 audit doc.

### Area: Pass 2 Performance (Backend)
- Summary: Optimized registry lookups in `atlas_orchestrator/knowledge.py` with precomputed normalized indexes and cached regex compilation for keyword matching.
- Risk: Low (lookup and matching internals refactor with same function signatures and outputs).
- Rollback: Revert the pass-2 backend optimization commit.

### Area: Pass 2 Performance (Frontend)
- Summary: Refactored `frontend/src/client/atlasClient.ts` to use shared JSON fetch helpers and in-flight GET request coalescing to reduce duplicate concurrent requests.
- Risk: Low (same endpoint URLs, methods, and error message patterns; no schema changes).
- Rollback: Revert the pass-2 frontend optimization commit.

### Area: Pass 3 Visual Polish
- Summary: Applied CSS-only visual consistency polish in `atlas_core_new/static/css/main.css` (spacing rhythm, hierarchy, card/button/input consistency, reduced glow/noise, maintained focus visibility and contrast).
- Risk: Low to medium (visual-only overrides may require tuning per theme).
- Rollback: Revert the pass-3 UI polish commit.
