# Pass 1 Cleanup Audit (No Behavior Change)

Date: 2026-02-17

## Scope

- Unused imports / variables
- Dead code paths
- Unused files
- Unused exports
- Duplicate utilities
- Unreachable routes
- Unused dependencies

## Findings

1. **Unused imports/variables**
   - Status: clean for `atlas_core_new` (`ruff F401/F841` passes).
   - Action: no further removal needed in this pass.

2. **Unreachable routes**
   - Status: active app routers are registered in `atlas_core_new/main.py`.
   - Note: some routers are intentionally optional and included only when integration modules are installed.

3. **Unused files**
   - Status: no runtime source files removed in this pass.
   - Prior archived generated metadata remains under `/archive`.

4. **Duplicate utilities**
   - Status: obvious duplicate version bump helper already deduplicated.
   - Action: continue targeted dedupe only where behavior-preserving.

5. **Dependencies**
   - `deptry` reports contain:
     - optional imports not declared as hard deps (e.g., `reportlab`, `trafilatura`, `elevenlabs`, `cv2`, `PIL`, `itsdangerous`);
     - static-analysis false positives for runtime/test dependencies (`uvicorn`, `python-multipart`, `pytest`).
   - Action: no removal in this pass to avoid unintended runtime feature changes.

## Safety Constraints Applied

- No route/schema/env var rename.
- No request/response shape changes.
- No source file deletions in this pass.
- All changes are reversible by commit.
