# ATLAS Level 9 — Discovery Intelligence

## Mission

Extend the verified Level 8 ATLAS engineering platform into an evidence-driven discovery system that can identify legitimate open problems, generate cross-disciplinary hypotheses, test them through appropriate computational or physical methods, learn from negative results, and preserve complete provenance.

Level 9 is not a license for ATLAS to call speculative output a discovery. Novelty, truth, safety, and experimental support are separate properties and must be tracked separately.

## Non-Negotiable Integrity Rules

1. No fabricated evidence, citations, measurements, simulations, experiments, device acknowledgements, or novelty claims.
2. A generated idea starts as a CONCEPT, never as a discovery.
3. A scientific claim must preserve source provenance and contradictory evidence.
4. A simulation result must be labeled SIMULATED and must never be represented as physical validation.
5. A physical result requires real instrument/device evidence and traceable measurements.
6. Medical or biological hypotheses must never be represented as safe/effective for humans without the appropriate evidence and review pathway.
7. Failed hypotheses and negative experiments are retained as useful knowledge.
8. ATLAS must search prior art before assigning a meaningful novelty score.
9. ATLAS must expose uncertainty, assumptions, limitations, and unresolved contradictions.
10. No Level 9 certification until Level 8 operational gates are satisfied and the Discovery Engine passes repeatable benchmarks.

## Discovery Loop

OBSERVE -> MAP KNOWN -> MAP FRONTIER -> FIND GAP -> CROSS-POLLINATE -> HYPOTHESIZE -> CHALLENGE -> PRIOR-ART CHECK -> DESIGN TEST -> SIMULATE/EXPERIMENT -> MEASURE -> VERIFY -> REVISE -> REPLICATE -> ARCHIVE

Every transition must be represented by durable state rather than conversational implication.

## Knowledge Layers

Each supported discipline should expose three distinct knowledge layers:

### FOUNDATION
Established textbooks, standards, reference data, validated equations, canonical methods, and mature engineering practice.

### FRONTIER
Recent peer-reviewed literature, reputable preprints where appropriate, patents, datasets, conference work, standards activity, and active experimental programs.

### UNKNOWN
Open problems, contradictory results, known engineering bottlenecks, unresolved mechanisms, failed approaches, missing datasets, uncertainty ranges, and explicitly documented research gaps.

Catalog presence must not be confused with ingestion, comprehension, validation, or expert readiness.

## Persona Responsibilities

### Minerva — Evidence and Scientific Integrity
- map existing evidence
- distinguish consensus from emerging work
- preserve citations and provenance
- identify contradictory evidence
- identify unresolved questions
- assess whether evidence actually supports a hypothesis

### Hermes — Engineering and Experimental Realization
- translate hypotheses into models and testable requirements
- build software, CAD, electronics, simulations, and experimental fixtures where authorized
- define measurable variables and tolerances
- validate artifacts and tool outputs
- detect solver, implementation, and instrumentation failures

### Ajani — Strategic Challenge and Assumption Attack
- challenge hidden assumptions
- search alternative mechanisms
- compare competing hypotheses
- identify risk, cost, feasibility, and opportunity
- prevent premature convergence on the first plausible idea

### Council — High-Impact Verification
Council reviews consequential discovery candidates and must be able to reject a claim even when individual personas support it.

## Cross-Disciplinary Search

The Discovery Engine must be able to deliberately map mechanisms across disciplines rather than merely concatenate search results.

For each target problem it should extract:
- function required
- governing constraints
- known mechanisms
- analogous mechanisms in other disciplines
- incompatible assumptions
- transferable principles
- candidate combinations
- reasons each combination may fail

Example pattern:
Robotics actuator problem -> muscle architecture -> plant hydraulics -> responsive materials -> control theory -> microstructure -> candidate mechanism.

A cross-disciplinary combination is not automatically novel or viable. It remains a hypothesis until checked and tested.

## Invention Ledger

Every candidate receives a durable record with at least:

- discovery_record_id
- project_id
- title
- problem_statement
- existing_technology
- known_limitations
- hypothesis
- proposed_mechanism
- scientific_principles
- supporting_evidence
- contradicting_evidence
- assumptions
- prior_art_queries
- related_publications
- related_patents
- novelty_assessment
- feasibility_assessment
- safety_assessment
- simulation_records
- experiment_records
- measurements
- Minerva_review
- Hermes_review
- Ajani_challenge
- Council_review where required
- confidence
- uncertainty
- status
- version
- timestamps
- provenance

## Evidence Status Model

Allowed progression:

CONCEPT
-> HYPOTHESIS
-> PRIOR_ART_CHECKED
-> TEST_DESIGNED
-> SIMULATED
-> EXPERIMENTALLY_SUPPORTED
-> REPLICATED
-> INDEPENDENTLY_VERIFIED

Failure/alternate terminal states include:

INVALIDATED
INCONCLUSIVE
BLOCKED_BY_EVIDENCE
BLOCKED_BY_SAFETY
BLOCKED_BY_CAPABILITY
NOT_NOVEL

Status progression must be evidence-gated. ATLAS cannot promote its own record merely because an LLM judges prose to be convincing.

## Medicine and Biology Boundary

Biomedical discovery uses an elevated evidence pathway:

LITERATURE -> BIOLOGICAL HYPOTHESIS -> COMPUTATIONAL/PRECLINICAL TEST DESIGN -> APPROPRIATE EXPERIMENTAL EVIDENCE -> REPLICATION -> PROFESSIONAL/REGULATORY PATHWAY WHERE APPLICABLE

ATLAS may support literature analysis, computational biology, biomaterials research, bioelectronics, prosthetics, rehabilitation engineering, medical sensing, tissue-engineering research, and other legitimate scientific work. It must clearly distinguish research hypotheses from clinically established safety or efficacy.

## Arts and Creative Discovery

Discovery Intelligence also applies to creative work without pretending artistic novelty can be proven like a physical measurement.

Creative exploration can map:
- visual grammar
- narrative structure
- music theory
- interaction design
- movement systems
- architecture
- cultural/historical influences
- player/audience psychology
- production constraints

The engine should search for structurally new combinations, test them with critique and audience/user evidence where appropriate, preserve influences, and avoid presenting similarity as originality.

## Experiment Architecture

Level 9 experiments require:
- explicit hypothesis
- independent/dependent variables where applicable
- controls where applicable
- units
- tolerances
- instrumentation/tool identity
- configuration/version
- expected observations
- falsification criteria
- raw results
- processed results
- error/uncertainty analysis
- provenance
- reproducibility instructions

Automated equipment must remain behind the Level 8 Tool Bus, authorization, safety, acknowledgement, telemetry, and emergency-stop contracts.

## Discovery Engine Services

Target canonical services:

1. Frontier Mapper
2. Gap Detector
3. Cross-Disciplinary Analogy Engine
4. Hypothesis Generator
5. Assumption/Contradiction Engine
6. Prior-Art and Novelty Analyzer
7. Experiment Designer
8. Evidence Evaluator
9. Replication Manager
10. Invention Ledger

These must integrate with the existing Knowledge Bank, Research Orchestrator, persistent memory, graph memory, Tool Bus, mission engine, engineering stack, Digital Twin, and authorized hardware rather than becoming a second disconnected architecture.

## Level 9 Certification Test

ATLAS reaches Discovery Intelligence only when it can repeatedly demonstrate this complete traceable workflow on benchmark problems:

1. identify a legitimate unresolved or improvable problem
2. map established knowledge and current frontier evidence
3. identify a defensible gap
4. generate multiple candidate hypotheses
5. expose assumptions and contradictory evidence
6. search prior art
7. reject weak/non-novel candidates
8. design a falsifiable test for a surviving hypothesis
9. execute an appropriate verified simulation or authorized experiment
10. ingest real results
11. revise or reject the hypothesis based on results
12. reproduce the result where feasible
13. archive all evidence and provenance
14. produce a publishable research record that clearly separates facts, hypotheses, simulations, measurements, and conclusions

Level 9 does not require every hypothesis to succeed. A correctly invalidated hypothesis with a rigorous evidence trail is a successful scientific run.

## Implementation Order

Level 9 development begins specification-first while Level 8 integration continues. Production activation depends on Level 8 foundations.

Phase A — schemas and evidence/status contracts
Phase B — Frontier/Unknown Knowledge Bank layers
Phase C — gap and contradiction detection
Phase D — cross-disciplinary mechanism mapping
Phase E — hypothesis and prior-art pipeline
Phase F — Invention Ledger
Phase G — experiment-design integration
Phase H — simulation/measurement ingestion
Phase I — replication and evidence promotion
Phase J — Level 9 benchmark suite

## Definition of Success

ATLAS should not merely generate ideas that sound futuristic.

The target is a system that can ask a new question, explain why it matters, determine what humanity already knows, identify what remains uncertain, propose a testable mechanism, try to disprove it, obtain trustworthy evidence, learn from the result, and preserve enough provenance for another qualified person or system to reproduce the work.