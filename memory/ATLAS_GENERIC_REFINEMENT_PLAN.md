# ATLAS Generic Refinement Plan

Purpose: remove generic product feel from ATLAS without breaking working systems.

## Rule

Do not rename or delete stable APIs blindly. Add polished ATLAS-facing command surfaces first, then migrate HUD and user-facing workflows to those surfaces.

## Generic Areas Identified

### 1. API naming

Current backend routes such as `/api/discovery-approval`, `/api/external-access`, and `/api/project-intelligence` are functional but generic.

Refinement path:

- Keep them for developer compatibility.
- Add ATLAS Headquarters routes for product-facing surfaces.
- Make the luxury HUD use Headquarters routes first.

New Headquarters routes:

- `/api/headquarters/status`
- `/api/headquarters/quality-gates`
- `/api/headquarters/atlas-standard`
- `/api/headquarters/mission-control`

### 2. Backend presentation

The backend has real systems, but the presentation layer should feel like an engineering command center rather than a collection of APIs.

Refinement path:

- Use Headquarters language for top-level reports.
- Keep developer APIs beneath the surface.
- Add product-grade status, quality, mission, and approval reports.

### 3. HUD identity

The HUD must not look like a generic AI dashboard.

Refinement path:

- Build around Headquarters, Council Chamber, Mission Control, Knowledge Gate, Project Briefing, and Source Clearance.
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

## Next Work

1. Add route tests for Headquarters.
2. Add route tests for Discovery Approval.
3. Add route tests for External Access.
4. Update HUD planning docs to use Headquarters language.
5. Add ATLAS Technical Debt Register.

## Standard

The goal is not to make ATLAS decorative. The goal is to make every surface feel intentional, precise, and unmistakably ATLAS.
