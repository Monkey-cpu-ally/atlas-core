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
