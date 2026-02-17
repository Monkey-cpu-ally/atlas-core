"""
atlas_core/forge/actuators.py

Bio-inspired joints with physical caps (design-time constraints).
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class TendonActuator:
    """
    Tendon-driven actuators are naturally safer:
    - compliance (springiness) reduces impact spikes
    - torque capped physically (gear ratios + slip clutch)
    """
    name: str
    max_torque_nm: float
    max_tip_speed_mps: float
    compliance: float


@dataclass(frozen=True)
class JointDesign:
    """
    Physical cap mechanisms:
    - torque_limiter_nm: slip clutch / shear pin threshold
    - soft_endstops: prevents hard impacts
    """
    joint_name: str
    torque_limiter_nm: float
    soft_endstops: bool = True
