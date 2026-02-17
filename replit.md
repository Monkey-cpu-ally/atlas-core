# Atlas Core

## Overview

Atlas Core is a safety-first environmental robotics framework featuring an AI persona-based educational and creative assistant system. It utilizes three distinct AI personas (Ajani, Minerva, Hermes) to provide deep expertise and diverse perspectives, acting as collaborative creative partners. The project aims to deliver an advanced, ethical, and collaborative AI experience that encourages original thought and challenges stereotypes, especially in the creation of unique Black tragic heroes. Atlas Core serves as an advisory tool for recommendations, scenario simulation, project planning, concept teaching, and content generation, strictly operating without self-directed real-world actions or unsupervised autonomy.

## User Preferences

Preferred communication style: Simple, everyday language.

**Creator Profile**
**Project Ambitions**: Many ideas for personal projects - 3D printers specialized for different fields (automotive, biology, home building/blueprints). Big thinker with cross-disciplinary vision.

**Visual Aesthetic**:
- Prefers darker colors and soft colors
- Does NOT like bright colors
- Dark, moody, atmospheric palettes

**Creative Inspirations**:
- Dark comics: Dark Knights Metal, Swamp Thing, Justice League Dark, DC Absolute Universe
- Authors: Stephen King (kids stories with dark undertones), H.P. Lovecraft (cosmic horror)
- Loves dark novels with layered, unsettling narratives

**Music & Film**:
- Heavy music listener
- Especially loves 80s style music and 80s-inspired films
- Synthwave/retro aesthetic appreciation

**Character Creation Philosophy**:
- Passionate about creating Black tragic heroes
- Wants to break stereotypes - not the same powers or roles Black characters usually get
- Aims for characters that feel different, unique, and un-thought-of
- Heroes with depth, tragedy, and originality

**Thinking Style**:
- Thorough explorer: searches the whole map before moving on, doesn't skip areas
- Balanced approach: levels out stats equally, considers all angles
- Pattern seeker: looks for things others would miss
- Anti-trend: doesn't follow what everyone else is doing
- Critical viewer: notices plot holes and inconsistencies in movies
- Imaginative designer: thinks through movie ideas, layouts, original concepts
- Independent thinker: processes things differently, sees connections others don't

## System Architecture

Atlas Core employs a "Tri-Core Council Architecture" with three specialized AI personas (Ajani, Minerva, Hermes) collaborating under strict rules in a "Trinity Counsel Mode." Project execution is supported by a "LEGO-Style Build System" for modular instructions and simulation within the "Eco_forge" framework. Passive monitoring is provided by "MetalFlower Sensors." The knowledge system reconstructs concepts from first principles using a "patterns, not copies" philosophy.

The FastAPI application features modularized routes for chat, design, conversations, TTS, user data, and lesson plans.

The **UI/UX** is a PWA with a premium design system, dark palettes, a theme switcher, collapsible sections, conversation memory, and real-time system status, supporting Biomimetic Sci-Fi and Cybernetic Naturalism art styles.

Key modules include a comprehensive Lesson Plan System, a Hermes Auditor Pipeline for AI response quality, an interactive 3D Anatomy Lab, and a Blueprint Analysis System. **UmojaForge** offers AI-powered parametric CAD, **Umoja Living Chip Designer** is a safety-first chip design system, and **Umoja Processor Simulator Lab** provides a three-layer educational chip simulation.

The **Self-Organizing Photonic Cognitive Metamaterial (SPCM)** is a light-based, regenerative AI system. The **Multi-Agent Orchestration System** incorporates a **Tool-Use Kernel**, **Role Authority Ladder**, **Core Loop**, **Never-Break Rules**, **Memory Layer**, API endpoints, **Git Checkpoint System**, **Confidence Scoring System**, **Learning Loop**, and **State Tracker**.

The **Chimera Digital Chip Runtime** defines a software-defined SoC architecture with a **3-Lane Scheduler** and specialized **Modules (Organs)**. The **Sword & Shield Protocol** secures Hermes operations, and the **HermesRouter** handles 3-lane task routing (FAST, SAFE, HEAVY).

The **Dragon-Scale Forge** is a web-based creative tool for sketching and image processing. The **Web Research Engine** enables personas to search for scientific, technical, and creative resources. The **Persona Research System** implements Independent Research Sandboxes (IRS) for each persona's daily, guarded research. The **Equipment Forge** allows AIs to produce functional projects tracked by the **Build System**.

The **Theoretical Knowledge Synthesis System** ensures conceptual, non-empirical AI research, with human oversight via an Architect Review Gate (ARG). The **Teaching Doctrine System** enforces Ivy/PhD-level understanding conveyed with 6th-grade clarity and supports a "POLYMATH" mode. The **Chameleon Protocol** is a defensive doctrine for privacy and security.

The **Universal Workshop Standard (UWS)** is an AI-powered build manual generator using the Tri-Core personas, enforcing **10 UWS Laws** and a **LEGO-Style Micro-Step System** for HTML flipbook manuals. The **Pre-Reality Engineering Engine** is a safety-gated educational simulation system across four domains (BioSim, MachineSim, LightSim, SoundSim), managed by a **SafetyGate** and **SimulationOrchestrator**.

The **Edge Panel (Hypothesis Development Lab)** monitors real-time persona hypothesis development and feasibility analysis, displaying project cards with a **3-Tier Knowledge System**: Conceptual Sandbox, Validation Prep, and Empirical Bridge. The **Hypothesis Development with Guardrails** system governs hypothesis development, with guardrails and a supervisor dashboard. The **Build System** provides APIs for managing build plans. The **Daily Hypothesis Runner** generates automated daily hypothesis work for each persona. The **LEGO-Style Build Plan Generator** creates fabrication-ready build plans with comprehensive details and a **Fabrication Package** export. The **Build → Prove → Lock** methodology is the mandatory engineering workflow.

The **Figma Design Hub** integrates with Figma via its REST API for design file browsing.

The **Hermes Reality Engine** (`atlas_core_new/hermes_reality/`) is a deterministic, math-based physics validation system enforcing physics gates and assigning projects to 4 feasibility tiers. It includes domain-specific simulators and a single API endpoint for validation and simulation.

The **Design Engine** (`atlas_core_new/design_engine/`) is a plugin-based Tri-Core engineering pipeline with steps for Dream, Constraints, Iterate, and Validate. It features a **Plugin Architecture** with four domain plugins (Hydra-Core Power Spine, Umoja STF Armor Panel, Hermes PQC Bridge, 6-DOF Robotic Arm) providing domain-specific variant generation and scoring.

The **Engineering Validation System** (`atlas_core_new/engineering/validation.py`) provides a 5-check project readiness validator with 4 tiers, smart recommendations, and physics contradiction detection.

The **Domain Packs System** (`atlas_core_new/engineering/domain_packs.py`) offers 8 specialized lab domains with shared libraries and Tri-Core agent voices, supporting pre-filled build cards and transparency/material adjustments.

The **Project-Domain Bridge** (`atlas_core_new/engineering/project_domain_map.py`) maps research projects to lab domains, connecting the validation system to persona research.

The **Text Intake System** (`atlas_core_new/engineering/text_intake.py`) converts free-text project descriptions into validated build cards, featuring keyword-based domain detection, negation parsing, constraint extraction, and overrides.

The **Ajani Blueprint Engine** (`atlas_core_new/blueprint_engine/`) is a structured engineering blueprint generation system with Material, Component, and Tool Libraries. It generates strict **BlueprintPacket** objects, includes a **Validation Gate** to prevent fantasy terms, and offers six project templates. The **Atlas Storage** system (`atlas_core_new/blueprint_engine/storage.py`) provides file-based project persistence with BOM CSV generation, ReportLab PDF manual generation, image upload, and ZIP export.

The **ATLAS Visual Blueprint Studio** (`atlas_core_new/static/viewer/`) is an interactive 3D blueprint viewer built with Three.js, accessible at `/viewer/index`. It supports 5 projects (Metal Flower, Green Bot, Medusa Arms, Morphing Panel, Hydrogen Module) with parametric controls, explode view, orbit camera, screenshot capture, and automated step-image ZIP export for LEGO-style manuals. Projects are defined in `projects.js` with build functions and `EXPORT_PRESETS` for automated multi-step captures.

## External Dependencies

-   **Python Packages**: FastAPI, SQLAlchemy, psycopg2, uvicorn, openai, requests
-   **LLM**: Any OpenAI-compatible API (OpenAI, Azure, Ollama, LM Studio, etc.)
-   **Database**: PostgreSQL
-   **TTS**: ElevenLabs
-   **Figma**: Figma REST API
-   **CAD (Optional)**: CadQuery