"""
Mini Oxygen Converter Project
Personal emergency oxygen / medical support concept (hockey-puck size)
"""
from .base import (
    Project, ProjectPhase, BuildModule, BuildStep, PersonaRole, 
    SafetyConstraint, ProjectStatus, StepType, project_registry
)


def create_oxygen_converter_project() -> Project:
    """Build the Mini Oxygen Converter project specification"""
    
    project = Project(
        id="oxygen-converter",
        name="Mini Oxygen Converter",
        purpose="Personal emergency oxygen - educational engineering prototype",
        big_picture="""You're building a hockey-puck sized device that separates oxygen from air.
This is NOT a medical device - it's an educational prototype to understand air separation,
filtration, and energy efficiency. The goal is 5-7 hours of runtime on minimal power.
Think of it as learning how oxygen concentrators work at a fundamental level.""",
        what_it_does_not_do=[
            "This is NOT a certified medical device",
            "This should NOT be relied on for life-critical situations",
            "This does NOT replace professional medical equipment",
            "This is NOT for sale or distribution without proper certification"
        ],
        category="life-support-research",
        status=ProjectStatus.CONCEPT,
        related_fields=["engineering", "biology", "physics", "electronics"],
        phases=[
            ProjectPhase(
                id="oc-phase-1",
                name="Fundamentals",
                purpose="Understand the science before building anything",
                modules=[
                    BuildModule(
                        id="oc-science",
                        name="Air Separation Science",
                        description="Learn how we separate gases from air",
                        completion_test="Can explain 3 different air separation methods",
                        steps=[
                            BuildStep(
                                id="oc-s1",
                                instruction="LEARN: Air is 78% nitrogen, 21% oxygen, 1% other. Why does this matter?",
                                step_type=StepType.LEARN
                            ),
                            BuildStep(
                                id="oc-s2",
                                instruction="LEARN: Pressure Swing Adsorption (PSA) - how zeolites grab nitrogen",
                                step_type=StepType.LEARN,
                                visual_ref="psa_process.png"
                            ),
                            BuildStep(
                                id="oc-s3",
                                instruction="LEARN: Membrane separation - different gases pass through at different rates",
                                step_type=StepType.LEARN,
                                visual_ref="membrane_separation.png"
                            ),
                            BuildStep(
                                id="oc-s4",
                                instruction="CHECKPOINT: If you had to choose one method for a small, low-power device, which and why?",
                                step_type=StepType.CHECKPOINT,
                                checkpoint_question="What's the most energy-efficient method for small scale?"
                            )
                        ]
                    ),
                    BuildModule(
                        id="oc-power",
                        name="Power Requirements",
                        description="Calculate what power you need for 5-7 hour runtime",
                        prerequisites=["oc-science"],
                        completion_test="Power budget calculated with safety margin",
                        steps=[
                            BuildStep(
                                id="oc-p1",
                                instruction="LEARN: How much power does a small compressor draw?",
                                step_type=StepType.LEARN
                            ),
                            BuildStep(
                                id="oc-p2",
                                instruction="Calculate: Battery capacity needed for 7 hours at X watts",
                                step_type=StepType.LEARN
                            ),
                            BuildStep(
                                id="oc-p3",
                                instruction="SIMULATE: Trade-off between output rate and battery life",
                                step_type=StepType.SIMULATE
                            )
                        ]
                    )
                ]
            ),
            ProjectPhase(
                id="oc-phase-2",
                name="Prototype Design",
                purpose="Design the hockey-puck form factor",
                scope_notes="Paper prototyping and simulation before any physical build",
                modules=[
                    BuildModule(
                        id="oc-layout",
                        name="Component Layout",
                        description="Fit everything into a small, portable package",
                        completion_test="Layout diagram complete with dimensions",
                        steps=[
                            BuildStep(
                                id="oc-l1",
                                instruction="List all components needed: pump, filter, membrane/zeolite, battery, controls",
                                step_type=StepType.BUILD
                            ),
                            BuildStep(
                                id="oc-l2",
                                instruction="Measure each component's size",
                                step_type=StepType.BUILD
                            ),
                            BuildStep(
                                id="oc-l3",
                                instruction="SIMULATE: Arrange components in hockey-puck footprint (75mm diameter, 25mm height)",
                                step_type=StepType.SIMULATE,
                                visual_ref="puck_layout.png"
                            ),
                            BuildStep(
                                id="oc-l4",
                                instruction="CHECKPOINT: Does everything fit? What's the tightest constraint?",
                                step_type=StepType.CHECKPOINT
                            )
                        ]
                    )
                ]
            ),
            ProjectPhase(
                id="oc-phase-3",
                name="Boundaries and Ethics",
                purpose="Understand what this project is NOT",
                scope_notes="Critical legal and ethical learning",
                modules=[
                    BuildModule(
                        id="oc-legal",
                        name="Medical Device Boundaries",
                        description="Learn what separates educational prototypes from medical devices",
                        completion_test="Can list 5 requirements for medical device certification",
                        steps=[
                            BuildStep(
                                id="oc-lg1",
                                instruction="LEARN: FDA classification of oxygen devices",
                                step_type=StepType.LEARN
                            ),
                            BuildStep(
                                id="oc-lg2",
                                instruction="LEARN: What testing is required before human use",
                                step_type=StepType.LEARN
                            ),
                            BuildStep(
                                id="oc-lg3",
                                instruction="REFLECT: Why do these regulations exist? Who are they protecting?",
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
                    "Energy efficiency optimization",
                    "Runtime calculations",
                    "Power system design"
                ],
                teaching_focus=[
                    "How compressors work",
                    "Battery chemistry basics",
                    "Power budgeting"
                ]
            ),
            PersonaRole(
                persona="hermes",
                responsibilities=[
                    "Safety limit enforcement",
                    "Legal boundary flagging",
                    "Failure mode analysis"
                ],
                teaching_focus=[
                    "Gas laws and pressure safety",
                    "What makes something a medical device legally",
                    "Pattern recognition in device failures"
                ]
            ),
            PersonaRole(
                persona="minerva",
                responsibilities=[
                    "Ethical framing",
                    "Historical context of oxygen therapy",
                    "Access and equity considerations"
                ],
                teaching_focus=[
                    "History of respiratory medicine",
                    "Why oxygen access matters globally",
                    "Ethics of medical device development"
                ]
            )
        ],
        safety_constraints=[
            SafetyConstraint(
                category="medical",
                constraint="This is NOT a medical device - never use on humans",
                reason="Medical devices require FDA approval and clinical testing",
                is_absolute=True
            ),
            SafetyConstraint(
                category="pressure",
                constraint="Maximum operating pressure: 15 PSI",
                reason="Higher pressures require specialized containment",
                is_absolute=True
            ),
            SafetyConstraint(
                category="labeling",
                constraint="All prototypes must be labeled 'EDUCATIONAL PROTOTYPE - NOT FOR HUMAN USE'",
                reason="Prevents accidental misuse",
                is_absolute=True
            )
        ]
    )
    
    return project


oxygen_converter_project = create_oxygen_converter_project()
project_registry.register(oxygen_converter_project)
