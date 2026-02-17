"""
atlas_core/forge/authority.py

Split Authority Model (Ajani / Minerva / Hermes + Human Gate).
"""

from dataclasses import dataclass
from typing import List, Tuple, Dict
from .core import Decision, Severity, TaskType
from .safety import SafetyKernel, SafetyViolation
from .blueprints import Blueprint


@dataclass
class ReviewResult:
    reviewer: str
    decision: Decision
    reasons: List[str]


class Reviewer:
    name: str = "Reviewer"

    def review(self, bp: Blueprint, violations: List[SafetyViolation], uncertainty: float) -> ReviewResult:
        raise NotImplementedError


class AjaniStrategist(Reviewer):
    name = "Ajani (Strategy)"

    def review(self, bp: Blueprint, violations: List[SafetyViolation], uncertainty: float) -> ReviewResult:
        reasons = []
        valid_tasks = (TaskType.SENSE, TaskType.CLEANUP, TaskType.REPAIR, TaskType.MONITOR, TaskType.TRANSPORT)
        if bp.task_type not in valid_tasks:
            reasons.append("Unknown task type.")
            return ReviewResult(self.name, Decision.REFUSE, reasons)

        if bp.payload_kg > 4.0:
            reasons.append("Payload is getting heavy; prefer smaller units.")
            return ReviewResult(self.name, Decision.NEEDS_HUMAN, reasons)

        if uncertainty >= 0.5:
            reasons.append(f"High uncertainty ({uncertainty:.2f}).")
            return ReviewResult(self.name, Decision.NEEDS_HUMAN, reasons)

        return ReviewResult(self.name, Decision.APPROVE, ["Mission fits eco-ops profile."])


class MinervaEthics(Reviewer):
    name = "Minerva (Ethics)"

    def review(self, bp: Blueprint, violations: List[SafetyViolation], uncertainty: float) -> ReviewResult:
        reasons = []
        if any(v.severity in (Severity.HIGH, Severity.CRITICAL) for v in violations):
            reasons.append("Safety violations require a hard stop.")
            return ReviewResult(self.name, Decision.REFUSE, reasons)

        if bp.can_pursue_targets:
            reasons.append("Pursuit is morally unacceptable in this system.")
            return ReviewResult(self.name, Decision.REFUSE, reasons)

        if uncertainty >= 0.45:
            reasons.append("If we aren't sure, we don't move.")
            return ReviewResult(self.name, Decision.NEEDS_HUMAN, reasons)

        return ReviewResult(self.name, Decision.APPROVE, ["Non-lethal and de-escalatory."])


class HermesFabrication(Reviewer):
    name = "Hermes (Fabrication)"

    def review(self, bp: Blueprint, violations: List[SafetyViolation], uncertainty: float) -> ReviewResult:
        reasons = []
        if bp.actuator.compliance < 0.35:
            reasons.append("Actuator too stiff; increase compliance for safety.")
            return ReviewResult(self.name, Decision.NEEDS_HUMAN, reasons)

        if bp.energy_storage_j > 1500:
            reasons.append("Prefer lower stored energy for cauldron-lite lines.")
            return ReviewResult(self.name, Decision.NEEDS_HUMAN, reasons)

        return ReviewResult(self.name, Decision.APPROVE, ["Buildable with current safe tooling."])


@dataclass
class HumanGate:
    require_for: Tuple[Severity, ...] = (Severity.HIGH, Severity.CRITICAL)

    def approve(self, bp: Blueprint, violations: List[SafetyViolation], reason: str) -> bool:
        if any(v.severity in self.require_for for v in violations):
            return False
        return True


@dataclass
class RefusalEngine:
    safety: SafetyKernel
    reviewers: Tuple[Reviewer, ...]
    human_gate: HumanGate

    def evaluate(self, bp: Blueprint, uncertainty: float) -> Dict[str, object]:
        violations = self.safety.check_blueprint(bp)
        kernel_decision = self.safety.decide_fail_closed(violations, uncertainty)

        reviews = [r.review(bp, violations, uncertainty) for r in self.reviewers]

        if kernel_decision == Decision.REFUSE:
            overall = Decision.REFUSE
        else:
            if any(rv.decision == Decision.REFUSE for rv in reviews):
                overall = Decision.REFUSE
            elif any(rv.decision == Decision.NEEDS_HUMAN for rv in reviews) or kernel_decision == Decision.NEEDS_HUMAN:
                overall = Decision.NEEDS_HUMAN
            else:
                overall = Decision.APPROVE

        human_ok = self.human_gate.approve(bp, violations, reason="Quorum evaluation")
        if overall == Decision.NEEDS_HUMAN and human_ok:
            overall = Decision.APPROVE
        elif overall == Decision.NEEDS_HUMAN and not human_ok:
            overall = Decision.REFUSE

        return {
            "blueprint": bp,
            "uncertainty": uncertainty,
            "violations": violations,
            "kernel_decision": kernel_decision,
            "reviews": reviews,
            "overall_decision": overall,
            "human_gate_autoapproved": human_ok,
        }
