# ATLAS Core

ATLAS Core is the main repository for the ATLAS engineering operating system. It is the long-term home for the core AI architecture, memory foundations, agent runtime, research systems, HUD assets, blueprint engines, digital twin planning, and future tool integrations.

## Primary ATLAS Roles

- **Ajani** — strategy, execution, risk, business planning, operations, and practical decision-making.
- **Hermes** — engineering, software, robotics, manufacturing, architecture, materials, validation, and tool use.
- **Minerva** — research, science, education, culture, botany, environment, storytelling, and knowledge organization.
- **Council** — combined review and synthesis when important decisions need more than one viewpoint.

## Repository Map

| Path | Purpose |
| --- | --- |
| `memory/` | Permanent ATLAS foundation documents, protocols, reports, design language, and long-term memory rules. |
| `atlas_core/` | Python ATLAS Core v1 service, engines, cores, council router, shield, memory interface, and API entry points. |
| `atlas-agent-runtime/` | Agent runtime scaffold for Hermes, Minerva, Ajani, Council, and future coordinated agents. |
| `backend/` | Existing backend services and integrations used by the broader ATLAS application. |
| `frontend/` | HUD and user interface components. |
| `design_bank/` | Visual design references, HUD contracts, Frazier design language assets, and UI design memory. |
| `graph-memory/` | Early graph memory definitions and connected-knowledge structure. |
| `knowledge-division/` | Research sources, catalogs, operating prompts, and knowledge-bank scaffolding. |
| `innovation-lab/` | Invention concepts, project intake files, digital twin planning, and future R&D workflows. |
| `themes/` | HUD color, motion, and style tokens. |
| `docs/` | Repository-level architecture, structure, naming, and governance documentation. |

See `docs/REPO_STRUCTURE.md` for a fuller map.

## Current Status

ATLAS already contains foundation memory, agent definitions, integration planning, HUD design assets, graph-memory notes, and early Python core systems. Some areas are production code, some are scaffolds, and some are design documentation. The next major cleanup goal is to align naming, document folder ownership, and make the root repository easier to navigate.

## Naming Alignment

Some older files use legacy internal names such as Titan, Gaia, and Mercury. These should be treated as early aliases or implementation names, not the final user-facing identities.

Preferred user-facing names:

- Titan → Ajani
- Gaia → Minerva
- Mercury → Hermes

See `docs/ATLAS_NAMING_ALIGNMENT.md`.

## Build Principle

ATLAS should stay modular, layered, and persistent. New systems should plug into ATLAS without breaking existing memory, agent roles, or future tool integrations.
