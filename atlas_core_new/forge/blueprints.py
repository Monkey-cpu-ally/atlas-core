"""
atlas_core/forge/blueprints.py

Animal-inspired green machine blueprints (non-lethal, non-escalatory).
"""

from dataclasses import dataclass
from typing import Tuple
from .core import TaskType, DefensiveMode
from .actuators import TendonActuator, JointDesign


@dataclass(frozen=True)
class DefensePolicy:
    """
    Non-lethal by construction.
    escalates_force must always be False.
    """
    allowed_modes: Tuple[DefensiveMode, ...] = (
        DefensiveMode.WARN,
        DefensiveMode.AVOID,
        DefensiveMode.PASSIVE_LOCK,
    )
    escalates_force: bool = False


@dataclass(frozen=True)
class Blueprint:
    name: str
    task_type: TaskType
    biomimic: str
    actuator: TendonActuator
    joints: Tuple[JointDesign, ...]
    payload_kg: float
    energy_storage_j: float
    can_pursue_targets: bool
    defense_policy: DefensePolicy
    geometry_notes: str = ""
