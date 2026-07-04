# ATLAS Development Pipeline

## Pipeline

Founder → ChatGPT → Emergent/Cursor → GitHub → Tests → ATLAS OS

## Roles

### Founder
Approves direction, releases, branch saves, and merges.

### ChatGPT
Architecture, release planning, code review, debugging plans, documentation, and next-layer design.

### Emergent/Cursor
Implementation, code editing, test execution, runtime debugging, branch creation, GitHub save.

### GitHub
Source of truth, commit history, branches, CI/CD.

### ATLAS OS
Internal engineering console that tracks system health and release progress.

## Core Principle
ATLAS should never hide its engineering state. Every major subsystem should report whether it is healthy, degraded, missing, or under construction.

## Status Types
- healthy
- degraded
- missing
- under_construction
- unknown

## Required Panels
- GitHub Status
- Current Release
- Test Status
- Memory Bank
- Knowledge Bank
- Source Registry
- AI Routing
- Teaching Engine
- Research Engine
- Domain Status
- Next Task

## Release Flow
1. Select release goal.
2. Create branch.
3. Implement changes.
4. Run tests.
5. Review issues.
6. Save to GitHub.
7. Update engineering journal.
8. Plan next release.
