"""
ATLAS Power Cell Project
Safe, modular energy generation - scale later
"""
from .base import (
    Project, ProjectPhase, BuildModule, BuildStep, PersonaRole, 
    SafetyConstraint, ProjectStatus, StepType, project_registry
)


def create_power_cell_project() -> Project:
    """Build the complete ATLAS Power Cell project specification"""
    
    project = Project(
        id="power-cell",
        name="ATLAS Power Cell",
        purpose="Safe, modular energy generation that can scale over time",
        big_picture="""You're building a small, cartridge-style power cell that generates electricity safely.
Think of it like building blocks - start tiny, prove it works, then stack more cells to get more power.
This isn't about making a battery to power your house right now. It's about understanding how energy
flows, how to contain it safely, and how to scale up when you're ready.""",
        what_it_does_not_do=[
            "This is NOT a replacement for commercial batteries yet",
            "This will NOT power your house in Phase 1-3",
            "This is NOT ready for medical or life-critical applications",
            "This does NOT skip safety testing between phases"
        ],
        category="energy",
        status=ProjectStatus.CONCEPT,
        related_fields=["engineering", "energy_systems", "electronics", "physics"],
        phases=[
            create_phase_1_prototype(),
            create_phase_2_stacking(),
            create_phase_3_generator(),
            create_phase_4_home_scale()
        ],
        persona_roles=[
            PersonaRole(
                persona="ajani",
                responsibilities=[
                    "Energy flow optimization",
                    "Efficiency calculations",
                    "Scaling logic and planning",
                    "Power management strategies"
                ],
                teaching_focus=[
                    "How electricity moves through conductors",
                    "Why series vs parallel matters",
                    "Calculating power needs before building",
                    "When to push forward vs when to stop and test"
                ]
            ),
            PersonaRole(
                persona="hermes",
                responsibilities=[
                    "Safety limit validation",
                    "Voltage and current checks",
                    "Failure mode analysis",
                    "Circuit integrity verification"
                ],
                teaching_focus=[
                    "What happens when things go wrong",
                    "How to read voltage/current safely",
                    "Pattern recognition in electrical failures",
                    "Building in safety margins"
                ]
            ),
            PersonaRole(
                persona="minerva",
                responsibilities=[
                    "Design meaning and context",
                    "Sustainability framing",
                    "Historical context of energy innovation",
                    "Ethical considerations of power access"
                ],
                teaching_focus=[
                    "Why energy independence matters",
                    "The story of batteries through history",
                    "Environmental impact of different energy choices",
                    "Who benefits when people can generate their own power"
                ]
            )
        ],
        safety_constraints=[
            SafetyConstraint(
                category="voltage",
                constraint="Phase 1 cells must not exceed 5V",
                reason="Low voltage allows safe handling and testing without shock risk",
                is_absolute=True
            ),
            SafetyConstraint(
                category="materials",
                constraint="Gel electrolyte only - no liquid acids",
                reason="Gel cannot spill, splash, or leak dangerously",
                is_absolute=True
            ),
            SafetyConstraint(
                category="testing",
                constraint="Every module requires checkpoint test before proceeding",
                reason="Catching problems early prevents bigger failures later",
                is_absolute=True
            ),
            SafetyConstraint(
                category="scaling",
                constraint="No stacking until single cell is proven stable",
                reason="Multiplying an unstable design multiplies the danger",
                is_absolute=True
            ),
            SafetyConstraint(
                category="simulation",
                constraint="Phase 4 (home scale) is simulation only until proven",
                reason="Home-scale energy requires professional verification",
                is_absolute=True
            )
        ]
    )
    
    return project


def create_phase_1_prototype() -> ProjectPhase:
    """Phase 1: Small cartridge-style power cell"""
    return ProjectPhase(
        id="phase-1",
        name="Prototype Cell",
        purpose="Build and validate a single, small, safe power cell",
        scope_notes="Low voltage, safe testing. This is about learning, not power output.",
        modules=[
            BuildModule(
                id="p1-housing",
                name="Cell Housing",
                description="Build the outer container that holds everything safely",
                completion_test="Housing is sealed, no gaps, can withstand gentle pressure",
                steps=[
                    BuildStep(
                        id="p1-h1",
                        instruction="Gather materials: small plastic or acrylic tube (50mm length), two end caps",
                        step_type=StepType.BUILD,
                        parts_needed=["tube_50mm", "end_cap_x2"]
                    ),
                    BuildStep(
                        id="p1-h2",
                        instruction="Drill small hole in each end cap for conductor wire",
                        step_type=StepType.BUILD,
                        visual_ref="housing_drill_diagram.png",
                        parts_needed=["drill_bit_2mm"]
                    ),
                    BuildStep(
                        id="p1-h3",
                        instruction="Sand edges of holes smooth - no sharp edges that could cut wire insulation",
                        step_type=StepType.BUILD
                    ),
                    BuildStep(
                        id="p1-h4",
                        instruction="CHECKPOINT: Hold housing up to light. Any cracks? Any rough spots inside?",
                        step_type=StepType.CHECKPOINT,
                        checkpoint_question="Can you see any light through the walls or cracks?",
                        failure_scenario="Cracks mean electrolyte leak. Start over with new tube."
                    )
                ]
            ),
            BuildModule(
                id="p1-conductors",
                name="Copper Conductors",
                description="Prepare the metal parts that carry electricity",
                prerequisites=["p1-housing"],
                completion_test="Two conductors ready, sized to fit housing, ends stripped and clean",
                steps=[
                    BuildStep(
                        id="p1-c1",
                        instruction="Cut two copper strips to fit inside housing (45mm each)",
                        step_type=StepType.BUILD,
                        parts_needed=["copper_strip", "cutting_tool"]
                    ),
                    BuildStep(
                        id="p1-c2",
                        instruction="Clean copper with fine sandpaper until shiny - oxidation blocks current",
                        step_type=StepType.BUILD,
                        parts_needed=["sandpaper_fine"]
                    ),
                    BuildStep(
                        id="p1-c3",
                        instruction="Attach lead wires to each copper strip - solder or crimp connection",
                        step_type=StepType.BUILD,
                        parts_needed=["lead_wire_x2", "solder_or_crimps"]
                    ),
                    BuildStep(
                        id="p1-c4",
                        instruction="CHECKPOINT: Tug each wire gently. Does the connection hold?",
                        step_type=StepType.CHECKPOINT,
                        checkpoint_question="Did either connection come loose?",
                        failure_scenario="Loose connection = no power flow. Re-solder or re-crimp."
                    )
                ]
            ),
            BuildModule(
                id="p1-electrolyte",
                name="Gel Electrolyte",
                description="Prepare the gel that allows ions to move between conductors",
                prerequisites=["p1-housing", "p1-conductors"],
                completion_test="Gel is consistent, no lumps, fills housing without overflow",
                steps=[
                    BuildStep(
                        id="p1-e1",
                        instruction="Mix electrolyte gel according to formula (see recipe card)",
                        step_type=StepType.BUILD,
                        parts_needed=["electrolyte_powder", "distilled_water", "mixing_container"]
                    ),
                    BuildStep(
                        id="p1-e2",
                        instruction="Let gel set for 10 minutes - too thin and it won't hold, too thick and ions can't move",
                        step_type=StepType.BUILD
                    ),
                    BuildStep(
                        id="p1-e3",
                        instruction="LEARN: Why gel instead of liquid?",
                        step_type=StepType.LEARN,
                        visual_ref="gel_vs_liquid_safety.png"
                    ),
                    BuildStep(
                        id="p1-e4",
                        instruction="CHECKPOINT: Gel should hold its shape when tilted but still be soft",
                        step_type=StepType.CHECKPOINT,
                        checkpoint_question="Does the gel wobble or run like water?",
                        failure_scenario="Too runny = add more powder. Too stiff = won't conduct well."
                    )
                ]
            ),
            BuildModule(
                id="p1-assembly",
                name="Cell Assembly",
                description="Put all components together into working cell",
                prerequisites=["p1-housing", "p1-conductors", "p1-electrolyte"],
                completion_test="Cell produces measurable voltage, holds stable for 5 minutes",
                steps=[
                    BuildStep(
                        id="p1-a1",
                        instruction="Thread lead wire through one end cap, place copper strip inside",
                        step_type=StepType.BUILD
                    ),
                    BuildStep(
                        id="p1-a2",
                        instruction="Carefully fill housing with gel electrolyte - leave 5mm gap at top",
                        step_type=StepType.BUILD
                    ),
                    BuildStep(
                        id="p1-a3",
                        instruction="Insert second copper strip, thread wire through second end cap",
                        step_type=StepType.BUILD
                    ),
                    BuildStep(
                        id="p1-a4",
                        instruction="Seal end caps - ensure wires have strain relief",
                        step_type=StepType.BUILD,
                        parts_needed=["sealant", "strain_relief"]
                    ),
                    BuildStep(
                        id="p1-a5",
                        instruction="TEST: Use multimeter to measure voltage across leads",
                        step_type=StepType.TEST,
                        parts_needed=["multimeter"],
                        checkpoint_question="What voltage do you read?",
                        failure_scenario="Zero voltage = check connections. Negative = swap leads."
                    ),
                    BuildStep(
                        id="p1-a6",
                        instruction="REFLECT: Explain what you built. Where would it fail? How would you improve it?",
                        step_type=StepType.REFLECT
                    )
                ]
            )
        ]
    )


def create_phase_2_stacking() -> ProjectPhase:
    """Phase 2: Multiple cells in series/parallel"""
    return ProjectPhase(
        id="phase-2",
        name="Cell Stacking",
        purpose="Combine multiple cells to increase voltage and current safely",
        scope_notes="Only proceed after Phase 1 cell is proven stable for 24+ hours",
        modules=[
            BuildModule(
                id="p2-learn",
                name="Series vs Parallel",
                description="Understand why connection type changes the output",
                completion_test="Can explain the difference and predict output",
                steps=[
                    BuildStep(
                        id="p2-l1",
                        instruction="LEARN: Series connection - cells in a row. Voltage adds, current stays same.",
                        step_type=StepType.LEARN,
                        visual_ref="series_connection.png"
                    ),
                    BuildStep(
                        id="p2-l2",
                        instruction="LEARN: Parallel connection - cells side by side. Voltage stays same, current adds.",
                        step_type=StepType.LEARN,
                        visual_ref="parallel_connection.png"
                    ),
                    BuildStep(
                        id="p2-l3",
                        instruction="CHECKPOINT: If each cell is 1.5V and 100mA, what does 3 cells in series give you?",
                        step_type=StepType.CHECKPOINT,
                        checkpoint_question="Calculate: 3 cells in series = ? volts, ? mA"
                    )
                ]
            ),
            BuildModule(
                id="p2-build",
                name="Stack Assembly",
                description="Connect multiple proven cells",
                prerequisites=["p2-learn"],
                completion_test="Stack produces expected combined output, stable for 1 hour",
                steps=[
                    BuildStep(
                        id="p2-b1",
                        instruction="Build 2 more cells using Phase 1 process - each must pass all checkpoints",
                        step_type=StepType.BUILD
                    ),
                    BuildStep(
                        id="p2-b2",
                        instruction="Connect cells in series - positive to negative chain",
                        step_type=StepType.BUILD,
                        visual_ref="series_wiring.png"
                    ),
                    BuildStep(
                        id="p2-b3",
                        instruction="TEST: Measure total voltage. Should be sum of individual cells.",
                        step_type=StepType.TEST,
                        parts_needed=["multimeter"]
                    ),
                    BuildStep(
                        id="p2-b4",
                        instruction="SIMULATE: Before parallel, calculate what happens if one cell fails",
                        step_type=StepType.SIMULATE
                    ),
                    BuildStep(
                        id="p2-b5",
                        instruction="REFLECT: What's the trade-off between series and parallel for your goals?",
                        step_type=StepType.REFLECT
                    )
                ]
            )
        ]
    )


def create_phase_3_generator() -> ProjectPhase:
    """Phase 3: Power small devices / emergency loads"""
    return ProjectPhase(
        id="phase-3",
        name="Generator Module",
        purpose="Use your cell stack to power real devices safely",
        scope_notes="Start with low-power devices only (LEDs, small fans, sensors)",
        modules=[
            BuildModule(
                id="p3-regulation",
                name="Voltage Regulation",
                description="Add regulation to provide stable, consistent power",
                completion_test="Output stays within 5% of target voltage under varying load",
                steps=[
                    BuildStep(
                        id="p3-r1",
                        instruction="LEARN: Why raw cell voltage isn't safe for devices",
                        step_type=StepType.LEARN
                    ),
                    BuildStep(
                        id="p3-r2",
                        instruction="Build simple voltage regulator circuit",
                        step_type=StepType.BUILD,
                        visual_ref="regulator_circuit.png",
                        parts_needed=["voltage_regulator_ic", "capacitors", "resistors"]
                    ),
                    BuildStep(
                        id="p3-r3",
                        instruction="TEST: Measure output with and without load",
                        step_type=StepType.TEST,
                        parts_needed=["multimeter", "test_load"]
                    )
                ]
            ),
            BuildModule(
                id="p3-load",
                name="Load Connection",
                description="Safely power your first device",
                prerequisites=["p3-regulation"],
                completion_test="Device runs for 30 minutes without issues",
                steps=[
                    BuildStep(
                        id="p3-l1",
                        instruction="Choose a low-power target device (LED recommended for first test)",
                        step_type=StepType.BUILD,
                        parts_needed=["led_5mm", "resistor_330ohm"]
                    ),
                    BuildStep(
                        id="p3-l2",
                        instruction="Calculate runtime: cell capacity / device draw = hours",
                        step_type=StepType.LEARN
                    ),
                    BuildStep(
                        id="p3-l3",
                        instruction="Connect device through regulator, observe for 30 minutes",
                        step_type=StepType.TEST
                    ),
                    BuildStep(
                        id="p3-l4",
                        instruction="REFLECT: What would you need to change to power something bigger?",
                        step_type=StepType.REFLECT
                    )
                ]
            )
        ]
    )


def create_phase_4_home_scale() -> ProjectPhase:
    """Phase 4: Home Scale - simulation and modeling only"""
    return ProjectPhase(
        id="phase-4",
        name="Home Scale Planning",
        purpose="Model and simulate home-scale energy systems",
        scope_notes="SIMULATION ONLY - no physical home-scale builds without professional verification",
        simulation_only=True,
        modules=[
            BuildModule(
                id="p4-requirements",
                name="Load Analysis",
                description="Calculate what a home actually needs",
                completion_test="Complete power audit with realistic numbers",
                steps=[
                    BuildStep(
                        id="p4-r1",
                        instruction="LEARN: How to read a power bill and understand usage",
                        step_type=StepType.LEARN
                    ),
                    BuildStep(
                        id="p4-r2",
                        instruction="SIMULATE: Model your home's power needs over 24 hours",
                        step_type=StepType.SIMULATE
                    ),
                    BuildStep(
                        id="p4-r3",
                        instruction="Calculate how many of your cells would be needed (it's a LOT)",
                        step_type=StepType.LEARN
                    )
                ]
            ),
            BuildModule(
                id="p4-future",
                name="Scaling Roadmap",
                description="Plan the path from prototype to real application",
                prerequisites=["p4-requirements"],
                completion_test="Realistic roadmap with safety checkpoints",
                steps=[
                    BuildStep(
                        id="p4-f1",
                        instruction="LEARN: What certifications and testing home power systems need",
                        step_type=StepType.LEARN
                    ),
                    BuildStep(
                        id="p4-f2",
                        instruction="SIMULATE: Model costs, timelines, and safety requirements",
                        step_type=StepType.SIMULATE
                    ),
                    BuildStep(
                        id="p4-f3",
                        instruction="REFLECT: Is this the right path? What alternatives exist?",
                        step_type=StepType.REFLECT
                    )
                ]
            )
        ]
    )


power_cell_project = create_power_cell_project()
project_registry.register(power_cell_project)
