# ATLAS HUD Hidden Systems Policy

## Purpose

ATLAS must preserve the approved reference design and avoid feature creep. The HUD is the visible face of the system, not a dashboard for every internal service.

## Core Rule

> Evolve the brain. Preserve the face.

If a system does not require direct, repeated user interaction, it must remain behind the scenes.

## Hidden Backstage Systems

The following systems must not have permanent buttons, tabs, launchers, panels, rings, cards, meters, or decorative indicators on the main HUD:

- Knowledge Bank and subject knowledge banks
- Memory Bank and persona memory stores
- Research Bank
- Media Bank
- Source Registry
- Knowledge Graph / Graph Memory
- Vector search and indexes
- Caches
- Ingestion queues and processing pipelines
- Confidence-scoring machinery
- Internal routing, classification, and deduplication systems
- Background learning and synchronization services

These systems may still operate normally through backend services, AI conversations, voice commands, project workflows, or developer diagnostics.

## Visible HUD Boundary

The HUD should remain faithful to the approved reference design:

- Central ATLAS core
- Slow transparent rings
- Small AI face HUDs outside the rings
- Ajani, Minerva, Hermes, and Council interaction
- Existing approved project, assist, blueprint, lab, settings, and diagnostics interactions
- Temporary contextual results only when the user requests them

A hidden system may surface a short result, alert, citation, or status when relevant, but the storage system itself must not become a permanent visual destination.

## Examples

Correct:

- Hermes answers using the Knowledge Bank without opening a Knowledge Bank screen.
- Minerva cites trusted sources without displaying a Source Registry dashboard.
- ATLAS connects related ideas through Graph Memory without showing a graph launcher.
- A project result briefly reports that supporting knowledge was found.

Incorrect:

- A permanent `Knowledge Bank` button on the HUD.
- A `Memory Bank` ring segment.
- A `Graph Memory` launcher on the main screen.
- Separate visible panels for every database, cache, queue, or internal engine.

## Implementation Rule

Frontend code must not expose backstage systems as permanent HUD controls. New HUD work should be reviewed against this document before merging.

Legacy internal panels may remain in the codebase temporarily for developer diagnostics, but they must not be reachable from the normal user-facing HUD unless Frazier explicitly approves a design change.
