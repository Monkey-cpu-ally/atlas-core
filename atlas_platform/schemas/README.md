# ATLAS Shared Schemas

This folder will contain Python data models shared across ATLAS.

Schemas are the backbone of the system. They keep every division speaking the same language.

---

# Planned Schema Groups

- Project schemas
- AI role schemas
- Evidence schemas
- Risk schemas
- Council decision schemas
- Digital Twin schemas
- Graph Memory schemas
- Prototype schemas
- Research source schemas

---

# Design Rules

1. Use clear names.
2. Prefer explicit fields over vague blobs.
3. Every model should support confidence levels where uncertainty matters.
4. Every model should be serializable to JSON.
5. Every model should be readable by humans and useful to AI agents.

---

# First Implementation Target

The first code pass should create dataclasses or Pydantic models for:

- `AtlasProject`
- `AtlasRisk`
- `EvidenceSource`
- `GraphNode`
- `GraphEdge`
- `DigitalTwinComponent`
- `PrototypeRecord`
- `CouncilDecision`
