# ATLAS Foundation Cleanup Plan

This plan defines the next safe cleanup steps for `Monkey-cpu-ally/atlas-core`.

## Completed In This Cleanup Branch

- Updated the root `README.md` so the repository explains what ATLAS Core is.
- Added `docs/REPO_STRUCTURE.md` to define where systems belong.
- Added `docs/ATLAS_NAMING_ALIGNMENT.md` to map legacy names to official ATLAS names.

## Main Cleanup Goals

### 1. Protect the Right Repository

`Monkey-cpu-ally/atlas-core` is the main ATLAS repository.

Do not move ATLAS Core systems into unrelated repositories.

### 2. Improve Navigation

The repository already contains important ATLAS systems, but many are hard to discover from the root.

The root README should stay updated whenever major systems are added.

### 3. Align Names

Official names:

- Ajani
- Minerva
- Hermes
- Council

Legacy names:

- Titan → Ajani
- Gaia → Minerva
- Mercury → Hermes

Keep compatibility until tests confirm safe renames.

### 4. Build the Tool Bus Later

The Tool Bus should be added as implementation, not just scattered notes.

Recommended future paths:

```text
src/atlas/tool_bus/
src/atlas/integrations/
docs/integrations/
```

### 5. Keep Documentation and Code Connected

Every major document should point to the code or system it governs.

Every major code system should have a README or module docstring explaining how it fits ATLAS.

## Next Recommended Pull Requests

### PR 1 — Foundation Cleanup

Current branch:

```text
atlas/repo-cleanup-foundation
```

Purpose:

- root README cleanup
- repo map
- naming alignment

### PR 2 — Tool Bus Scaffold

Future branch:

```text
atlas/tool-bus-scaffold
```

Purpose:

- adapter interface
- no live integrations
- no secrets
- no destructive tool calls

### PR 3 — Agent Runtime Alignment

Future branch:

```text
atlas/agent-runtime-alignment
```

Purpose:

- align agent runtime docs with official names
- add wrappers if needed
- keep legacy imports stable

## Final Rule

Clean architecture beats fast chaos. ATLAS should grow like a system, not like a junk drawer.
