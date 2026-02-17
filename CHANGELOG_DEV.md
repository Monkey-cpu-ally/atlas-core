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
- TODO: If you want a dedicated `cleanup-perf-ui` branch in this environment, confirm branch-policy override so commits can be moved safely.

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

### Area: Specification Authoring
- Summary: Added 10 structured markdown specifications for Polymath Forge and Atlas hybrid system:
  - `docs/00_MASTER_DOCTRINE.md`
  - `docs/01_ACADEMY_STRUCTURE_22_SUBJECTS.md`
  - `docs/02_TEACHING_STANDARD_IVY_SIMPLE.md`
  - `docs/03_TOME_UI_BOOK_LAYOUT_SPEC.md`
  - `docs/04_TOOL_SYSTEM_SPEC.md`
  - `docs/05_MATERIAL_VAULT_SPEC.md`
  - `docs/06_BIO_STUDY_MODELS_SPEC.md`
  - `docs/07_PROJECT_ARTIFACT_VAULT_SPEC.md`
  - `docs/08_UNLOCKS_TESTS_RETEST_ENGINE_SPEC.md`
  - `docs/09_BUILDER_ROADMAP.md`
- Risk: Low (documentation-only; no application code changes).
- Rollback: Revert the documentation commit for these files.

### Area: Specification Gap Closure
- Summary: Updated spec set to explicitly include:
  - minimum 2+ anchor projects for each of 22 subjects (`docs/01_ACADEMY_STRUCTURE_22_SUBJECTS.md`)
  - the exact rule "PhD backbone / 6th-grade clarity" (`docs/02_TEACHING_STANDARD_IVY_SIMPLE.md`)
  - explicit book/tome tab system with red bookmark behavior (`docs/03_TOME_UI_BOOK_LAYOUT_SPEC.md`)
- Risk: Low (documentation-only refinements).
- Rollback: Revert the documentation gap-closure commit.
