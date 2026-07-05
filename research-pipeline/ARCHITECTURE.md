# ATLAS Research Pipeline — Architecture

## Purpose
The Research Pipeline is the controlled knowledge-gathering system for ATLAS.

It helps Ajani, Minerva, and Hermes research ideas without mixing strong evidence, weak claims, inspiration, and speculation into one pile.

---

# Core Goal
Turn outside information into trustworthy ATLAS knowledge.

The pipeline should answer:

- What is the source?
- How reliable is it?
- What claim does it support?
- What claim does it challenge?
- Which project does it affect?
- Which AI should study it?
- What should be researched next?

---

# Pipeline Stages

## Stage 1 — Intake
Capture source information.

Fields:
- Title
- Author or organization
- Date
- Source type
- Link or identifier
- Project connection
- AI owner

## Stage 2 — Classification
Classify the source.

Types:
- Peer-reviewed paper
- Patent
- Datasheet
- Standard
- Government report
- Technical documentation
- Book
- Video
- Article
- Forum
- Concept art
- Product page

## Stage 3 — Reliability Rating
Assign reliability level.

Levels:
- Level 1: Strongest evidence
- Level 2: Useful technical source
- Level 3: Inspiration source
- Level 4: Weak or unsafe source

## Stage 4 — Claim Extraction
Pull out important claims.

Each claim should be labeled:
- Proven
- Strong evidence
- Promising evidence
- Early research
- Plausible assumption
- Speculative
- Unsupported
- Unsafe or rejected

## Stage 5 — Project Mapping
Connect source and claims to ATLAS projects.

Examples:
- Power Cell
- Weaver
- Green Robots
- Digital Twin Engine
- Plant Library
- Luxury Design Intelligence

## Stage 6 — AI Routing
Send knowledge to the correct AI.

- Ajani: strategy, competition, market, patent, business, risk
- Minerva: science, biology, chemistry, medicine, environment, source quality
- Hermes: engineering, manufacturing, robotics, electronics, materials, CAD

## Stage 7 — Graph Memory Update
Create graph relationships:
- SOURCE_SUPPORTS_CLAIM
- SOURCE_CONTRADICTS_CLAIM
- PROJECT_SUPPORTED_BY_SOURCE
- PROJECT_REQUIRES_RESEARCH

## Stage 8 — Research Report
Generate a Markdown report.

---

# Research Report Template

```markdown
# Research Report — Topic

## Source Summary

## Reliability Level

## Key Claims

## Evidence Labels

## What This Supports

## What This Challenges

## Unknowns

## Risks

## Connected ATLAS Projects

## Assigned AI

## Recommended Next Research
```

---

# Rule
ATLAS may use inspiration from anywhere, but proof must come from strong sources.
