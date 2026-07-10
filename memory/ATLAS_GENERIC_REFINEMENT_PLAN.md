# ATLAS Generic Refinement Plan

Purpose: remove generic product feel from ATLAS without breaking working systems.

## Rule

Do not rename or delete stable APIs blindly. Add polished ATLAS-facing command surfaces first, then migrate HUD and user-facing workflows to those surfaces.

## Generic Areas Identified

### 1. API naming

Current backend routes such as `/api/discovery-approval`, `/api/external-access`, `/api/project-intelligence`, and `/api/self-improve` are functional but generic.

Refinement path:

- Keep them for developer compatibility.
- Add ATLAS Headquarters routes for product-facing surfaces.
- Make the luxury HUD use Headquarters routes first.

New Headquarters routes:

- `/api/headquarters/status`
- `/api/headquarters/quality-gates`
- `/api/headquarters/atlas-standard`
- `/api/headquarters/mission-control`
- `/api/headquarters/knowledge-gate`
- `/api/headquarters/source-clearance`
- `/api/headquarters/project-briefing`
- `/api/headquarters/refinement`
- `/api/headquarters/technical-debt`

### 2. Backend presentation

The backend has real systems, but the presentation layer should feel like an engineering command center rather than a collection of APIs.

Refinement path:

- Use Headquarters language for top-level reports.
- Keep developer APIs beneath the surface.
- Add product-grade status, quality, mission, approval, source, project, refinement, and technical-debt reports.

### 3. HUD identity

The HUD must not look like a generic AI dashboard.

Refinement path:

- Build around Headquarters, Council Chamber, Mission Control, Knowledge Gate, Project Briefing, Source Clearance, and Refinement Office.
- Avoid generic cards and random neon UI.
- Use calm motion, premium spacing, and purposeful animation.

### 4. AI interaction

The AIs should not behave like renamed versions of the same assistant.

Refinement path:

- Ajani challenges engineering assumptions.
- Hermes challenges design, robotics, and serviceability.
- Minerva challenges evidence and scientific confidence.
- Council summarizes trade-offs and final decision logic.

### 5. Testing and reporting

Generic pass/fail output should become ATLAS Headquarters review output.

Refinement path:

- Keep normal CI for developers.
- Add ATLAS quality-gate reports for the HUD.
- Use seven seals: Architecture, Engineering, Testing, Documentation, Security, Performance, Luxury Review.

## Current Work Completed

- Added `backend/services/headquarters_engine.py`.
- Added `backend/routes/headquarters.py`.
- Mounted Headquarters routes in `backend/server.py`.
- Added `backend/tests/test_headquarters_engine.py`.
- Added `backend/tests/test_headquarters_routes.py`.
- Added command surfaces for Knowledge Gate, Source Clearance, Project Briefing, and Refinement Office.
- Added `backend/tests/test_command_surface_routes.py`.
- Added route coverage for Discovery Approval draft-review-Council approval flow.
- Added route coverage for External Access default seeding and permission-first import plans.
- Added route coverage for Project Intelligence briefs, risks, recommendations, and cross-project reuse signals.
- Updated `memory/HUD_AUDIT.md` to use Headquarters, Council Chamber, Headquarters Systems, and Mission Departments language.
- Updated `exports/README-HUD.md` to describe the HUD as the ATLAS Headquarters command layer.
- Updated `design_bank/atlas_hud/README.md` with Headquarters zones and Figma page recommendations.
- Added `memory/ATLAS_TECHNICAL_DEBT_REGISTER.md`.
- Added `TECHNICAL_DEBT_ITEMS` and `technical_debt_register()` to `backend/services/headquarters_engine.py`.
- Added `/api/headquarters/technical-debt`.
- Added engine and route tests for technical debt reporting and filtering.
- Connected technical debt summary into `/api/headquarters/status` and `/api/headquarters/refinement`.
- Added integration coverage proving Headquarters command surfaces remain mapped to their developer APIs.
- Closed `DEBT-HQ-001` after adding the Headquarters mapping test.
- Added `backend/tests/test_startup_persistence_wiring.py`.
- Added startup persistence coverage for Discovery Approval drafts/reviews/decisions, Knowledge Records, Chronicle entries, External Access connections/import plans, and Project Intelligence briefs.
- Closed `DEBT-PERSIST-001` after adding persistence hydration coverage.
- Verified the World Knowledge Graph router import and `app.include_router(...)` mounting in `backend/server.py`.
- Added `backend/tests/test_world_knowledge_graph_routes.py`.
- Added route coverage for World Knowledge Graph health, foundation seeding, summaries, node creation/filtering/fetching, edge creation/filtering, neighborhood traversal, and HTTP error translation.

## Next Work

1. Run CI confirmation for World Knowledge Graph route coverage and close `DEBT-KNOW-001` after a passing result.
2. Continue the Knowledge Division roadmap with Source Reliability Ranking.
3. Begin the Digital Twin engineering stack after Headquarters and Knowledge Division hardening.
4. Keep persistence and route-mounting tests updated when adding new command surfaces.

## Standard

The goal is not to make ATLAS decorative. The goal is to make every surface feel intentional, precise, and unmistakably ATLAS.