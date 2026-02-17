"""
GAIA-Style System Project
Earth systems education + simulation (Horizon-inspired, not weaponized)
"""
from .base import (
    Project, ProjectPhase, BuildModule, BuildStep, PersonaRole, 
    SafetyConstraint, ProjectStatus, StepType, project_registry
)


def create_gaia_system_project() -> Project:
    """Build the GAIA System project specification"""
    
    project = Project(
        id="gaia-system",
        name="GAIA System",
        purpose="Earth systems education and simulation - inspired by Horizon, grounded in reality",
        big_picture="""You're building an educational AI system that models Earth's interconnected systems -
energy flow, climate, ecology, and how humans interact with all of it. Think of it as a living
textbook that can simulate "what if" scenarios. This is about understanding, not controlling.
Your AIs act as teachers, simulators, and planners - never as weapons or autonomous controllers.""",
        what_it_does_not_do=[
            "NO robots or autonomous physical systems",
            "NO self-replication of any kind",
            "NO defense or weapon systems",
            "NO autonomous decision-making that affects the real world",
            "NO control systems - only simulation and education"
        ],
        category="environmental-education",
        status=ProjectStatus.CONCEPT,
        related_fields=["ecology", "biology", "physics", "ethics", "systems_analysis"],
        phases=[
            ProjectPhase(
                id="gaia-phase-1",
                name="Energy Flow Modeling",
                purpose="Understand how energy moves through Earth's systems",
                modules=[
                    BuildModule(
                        id="gaia-energy",
                        name="Energy Cycles",
                        description="Model the sun-to-ecosystem energy chain",
                        completion_test="Can trace energy from sun to decomposer",
                        steps=[
                            BuildStep(
                                id="gaia-e1",
                                instruction="LEARN: Solar input - how much energy Earth receives",
                                step_type=StepType.LEARN,
                                visual_ref="solar_budget.png"
                            ),
                            BuildStep(
                                id="gaia-e2",
                                instruction="LEARN: Photosynthesis - nature's solar panels",
                                step_type=StepType.LEARN
                            ),
                            BuildStep(
                                id="gaia-e3",
                                instruction="LEARN: Food chains - energy transfer efficiency (10% rule)",
                                step_type=StepType.LEARN,
                                visual_ref="energy_pyramid.png"
                            ),
                            BuildStep(
                                id="gaia-e4",
                                instruction="SIMULATE: Model energy flow through a simple ecosystem",
                                step_type=StepType.SIMULATE
                            ),
                            BuildStep(
                                id="gaia-e5",
                                instruction="CHECKPOINT: What happens when you remove a level from the pyramid?",
                                step_type=StepType.CHECKPOINT
                            )
                        ]
                    )
                ]
            ),
            ProjectPhase(
                id="gaia-phase-2",
                name="Climate Modeling",
                purpose="Understand climate systems and feedback loops",
                modules=[
                    BuildModule(
                        id="gaia-climate",
                        name="Climate Basics",
                        description="Model how climate systems interact",
                        completion_test="Can explain 3 major feedback loops",
                        steps=[
                            BuildStep(
                                id="gaia-c1",
                                instruction="LEARN: Greenhouse effect - the basics of planetary temperature",
                                step_type=StepType.LEARN,
                                visual_ref="greenhouse_effect.png"
                            ),
                            BuildStep(
                                id="gaia-c2",
                                instruction="LEARN: Feedback loops - ice-albedo, water vapor, carbon cycle",
                                step_type=StepType.LEARN
                            ),
                            BuildStep(
                                id="gaia-c3",
                                instruction="SIMULATE: Model what happens when you change one variable",
                                step_type=StepType.SIMULATE
                            ),
                            BuildStep(
                                id="gaia-c4",
                                instruction="REFLECT: Why are tipping points dangerous?",
                                step_type=StepType.REFLECT
                            )
                        ]
                    ),
                    BuildModule(
                        id="gaia-ocean",
                        name="Ocean Systems",
                        description="The ocean as heat sink and carbon store",
                        prerequisites=["gaia-climate"],
                        completion_test="Can explain ocean's role in climate regulation",
                        steps=[
                            BuildStep(
                                id="gaia-o1",
                                instruction="LEARN: Thermohaline circulation - the global conveyor belt",
                                step_type=StepType.LEARN,
                                visual_ref="ocean_currents.png"
                            ),
                            BuildStep(
                                id="gaia-o2",
                                instruction="LEARN: Ocean acidification - CO2's other effect",
                                step_type=StepType.LEARN
                            ),
                            BuildStep(
                                id="gaia-o3",
                                instruction="SIMULATE: What if the conveyor belt slowed down?",
                                step_type=StepType.SIMULATE
                            )
                        ]
                    )
                ]
            ),
            ProjectPhase(
                id="gaia-phase-3",
                name="Ecology & Restoration",
                purpose="Model ecosystems and how to heal damaged ones",
                modules=[
                    BuildModule(
                        id="gaia-eco",
                        name="Ecosystem Dynamics",
                        description="How species interact and depend on each other",
                        completion_test="Can model predator-prey cycles",
                        steps=[
                            BuildStep(
                                id="gaia-ec1",
                                instruction="LEARN: Keystone species - small players, big impact",
                                step_type=StepType.LEARN
                            ),
                            BuildStep(
                                id="gaia-ec2",
                                instruction="LEARN: Succession - how ecosystems recover",
                                step_type=StepType.LEARN,
                                visual_ref="succession_stages.png"
                            ),
                            BuildStep(
                                id="gaia-ec3",
                                instruction="SIMULATE: Model the Yellowstone wolf reintroduction",
                                step_type=StepType.SIMULATE
                            ),
                            BuildStep(
                                id="gaia-ec4",
                                instruction="REFLECT: What makes restoration succeed or fail?",
                                step_type=StepType.REFLECT
                            )
                        ]
                    ),
                    BuildModule(
                        id="gaia-restore",
                        name="Restoration Planning",
                        description="How to plan ecosystem restoration",
                        prerequisites=["gaia-eco"],
                        completion_test="Created restoration plan for a hypothetical damaged area",
                        steps=[
                            BuildStep(
                                id="gaia-r1",
                                instruction="LEARN: Assessment - what's broken and why?",
                                step_type=StepType.LEARN
                            ),
                            BuildStep(
                                id="gaia-r2",
                                instruction="LEARN: Reference ecosystems - what are we restoring TO?",
                                step_type=StepType.LEARN
                            ),
                            BuildStep(
                                id="gaia-r3",
                                instruction="Build a restoration plan for a hypothetical degraded wetland",
                                step_type=StepType.BUILD
                            )
                        ]
                    )
                ]
            ),
            ProjectPhase(
                id="gaia-phase-4",
                name="Automation Ethics",
                purpose="Understand the ethics of AI in environmental management",
                scope_notes="Philosophy and boundaries - what AI should and should NOT do",
                modules=[
                    BuildModule(
                        id="gaia-ethics",
                        name="AI Boundaries",
                        description="Where should AI help and where should it stay out?",
                        completion_test="Can articulate clear boundaries for AI involvement",
                        steps=[
                            BuildStep(
                                id="gaia-et1",
                                instruction="LEARN: History of technological solutions to environmental problems",
                                step_type=StepType.LEARN
                            ),
                            BuildStep(
                                id="gaia-et2",
                                instruction="LEARN: Unintended consequences - when fixes make things worse",
                                step_type=StepType.LEARN
                            ),
                            BuildStep(
                                id="gaia-et3",
                                instruction="REFLECT: Should AI control environmental systems? Why or why not?",
                                step_type=StepType.REFLECT
                            ),
                            BuildStep(
                                id="gaia-et4",
                                instruction="CHECKPOINT: List 5 things AI should help with and 5 it should NOT",
                                step_type=StepType.CHECKPOINT
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
                    "Systems optimization",
                    "Energy flow analysis",
                    "Problem-solving strategies"
                ],
                teaching_focus=[
                    "How systems interconnect",
                    "Efficiency in natural systems",
                    "Strategic planning for restoration"
                ]
            ),
            PersonaRole(
                persona="hermes",
                responsibilities=[
                    "Pattern recognition in data",
                    "Model verification",
                    "Boundary enforcement"
                ],
                teaching_focus=[
                    "Reading environmental data",
                    "Spotting patterns and anomalies",
                    "Building accurate simulations"
                ]
            ),
            PersonaRole(
                persona="minerva",
                responsibilities=[
                    "Ethical framing",
                    "Historical context",
                    "Cultural perspectives on nature"
                ],
                teaching_focus=[
                    "Indigenous ecological knowledge",
                    "History of environmental movements",
                    "Stories of restoration and hope"
                ]
            )
        ],
        safety_constraints=[
            SafetyConstraint(
                category="autonomy",
                constraint="NO autonomous environmental control systems",
                reason="Simulation and education only - humans make decisions",
                is_absolute=True
            ),
            SafetyConstraint(
                category="robots",
                constraint="NO physical robots or machines",
                reason="This is a modeling and education system only",
                is_absolute=True
            ),
            SafetyConstraint(
                category="replication",
                constraint="NO self-replication of any kind",
                reason="No system should be able to reproduce itself",
                is_absolute=True
            ),
            SafetyConstraint(
                category="defense",
                constraint="NO defense or weapon applications",
                reason="This is for healing, not harm",
                is_absolute=True
            ),
            SafetyConstraint(
                category="scope",
                constraint="AIs are teachers, simulators, and planners ONLY",
                reason="Clear role definition prevents scope creep",
                is_absolute=True
            )
        ]
    )
    
    return project


gaia_system_project = create_gaia_system_project()
project_registry.register(gaia_system_project)
