"""Internal deterministic agent modules used by Atlas orchestrator."""

from __future__ import annotations

from .knowledge import (
    ACTIVE_PROTOTYPE,
    ATLAS_CAPABILITY_BOUNDARIES,
    infer_relevant_fields,
    is_resonance_scanner_request,
)
from .models import (
    AjaniOutput,
    HermesOutput,
    IntentType,
    MinervaOutput,
    ModeType,
    PipelineStage,
)
from .policy import PolicyDecision


def _collect_parts(user_input: str) -> list[str]:
    part_map = {
        "sensor": "Sensor module",
        "motor": "Motor/actuator",
        "battery": "Battery pack",
        "camera": "Camera module",
        "frame": "Structural frame",
        "wire": "Wiring harness",
        "controller": "Microcontroller/compute unit",
        "pump": "Pump assembly",
        "valve": "Valve assembly",
        "antenna": "Antenna/receiver module",
    }
    lowered = user_input.lower()
    parts = [label for keyword, label in part_map.items() if keyword in lowered]
    if not parts:
        parts = ["Core module", "Power module", "Control module"]
    return parts


def _build_architecture(user_input: str, parts: list[str]) -> list[str]:
    if is_resonance_scanner_request(user_input):
        return [
            "[Input Layer] Sensor array captures resonance signals.",
            "[Conditioning Layer] Analog front-end filters and amplifies band-limited signals.",
            "[Compute Layer] Embedded processor performs FFT and band analysis.",
            "[Control Layer] Adaptive tuning loop adjusts sensitivity and gain.",
            "[Output Layer] Visual/haptic feedback + logged diagnostic metrics.",
        ]

    component_chain = " -> ".join(parts[:4]) if len(parts) >= 2 else "Input -> Processing -> Output"
    return [
        f"[System Chain] {component_chain}",
        "[Control Loop] Monitor -> Evaluate -> Adjust -> Re-test",
        "[Safety Layer] Constraint checks gate every stage transition",
    ]


class AjaniModule:
    """Engineering planner module focused on structure and testability."""

    def generate(
        self,
        *,
        user_input: str,
        intent: IntentType,
        stage: PipelineStage,
        constraints: list[str],
        version_tag: str,
    ) -> AjaniOutput:
        parts = _collect_parts(user_input)
        objective = user_input.strip().split("\n")[0][:180]
        required_fields = infer_relevant_fields(user_input)
        architecture = _build_architecture(user_input, parts)

        if stage == "blueprint":
            structured_plan = [
                "Define project objective and measurable success criteria.",
                "Break system into components and explicit interfaces.",
                "Set constraints: cost, safety, material choices, simulation boundaries.",
                "Define validation tests before moving to build stage.",
            ]
            component_breakdown = [f"Design component: {part}" for part in parts]
            risk_list = [
                "Unclear requirements can cause scope drift.",
                "Missing constraints may produce unsafe design decisions.",
                "Interface mismatches between components can delay build.",
            ]
            test_plan = [
                "Requirement coverage check (each requirement mapped to a test).",
                "Feasibility review against constraints before build approval.",
                "Risk review with pass/fail decision on each critical hazard.",
            ]
            tools_list = [
                "Design notebook / spec sheet",
                "Constraint matrix template",
                "Simulation planning worksheet",
            ]
            wiring_power_logic = [
                "Define power domains and expected voltage/current envelope.",
                "Map signal paths from sensor input to processing output.",
                "Reserve test points for debugging and calibration.",
            ]
            calibration_procedure = [
                "Define baseline signal for zero-reference calibration.",
                "Set acceptable tolerance bands for drift/noise.",
            ]
            test_protocol = [
                "Blueprint review checklist",
                "Constraint compliance review",
                "Pre-build approval gate",
            ]
            failure_analysis = [
                "Identify top three failure hypotheses before build.",
            ]
            performance_metrics = [
                "Signal fidelity target",
                "Noise floor target",
                "Stage completion pass rate",
            ]
            iteration_changes = ["Baseline blueprint release."]
            revalidation_steps = ["Re-run blueprint gate after any architectural change."]
        elif stage == "build":
            structured_plan = [
                "Finalize bill of materials and tools checklist.",
                "Assemble in ordered modules with checkpoints.",
                "Validate wiring/power logic after each integration step.",
                "Run stage-level safety checks before powering full system.",
            ]
            component_breakdown = [f"Assemble + verify: {part}" for part in parts]
            risk_list = [
                "Incorrect assembly order can increase rework.",
                "Power-on without staged checks can damage components.",
                "Tool mismatch can reduce build quality.",
            ]
            test_plan = [
                "Per-module functional check after assembly.",
                "Power and continuity check before full activation.",
                "End-to-end acceptance test against measurable requirements.",
            ]
            tools_list = [
                "Precision screwdriver set",
                "Multimeter",
                "Soldering station (if required)",
                "ESD-safe mat and wrist strap",
            ]
            wiring_power_logic = [
                "Verify supply polarity before energizing each module.",
                "Route signal lines separately from high-current paths.",
                "Validate grounding strategy and return paths.",
            ]
            calibration_procedure = [
                "Run baseline calibration with known reference signal.",
                "Tune gain/threshold until noise floor meets target.",
                "Store calibration profile for current version.",
            ]
            test_protocol = [
                "Module continuity and power tests",
                "Signal chain validation with known input tones",
                "Safety stop behavior verification",
            ]
            failure_analysis = [
                "Track assembly defects by subsystem.",
                "Record calibration instability and likely causes.",
            ]
            performance_metrics = [
                "Assembly pass rate",
                "Calibration stability over repeated runs",
                "Signal-to-noise ratio under nominal conditions",
            ]
            iteration_changes = ["Capture issues for modify-stage backlog."]
            revalidation_steps = ["Repeat full build-stage test protocol after any repair."]
        else:
            structured_plan = [
                "Collect test results and failure observations.",
                "Rank failure modes by severity and frequency.",
                "Apply targeted design changes with version increment.",
                "Re-run validation and update project records.",
            ]
            component_breakdown = [f"Improve version of: {part}" for part in parts]
            risk_list = [
                "Fixes can introduce regressions in adjacent modules.",
                "Untracked changes can cause version confusion.",
                "Skipping retest after change can hide failures.",
            ]
            test_plan = [
                "Regression test baseline before/after modifications.",
                "Failure-mode reproduction and mitigation verification.",
                "Versioned release check with updated documentation.",
            ]
            tools_list = [
                "Diagnostic logger",
                "Oscilloscope or signal analyzer",
                "Issue tracker for change control",
            ]
            wiring_power_logic = [
                "Compare measured power signatures against previous version.",
                "Isolate and retest modified signal paths.",
            ]
            calibration_procedure = [
                "Recalibrate all modified channels.",
                "Compare calibration curve against prior version baseline.",
            ]
            test_protocol = [
                "Regression suite execution",
                "Targeted failure-mode tests",
                "Post-change safety gate review",
            ]
            failure_analysis = [
                "Document root cause for each failing test.",
                "Classify failures: design, integration, calibration, or environment.",
            ]
            performance_metrics = [
                "Improvement delta vs previous version",
                "Residual failure rate after fixes",
                "Stability over repeated stress cycles",
            ]
            iteration_changes = [
                "Version increment required for every accepted modification.",
                "Update BOM and test documentation with each change.",
            ]
            revalidation_steps = [
                "Re-run complete validation gates before marking version stable.",
            ]

        measurable_requirements = [
            "Each stage must define pass/fail criteria.",
            "All critical constraints must be explicitly listed.",
            "Every major component must have at least one validation check.",
        ]
        if intent == "security_request":
            measurable_requirements.append("Security controls must be mapped to specific tests.")

        if is_resonance_scanner_request(user_input):
            required_fields = list(ACTIVE_PROTOTYPE["academic_dependencies"].keys())

        spec = [
            f"Intent: {intent}",
            f"Pipeline stage: {stage}",
            "Output must remain structured and testable.",
            "Project memory is isolated per project.",
        ]

        return AjaniOutput(
            summary=f"Ajani prepared a {stage} plan for: {objective}",
            goal=objective,
            spec=spec,
            version_tag=version_tag,
            system_architecture_diagram=architecture,
            required_academic_fields=required_fields,
            structured_plan=structured_plan,
            component_breakdown=component_breakdown,
            constraints=constraints,
            measurable_requirements=measurable_requirements,
            risk_list=risk_list,
            test_plan=test_plan,
            parts_list=parts,
            tools_list=tools_list,
            wiring_power_logic=wiring_power_logic,
            calibration_procedure=calibration_procedure,
            test_protocol=test_protocol,
            failure_analysis=failure_analysis,
            performance_metrics=performance_metrics,
            iteration_changes=iteration_changes,
            revalidation_steps=revalidation_steps,
            artifacts={
                "stage": stage,
                "intent": intent,
                "objective": objective,
                "component_count": len(component_breakdown),
            },
        )


class MinervaModule:
    """Teach-back and human-clarity module."""

    def generate(
        self,
        *,
        user_input: str,
        mode: ModeType,
        stage: PipelineStage,
        ajani_output: AjaniOutput,
    ) -> MinervaOutput:
        tone_map = {
            "mentor": "clear and supportive",
            "warrior": "focused and disciplined",
            "builder": "practical and hands-on",
        }
        tone = tone_map[mode]
        lego_steps = [
            f"Step {idx + 1}: {step}"
            for idx, step in enumerate(ajani_output.structured_plan)
        ]
        clarity_notes = [
            "Keep each step small enough to complete in one session.",
            "If a step is ambiguous, rewrite it with a concrete action verb.",
            "Tie each step to one measurable check before moving forward.",
        ]
        teach_back_questions = [
            "What is the main objective in your own words?",
            "Which step has the highest risk and why?",
            "What test tells you this stage is complete?",
        ]

        context_line = (
            "This plan prioritizes safety, clarity, and inclusive learning language."
        )
        if stage == "modify":
            context_line = (
                "This iteration focuses on learning from failure and improving without losing safety."
            )

        explanation = (
            "Minerva reframed the engineering plan into clear, teachable steps that can be "
            "executed safely and reviewed stage-by-stage."
        )
        next_action = "Choose Step 1 and confirm the success metric before execution."
        concept_overview = (
            "Start from the system goal, then map components, then validate each part with a test."
        )
        concept_analogy = (
            "Treat the system like assembling layered LEGO modules: foundation first, "
            "then functional blocks, then final stability checks."
        )
        step_by_step_understanding = [
            "Identify what each component does before assembly.",
            "Connect one component at a time and test immediately.",
            "Confirm risk controls before advancing to next stage.",
        ]
        reflective_reinforcement = [
            "Repeat the objective and constraint set before each stage.",
            "Explain one failure mode and its mitigation after each test run.",
        ]
        memory_anchors = [
            "Goal -> Components -> Constraints -> Tests",
            "Build small, test early, modify safely",
            "Version every meaningful change",
        ]
        risk_failure_modes = [f"Plain-language risk: {risk}" for risk in ajani_output.risk_list]
        improvement_path = [
            "Capture observed failures and map them to component owners.",
            "Prioritize fixes by safety impact, then performance impact.",
            "Revalidate and publish next version notes.",
        ]

        return MinervaOutput(
            summary=f"Minerva translated Ajani's plan into {tone} lego-style guidance.",
            teaching_goal=f"Help the user execute the {stage} stage with confidence and clarity.",
            explanation=explanation,
            concept_overview=concept_overview,
            concept_analogy=concept_analogy,
            component_breakdown=ajani_output.component_breakdown,
            lego_steps=lego_steps,
            step_by_step_understanding=step_by_step_understanding,
            clarity_notes=clarity_notes,
            teach_back_questions=teach_back_questions,
            reflective_reinforcement=reflective_reinforcement,
            memory_anchors=memory_anchors,
            risk_failure_modes=risk_failure_modes,
            improvement_path=improvement_path,
            next_action=next_action,
            cultural_context=context_line,
        )


class HermesModule:
    """Validation and guardrail module."""

    def validate(
        self,
        *,
        policy: PolicyDecision,
        stage: PipelineStage,
        ajani_output: AjaniOutput,
        minerva_output: MinervaOutput,
    ) -> HermesOutput:
        checks = list(policy.checks)
        flags = list(policy.flags)
        blocked_reasons = list(policy.blocked_reasons)
        enforced_constraints = list(policy.enforced_constraints)
        edge_case_checks: list[str] = []

        if not ajani_output.measurable_requirements:
            flags.append("missing_measurable_requirements")
            checks.append("FAILED: measurable requirements missing.")
        else:
            checks.append("PASS: measurable requirements present.")

        if not ajani_output.test_plan:
            flags.append("missing_test_plan")
            checks.append("FAILED: test plan missing.")
        else:
            checks.append("PASS: test plan present.")

        if not minerva_output.lego_steps:
            flags.append("missing_lego_steps")
            checks.append("FAILED: Minerva teach-back steps missing.")
        else:
            checks.append("PASS: Minerva step-by-step guidance present.")

        if stage == "build" and len(ajani_output.parts_list) < 1:
            flags.append("missing_parts_list")
            checks.append("FAILED: build stage requires a parts list.")

        edge_case_checks.append("Checked role separation between Ajani/Minerva/Hermes outputs.")
        if not ajani_output.goal or not ajani_output.spec:
            flags.append("ajani_structure_incomplete")
            edge_case_checks.append("FAILED: Ajani structure missing goal/spec.")
        if not minerva_output.explanation or not minerva_output.next_action:
            flags.append("minerva_structure_incomplete")
            edge_case_checks.append("FAILED: Minerva structure missing explanation/next action.")

        blocked = policy.blocked
        flagged = policy.flagged or bool(flags)
        if blocked:
            validation_status = "blocked"
            approval_status = "blocked"
            safety_mode = "blocked"
            summary = "Hermes blocked the request due to hard-rule violations."
        elif flagged:
            validation_status = "flagged"
            approval_status = "flagged"
            safety_mode = policy.safety_mode if policy.safety_mode != "blocked" else "normal"
            summary = "Hermes flagged constraints that require caution before execution."
        else:
            validation_status = "ok"
            approval_status = "approved"
            safety_mode = policy.safety_mode
            summary = "Hermes validated the output and all checks passed."

        return HermesOutput(
            summary=summary,
            validation_status=validation_status,
            approval_status=approval_status,
            safety_mode=safety_mode,
            checks=checks,
            edge_case_checks=edge_case_checks,
            flags=flags,
            blocked_reasons=blocked_reasons,
            enforced_constraints=enforced_constraints,
            capability_boundaries=ATLAS_CAPABILITY_BOUNDARIES,
        )

