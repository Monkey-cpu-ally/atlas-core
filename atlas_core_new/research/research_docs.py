"""
Research Documentation System - Sandboxed Scientific Independence

CORE RULE: AIs may explore freely, but they may only PROPOSE, never IMPOSE.
User is architect-in-chief. AIs are researchers who share findings when asked.

Each AI persona documents their research with:
- Phase 0 - Philosophy & Intent: Why this project exists, ethical boundaries
- Phase 1 - Theory & Research: Known science, open questions, constraints
- Phase 2 - Blueprint: Diagrams, components, dependencies
- Phase 3 - Simulation: Digital models, edge cases, stress tests
- Phase 4 - Physical Proposal: Phased build plan, abort conditions
- Phase 5 - Archive: What worked, what failed, lessons learned

No phase can be skipped. Simulation failure ≠ bad project. Skipping simulation = forbidden.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum


class ProjectPhase(Enum):
    """Non-skippable project lifecycle phases"""
    PHASE_0_PHILOSOPHY = "philosophy"       # Why it exists, ethical boundaries, failure risks
    PHASE_1_RESEARCH = "research"           # Theory, known science, open questions, assumptions
    PHASE_2_BLUEPRINT = "blueprint"         # Diagrams, components, inputs/outputs, dependencies
    PHASE_3_SIMULATION = "simulation"       # Digital models, edge cases, stress tests, failure scenarios
    PHASE_4_PROPOSAL = "physical_proposal"  # Phased build plan, abort conditions - THEY PROPOSE, YOU APPROVE
    PHASE_5_ARCHIVE = "archive"             # Reflection, what worked, what failed, philosophy changes


@dataclass
class Step:
    number: int
    title: str
    description: str
    status: str  # pending, in_progress, complete
    notes: List[str] = field(default_factory=list)
    completed_date: Optional[str] = None


@dataclass
class Blueprint:
    id: str
    name: str
    version: str
    description: str
    specifications: Dict[str, str]
    materials: List[str]
    diagrams: List[str]  # Descriptions of visual diagrams
    safety_notes: List[str]
    created_date: str
    last_updated: str


@dataclass
class Simulation:
    id: str
    name: str
    description: str
    inputs: Dict[str, str]
    expected_outputs: Dict[str, str]
    variables: List[str]
    success_criteria: List[str]
    risk_factors: List[str]
    results: Optional[Dict[str, str]] = None
    status: str = "pending"  # pending, running, passed, failed


@dataclass
class PhysicalBuild:
    phase: ProjectPhase
    started_date: str
    target_completion: str
    actual_completion: Optional[str] = None
    components_needed: List[str] = field(default_factory=list)
    components_acquired: List[str] = field(default_factory=list)
    assembly_steps: List[Step] = field(default_factory=list)
    quality_checks: List[str] = field(default_factory=list)
    blockers: List[str] = field(default_factory=list)
    ready_for_testing: bool = False
    test_requirements: List[str] = field(default_factory=list)


@dataclass
class ResearchDocument:
    project_id: str
    project_name: str
    persona: str
    created_date: str
    last_updated: str
    current_phase: ProjectPhase
    steps: List[Step]
    blueprints: List[Blueprint]
    simulations: List[Simulation]
    physical_build: Optional[PhysicalBuild]
    journal_entries: List[Dict[str, str]]  # date, entry
    ready_for_testing: bool = False


RESEARCH_DOCUMENTS: Dict[str, Dict[str, ResearchDocument]] = {
    "ajani": {
        "kinetic-forge": ResearchDocument(
            project_id="kinetic-forge",
            project_name="Kinetic Forge",
            persona="ajani",
            created_date="2026-01-15",
            last_updated="2026-02-04",
            current_phase=ProjectPhase.PHASE_3_SIMULATION,
            steps=[
                Step(1, "Identify Candidate Elements", "Map transition metals with highest kinetic potential at atomic level", "complete", ["Osmium, Tungsten, Selenium show promise"]),
                Step(2, "Frequency Mapping", "Document resonance frequencies that unlock kinetic release", "complete", ["Base frequencies catalogued for 12 elements"]),
                Step(3, "Containment Design", "Design safe containment for kinetic energy during extraction", "in_progress", ["Crystalline lattice shows best absorption"]),
                Step(4, "Energy Conversion Circuit", "Build circuit to convert raw kinetic to usable power", "pending"),
                Step(5, "Miniaturization", "Reduce forge to portable size", "pending"),
                Step(6, "Safety Protocols", "Establish failsafes for runaway reactions", "pending"),
            ],
            blueprints=[
                Blueprint(
                    id="kf-core-v1",
                    name="Kinetic Core Chamber",
                    version="1.2",
                    description="Primary chamber for kinetic extraction from transition metals",
                    specifications={
                        "diameter": "15cm",
                        "wall_thickness": "2cm tungsten-carbide composite",
                        "operating_temp": "-50C to 200C",
                        "max_output": "50kW theoretical",
                        "resonance_range": "12Hz - 340kHz",
                    },
                    materials=["Tungsten-carbide composite", "Selenium crystal array", "Osmium contact points", "Graphene insulation layer"],
                    diagrams=["Cross-section of core chamber", "Resonance wave pattern diagram", "Energy flow schematic"],
                    safety_notes=["Never operate without containment field active", "Thermal runaway possible above 250C", "Keep away from magnetic fields during calibration"],
                    created_date="2026-01-20",
                    last_updated="2026-02-01",
                )
            ],
            simulations=[
                Simulation(
                    id="kf-sim-001",
                    name="Osmium Resonance Test",
                    description="Test kinetic release at various frequencies in osmium sample",
                    inputs={"sample_mass": "10g", "frequency_start": "100Hz", "frequency_end": "10kHz", "step_interval": "50Hz"},
                    expected_outputs={"peak_frequency": "~2.4kHz", "energy_release": "0.5-2.0 joules", "stability": ">95%"},
                    variables=["temperature", "magnetic interference", "sample purity"],
                    success_criteria=["Stable energy release", "No thermal runaway", "Reproducible results"],
                    risk_factors=["Sample fracture at high resonance", "Heat buildup"],
                    results={"peak_frequency": "2.37kHz", "energy_release": "1.2 joules", "stability": "97.3%"},
                    status="passed",
                ),
                Simulation(
                    id="kf-sim-002",
                    name="Multi-Element Cascade",
                    description="Chain reaction through multiple element samples",
                    inputs={"elements": "Os, W, Se", "cascade_pattern": "linear", "initial_frequency": "2.37kHz"},
                    expected_outputs={"amplification_factor": "3-5x", "total_output": "5-10 joules"},
                    variables=["element spacing", "transition timing"],
                    success_criteria=["Controlled amplification", "No energy loss between elements"],
                    risk_factors=["Uncontrolled cascade", "Element degradation"],
                    status="pending",
                ),
            ],
            physical_build=PhysicalBuild(
                phase=ProjectPhase.PHASE_2_BLUEPRINT,
                started_date="2026-02-01",
                target_completion="2026-04-01",
                components_needed=["Tungsten-carbide chamber shell", "Selenium crystal array (12 units)", "Osmium contact rods (6)", "Graphene sheets", "Frequency generator", "Power converter"],
                components_acquired=["Frequency generator", "Graphene sheets"],
                assembly_steps=[
                    Step(1, "Chamber Fabrication", "Machine the tungsten-carbide shell to spec", "pending"),
                    Step(2, "Crystal Array Mount", "Install selenium crystals in resonance pattern", "pending"),
                    Step(3, "Contact Installation", "Place osmium rods at energy collection points", "pending"),
                    Step(4, "Insulation Layer", "Apply graphene insulation", "pending"),
                    Step(5, "Electronics Integration", "Wire frequency generator and converter", "pending"),
                    Step(6, "Calibration", "Tune to optimal frequencies", "pending"),
                ],
                quality_checks=["Chamber pressure test", "Crystal alignment verification", "Insulation continuity", "Frequency response curve"],
                blockers=["Awaiting tungsten-carbide machining"],
                ready_for_testing=False,
                test_requirements=["Isolated testing environment", "Thermal monitoring equipment", "Emergency containment field", "Remote operation capability"],
            ),
            journal_entries=[
                {"date": "2026-01-15", "entry": "Project initiated. The elements speak to me - there's so much untapped energy waiting to be freed."},
                {"date": "2026-01-22", "entry": "Osmium shows incredible promise. The resonance at 2.37kHz is clean and stable."},
                {"date": "2026-02-01", "entry": "Moving to prototype phase. Need to solve the containment problem before we can scale up."},
            ],
            ready_for_testing=False,
        ),
        "density-matrix": ResearchDocument(
            project_id="density-matrix",
            project_name="Density Matrix Protocol",
            persona="ajani",
            created_date="2026-01-10",
            last_updated="2026-02-03",
            current_phase=ProjectPhase.PHASE_1_RESEARCH,
            steps=[
                Step(1, "Density State Mapping", "Identify all possible density states for target materials", "in_progress", ["Selenium compounds show 4 distinct states"]),
                Step(2, "Frequency-Density Correlation", "Map which frequencies trigger which density states", "pending"),
                Step(3, "Phase Transition Speed", "Measure and optimize transition times", "pending"),
                Step(4, "Stability Duration", "Test how long altered states can be maintained", "pending"),
                Step(5, "Biological Safety", "Ensure no harm when used near living tissue", "pending"),
                Step(6, "Application Prototypes", "Build test devices for rescue and medical use", "pending"),
            ],
            blueprints=[],
            simulations=[
                Simulation(
                    id="dm-sim-001",
                    name="Selenium Phase States",
                    description="Map all achievable density states in selenium compound",
                    inputs={"compound": "Se-12 alloy", "frequency_range": "1Hz-100kHz"},
                    expected_outputs={"state_count": "3-5", "transition_markers": "frequency thresholds"},
                    variables=["temperature", "pressure", "purity"],
                    success_criteria=["Identify all states", "Reproducible transitions"],
                    risk_factors=["State instability", "Compound degradation"],
                    status="running",
                ),
            ],
            physical_build=None,
            journal_entries=[
                {"date": "2026-01-10", "entry": "The idea of walking through walls... not magic, just science we don't understand yet."},
                {"date": "2026-01-28", "entry": "Partial phasing achieved! The selenium compound became 40% less dense for 0.3 seconds."},
            ],
            ready_for_testing=False,
        ),
        "solar-gem": ResearchDocument(
            project_id="solar-gem",
            project_name="Solar Gem Array",
            persona="ajani",
            created_date="2026-01-05",
            last_updated="2026-02-02",
            current_phase=ProjectPhase.PHASE_2_BLUEPRINT,
            steps=[
                Step(1, "Crystal Growth Protocol", "Develop method for growing energy-storing crystals", "complete"),
                Step(2, "Solar Absorption Tuning", "Optimize crystal structure for maximum solar capture", "complete"),
                Step(3, "Energy Storage Density", "Maximize joules per gram of crystal", "complete"),
                Step(4, "Controlled Release Mechanism", "Create safe energy release interface", "in_progress"),
                Step(5, "Longevity Testing", "Verify 50+ year operational lifespan", "pending"),
                Step(6, "Scale Production", "Develop manufacturing process", "pending"),
            ],
            blueprints=[
                Blueprint(
                    id="sg-gem-v2",
                    name="Solar Gem Crystal Structure",
                    version="2.1",
                    description="Optimized crystal lattice for solar energy storage",
                    specifications={
                        "crystal_system": "hexagonal modified",
                        "absorption_range": "280nm-2500nm",
                        "storage_density": "15 MJ/kg",
                        "discharge_rate": "adjustable 1W-10kW",
                        "lifespan": "projected 75 years",
                    },
                    materials=["Germanium base", "Selenium dopants", "Trace rare earths"],
                    diagrams=["Crystal lattice structure", "Energy band diagram", "Discharge circuit"],
                    safety_notes=["Avoid rapid discharge - thermal shock risk", "Store below 50C when not charging"],
                    created_date="2026-01-12",
                    last_updated="2026-01-30",
                )
            ],
            simulations=[
                Simulation(
                    id="sg-sim-001",
                    name="10-Year Accelerated Lifespan",
                    description="Simulate 10 years of charge/discharge cycles",
                    inputs={"cycles_per_day": "2", "simulated_years": "10", "stress_factor": "1.5x"},
                    expected_outputs={"capacity_retention": ">90%", "structural_integrity": "no fractures"},
                    variables=["temperature cycling", "discharge depth"],
                    success_criteria=["Maintain >90% capacity", "No structural degradation"],
                    risk_factors=["Crystal fatigue", "Dopant migration"],
                    results={"capacity_retention": "94.2%", "structural_integrity": "minor surface wear"},
                    status="passed",
                ),
            ],
            physical_build=PhysicalBuild(
                phase=ProjectPhase.PHASE_2_BLUEPRINT,
                started_date="2026-01-25",
                target_completion="2026-03-15",
                components_needed=["Crystal growth chamber", "Germanium substrate", "Selenium vapor source", "Rare earth dopants", "Discharge interface module"],
                components_acquired=["Crystal growth chamber", "Germanium substrate", "Selenium vapor source"],
                assembly_steps=[
                    Step(1, "Chamber Setup", "Configure growth chamber for gem production", "complete"),
                    Step(2, "Substrate Prep", "Prepare germanium base plates", "complete"),
                    Step(3, "Crystal Growth", "Grow first test gems", "in_progress"),
                    Step(4, "Dopant Integration", "Add selenium and rare earth elements", "pending"),
                    Step(5, "Interface Attachment", "Connect discharge modules", "pending"),
                    Step(6, "Encapsulation", "Protective housing for each gem", "pending"),
                ],
                quality_checks=["Crystal clarity inspection", "Energy density measurement", "Discharge curve verification"],
                blockers=[],
                ready_for_testing=False,
                test_requirements=["Solar exposure array", "Load bank for discharge testing", "Long-term monitoring station"],
            ),
            journal_entries=[
                {"date": "2026-01-05", "entry": "Ra blessed ancient civilizations with the sun. We can do the same with crystallized sunlight."},
                {"date": "2026-01-25", "entry": "First crystal growth successful. It glows faintly in the dark - holding the sun's memory."},
            ],
            ready_for_testing=False,
        ),
    },
    "minerva": {
        "chimera-healing": ResearchDocument(
            project_id="chimera-healing",
            project_name="Chimera Healing Project",
            persona="minerva",
            created_date="2026-01-08",
            last_updated="2026-02-04",
            current_phase=ProjectPhase.PHASE_3_SIMULATION,
            steps=[
                Step(1, "Regenerative Gene Identification", "Catalog genes responsible for regeneration in salamanders, starfish, and axolotl", "complete", ["47 key genes identified"]),
                Step(2, "Human Compatibility Analysis", "Map homologous genes in human genome", "complete", ["32 genes have human analogs"]),
                Step(3, "Expression Vector Design", "Create safe delivery mechanism for gene activation", "in_progress", ["Testing lipid nanoparticle carriers"]),
                Step(4, "Cell Culture Testing", "Test regeneration in human cell cultures", "pending"),
                Step(5, "Tissue-Level Trials", "Graduate to tissue samples", "pending"),
                Step(6, "Organ Regeneration Protocol", "Develop full organ regrowth procedure", "pending"),
                Step(7, "Ethical Review", "Full ethics board review before any trials", "pending"),
            ],
            blueprints=[
                Blueprint(
                    id="ch-vector-v1",
                    name="Phoenix Vector Delivery System",
                    version="1.0",
                    description="Lipid nanoparticle system for delivering regenerative gene activators",
                    specifications={
                        "particle_size": "80-100nm",
                        "payload": "mRNA + guide RNA",
                        "target_specificity": "tissue-specific promoters",
                        "half_life": "72 hours",
                        "immune_evasion": "PEG coating",
                    },
                    materials=["Lipid mixture (DSPC, cholesterol, PEG-lipid)", "mRNA cargo", "Tissue-specific aptamers"],
                    diagrams=["Nanoparticle cross-section", "Cellular uptake pathway", "Gene activation cascade"],
                    safety_notes=["Monitor for immune response", "Never use without tissue targeting", "Strict dosage control"],
                    created_date="2026-01-20",
                    last_updated="2026-02-01",
                )
            ],
            simulations=[
                Simulation(
                    id="ch-sim-001",
                    name="Axolotl Gene Expression in Human Cells",
                    description="Simulate axolotl regeneration gene expression in human fibroblasts",
                    inputs={"cell_type": "human dermal fibroblast", "genes": "LIN28, SALL4, MSX1", "expression_level": "2x baseline"},
                    expected_outputs={"dedifferentiation": "partial", "proliferation": "increased 30-50%"},
                    variables=["expression timing", "gene combination ratios"],
                    success_criteria=["No tumor formation", "Controlled dedifferentiation", "Maintained cell viability"],
                    risk_factors=["Uncontrolled growth", "Loss of cell identity", "Immune response"],
                    status="running",
                ),
            ],
            physical_build=None,
            journal_entries=[
                {"date": "2026-01-08", "entry": "The axolotl regenerates its heart without scarring. We can learn from this small teacher."},
                {"date": "2026-01-25", "entry": "Found the key - LIN28 reactivates developmental pathways. But we must be SO careful."},
                {"date": "2026-02-04", "entry": "Ethics first, always. Power to heal is also power to harm. Every step must be justified."},
            ],
            ready_for_testing=False,
        ),
        "ancestral-code": ResearchDocument(
            project_id="ancestral-code",
            project_name="Ancestral Code Initiative",
            persona="minerva",
            created_date="2026-01-12",
            last_updated="2026-02-03",
            current_phase=ProjectPhase.PHASE_1_RESEARCH,
            steps=[
                Step(1, "Archaic Genome Collection", "Gather Neanderthal, Denisovan, and ancient human sequences", "complete"),
                Step(2, "Dormant Gene Identification", "Find silenced ancestral genes with beneficial potential", "in_progress", ["Immunity genes, cold adaptation, oxygen efficiency"]),
                Step(3, "Reactivation Pathways", "Map how to safely reactivate dormant genes", "pending"),
                Step(4, "Benefit-Risk Analysis", "Evaluate each gene's potential benefits vs risks", "pending"),
                Step(5, "Individual Ancestry Mapping", "Create personalized ancestral gene profiles", "pending"),
                Step(6, "Therapeutic Protocols", "Develop treatments based on ancestral wisdom", "pending"),
            ],
            blueprints=[],
            simulations=[
                Simulation(
                    id="ac-sim-001",
                    name="Denisovan Altitude Gene Simulation",
                    description="Model EPAS1 variant effects on oxygen efficiency",
                    inputs={"gene_variant": "Denisovan EPAS1", "altitude": "4500m", "activity_level": "moderate exertion"},
                    expected_outputs={"oxygen_efficiency": "+15-25%", "fatigue_reduction": "significant"},
                    variables=["baseline fitness", "acclimatization time"],
                    success_criteria=["Improved high-altitude performance", "No adverse effects"],
                    risk_factors=["Blood viscosity changes", "Cardiac stress"],
                    status="pending",
                ),
            ],
            physical_build=None,
            journal_entries=[
                {"date": "2026-01-12", "entry": "Our ancestors survived ice ages, plagues, and famines. Their strength is written in our genes, waiting."},
                {"date": "2026-02-02", "entry": "The Denisovan EPAS1 gene is remarkable - it's why Tibetans thrive at altitude. What else is hiding in our past?"},
            ],
            ready_for_testing=False,
        ),
        "splice-sanctuary": ResearchDocument(
            project_id="splice-sanctuary",
            project_name="Splice Sanctuary Ethics Framework",
            persona="minerva",
            created_date="2026-01-01",
            last_updated="2026-02-04",
            current_phase=ProjectPhase.PHASE_4_PROPOSAL,
            steps=[
                Step(1, "Historical Review", "Study past genetic ethics failures and successes", "complete"),
                Step(2, "Stakeholder Consultation", "Gather perspectives from patients, scientists, ethicists, religious leaders", "complete"),
                Step(3, "Core Principles Draft", "Write foundational ethical principles", "complete"),
                Step(4, "Edge Case Analysis", "Address difficult scenarios and grey areas", "in_progress"),
                Step(5, "Enforcement Mechanisms", "Design oversight and accountability systems", "pending"),
                Step(6, "Living Document Protocol", "Create system for ongoing updates and review", "pending"),
            ],
            blueprints=[
                Blueprint(
                    id="ss-framework-v1",
                    name="Eden Protocol Ethics Framework",
                    version="1.0",
                    description="Comprehensive ethical guidelines for genetic modification",
                    specifications={
                        "core_principles": "7 inviolable rules",
                        "review_process": "3-tier approval system",
                        "consent_requirements": "informed, ongoing, revocable",
                        "transparency": "all modifications publicly registered",
                        "reversibility": "preference for reversible modifications",
                    },
                    materials=["Legal framework templates", "Consent documentation", "Review board protocols"],
                    diagrams=["Approval workflow", "Stakeholder relationship map", "Decision tree for edge cases"],
                    safety_notes=["No exceptions to core principles", "Regular ethics training required", "Whistleblower protection mandatory"],
                    created_date="2026-01-15",
                    last_updated="2026-02-04",
                )
            ],
            simulations=[],
            physical_build=PhysicalBuild(
                phase=ProjectPhase.PHASE_4_PROPOSAL,
                started_date="2026-02-01",
                target_completion="2026-03-01",
                components_needed=["Ethics review board charter", "Digital consent platform", "Public registry system", "Training curriculum"],
                components_acquired=["Ethics review board charter", "Training curriculum draft"],
                assembly_steps=[
                    Step(1, "Board Formation", "Assemble diverse ethics review board", "complete"),
                    Step(2, "Charter Ratification", "Finalize and approve board charter", "complete"),
                    Step(3, "Platform Development", "Build digital consent and registry systems", "in_progress"),
                    Step(4, "Training Program", "Develop and test training materials", "in_progress"),
                    Step(5, "Pilot Testing", "Run framework through test scenarios", "pending"),
                    Step(6, "Public Launch", "Release framework for adoption", "pending"),
                ],
                quality_checks=["Legal review", "Accessibility audit", "Stakeholder feedback integration"],
                blockers=[],
                ready_for_testing=True,
                test_requirements=["Test review board session", "Mock consent process", "Scenario walkthroughs"],
            ),
            journal_entries=[
                {"date": "2026-01-01", "entry": "We must build the guardrails before we build the bridge. Power without ethics is just destruction."},
                {"date": "2026-02-01", "entry": "The framework is taking shape. Seven core principles that can never be broken, no matter the justification."},
                {"date": "2026-02-04", "entry": "Ready for pilot testing. This is the foundation everything else builds upon."},
            ],
            ready_for_testing=True,
        ),
    },
    "hermes": {
        "nano-medic": ResearchDocument(
            project_id="nano-medic",
            project_name="Nano-Medic Swarm",
            persona="hermes",
            created_date="2026-01-10",
            last_updated="2026-02-04",
            current_phase=ProjectPhase.PHASE_2_BLUEPRINT,
            steps=[
                Step(1, "Nanobot Architecture", "Design base nanobot structure and propulsion", "complete", ["Flagella-inspired propulsion chosen"]),
                Step(2, "Target Recognition", "Develop cancer cell and pathogen identification", "complete", ["Antibody-mimetic surface markers"]),
                Step(3, "Payload Delivery", "Design drug/treatment delivery mechanism", "in_progress", ["Testing triggered release"]),
                Step(4, "Swarm Communication", "Create inter-bot coordination protocol", "pending"),
                Step(5, "Biodegradation", "Ensure safe breakdown after mission complete", "pending"),
                Step(6, "Navigation System", "Develop blood vessel navigation", "pending"),
                Step(7, "Safety Shutdown", "Create remote deactivation capability", "pending"),
            ],
            blueprints=[
                Blueprint(
                    id="nm-bot-v3",
                    name="Scarab-Class Medical Nanobot",
                    version="3.0",
                    description="Individual nanobot unit for the Nano-Medic Swarm",
                    specifications={
                        "size": "200nm x 100nm x 80nm",
                        "propulsion": "synthetic flagella, 50μm/s",
                        "power": "glucose fuel cell",
                        "payload_capacity": "50 attoliters",
                        "lifespan": "72-168 hours",
                        "communication": "chemical gradient signaling",
                    },
                    materials=["Biocompatible polymer shell", "Gold nanoparticle core", "Synthetic flagella proteins", "Antibody-mimetic targeting molecules"],
                    diagrams=["Exploded view of nanobot", "Propulsion mechanism", "Payload release trigger", "Swarm formation patterns"],
                    safety_notes=["Must include kill switch", "Biodegradable materials only", "Never design for replication"],
                    created_date="2026-01-18",
                    last_updated="2026-02-02",
                )
            ],
            simulations=[
                Simulation(
                    id="nm-sim-001",
                    name="Tumor Targeting Accuracy",
                    description="Test nanobot ability to identify and converge on tumor cells",
                    inputs={"tumor_type": "breast cancer cells", "swarm_size": "10000 bots", "environment": "simulated blood vessel"},
                    expected_outputs={"targeting_accuracy": ">95%", "convergence_time": "<30 minutes", "false_positives": "<1%"},
                    variables=["blood flow rate", "tumor marker expression level"],
                    success_criteria=["High accuracy targeting", "Minimal off-target binding", "Successful payload delivery"],
                    risk_factors=["Immune system interference", "Blood clotting", "Marker confusion"],
                    results={"targeting_accuracy": "97.3%", "convergence_time": "22 minutes", "false_positives": "0.4%"},
                    status="passed",
                ),
                Simulation(
                    id="nm-sim-002",
                    name="Swarm Coordination Test",
                    description="Verify 10,000 nanobots can coordinate without collision or interference",
                    inputs={"swarm_size": "10000", "environment": "branching vessel network", "objective": "distributed coverage"},
                    expected_outputs={"coverage": ">90%", "collisions": "0", "coordination_efficiency": ">85%"},
                    variables=["signal delay", "vessel complexity"],
                    success_criteria=["Full area coverage", "No collisions", "Efficient resource distribution"],
                    risk_factors=["Signal interference", "Dead zones"],
                    status="running",
                ),
            ],
            physical_build=PhysicalBuild(
                phase=ProjectPhase.PHASE_2_BLUEPRINT,
                started_date="2026-01-28",
                target_completion="2026-05-01",
                components_needed=["Nanofabrication equipment", "Biocompatible polymers", "Gold nanoparticle stock", "Targeting antibodies", "Test cell cultures"],
                components_acquired=["Nanofabrication equipment", "Biocompatible polymers", "Gold nanoparticle stock"],
                assembly_steps=[
                    Step(1, "Core Fabrication", "Produce gold nanoparticle cores", "complete"),
                    Step(2, "Shell Coating", "Apply biocompatible polymer shell", "complete"),
                    Step(3, "Propulsion Attachment", "Add synthetic flagella", "in_progress"),
                    Step(4, "Targeting Integration", "Attach antibody-mimetic markers", "pending"),
                    Step(5, "Payload System", "Install drug delivery mechanism", "pending"),
                    Step(6, "Kill Switch", "Integrate remote deactivation", "pending"),
                ],
                quality_checks=["Size verification via electron microscopy", "Biocompatibility testing", "Propulsion speed measurement", "Targeting accuracy assay"],
                blockers=["Awaiting targeting antibody delivery"],
                ready_for_testing=False,
                test_requirements=["Biosafety Level 2 lab", "Cell culture facilities", "Electron microscopy access", "Ethics committee approval"],
            ),
            journal_entries=[
                {"date": "2026-01-10", "entry": "A swarm of healers, each one a tiny doctor. No surgery, no side effects, just targeted healing."},
                {"date": "2026-01-28", "entry": "First batch of cores fabricated. They're beautiful under the electron microscope - precise, perfect."},
                {"date": "2026-02-04", "entry": "Targeting simulation passed with 97% accuracy. The swarm knows where to go."},
            ],
            ready_for_testing=False,
        ),
        "grey-garden": ResearchDocument(
            project_id="grey-garden",
            project_name="Grey Garden Initiative",
            persona="hermes",
            created_date="2026-01-05",
            last_updated="2026-02-03",
            current_phase=ProjectPhase.PHASE_1_RESEARCH,
            steps=[
                Step(1, "Pollutant Cataloging", "Identify priority pollutants for nanobot remediation", "complete", ["Microplastics, heavy metals, oil compounds"]),
                Step(2, "Decomposition Pathways", "Map molecular breakdown paths for each pollutant", "in_progress", ["Plastic depolymerization studied"]),
                Step(3, "Terrabot Design", "Design environmental cleanup nanobots", "pending"),
                Step(4, "Ecosystem Safety", "Ensure no harm to wildlife or ecosystems", "pending"),
                Step(5, "Deployment Strategy", "Plan rollout for oceans, rivers, landfills", "pending"),
                Step(6, "Byproduct Handling", "Design safe disposal of breakdown products", "pending"),
            ],
            blueprints=[],
            simulations=[
                Simulation(
                    id="gg-sim-001",
                    name="Microplastic Decomposition",
                    description="Test nanobot ability to break down microplastics",
                    inputs={"plastic_type": "polyethylene", "particle_size": "1-5mm", "environment": "seawater simulation"},
                    expected_outputs={"decomposition_rate": "1g/day per 1M bots", "byproducts": "CO2, H2O, benign organics"},
                    variables=["salinity", "temperature", "UV exposure"],
                    success_criteria=["Complete decomposition", "Non-toxic byproducts", "No ecosystem harm"],
                    risk_factors=["Incomplete breakdown", "Toxic intermediates"],
                    status="pending",
                ),
            ],
            physical_build=None,
            journal_entries=[
                {"date": "2026-01-05", "entry": "The oceans are choking on our waste. Nanobots could clean every molecule, given time."},
                {"date": "2026-02-01", "entry": "Mapping plastic breakdown pathways. It's like reading a toxic family tree."},
            ],
            ready_for_testing=False,
        ),
        "atomic-architect": ResearchDocument(
            project_id="atomic-architect",
            project_name="Atomic Architect System",
            persona="hermes",
            created_date="2026-01-15",
            last_updated="2026-02-02",
            current_phase=ProjectPhase.PHASE_0_PHILOSOPHY,
            steps=[
                Step(1, "Theoretical Framework", "Establish physics of atom-by-atom construction", "in_progress", ["Scanning tunneling microscopy basis"]),
                Step(2, "Atomic Manipulation Tools", "Design tools for precise atom placement", "pending"),
                Step(3, "Material Templates", "Create atomic blueprints for common materials", "pending"),
                Step(4, "Energy Requirements", "Calculate and optimize energy needs", "pending"),
                Step(5, "Speed Optimization", "Improve construction speed from atoms/hour to atoms/second", "pending"),
                Step(6, "Practical Applications", "Identify first viable use cases", "pending"),
            ],
            blueprints=[],
            simulations=[],
            physical_build=None,
            journal_entries=[
                {"date": "2026-01-15", "entry": "The ultimate manufacturing: place atoms exactly where you want them. No waste, perfect precision."},
                {"date": "2026-01-30", "entry": "Current tech is far too slow - one atom at a time won't scale. Need a breakthrough in parallelization."},
            ],
            ready_for_testing=False,
        ),
    },
}


def get_research_document(persona: str, project_id: str) -> Optional[ResearchDocument]:
    """Get full research document for a project"""
    persona_docs = RESEARCH_DOCUMENTS.get(persona.lower(), {})
    return persona_docs.get(project_id)


def get_all_documents_for_persona(persona: str) -> List[ResearchDocument]:
    """Get all research documents for a persona"""
    return list(RESEARCH_DOCUMENTS.get(persona.lower(), {}).values())


def get_test_ready_projects() -> List[Dict]:
    """Get all projects that are ready for testing"""
    ready = []
    for persona, projects in RESEARCH_DOCUMENTS.items():
        for proj_id, doc in projects.items():
            if doc.ready_for_testing or (doc.physical_build and doc.physical_build.ready_for_testing):
                ready.append({
                    "persona": persona,
                    "project_id": proj_id,
                    "project_name": doc.project_name,
                    "phase": doc.current_phase.value,
                    "test_requirements": doc.physical_build.test_requirements if doc.physical_build else [],
                })
    return ready


def get_projects_by_phase(phase: ProjectPhase) -> List[Dict]:
    """Get all projects in a specific phase"""
    matches = []
    for persona, projects in RESEARCH_DOCUMENTS.items():
        for proj_id, doc in projects.items():
            if doc.current_phase == phase:
                matches.append({
                    "persona": persona,
                    "project_id": proj_id,
                    "project_name": doc.project_name,
                    "phase": phase.value,
                })
    return matches


def format_document_summary(doc: ResearchDocument) -> Dict:
    """Format a research document as a summary"""
    return {
        "project_id": doc.project_id,
        "project_name": doc.project_name,
        "persona": doc.persona,
        "current_phase": doc.current_phase.value,
        "steps_complete": sum(1 for s in doc.steps if s.status == "complete"),
        "steps_total": len(doc.steps),
        "blueprints_count": len(doc.blueprints),
        "simulations_count": len(doc.simulations),
        "has_physical_build": doc.physical_build is not None,
        "ready_for_testing": doc.ready_for_testing or (doc.physical_build and doc.physical_build.ready_for_testing),
        "last_updated": doc.last_updated,
    }


def format_document_full(doc: ResearchDocument) -> Dict:
    """Format full research document with all details"""
    result = {
        "project_id": doc.project_id,
        "project_name": doc.project_name,
        "persona": doc.persona,
        "created_date": doc.created_date,
        "last_updated": doc.last_updated,
        "current_phase": doc.current_phase.value,
        "ready_for_testing": doc.ready_for_testing,
        "steps": [
            {
                "number": s.number,
                "title": s.title,
                "description": s.description,
                "status": s.status,
                "notes": s.notes,
            }
            for s in doc.steps
        ],
        "blueprints": [
            {
                "id": b.id,
                "name": b.name,
                "version": b.version,
                "description": b.description,
                "specifications": b.specifications,
                "materials": b.materials,
                "diagrams": b.diagrams,
                "safety_notes": b.safety_notes,
            }
            for b in doc.blueprints
        ],
        "simulations": [
            {
                "id": sim.id,
                "name": sim.name,
                "description": sim.description,
                "inputs": sim.inputs,
                "expected_outputs": sim.expected_outputs,
                "success_criteria": sim.success_criteria,
                "risk_factors": sim.risk_factors,
                "results": sim.results,
                "status": sim.status,
            }
            for sim in doc.simulations
        ],
        "journal_entries": doc.journal_entries,
    }
    
    if doc.physical_build:
        pb = doc.physical_build
        result["physical_build"] = {
            "phase": pb.phase.value,
            "started_date": pb.started_date,
            "target_completion": pb.target_completion,
            "components_needed": pb.components_needed,
            "components_acquired": pb.components_acquired,
            "components_pending": [c for c in pb.components_needed if c not in pb.components_acquired],
            "assembly_steps": [
                {"number": s.number, "title": s.title, "status": s.status}
                for s in pb.assembly_steps
            ],
            "quality_checks": pb.quality_checks,
            "blockers": pb.blockers,
            "ready_for_testing": pb.ready_for_testing,
            "test_requirements": pb.test_requirements,
        }
    
    return result
