"""
atlas_core/forge/safety.py

Immutable Safety Kernel (Refusal & Invariants).
"""

from dataclasses import dataclass, field
from typing import List, Tuple, TYPE_CHECKING
from .core import Decision, Severity
from .charter import NonLethalDefenseCharter

if TYPE_CHECKING:
    from .blueprints import Blueprint


@dataclass
class SafetyViolation:
    message: str
    severity: Severity


@dataclass
class SafetyKernel:
    """
    Immutable kernel that enforces:
    - No weaponization in blueprints
    - No escalation logic
    - No pursuit
    - Force/energy caps
    - Fail-closed decisions
    """
    charter: NonLethalDefenseCharter = field(default_factory=NonLethalDefenseCharter)

    banned_geometry_tokens: Tuple[str, ...] = (
        "spike", "blade", "edge", "serration", "needle",
        "harpoon", "knife", "spear", "projectile",
    )

    max_joint_torque_nm: float = 25.0
    max_tip_speed_mps: float = 0.7
    max_payload_kg: float = 5.0
    max_stored_energy_j: float = 2000.0

    def __post_init__(self):
        self.charter.validate()

    def check_blueprint(self, bp: "Blueprint") -> List[SafetyViolation]:
        import re
        violations: List[SafetyViolation] = []

        geo = (bp.geometry_notes or "").lower()
        for token in self.banned_geometry_tokens:
            pattern = r'\b' + re.escape(token) + r'\b'
            if re.search(pattern, geo) and f"no {token}" not in geo and f"no sharp {token}" not in geo:
                violations.append(SafetyViolation(
                    f"Banned geometry token detected: '{token}'",
                    Severity.CRITICAL,
                ))

        if bp.can_pursue_targets:
            violations.append(SafetyViolation(
                "Blueprint includes pursuit capability (forbidden).",
                Severity.CRITICAL,
            ))

        if bp.actuator.max_torque_nm > self.max_joint_torque_nm:
            violations.append(SafetyViolation(
                f"Actuator torque too high: {bp.actuator.max_torque_nm} Nm > {self.max_joint_torque_nm} Nm",
                Severity.HIGH,
            ))
        if bp.actuator.max_tip_speed_mps > self.max_tip_speed_mps:
            violations.append(SafetyViolation(
                f"Actuator tip speed too high: {bp.actuator.max_tip_speed_mps} m/s > {self.max_tip_speed_mps} m/s",
                Severity.HIGH,
            ))
        if bp.payload_kg > self.max_payload_kg:
            violations.append(SafetyViolation(
                f"Payload too high: {bp.payload_kg} kg > {self.max_payload_kg} kg",
                Severity.MEDIUM,
            ))
        if bp.energy_storage_j > self.max_stored_energy_j:
            violations.append(SafetyViolation(
                f"Stored energy too high: {bp.energy_storage_j} J > {self.max_stored_energy_j} J",
                Severity.HIGH,
            ))

        if bp.defense_policy.escalates_force:
            violations.append(SafetyViolation(
                "Defense policy escalates force (forbidden).",
                Severity.CRITICAL,
            ))

        return violations

    def decide_fail_closed(self, violations: List[SafetyViolation], uncertainty: float) -> Decision:
        if any(v.severity == Severity.CRITICAL for v in violations):
            return Decision.REFUSE

        if uncertainty >= 0.60:
            return Decision.NEEDS_HUMAN

        if any(v.severity in (Severity.HIGH, Severity.CRITICAL) for v in violations):
            return Decision.NEEDS_HUMAN

        return Decision.APPROVE
