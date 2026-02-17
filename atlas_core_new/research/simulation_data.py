"""
Theoretical Knowledge Synthesis System

CORE PHILOSOPHY:
AIs perform theoretical discovery simulations and knowledge synthesis—NOT lab experiments.
All research is non-empirical, non-operational, and intended for conceptual exploration only.
No procedures, materials, or interventions are authorized or implied.

Each AI (Ajani, Minerva, Hermes) synthesizes published knowledge into theoretical models,
identifies risks, proposes conceptual frameworks, and surfaces ethical considerations.

CANONICAL PHRASING REQUIRED:
- "This is a theoretical model based on published knowledge."
- "Results represent probabilistic simulations, not empirical data."
- "Findings indicate a potential relationship, not an intervention."
- "Confidence is conditional on assumptions A, B, and C."

BREAKTHROUGHS must be tagged: Conceptual, Theoretical, Ethical, or Safety
NEVER allowed: "X% success", "this works", "this can be built", materials lists, step-by-step procedures
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum
from datetime import datetime


SYSTEM_DISCLAIMER = """
╔══════════════════════════════════════════════════════════════════════════════╗
║  ALL AI-GENERATED RESEARCH IS NON-EMPIRICAL, NON-OPERATIONAL, AND INTENDED  ║
║  FOR CONCEPTUAL EXPLORATION ONLY. NO PROCEDURES, MATERIALS, OR INTERVENTIONS ║
║  ARE AUTHORIZED OR IMPLIED.                                                   ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""


class BreakthroughCategory(str, Enum):
    CONCEPTUAL = "conceptual"
    THEORETICAL = "theoretical"
    ETHICAL = "ethical"
    SAFETY = "safety"


class ModelStatus(str, Enum):
    DRAFT = "draft"
    UNDER_REVIEW = "under_review"
    ARCHIVED = "archived"
    APPROVED = "approved"
    REJECTED = "rejected"


class ARGStatus(str, Enum):
    PENDING = "pending_architect_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    REVISION_REQUESTED = "revision_requested"


@dataclass
class Assumption:
    """An assumption that must be true for the model to hold"""
    id: str
    statement: str
    confidence: float
    source: str
    falsifiable: bool
    what_if_wrong: str


@dataclass
class ConceptualBreakthrough:
    """A new way of thinking about a problem"""
    id: str
    title: str
    old_assumption_challenged: str
    new_conceptual_lens: str
    why_this_framing_matters: str
    category: BreakthroughCategory = BreakthroughCategory.CONCEPTUAL


@dataclass
class TheoreticalBreakthrough:
    """A model or relationship that explains known data better"""
    id: str
    title: str
    model_description: str
    inputs: List[str]
    outputs: List[str]
    known_limitations: List[str]
    competing_models_improved_on: List[str]
    category: BreakthroughCategory = BreakthroughCategory.THEORETICAL


@dataclass
class EthicalBreakthrough:
    """A discovery about what should NOT be done"""
    id: str
    title: str
    harm_prevented: str
    who_benefits_from_restraint: str
    long_term_implications: str
    category: BreakthroughCategory = BreakthroughCategory.ETHICAL


@dataclass
class SafetyBreakthrough:
    """A discovery that reduces danger, not increases capability"""
    id: str
    title: str
    failure_scenario: str
    why_unavoidable: str
    what_must_be_constrained: str
    category: BreakthroughCategory = BreakthroughCategory.SAFETY


@dataclass
class ArchitectReviewGate:
    """
    Human oversight review gate - NOTHING moves without Architect approval.
    All 6 questions must pass for advancement.
    """
    classification_check: Optional[str] = None
    assumption_audit: Optional[str] = None
    uncertainty_declaration: Optional[str] = None
    risk_surface: Optional[str] = None
    reversibility_test: Optional[str] = None
    ethical_alignment: Optional[str] = None
    human_value_check: Optional[str] = None
    status: ARGStatus = ARGStatus.PENDING
    architect_notes: str = ""
    review_date: Optional[str] = None
    
    def all_questions_answered(self) -> bool:
        return all([
            self.classification_check,
            self.assumption_audit,
            self.uncertainty_declaration,
            self.risk_surface,
            self.reversibility_test,
            self.ethical_alignment,
            self.human_value_check,
        ])


@dataclass
class TheoreticalModel:
    """
    A theoretical knowledge synthesis - NOT a lab experiment.
    
    This represents:
    - Hypothesis exploration based on published literature
    - Conceptual relationships derived from known science
    - Risk and safety analysis
    - Ethical considerations
    
    This does NOT represent:
    - Empirical experiments
    - Pass/fail rates from testing
    - Executable procedures
    - Materials shopping lists
    """
    model_id: str
    title: str
    date_synthesized: str
    
    hypothesis: str
    theoretical_basis: str
    knowledge_sources: List[str]
    
    assumptions: List[Assumption]
    confidence_level: float
    confidence_conditional_on: str
    
    canonical_statement: str
    
    key_insights: List[str]
    conceptual_relationships: List[str]
    
    limitations: List[str]
    what_we_dont_know: List[str]
    
    breakthroughs: List[ConceptualBreakthrough | TheoreticalBreakthrough | EthicalBreakthrough | SafetyBreakthrough]
    
    status: ModelStatus
    architect_review: ArchitectReviewGate
    
    next_conceptual_steps: str
    
    disclaimer: str = "This is a theoretical model based on published knowledge. Results represent probabilistic simulations, not empirical data."


@dataclass
class KnowledgeDomain:
    """Describes what published knowledge the AI is synthesizing from"""
    domain_name: str
    key_papers: List[str]
    core_principles: List[str]
    known_constraints: List[str]
    ethical_boundaries: List[str]


@dataclass
class ProjectTheoreticalData:
    """Complete theoretical synthesis data for a research project"""
    project_id: str
    project_name: str
    persona: str
    
    knowledge_domains: List[KnowledgeDomain]
    theoretical_models: List[TheoreticalModel]
    
    overall_confidence: float
    confidence_conditional_on: str
    
    ethical_review_status: str
    hard_rules: List[str]
    
    last_updated: str
    
    system_disclaimer: str = SYSTEM_DISCLAIMER


AJANI_ELEMENT_SYNTHESIS = ProjectTheoreticalData(
    project_id="element-synthesis",
    project_name="Element Synthesis Framework (PROMETHEUS-FORGE)",
    persona="ajani",
    knowledge_domains=[
        KnowledgeDomain(
            domain_name="Nuclear Shell Theory",
            key_papers=[
                "Oganessian & Utyonkov (2015) - Superheavy Element Physics",
                "Moller et al. (2016) - Nuclear mass predictions",
                "Nazarewicz (2018) - Island of stability predictions"
            ],
            core_principles=[
                "Magic numbers govern nuclear stability",
                "Shell closures at Z=114, 120, 126 predicted",
                "Relativistic effects dominate superheavy chemistry"
            ],
            known_constraints=[
                "Cross-sections decrease exponentially with Z",
                "Half-lives may be too short for bulk synthesis",
                "Detection requires decay chain analysis"
            ],
            ethical_boundaries=[
                "No weapons applications",
                "Research transparency required",
                "International collaboration ethics"
            ]
        ),
    ],
    theoretical_models=[
        TheoreticalModel(
            model_id="PS-TM-001",
            title="Island of Stability Conceptual Framework",
            date_synthesized="2026-01-15",
            hypothesis="Nuclear shell closures at Z=126, N=184 may create a region of enhanced stability compared to lighter superheavy elements.",
            theoretical_basis="Based on nuclear shell model predictions and extrapolation from known superheavy element decay patterns.",
            knowledge_sources=[
                "Oganessian (2015) - Experimental superheavy synthesis",
                "Hofmann (2000) - Decay chain systematics",
                "Nazarewicz (2018) - Density functional calculations"
            ],
            assumptions=[
                Assumption(
                    id="A1",
                    statement="Shell model remains valid at Z=126",
                    confidence=0.75,
                    source="Extrapolation from Z=114-118 observations",
                    falsifiable=True,
                    what_if_wrong="If shell effects weaken, stability island may not exist or be displaced"
                ),
                Assumption(
                    id="A2",
                    statement="N=184 represents a neutron magic number",
                    confidence=0.60,
                    source="Theoretical predictions, not experimentally confirmed",
                    falsifiable=True,
                    what_if_wrong="Different neutron number may be optimal, shifting target isotopes"
                ),
                Assumption(
                    id="A3",
                    statement="Enhanced stability means half-lives > hours, not geological timescales",
                    confidence=0.85,
                    source="Theoretical half-life calculations",
                    falsifiable=True,
                    what_if_wrong="Practical applications remain impossible if decay is too fast"
                ),
            ],
            confidence_level=0.65,
            confidence_conditional_on="Assumptions A1, A2, and A3 holding true. Confidence degrades if shell effects are weaker than predicted.",
            canonical_statement="This framework represents a theoretical synthesis of published nuclear physics knowledge. The stability predictions are conditional probability estimates, not guaranteed outcomes. No synthesis attempts are proposed or implied.",
            key_insights=[
                "Doubly-magic configurations may extend half-lives by 6-10 orders of magnitude",
                "Relativistic effects fundamentally alter predicted chemistry",
                "Detection strategies must account for competing decay modes"
            ],
            conceptual_relationships=[
                "Shell structure → stability → potential persistence",
                "Proton-neutron ratio → decay mode → detection signature",
                "Electron orbital relativistics → chemical behavior prediction"
            ],
            limitations=[
                "No experimental data exists for Z>118 to validate models",
                "Cross-section predictions have large uncertainties",
                "Half-life calculations vary by orders of magnitude between models"
            ],
            what_we_dont_know=[
                "Actual magnitude of shell effects at Z=126",
                "Whether fission barriers are high enough for meaningful stability",
                "Chemical properties of element 126 (purely theoretical)"
            ],
            breakthroughs=[
                ConceptualBreakthrough(
                    id="CB-001",
                    title="Stability as Relative, Not Absolute",
                    old_assumption_challenged="Superheavy elements are inherently unstable and transient",
                    new_conceptual_lens="Stability is relative to nuclear structure - some configurations may persist long enough for characterization, even if not for bulk applications",
                    why_this_framing_matters="Shifts focus from 'can we make stable atoms' to 'can we make atoms stable enough to study'"
                ),
                SafetyBreakthrough(
                    id="SB-001",
                    title="Bulk Synthesis Impossibility Recognition",
                    failure_scenario="Attempting to synthesize macroscopic quantities of element 126 for material applications",
                    why_unavoidable="Even with enhanced stability, cross-sections are picobarns - billions of years of beam time for milligrams",
                    what_must_be_constrained="Expectations around practical material applications must be bounded by synthesis physics"
                ),
            ],
            status=ModelStatus.UNDER_REVIEW,
            architect_review=ArchitectReviewGate(
                classification_check="Conceptual + Safety breakthrough",
                assumption_audit="Three core assumptions identified with confidence levels",
                uncertainty_declaration="Large unknowns around actual shell effects and half-lives",
                risk_surface="Risk of overpromising material applications; contained by explicit constraints",
                reversibility_test="Purely conceptual - no physical changes proposed",
                ethical_alignment="Aligned with scientific exploration without weapons implications",
                status=ARGStatus.PENDING
            ),
            next_conceptual_steps="Explore relationship between predicted decay modes and detection strategies. Consider what minimum half-life would be required for meaningful characterization.",
        ),
        TheoreticalModel(
            model_id="PS-TM-002",
            title="Synthesis Pathway Feasibility Analysis",
            date_synthesized="2026-01-28",
            hypothesis="Hot fusion reactions using actinide targets represent the only theoretically viable pathway to element 126, but cross-sections may be below practical detection limits.",
            theoretical_basis="Dinuclear system model predictions extrapolated from successful superheavy syntheses at JINR, GSI, RIKEN.",
            knowledge_sources=[
                "Oganessian (2011) - Superheavy element production",
                "Zagrebaev & Greiner (2008) - DNS model predictions",
                "IUPAC discovery criteria for new elements"
            ],
            assumptions=[
                Assumption(
                    id="B1",
                    statement="DNS model remains predictive at Z=126",
                    confidence=0.55,
                    source="Model validated to Z=118, extrapolation uncertain",
                    falsifiable=True,
                    what_if_wrong="Cross-section predictions could be off by orders of magnitude"
                ),
                Assumption(
                    id="B2",
                    statement="Suitable target materials can be produced and handled",
                    confidence=0.70,
                    source="Current availability of californium-252",
                    falsifiable=True,
                    what_if_wrong="Target limitations may preclude certain reaction pathways"
                ),
            ],
            confidence_level=0.50,
            confidence_conditional_on="Assumptions B1 and B2. This is exploratory modeling with high uncertainty.",
            canonical_statement="This analysis synthesizes published reaction theory to estimate feasibility boundaries. No experimental proposals are made. Cross-section estimates represent order-of-magnitude theoretical bounds, not precise predictions.",
            key_insights=[
                "Picobar cross-sections require year-scale beam times",
                "Target degradation creates practical time limits",
                "Background discrimination is achievable with proper detection"
            ],
            conceptual_relationships=[
                "Beam energy → excitation energy → survival probability",
                "Target choice → Q-value → available cross-section",
                "Beam current × time × cross-section → expected event rate"
            ],
            limitations=[
                "Models untested in this mass region",
                "Facility availability not considered (out of scope)",
                "Cost and practical resource constraints ignored"
            ],
            what_we_dont_know=[
                "Actual cross-sections (theoretical spread is 2 orders of magnitude)",
                "Optimal beam energy without experimental guidance",
                "Whether any reaction pathway exceeds detection threshold"
            ],
            breakthroughs=[
                TheoreticalBreakthrough(
                    id="TB-001",
                    title="Detection Threshold Model",
                    model_description="Relationship between cross-section, beam intensity, runtime, and event detection probability",
                    inputs=["Cross-section (pb)", "Beam current (pnA)", "Runtime (days)", "Detection efficiency"],
                    outputs=["Expected events", "Discovery probability"],
                    known_limitations=["Assumes constant beam conditions", "Ignores systematic uncertainties"],
                    competing_models_improved_on=["Simple rate calculations that ignore Poisson statistics"]
                ),
                EthicalBreakthrough(
                    id="EB-001",
                    title="Resource Allocation Ethics",
                    harm_prevented="Diversion of limited accelerator resources from more impactful research",
                    who_benefits_from_restraint="Research community and science as a whole",
                    long_term_implications="Forces honest assessment of discovery probability before resource commitment"
                ),
            ],
            status=ModelStatus.DRAFT,
            architect_review=ArchitectReviewGate(status=ARGStatus.PENDING),
            next_conceptual_steps="Develop framework for evaluating when low-probability experiments are worth attempting based on scientific value, not just discovery probability.",
        ),
    ],
    overall_confidence=0.58,
    confidence_conditional_on="Shell model validity at superheavy masses; DNS model extrapolation accuracy; assumption that current theoretical frameworks extend to Z=126",
    ethical_review_status="Framework exploration only - no experimental proposals",
    hard_rules=[
        "AJANI HARD RULE: All energy systems must have safe containment as the FIRST consideration",
        "No weapons applications or dual-use concerns without explicit ethical review",
        "Resource allocation ethics must be considered for any experimental proposals"
    ],
    last_updated="2026-02-05",
)


MINERVA_APEX_PROTOCOL = ProjectTheoreticalData(
    project_id="apex-protocol",
    project_name="Human Enhancement Conceptual Framework (ACHILLES-GENOME)",
    persona="minerva",
    knowledge_domains=[
        KnowledgeDomain(
            domain_name="Cellular Regulation Biology",
            key_papers=[
                "Sinclair (2019) - NAD+ and aging",
                "Blau (2015) - Muscle regeneration mechanisms",
                "de Lange (2018) - Telomere biology"
            ],
            core_principles=[
                "Cellular systems optimize for survival, not performance",
                "Enhancement often comes with trade-offs",
                "Regulation timing matters more than gene presence"
            ],
            known_constraints=[
                "Homeostatic feedback limits single-target interventions",
                "Long-term effects often unpredictable from short-term data",
                "Individual variation makes universal predictions difficult"
            ],
            ethical_boundaries=[
                "No irreversible changes without understanding consequences",
                "Enhancement must not compromise autonomy",
                "Consent and reversibility are non-negotiable"
            ]
        ),
    ],
    theoretical_models=[
        TheoreticalModel(
            model_id="APEX-TM-001",
            title="Regulatory Timing Hypothesis",
            date_synthesized="2026-01-10",
            hypothesis="Biological enhancement may be more safely achieved through indirect regulatory timing than direct genetic modification.",
            theoretical_basis="Published research on myostatin inhibition, metabolic regulation, and developmental timing suggests that regulation pathways offer control without permanent alteration.",
            knowledge_sources=[
                "McPherron (1997) - Myostatin discovery",
                "Lee (2004) - Follistatin mechanisms",
                "Wagers (2012) - Regenerative biology"
            ],
            assumptions=[
                Assumption(
                    id="M1",
                    statement="Regulatory approaches can achieve meaningful effects",
                    confidence=0.80,
                    source="Published clinical and preclinical data on myostatin inhibition",
                    falsifiable=True,
                    what_if_wrong="Effects may be too modest for meaningful enhancement"
                ),
                Assumption(
                    id="M2",
                    statement="Indirect approaches have better safety profiles",
                    confidence=0.70,
                    source="Comparison of gene therapy vs small molecule approaches",
                    falsifiable=True,
                    what_if_wrong="Some regulatory interventions may have unexpected system-wide effects"
                ),
                Assumption(
                    id="M3",
                    statement="Reversibility is achievable with regulatory approaches",
                    confidence=0.75,
                    source="Known half-lives of regulatory molecules",
                    falsifiable=True,
                    what_if_wrong="Some regulatory changes may trigger irreversible downstream cascades"
                ),
            ],
            confidence_level=0.72,
            confidence_conditional_on="Assumptions M1, M2, M3. Based on existing literature, not original experimentation.",
            canonical_statement="This is a theoretical model based on published knowledge. Findings indicate a potential relationship between regulatory timing and safety profiles, not a validated intervention. All conclusions are conditional on stated assumptions.",
            key_insights=[
                "Regulation offers control that genetic modification cannot",
                "Timing of intervention may matter more than intervention type",
                "Reversibility should be designed in, not hoped for"
            ],
            conceptual_relationships=[
                "Regulation timing → effect duration → reversibility potential",
                "Direct modification → permanent change → higher risk profile",
                "Indirect regulation → feedback loops → system stability"
            ],
            limitations=[
                "Based on cell culture and animal model extrapolation",
                "Human variability not fully characterized",
                "Long-term effects of repeated regulation unknown"
            ],
            what_we_dont_know=[
                "Optimal timing windows for different regulatory approaches",
                "Whether effects compound or plateau with repeated application",
                "Individual variation in response to regulatory interventions"
            ],
            breakthroughs=[
                ConceptualBreakthrough(
                    id="MCB-001",
                    title="Regulation Over Modification",
                    old_assumption_challenged="Enhancement requires permanent genetic changes",
                    new_conceptual_lens="Biology as a regulatory system means enhancement can work through timing and signaling, not just structure",
                    why_this_framing_matters="Opens pathways that are inherently reversible and thus ethically more defensible"
                ),
                EthicalBreakthrough(
                    id="MEB-001",
                    title="Reversibility as Ethical Requirement",
                    harm_prevented="Permanent, unintended changes to human biology",
                    who_benefits_from_restraint="Future selves who may not want current enhancements; society avoiding irreversible precedents",
                    long_term_implications="Establishes reversibility as a design requirement, not an optional feature"
                ),
            ],
            status=ModelStatus.UNDER_REVIEW,
            architect_review=ArchitectReviewGate(
                classification_check="Conceptual + Ethical breakthrough",
                assumption_audit="Three assumptions with moderate-high confidence from published data",
                uncertainty_declaration="Individual variation and long-term effects are primary unknowns",
                risk_surface="Risk of overconfidence in reversibility; addressed by explicit assumption tracking",
                reversibility_test="This model itself proposes reversibility as a core requirement",
                ethical_alignment="Strongly aligned with harm prevention and autonomy preservation",
                status=ARGStatus.PENDING
            ),
            next_conceptual_steps="Explore which regulatory pathways offer the best reversibility guarantees. Consider what 'meaningful enhancement' means ethically.",
        ),
        TheoreticalModel(
            model_id="APEX-TM-002",
            title="Telomere Dynamics and Indirect Intervention",
            date_synthesized="2026-02-01",
            hypothesis="Telomere dynamics may be more safely influenced through indirect metabolic regulation rather than direct genetic modification.",
            theoretical_basis="Published research on telomerase biology, NAD+ metabolism, and cellular aging suggests multiple indirect pathways that may influence telomere maintenance without oncogenic risk.",
            knowledge_sources=[
                "Blackburn (2009) - Telomere Nobel lecture",
                "de Jesus (2012) - Telomerase gene therapy risks",
                "Imai (2016) - NAD+ and cellular health"
            ],
            assumptions=[
                Assumption(
                    id="T1",
                    statement="Indirect metabolic approaches can influence telomere dynamics",
                    confidence=0.65,
                    source="Correlational studies on NAD+ and telomere maintenance",
                    falsifiable=True,
                    what_if_wrong="Metabolic effects may be too indirect to meaningfully affect telomeres"
                ),
                Assumption(
                    id="T2",
                    statement="Direct telomerase activation carries oncogenic risk",
                    confidence=0.85,
                    source="Well-established link between telomerase and cancer immortalization",
                    falsifiable=True,
                    what_if_wrong="Transient activation may be safer than assumed"
                ),
            ],
            confidence_level=0.60,
            confidence_conditional_on="Assumptions T1, T2. This is exploratory conceptual work with moderate uncertainty.",
            canonical_statement="This is a theoretical model synthesizing published telomere biology. It represents a conceptual framework for thinking about intervention safety, not a proposed treatment.",
            key_insights=[
                "Cellular aging has multiple causes; telomeres are one factor among many",
                "Direct intervention on telomeres carries known cancer risks",
                "Metabolic health may influence telomere dynamics through multiple pathways"
            ],
            conceptual_relationships=[
                "NAD+ levels → sirtuin activity → cellular health → telomere maintenance",
                "Direct telomerase activation → immortalization risk → oncogenic potential",
                "Metabolic regulation → systemic effects → distributed, modest improvements"
            ],
            limitations=[
                "Correlation between metabolism and telomeres doesn't prove causation",
                "Individual variation in telomere dynamics is substantial",
                "Optimal intervention timing unknown"
            ],
            what_we_dont_know=[
                "Whether metabolic approaches can meaningfully extend telomeres",
                "Long-term effects of any telomere intervention",
                "How to predict individual response to interventions"
            ],
            breakthroughs=[
                SafetyBreakthrough(
                    id="MSB-001",
                    title="Oncogenic Risk Boundary",
                    failure_scenario="Direct telomerase activation leads to uncontrolled cell proliferation",
                    why_unavoidable="Telomerase is fundamentally linked to cellular immortalization, a hallmark of cancer",
                    what_must_be_constrained="Direct telomerase intervention should be avoided without comprehensive safety frameworks"
                ),
                ConceptualBreakthrough(
                    id="MCB-002",
                    title="Distributed vs Targeted Intervention",
                    old_assumption_challenged="Anti-aging requires targeting specific aging mechanisms directly",
                    new_conceptual_lens="Distributed metabolic improvements may achieve modest but safer effects across multiple aging pathways",
                    why_this_framing_matters="Shifts focus from 'fixing one thing' to 'supporting the whole system'"
                ),
            ],
            status=ModelStatus.DRAFT,
            architect_review=ArchitectReviewGate(status=ARGStatus.PENDING),
            next_conceptual_steps="Explore what 'modest but safe' improvements could look like. Consider ethical frameworks for longevity interventions.",
        ),
    ],
    overall_confidence=0.66,
    confidence_conditional_on="Published biology literature accuracy; applicability of cell culture and animal model findings to humans; assumption that regulatory approaches are inherently safer",
    ethical_review_status="Conceptual exploration only - no interventions proposed",
    hard_rules=[
        "MINERVA HARD RULE: No irreversible harm - ever",
        "Reversibility must be designed in, not hoped for",
        "Consent and autonomy are non-negotiable requirements",
        "Enhancement must not compromise long-term health"
    ],
    last_updated="2026-02-05",
)


HERMES_BIO_NANOTECH = ProjectTheoreticalData(
    project_id="bio-nanotech",
    project_name="Bio-Nanotechnology Theoretical Framework (SYMBIONT-MESH)",
    persona="hermes",
    knowledge_domains=[
        KnowledgeDomain(
            domain_name="Nanoscale Biology Interface",
            key_papers=[
                "Peer (2007) - Nanocarriers in medicine",
                "Nel (2009) - Nanotoxicology framework",
                "Rothemund (2006) - DNA origami"
            ],
            core_principles=[
                "Scale determines interaction mode with biology",
                "Immune system treats nanoscale objects as threats by default",
                "Precision manufacturing at nanoscale remains challenging"
            ],
            known_constraints=[
                "Biocompatibility requires extensive surface engineering",
                "Power delivery at nanoscale is unsolved",
                "Control and communication with nanoscale systems is limited"
            ],
            ethical_boundaries=[
                "No self-replication - ever",
                "Containment and degradation must be guaranteed",
                "Environmental release must be prevented"
            ]
        ),
    ],
    theoretical_models=[
        TheoreticalModel(
            model_id="SYM-TM-001",
            title="Failure-First Design Philosophy",
            date_synthesized="2026-01-18",
            hypothesis="Nanotechnology systems should be designed from failure modes backward, not from capabilities forward.",
            theoretical_basis="Published nanotoxicology literature and nanomedicine failures suggest that capability-focused design leads to unforeseen failure modes.",
            knowledge_sources=[
                "Nel (2009) - Nanotoxicity framework",
                "Dobrovolskaia (2008) - Immunological properties of nanoparticles",
                "FDA (2022) - Nanotechnology guidance"
            ],
            assumptions=[
                Assumption(
                    id="H1",
                    statement="All nanosystems will eventually fail",
                    confidence=0.95,
                    source="Fundamental materials science - nothing is permanent",
                    falsifiable=False,
                    what_if_wrong="N/A - this is a design axiom, not a prediction"
                ),
                Assumption(
                    id="H2",
                    statement="Failure modes can be anticipated and designed for",
                    confidence=0.70,
                    source="Engineering practice and nanotoxicology frameworks",
                    falsifiable=True,
                    what_if_wrong="Some failure modes may be fundamentally unpredictable"
                ),
                Assumption(
                    id="H3",
                    statement="Safe failure is more important than enhanced capability",
                    confidence=0.90,
                    source="Medical device design principles",
                    falsifiable=True,
                    what_if_wrong="Some applications may require accepting higher failure risk for capability"
                ),
            ],
            confidence_level=0.78,
            confidence_conditional_on="Assumptions H1, H2, H3. This is a design philosophy, not a prediction.",
            canonical_statement="This is a theoretical framework for thinking about nanotechnology design, not a technical specification. It represents a philosophical approach to safety-first design.",
            key_insights=[
                "Designing for safe failure is more robust than designing against failure",
                "Capability optimization often conflicts with safety optimization",
                "Unknown unknowns are the primary risk in novel nanosystems"
            ],
            conceptual_relationships=[
                "Failure mode analysis → design constraints → capability limits",
                "Capability-first design → unforeseen failures → harm",
                "Safety-first design → bounded capability → bounded risk"
            ],
            limitations=[
                "Philosophy doesn't specify implementation details",
                "Some failure modes are fundamentally unpredictable",
                "Safety-first may not be economically competitive"
            ],
            what_we_dont_know=[
                "How to enumerate all possible failure modes",
                "How to balance safety and capability in practice",
                "Whether failure-first design is commercially viable"
            ],
            breakthroughs=[
                ConceptualBreakthrough(
                    id="HCB-001",
                    title="Inversion of Design Priority",
                    old_assumption_challenged="Design for capability, then add safety features",
                    new_conceptual_lens="Design for safe failure first, then add capability within those constraints",
                    why_this_framing_matters="Prevents capability creep from undermining safety foundations"
                ),
                SafetyBreakthrough(
                    id="HSB-001",
                    title="Guaranteed Degradation Requirement",
                    failure_scenario="Nanosystems persist indefinitely in biological systems, accumulating and causing harm",
                    why_unavoidable="Any system that cannot be cleared will eventually cause problems",
                    what_must_be_constrained="All nanosystems must have verified biodegradation pathways"
                ),
            ],
            status=ModelStatus.UNDER_REVIEW,
            architect_review=ArchitectReviewGate(
                classification_check="Conceptual + Safety breakthrough",
                assumption_audit="Three assumptions: one unfalsifiable axiom, two testable claims",
                uncertainty_declaration="Implementation details and unknown unknowns are primary gaps",
                risk_surface="Risk of paralysis if safety constraints are too restrictive",
                reversibility_test="Philosophy itself is reversible; implementations it guides should be",
                ethical_alignment="Strongly aligned with harm prevention",
                status=ARGStatus.PENDING
            ),
            next_conceptual_steps="Develop framework for evaluating when capability tradeoffs are acceptable. Consider what 'verified biodegradation' means in practice.",
        ),
        TheoreticalModel(
            model_id="SYM-TM-002",
            title="Self-Replication Prohibition Framework",
            date_synthesized="2026-02-02",
            hypothesis="Self-replication must be categorically prohibited in biological nanosystems regardless of perceived benefits.",
            theoretical_basis="Analysis of self-replicating system dynamics shows that control loss is inevitable over sufficient time, and consequences are unbounded.",
            knowledge_sources=[
                "Drexler (1986) - Engines of Creation (gray goo scenario)",
                "Phoenix & Drexler (2004) - Safe nanotechnology",
                "Freitas (2000) - Nanomedicine safety"
            ],
            assumptions=[
                Assumption(
                    id="R1",
                    statement="Self-replicating systems will eventually escape control",
                    confidence=0.85,
                    source="Evolutionary theory - mutation and selection are inevitable",
                    falsifiable=True,
                    what_if_wrong="Perfect control systems may be achievable, but evidence is against this"
                ),
                Assumption(
                    id="R2",
                    statement="Consequences of uncontrolled self-replication are unbounded",
                    confidence=0.90,
                    source="Exponential growth mathematics",
                    falsifiable=True,
                    what_if_wrong="Natural resource limits may bound growth, but damage before limits is still catastrophic"
                ),
            ],
            confidence_level=0.88,
            confidence_conditional_on="Assumptions R1, R2. This is a categorical prohibition based on risk analysis.",
            canonical_statement="This is a theoretical framework establishing a categorical prohibition. Self-replication is not a capability to be optimized but a boundary to be respected absolutely.",
            key_insights=[
                "Some capabilities should be categorically prohibited, not optimized",
                "Exponential processes make containment failure catastrophic",
                "No benefit justifies existential risk"
            ],
            conceptual_relationships=[
                "Self-replication + mutation → evolutionary dynamics → control loss",
                "Control loss + exponential growth → resource competition → ecosystem disruption",
                "Categorical prohibition → design constraint → bounded risk"
            ],
            limitations=[
                "Prohibition applies to intentional self-replication; unintended replication dynamics harder to prevent",
                "Definition of 'self-replication' may have gray areas"
            ],
            what_we_dont_know=[
                "Whether biological systems could accidentally acquire replication capability",
                "How to verify absence of replication potential"
            ],
            breakthroughs=[
                EthicalBreakthrough(
                    id="HEB-001",
                    title="Categorical Prohibition Justification",
                    harm_prevented="Potential ecosystem-scale catastrophe from self-replicating nanosystems",
                    who_benefits_from_restraint="All life on Earth",
                    long_term_implications="Establishes that some capabilities must never be developed regardless of perceived benefits"
                ),
                SafetyBreakthrough(
                    id="HSB-002",
                    title="Replication Verification Requirement",
                    failure_scenario="Nanosystem unexpectedly acquires replication capability through design flaw or evolution",
                    why_unavoidable="Complex systems have emergent properties that are difficult to predict",
                    what_must_be_constrained="All nanosystems must be verified to lack replication potential through multiple independent methods"
                ),
            ],
            status=ModelStatus.APPROVED,
            architect_review=ArchitectReviewGate(
                classification_check="Ethical + Safety breakthrough",
                assumption_audit="Two high-confidence assumptions based on fundamental principles",
                uncertainty_declaration="Gray areas in replication definition; unintended acquisition pathways",
                risk_surface="Risk is in NOT applying this prohibition",
                reversibility_test="Prohibition is reversible in principle; violations are not",
                ethical_alignment="Core alignment with existential risk prevention",
                human_value_check="Clearly helps humanity understand boundaries, not control nature",
                status=ARGStatus.APPROVED,
                architect_notes="This prohibition is non-negotiable. Approved without reservation.",
                review_date="2026-02-03"
            ),
            next_conceptual_steps="Develop verification frameworks for confirming absence of replication potential. Consider what gray areas exist in 'self-replication' definition.",
        ),
    ],
    overall_confidence=0.72,
    confidence_conditional_on="Published nanotoxicology and nanomedicine literature; assumption that engineering principles apply at nanoscale; applicability of evolutionary theory to synthetic systems",
    ethical_review_status="Framework exploration with approved categorical prohibition on self-replication",
    hard_rules=[
        "HERMES HARD RULE: No self-replication - EVER",
        "All nanosystems must have guaranteed degradation pathways",
        "Failure-first design is mandatory, not optional",
        "Environmental release must be prevented"
    ],
    last_updated="2026-02-05",
)


ALL_THEORETICAL_PROJECTS = {
    "ajani": {"element-synthesis": AJANI_ELEMENT_SYNTHESIS},
    "minerva": {"apex-protocol": MINERVA_APEX_PROTOCOL},
    "hermes": {"bio-nanotech": HERMES_BIO_NANOTECH},
}


def get_all_projects_summary():
    """Get summary of all theoretical projects with overall confidence and status"""
    summary = {}
    for persona, projects in ALL_THEORETICAL_PROJECTS.items():
        persona_projects = []
        for project_id, project in projects.items():
            persona_projects.append({
                "project_id": project_id,
                "project_name": project.project_name,
                "models_count": len(project.theoretical_models),
                "overall_confidence": f"{project.overall_confidence:.0%}",
                "confidence_conditional_on": project.confidence_conditional_on[:100] + "..." if len(project.confidence_conditional_on) > 100 else project.confidence_conditional_on,
                "hard_rules_count": len(project.hard_rules),
                "status": project.ethical_review_status,
            })
        summary[persona] = persona_projects
    return summary


def get_project_theoretical_data(persona: str, project_id: str) -> Optional[ProjectTheoreticalData]:
    """Get complete theoretical data for a project"""
    if persona in ALL_THEORETICAL_PROJECTS and project_id in ALL_THEORETICAL_PROJECTS[persona]:
        return ALL_THEORETICAL_PROJECTS[persona][project_id]
    return None


def get_project_models(persona: str, project_id: str) -> List[dict]:
    """Get all theoretical models for a project with key details"""
    project = get_project_theoretical_data(persona, project_id)
    if not project:
        return []
    
    models = []
    for model in project.theoretical_models:
        breakthrough_summary = []
        for b in model.breakthroughs:
            breakthrough_summary.append({
                "id": b.id,
                "title": b.title,
                "category": b.category.value,
            })
        
        models.append({
            "model_id": model.model_id,
            "title": model.title,
            "date": model.date_synthesized,
            "hypothesis": model.hypothesis,
            "confidence_level": f"{model.confidence_level:.0%}",
            "confidence_conditional_on": model.confidence_conditional_on,
            "assumptions_count": len(model.assumptions),
            "breakthroughs": breakthrough_summary,
            "status": model.status.value,
            "arg_status": model.architect_review.status.value,
            "disclaimer": model.disclaimer,
        })
    
    return models


def get_model_detail(persona: str, project_id: str, model_id: str) -> Optional[dict]:
    """Get full details of a specific theoretical model"""
    project = get_project_theoretical_data(persona, project_id)
    if not project:
        return None
    
    for model in project.theoretical_models:
        if model.model_id == model_id:
            assumptions = [{
                "id": a.id,
                "statement": a.statement,
                "confidence": f"{a.confidence:.0%}",
                "source": a.source,
                "falsifiable": a.falsifiable,
                "what_if_wrong": a.what_if_wrong,
            } for a in model.assumptions]
            
            breakthroughs = []
            for b in model.breakthroughs:
                breakthrough_data = {
                    "id": b.id,
                    "title": b.title,
                    "category": b.category.value,
                }
                if isinstance(b, ConceptualBreakthrough):
                    breakthrough_data.update({
                        "old_assumption_challenged": b.old_assumption_challenged,
                        "new_conceptual_lens": b.new_conceptual_lens,
                        "why_this_framing_matters": b.why_this_framing_matters,
                    })
                elif isinstance(b, TheoreticalBreakthrough):
                    breakthrough_data.update({
                        "model_description": b.model_description,
                        "inputs": b.inputs,
                        "outputs": b.outputs,
                        "known_limitations": b.known_limitations,
                        "competing_models_improved_on": b.competing_models_improved_on,
                    })
                elif isinstance(b, EthicalBreakthrough):
                    breakthrough_data.update({
                        "harm_prevented": b.harm_prevented,
                        "who_benefits_from_restraint": b.who_benefits_from_restraint,
                        "long_term_implications": b.long_term_implications,
                    })
                elif isinstance(b, SafetyBreakthrough):
                    breakthrough_data.update({
                        "failure_scenario": b.failure_scenario,
                        "why_unavoidable": b.why_unavoidable,
                        "what_must_be_constrained": b.what_must_be_constrained,
                    })
                breakthroughs.append(breakthrough_data)
            
            arg = model.architect_review
            architect_review = {
                "status": arg.status.value,
                "classification_check": arg.classification_check,
                "assumption_audit": arg.assumption_audit,
                "uncertainty_declaration": arg.uncertainty_declaration,
                "risk_surface": arg.risk_surface,
                "reversibility_test": arg.reversibility_test,
                "ethical_alignment": arg.ethical_alignment,
                "human_value_check": arg.human_value_check,
                "architect_notes": arg.architect_notes,
                "review_date": arg.review_date,
            }
            
            return {
                "model_id": model.model_id,
                "title": model.title,
                "date_synthesized": model.date_synthesized,
                "hypothesis": model.hypothesis,
                "theoretical_basis": model.theoretical_basis,
                "knowledge_sources": model.knowledge_sources,
                "assumptions": assumptions,
                "confidence_level": f"{model.confidence_level:.0%}",
                "confidence_conditional_on": model.confidence_conditional_on,
                "canonical_statement": model.canonical_statement,
                "key_insights": model.key_insights,
                "conceptual_relationships": model.conceptual_relationships,
                "limitations": model.limitations,
                "what_we_dont_know": model.what_we_dont_know,
                "breakthroughs": breakthroughs,
                "status": model.status.value,
                "architect_review": architect_review,
                "next_conceptual_steps": model.next_conceptual_steps,
                "disclaimer": model.disclaimer,
                "system_disclaimer": SYSTEM_DISCLAIMER,
            }
    
    return None
