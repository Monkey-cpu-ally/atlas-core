# ATLAS Graph Memory — Data Model

## Purpose
This file defines the first machine-readable structure for ATLAS Graph Memory.

Graph Memory connects projects, concepts, sources, risks, materials, components, AI roles, Council decisions, and domains.

---

# Node Schema

```json
{
  "node_id": "string",
  "node_type": "project | concept | component | material | source | risk | ai | decision | skill | domain",
  "name": "string",
  "summary": "string",
  "status": "active | paused | archived | unknown",
  "created_from": "chat | file | research | council | prototype | user",
  "confidence": "low | medium | high",
  "tags": []
}
```

---

# Edge Schema

```json
{
  "edge_id": "string",
  "from_node": "string",
  "to_node": "string",
  "relationship": "string",
  "summary": "string",
  "confidence": "low | medium | high",
  "evidence": []
}
```

---

# Recommended Relationship Types

## Project Relationships

- PROJECT_USES_COMPONENT
- PROJECT_USES_MATERIAL
- PROJECT_HAS_RISK
- PROJECT_SUPPORTED_BY_SOURCE
- PROJECT_OWNED_BY_AI
- PROJECT_BELONGS_TO_DOMAIN
- PROJECT_DEPENDS_ON_SKILL
- PROJECT_CONNECTS_TO_PROJECT

## Concept Relationships

- CONCEPT_PART_OF_PROJECT
- CONCEPT_INSPIRED_BY
- CONCEPT_REQUIRES_RESEARCH
- CONCEPT_HAS_UNKNOWN

## Source Relationships

- SOURCE_SUPPORTS_CLAIM
- SOURCE_CONTRADICTS_CLAIM
- SOURCE_REQUIRES_VERIFICATION

## Risk Relationships

- RISK_MITIGATED_BY
- RISK_BLOCKS_PROTOTYPE
- RISK_REQUIRES_PROFESSIONAL_REVIEW

## AI Relationships

- AI_RESPONSIBLE_FOR_DOMAIN
- AI_REVIEWS_PROJECT
- AI_GENERATED_DECISION

---

# Example Node

```json
{
  "node_id": "project_digital_twin_engine",
  "node_type": "project",
  "name": "ATLAS Digital Twin Engine",
  "summary": "Simulation and modeling layer for ATLAS inventions.",
  "status": "active",
  "created_from": "chat",
  "confidence": "medium",
  "tags": ["simulation", "engineering", "innovation-lab"]
}
```

# Example Edge

```json
{
  "edge_id": "edge_digital_twin_owned_by_hermes",
  "from_node": "project_digital_twin_engine",
  "to_node": "ai_hermes",
  "relationship": "PROJECT_OWNED_BY_AI",
  "summary": "Hermes leads engineering architecture for the Digital Twin Engine.",
  "confidence": "high",
  "evidence": ["innovation-lab/projects/ATLAS_DIGITAL_TWIN_ENGINE_INTAKE.md"]
}
```

---

# Rule
Graph records must be simple enough to update often. A messy graph becomes another junk drawer.
