# ATLAS Graph Memory — Architecture

## Purpose
Graph Memory is the relationship layer of ATLAS. It connects ideas, projects, sources, people, components, materials, risks, decisions, and AI memories.

Normal folders store documents. Graph Memory stores meaning.

---

# Why ATLAS Needs Graph Memory

ATLAS has many connected ideas:
- Weaver connects to robotics, manufacturing, cameras, materials, energy, and digital twins.
- Power Cell connects to chemistry, energy, safety, runtime, and prototypes.
- Green Robots connect to biology, environment, animal movement, plant systems, and repair robotics.
- Luxury Design Intelligence connects to fashion, materials, visual style, brands, and critique.

A graph lets ATLAS ask:
- What projects use this material?
- What risks appear across multiple inventions?
- What sources support this idea?
- Which AI owns this domain?
- What old concept connects to this new idea?
- What should be researched next?

---

# Core Node Types

## Project
An invention, system, story, product, or research direction.

## Concept
A smaller idea inside a project.

## Component
A physical or software part.

## Material
A substance, structure, fabric, alloy, polymer, biomaterial, or composite.

## Source
A paper, video, article, patent, datasheet, book, or technical document.

## Risk
A safety, technical, cost, legal, environmental, or ethical risk.

## AI
Ajani, Minerva, Hermes, or Council.

## Decision
A Council judgment or project milestone.

## Skill
A capability ATLAS needs to learn.

## Domain
A knowledge area, such as robotics, AI, biology, manufacturing, or design.

---

# Core Relationship Types

- PROJECT_USES_COMPONENT
- PROJECT_USES_MATERIAL
- PROJECT_HAS_RISK
- PROJECT_SUPPORTED_BY_SOURCE
- PROJECT_OWNED_BY_AI
- PROJECT_BELONGS_TO_DOMAIN
- PROJECT_DEPENDS_ON_SKILL
- CONCEPT_PART_OF_PROJECT
- COMPONENT_REQUIRES_MATERIAL
- SOURCE_SUPPORTS_CLAIM
- SOURCE_CONTRADICTS_CLAIM
- RISK_MITIGATED_BY
- AI_RESPONSIBLE_FOR_DOMAIN
- DECISION_APPLIES_TO_PROJECT
- PROJECT_CONNECTS_TO_PROJECT

---

# MVP Storage

Start simple:
- Markdown files for human readability
- JSON files for machine readability
- Later SQLite or Neo4j-style graph database

---

# First Goal
Create graph records for the major ATLAS projects and connect them to their domains and lead AIs.

---

# Rule
Memory is only powerful if it is organized. Graph Memory must prevent ATLAS from forgetting how ideas connect.
