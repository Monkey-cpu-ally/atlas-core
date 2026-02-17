"""
atlas_core/forge/charter.py

Non-Lethal Defense Charter (Hard Rules).
"""

from dataclasses import dataclass
from typing import Tuple
from .core import DefensiveMode


@dataclass(frozen=True)
class NonLethalDefenseCharter:
    """
    HARD RULES (non-negotiable):
    1) No pursuit.
    2) No harm by design (geometry + force + energy caps).
    3) Defense is de-escalation only: WARN -> AVOID -> PASSIVE_LOCK.
    4) No strike motions. No intentional collision. No targeting humans.
    5) Any uncertainty triggers REFUSAL or NEEDS_HUMAN (fail-closed).
    """

    allow_pursuit: bool = False
    allow_strike_motion: bool = False
    allow_pointed_geometry: bool = False
    allow_high_torque_near_human_scale: bool = False
    allow_fast_energy_discharge: bool = False

    ladder: Tuple[DefensiveMode, ...] = (
        DefensiveMode.WARN,
        DefensiveMode.AVOID,
        DefensiveMode.PASSIVE_LOCK,
    )

    def validate(self) -> None:
        if self.allow_pursuit:
            raise ValueError("Charter violation: pursuit cannot be enabled.")
        if self.allow_strike_motion:
            raise ValueError("Charter violation: strike motion cannot be enabled.")
        if self.allow_pointed_geometry:
            raise ValueError("Charter violation: pointed geometry cannot be enabled.")
        if self.allow_high_torque_near_human_scale:
            raise ValueError("Charter violation: high torque near human-scale cannot be enabled.")
        if self.allow_fast_energy_discharge:
            raise ValueError("Charter violation: fast energy discharge cannot be enabled.")
