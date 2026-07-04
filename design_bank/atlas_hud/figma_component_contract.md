# Figma Component Contract for ATLAS HUD

## Purpose
This file defines how the Figma HUD design should map into frontend code.

## Naming Rule
Figma components should use predictable names so developers and automation can map them to code.

Recommended format:

```text
ATLAS/HUD/Core/Idle
ATLAS/HUD/Core/Active
ATLAS/HUD/Ring/Primary
ATLAS/HUD/Ring/Secondary
ATLAS/HUD/AI/AjaniPortrait
ATLAS/HUD/AI/HermesPortrait
ATLAS/HUD/AI/MinervaPortrait
ATLAS/HUD/AI/CouncilPortrait
ATLAS/HUD/Graph/Node
ATLAS/HUD/Graph/Edge
ATLAS/HUD/Panel/Glass
ATLAS/HUD/Panel/ResearchQueue
ATLAS/HUD/Panel/KnowledgeGraph
ATLAS/HUD/Panel/EngineeringConsole
ATLAS/HUD/State/Idle
ATLAS/HUD/State/Ajani
ATLAS/HUD/State/Hermes
ATLAS/HUD/State/Minerva
ATLAS/HUD/State/Council
```

## Component Mapping

| Figma Component | Frontend Component Target | Notes |
|---|---|---|
| ATLAS/HUD/Core/Idle | AtlasCoreOrb | Amber default core |
| ATLAS/HUD/Core/Active | AtlasCoreOrb | Uses AI color token |
| ATLAS/HUD/Ring/Primary | OrbitalRing | Slow transparent rotation |
| ATLAS/HUD/Graph/Node | KnowledgeNode | Used for AI knowledge graph |
| ATLAS/HUD/Graph/Edge | KnowledgeEdge | Animated energy link |
| ATLAS/HUD/Panel/Glass | GlassPanel | Reusable HUD panel |
| ATLAS/HUD/Panel/ResearchQueue | ResearchQueuePanel | Connects to /api/research-labs |
| ATLAS/HUD/Panel/KnowledgeGraph | KnowledgeGraphPanel | Connects to future graph API |

## Motion Rule
Figma variants should include:
- idle
- hover
- active
- speaking
- researching
- council_review
- alert

## Developer Rule
Frontend should not hardcode colors. Use `design_bank/atlas_hud/design_tokens.json` as the source for ATLAS HUD colors and motion timing.
