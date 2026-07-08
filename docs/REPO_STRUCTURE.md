# ATLAS Repository Structure

This document explains where ATLAS systems should live so the repository stays organized as it grows.

## Source of Truth

`Monkey-cpu-ally/atlas-core` is the main ATLAS repository.

This repository should hold the ATLAS operating system foundation:

- AI role architecture
- Memory and knowledge foundations
- Agent runtime
- Core backend services
- HUD and interface systems
- Research systems
- Blueprint and digital twin workflows
- Tool integration scaffolding
- Long-term engineering documentation

Other repositories should stay separate unless intentionally connected later through documented interfaces.

## Main Folders

### `memory/`

Permanent ATLAS memory and governing documents.

Use this folder for:

- Constitution files
- Council protocols
- research rules
- design language memory
- capability reports
- verification reports
- truth/risk/architecture audits
- long-term ATLAS principles

These files are not random notes. They are governing memory documents.

### `atlas_core/`

Python ATLAS Core v1.

Use this folder for:

- core Python services
- engines
- council routing
- shield/security logic
- memory interfaces
- teaching engines
- blueprint engines
- API entry points

This should remain focused on executable ATLAS core logic.

### `atlas-agent-runtime/`

Agent runtime scaffold.

Use this folder for:

- Hermes, Minerva, Ajani, and Council runtime definitions
- agent contracts
- agent orchestration
- task queues
- available tool definitions
- future agent execution services

### `backend/`

Existing backend application services.

Use this folder for broader backend services that support the application but are not part of the clean standalone `atlas_core/` package yet.

Over time, stable backend logic can be migrated into clearer ATLAS modules.

### `frontend/`

User-facing interface and HUD code.

Use this folder for:

- ATLAS HUD
- face panels
- dashboard components
- frontend API calls
- visual controls
- user interaction flows

### `design_bank/`

Design memory and visual system references.

Use this folder for:

- HUD design contracts
- Figma component notes
- visual style references
- design rules
- Frazier Design Language assets

### `graph-memory/`

Graph memory structure.

Use this folder for:

- initial graph schemas
- relationship maps
- concept-linking documents
- Neo4j-ready planning
- connected knowledge models

### `knowledge-division/`

Research and knowledge systems.

Use this folder for:

- source catalogs
- research operating prompts
- knowledge-bank scaffolding
- ingestion rules
- learning division documentation

### `innovation-lab/`

Invention and R&D project space.

Use this folder for:

- invention intake files
- digital twin plans
- project concepts
- prototype planning
- Weaver/robotics/manufacturing ideas
- future engineering experiments

### `themes/`

Shared design tokens.

Use this folder for:

- color tokens
- motion tokens
- HUD theme definitions
- style constants used by the interface

### `docs/`

Repository-level documentation.

Use this folder for:

- repo structure
- architecture summaries
- naming alignment
- integration strategy
- setup notes
- governance and cleanup plans

## Recommended Future Folders

These folders should be added only when real implementation begins:

```text
src/atlas/tool_bus/
src/atlas/integrations/
src/atlas/integrations/hermes/
src/atlas/integrations/minerva/
src/atlas/integrations/ajani/
docs/integrations/
docs/architecture/
```

## Rule Going Forward

Do not dump new ATLAS work randomly into the repository root.

Every new file should answer one question:

> Which ATLAS system owns this?

If the answer is unclear, place it in `docs/` first as a planning file, then move it into the correct system folder when implementation begins.
