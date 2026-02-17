"""Internal deterministic agent modules used by Atlas orchestrator."""

from __future__ import annotations

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
    }
    lowered = user_input.lower()
    parts = [label for keyword, label in part_map.items() if keyword in lowered]
    if not parts:
        parts = ["Core module", "Power module", "Control module"]
    return parts


class AjaniModule:
    """Engineering planner module focused on structure and testability."""

    def generate(
        self,
        *,
        user_input: str,
        intent: IntentType,
        stage: PipelineStage,
        constraints: list[str],
    ) -> AjaniOutput:
        parts = _collect_parts(user_input)
        objective = user_input.strip().split("\n")[0][:180]

        if stage == "blueprint":
            structured_plan = [
                "Define project objective and success criteria.",
                "Break system into major components and interfaces.",
                "Set constraints: cost, safety, materials, and simulation boundaries.",
                "Define verification tests before build begins.",
            ]
            component_breakdown = [f"Design component: {part}" for part in parts]
            risk_list = [
                "Unclear requirements can cause scope drift.",
                "Missing constraints may produce unsafe design choices.",
                "Interface mismatches between components can delay build.",
            ]
            test_plan = [
                "Requirement coverage check (each requirement mapped to a test).",
                "Feasibility review against constraints before build approval.",
                "Risk review with pass/fail decision on each critical hazard.",
            ]
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

        measurable_requirements = [
            "Each stage must define pass/fail criteria.",
            "All critical constraints must be explicitly listed.",
            "Every major component must have at least one validation check.",
        ]
        if intent == "security_request":
            measurable_requirements.append("Security controls must be mapped to specific tests.")

        return AjaniOutput(
            summary=f"Ajani prepared a {stage} plan for: {objective}",
            structured_plan=structured_plan,
            component_breakdown=component_breakdown,
            constraints=constraints,
            measurable_requirements=measurable_requirements,
            risk_list=risk_list,
            test_plan=test_plan,
            parts_list=parts,
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

        return MinervaOutput(
            summary=f"Minerva translated Ajani's plan into {tone} lego-style guidance.",
            teaching_goal=f"Help the user execute the {stage} stage with confidence and clarity.",
            lego_steps=lego_steps,
            clarity_notes=clarity_notes,
            teach_back_questions=teach_back_questions,
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

        if not ajani_output.measurable_requirements:
            flags.append("missing_measurable_requirements")
            checks.append("FAILED: measurable requirements missing.")

        if not ajani_output.test_plan:
            flags.append("missing_test_plan")
            checks.append("FAILED: test plan missing.")

        if not minerva_output.lego_steps:
            flags.append("missing_lego_steps")
            checks.append("FAILED: Minerva teach-back steps missing.")

        if stage == "build" and len(ajani_output.parts_list) < 1:
            flags.append("missing_parts_list")
            checks.append("FAILED: build stage requires a parts list.")

        blocked = policy.blocked
        flagged = policy.flagged or bool(flags)
        if blocked:
            validation_status = "blocked"
            safety_mode = "blocked"
            summary = "Hermes blocked the request due to hard-rule violations."
        elif flagged:
            validation_status = "flagged"
            safety_mode = policy.safety_mode if policy.safety_mode != "blocked" else "normal"
            summary = "Hermes flagged constraints that require caution before execution."
        else:
            validation_status = "ok"
            safety_mode = policy.safety_mode
            summary = "Hermes validated the output and all checks passed."

        return HermesOutput(
            summary=summary,
            validation_status=validation_status,
            safety_mode=safety_mode,
            checks=checks,
            flags=flags,
            blocked_reasons=blocked_reasons,
            enforced_constraints=enforced_constraints,
        )

