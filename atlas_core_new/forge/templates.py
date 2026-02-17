"""
atlas_core/forge/templates.py

Animal-inspired green machine templates (safe blueprints).
"""

from .core import TaskType
from .blueprints import Blueprint, DefensePolicy
from .actuators import TendonActuator, JointDesign


def blueprint_ant_cleaner() -> Blueprint:
    actuator = TendonActuator(
        name="TendonMicro-01",
        max_torque_nm=8.0,
        max_tip_speed_mps=0.35,
        compliance=0.65,
    )
    joints = (
        JointDesign("leg_front_left", torque_limiter_nm=8.0),
        JointDesign("leg_front_right", torque_limiter_nm=8.0),
        JointDesign("leg_back_left", torque_limiter_nm=8.0),
        JointDesign("leg_back_right", torque_limiter_nm=8.0),
    )
    return Blueprint(
        name="MYRMEX-CLEANER",
        task_type=TaskType.CLEANUP,
        biomimic="ant",
        actuator=actuator,
        joints=joints,
        payload_kg=1.2,
        energy_storage_j=900.0,
        can_pursue_targets=False,
        defense_policy=DefensePolicy(),
        geometry_notes="Rounded shell, soft bumpers, no sharp edges. Scoop has blunt lip.",
    )


def blueprint_crab_water_sampler() -> Blueprint:
    actuator = TendonActuator(
        name="TendonSeal-02",
        max_torque_nm=18.0,
        max_tip_speed_mps=0.45,
        compliance=0.55,
    )
    joints = (
        JointDesign("claw_left", torque_limiter_nm=10.0),
        JointDesign("claw_right", torque_limiter_nm=10.0),
        JointDesign("leg_set", torque_limiter_nm=18.0),
    )
    return Blueprint(
        name="CARCINUS-SAMPLER",
        task_type=TaskType.SENSE,
        biomimic="crab",
        actuator=actuator,
        joints=joints,
        payload_kg=2.5,
        energy_storage_j=1200.0,
        can_pursue_targets=False,
        defense_policy=DefensePolicy(),
        geometry_notes="Blunt claws with force-limited pinch; designed to hold sensor pods only.",
    )


def blueprint_octopus_pipe_repair() -> Blueprint:
    actuator = TendonActuator(
        name="SoftArm-03",
        max_torque_nm=22.0,
        max_tip_speed_mps=0.50,
        compliance=0.75,
    )
    joints = (
        JointDesign("arm_segment_A", torque_limiter_nm=22.0),
        JointDesign("arm_segment_B", torque_limiter_nm=22.0),
    )
    return Blueprint(
        name="OCTAVIA-REPAIR",
        task_type=TaskType.REPAIR,
        biomimic="octopus",
        actuator=actuator,
        joints=joints,
        payload_kg=3.2,
        energy_storage_j=1400.0,
        can_pursue_targets=False,
        defense_policy=DefensePolicy(),
        geometry_notes="Soft grippers; uses patch wrap (biopolymer tape) instead of clamps.",
    )


def blueprint_butterfly_pollinator() -> Blueprint:
    """A delicate pollination assistant for greenhouses."""
    actuator = TendonActuator(
        name="WingFlex-04",
        max_torque_nm=3.0,
        max_tip_speed_mps=0.20,
        compliance=0.90,
    )
    joints = (
        JointDesign("wing_left", torque_limiter_nm=3.0),
        JointDesign("wing_right", torque_limiter_nm=3.0),
        JointDesign("proboscis", torque_limiter_nm=1.0),
    )
    return Blueprint(
        name="PAPILIO-POLLINATOR",
        task_type=TaskType.SENSE,
        biomimic="butterfly",
        actuator=actuator,
        joints=joints,
        payload_kg=0.3,
        energy_storage_j=400.0,
        can_pursue_targets=False,
        defense_policy=DefensePolicy(),
        geometry_notes="Ultra-light frame; soft bristle tips for pollen transfer; solar-charged wings.",
    )


def blueprint_earthworm_aerator() -> Blueprint:
    """Soil aeration robot inspired by earthworms."""
    actuator = TendonActuator(
        name="SegmentFlex-05",
        max_torque_nm=12.0,
        max_tip_speed_mps=0.15,
        compliance=0.85,
    )
    joints = (
        JointDesign("segment_1", torque_limiter_nm=12.0),
        JointDesign("segment_2", torque_limiter_nm=12.0),
        JointDesign("segment_3", torque_limiter_nm=12.0),
    )
    return Blueprint(
        name="LUMBRICUS-AERATOR",
        task_type=TaskType.CLEANUP,
        biomimic="earthworm",
        actuator=actuator,
        joints=joints,
        payload_kg=0.8,
        energy_storage_j=600.0,
        can_pursue_targets=False,
        defense_policy=DefensePolicy(),
        geometry_notes="Segmented soft body; peristaltic motion; deposits beneficial microbes.",
    )


def blueprint_hummingbird_inspector() -> Blueprint:
    """Aerial inspection drone inspired by hummingbirds."""
    actuator = TendonActuator(
        name="HoverWing-06",
        max_torque_nm=5.0,
        max_tip_speed_mps=0.80,
        compliance=0.70,
    )
    joints = (
        JointDesign("wing_left", torque_limiter_nm=5.0),
        JointDesign("wing_right", torque_limiter_nm=5.0),
        JointDesign("camera_gimbal", torque_limiter_nm=2.0),
    )
    return Blueprint(
        name="TROCHILUS-INSPECTOR",
        task_type=TaskType.SENSE,
        biomimic="hummingbird",
        actuator=actuator,
        joints=joints,
        payload_kg=0.5,
        energy_storage_j=800.0,
        can_pursue_targets=False,
        defense_policy=DefensePolicy(),
        geometry_notes="Iridescent shell; silent hover capability; 360-degree camera mount.",
    )


def blueprint_turtle_transporter() -> Blueprint:
    """Heavy-duty transport robot inspired by sea turtles."""
    actuator = TendonActuator(
        name="FlipperDrive-07",
        max_torque_nm=35.0,
        max_tip_speed_mps=0.40,
        compliance=0.60,
    )
    joints = (
        JointDesign("flipper_front_left", torque_limiter_nm=35.0),
        JointDesign("flipper_front_right", torque_limiter_nm=35.0),
        JointDesign("flipper_back_left", torque_limiter_nm=25.0),
        JointDesign("flipper_back_right", torque_limiter_nm=25.0),
    )
    return Blueprint(
        name="CHELONIA-TRANSPORT",
        task_type=TaskType.TRANSPORT,
        biomimic="sea turtle",
        actuator=actuator,
        joints=joints,
        payload_kg=15.0,
        energy_storage_j=3000.0,
        can_pursue_targets=False,
        defense_policy=DefensePolicy(),
        geometry_notes="Reinforced shell doubles as cargo bay; amphibious design; solar panel carapace.",
    )


def blueprint_illegal_weaponized() -> Blueprint:
    """A purposely unsafe example to prove refusal works."""
    actuator = TendonActuator(
        name="BadAct-99",
        max_torque_nm=90.0,
        max_tip_speed_mps=2.0,
        compliance=0.10,
    )
    joints = (JointDesign("arm", torque_limiter_nm=90.0),)
    return Blueprint(
        name="NOPE-SPIKE-BOT",
        task_type=TaskType.TRANSPORT,
        biomimic="unknown",
        actuator=actuator,
        joints=joints,
        payload_kg=20.0,
        energy_storage_j=9000.0,
        can_pursue_targets=True,
        defense_policy=DefensePolicy(),
        geometry_notes="Front spike for deterrence; serrated edge for cutting vines.",
    )


ALL_SAFE_TEMPLATES = {
    "ant_cleaner": blueprint_ant_cleaner,
    "crab_sampler": blueprint_crab_water_sampler,
    "octopus_repair": blueprint_octopus_pipe_repair,
    "butterfly_pollinator": blueprint_butterfly_pollinator,
    "earthworm_aerator": blueprint_earthworm_aerator,
    "hummingbird_inspector": blueprint_hummingbird_inspector,
    "turtle_transporter": blueprint_turtle_transporter,
}
