"""
MIMIC CELL / Techno-Organic Cell Project
Research concept - signal mimicry, not biological replacement
"""
from .base import (
    Project, ProjectPhase, BuildModule, BuildStep, PersonaRole, 
    SafetyConstraint, ProjectStatus, StepType, project_registry
)


def create_mimic_cell_project() -> Project:
    """Build the MIMIC Cell project specification"""
    
    project = Project(
        id="mimic-cell",
        name="MIMIC Cell",
        purpose="Research concept - mimicking biological signaling, not creating life",
        big_picture="""You're researching how to create materials that can mimic biological signals
WITHOUT being alive. Think of it like a prosthetic that communicates with tissue, not replaces it.
This is gel membranes, electrical signals, and scaffold materials - not DNA, not replication,
not anything that could grow or reproduce. You are mimicking FUNCTION, not LIFE.""",
        what_it_does_not_do=[
            "NO DNA - this is not genetic engineering",
            "NO replication - nothing grows or reproduces",
            "NO autonomy - materials don't make decisions",
            "NO implantation - simulation and materials research only",
            "NO biological cells - only synthetic mimics"
        ],
        category="materials-research",
        status=ProjectStatus.CONCEPT,
        related_fields=["biology", "engineering", "electronics", "biomimicry"],
        phases=[
            ProjectPhase(
                id="mc-phase-1",
                name="Signal Fundamentals",
                purpose="Understand how biological signaling works",
                modules=[
                    BuildModule(
                        id="mc-signals",
                        name="Biological Signal Types",
                        description="Learn the different ways cells communicate",
                        completion_test="Can explain electrical, chemical, and mechanical signaling",
                        steps=[
                            BuildStep(
                                id="mc-s1",
                                instruction="LEARN: Electrical signals - how neurons fire",
                                step_type=StepType.LEARN,
                                visual_ref="neuron_signal.png"
                            ),
                            BuildStep(
                                id="mc-s2",
                                instruction="LEARN: Chemical signals - hormones and neurotransmitters",
                                step_type=StepType.LEARN
                            ),
                            BuildStep(
                                id="mc-s3",
                                instruction="LEARN: Mechanical signals - pressure and stretch receptors",
                                step_type=StepType.LEARN
                            ),
                            BuildStep(
                                id="mc-s4",
                                instruction="CHECKPOINT: Which signal type is easiest to mimic with electronics?",
                                step_type=StepType.CHECKPOINT,
                                checkpoint_question="Why is electrical signaling the starting point for mimicry?"
                            )
                        ]
                    )
                ]
            ),
            ProjectPhase(
                id="mc-phase-2",
                name="Gel Membrane Research",
                purpose="Study materials that can conduct and respond",
                scope_notes="Pure materials science - no biological components",
                modules=[
                    BuildModule(
                        id="mc-gels",
                        name="Conductive Gels",
                        description="Explore gel materials that can carry electrical signals",
                        completion_test="Created test gel sample, measured conductivity",
                        steps=[
                            BuildStep(
                                id="mc-g1",
                                instruction="LEARN: What makes a gel conductive?",
                                step_type=StepType.LEARN
                            ),
                            BuildStep(
                                id="mc-g2",
                                instruction="Research hydrogel compositions - water content, ion concentration",
                                step_type=StepType.LEARN
                            ),
                            BuildStep(
                                id="mc-g3",
                                instruction="SIMULATE: Model signal propagation through gel material",
                                step_type=StepType.SIMULATE
                            ),
                            BuildStep(
                                id="mc-g4",
                                instruction="Build test gel sample (if materials available)",
                                step_type=StepType.BUILD,
                                parts_needed=["hydrogel_powder", "distilled_water", "salt", "mixing_equipment"]
                            )
                        ]
                    ),
                    BuildModule(
                        id="mc-scaffolds",
                        name="Scaffold Structures",
                        description="Learn about 3D structures for tissue support",
                        prerequisites=["mc-gels"],
                        completion_test="Designed scaffold structure on paper",
                        steps=[
                            BuildStep(
                                id="mc-sc1",
                                instruction="LEARN: What is a tissue scaffold and why does shape matter?",
                                step_type=StepType.LEARN,
                                visual_ref="scaffold_types.png"
                            ),
                            BuildStep(
                                id="mc-sc2",
                                instruction="SIMULATE: Model how cells would grow on different scaffold shapes",
                                step_type=StepType.SIMULATE
                            ),
                            BuildStep(
                                id="mc-sc3",
                                instruction="Design a scaffold pattern optimized for signal propagation",
                                step_type=StepType.BUILD
                            )
                        ]
                    )
                ]
            ),
            ProjectPhase(
                id="mc-phase-3",
                name="Swarm Coordination (Abstract)",
                purpose="Model how multiple mimic cells could coordinate",
                scope_notes="Pure simulation - abstract algorithms, not physical systems",
                simulation_only=True,
                modules=[
                    BuildModule(
                        id="mc-swarm",
                        name="Coordination Logic",
                        description="How would synthetic cells communicate without central control?",
                        completion_test="Working simulation of local-rule coordination",
                        steps=[
                            BuildStep(
                                id="mc-sw1",
                                instruction="LEARN: Swarm intelligence in nature - ants, bees, slime molds",
                                step_type=StepType.LEARN
                            ),
                            BuildStep(
                                id="mc-sw2",
                                instruction="SIMULATE: Model local-only rules that create group behavior",
                                step_type=StepType.SIMULATE
                            ),
                            BuildStep(
                                id="mc-sw3",
                                instruction="REFLECT: What safeguards prevent unwanted emergent behavior?",
                                step_type=StepType.REFLECT
                            )
                        ]
                    )
                ]
            )
        ],
        persona_roles=[
            PersonaRole(
                persona="ajani",
                responsibilities=[
                    "Materials engineering",
                    "Signal transmission optimization",
                    "Energy efficiency"
                ],
                teaching_focus=[
                    "How to measure conductivity",
                    "Material selection for biocompatibility",
                    "Power requirements for signal transmission"
                ]
            ),
            PersonaRole(
                persona="hermes",
                responsibilities=[
                    "Safety boundary enforcement",
                    "Pattern analysis in signaling",
                    "Failure mode identification"
                ],
                teaching_focus=[
                    "Why certain boundaries are non-negotiable",
                    "How to recognize when you're crossing into biology",
                    "Verification methods for synthetic systems"
                ]
            ),
            PersonaRole(
                persona="minerva",
                responsibilities=[
                    "Ethical framing",
                    "Historical context of prosthetics and tissue engineering",
                    "Cultural implications of human augmentation"
                ],
                teaching_focus=[
                    "History of artificial organs",
                    "Ethics of human-machine interfaces",
                    "Stories of healing and restoration"
                ]
            )
        ],
        safety_constraints=[
            SafetyConstraint(
                category="biological",
                constraint="NO DNA or genetic material",
                reason="This is materials research, not genetic engineering",
                is_absolute=True
            ),
            SafetyConstraint(
                category="replication",
                constraint="NO self-replication capability",
                reason="Nothing created should be able to reproduce",
                is_absolute=True
            ),
            SafetyConstraint(
                category="autonomy",
                constraint="NO autonomous decision-making",
                reason="Materials respond to stimuli, they don't decide",
                is_absolute=True
            ),
            SafetyConstraint(
                category="implantation",
                constraint="NO human or animal implantation",
                reason="This is bench research only",
                is_absolute=True
            ),
            SafetyConstraint(
                category="scope",
                constraint="Mimicking FUNCTION only, never creating LIFE",
                reason="Clear boundary between engineering and biology",
                is_absolute=True
            )
        ]
    )
    
    return project


mimic_cell_project = create_mimic_cell_project()
project_registry.register(mimic_cell_project)
