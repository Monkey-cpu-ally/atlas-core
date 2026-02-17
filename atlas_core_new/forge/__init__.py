"""Hephaestus-class Forge - Split Authority + Cauldron-Lite + Non-Lethal Charter."""

from .core import (
    Decision,
    Severity,
    TaskType,
    DefensiveMode,
    HEPHAESTUS_CROSSED_THE_LINE,
)
from .charter import NonLethalDefenseCharter
from .safety import SafetyKernel, SafetyViolation
from .actuators import TendonActuator, JointDesign
from .blueprints import Blueprint, DefensePolicy
from .authority import (
    Reviewer,
    ReviewResult,
    AjaniStrategist,
    MinervaEthics,
    HermesFabrication,
    HumanGate,
    RefusalEngine,
)
from .factory import CauldronLiteFactory, FederatedOrchestrator
from .templates import (
    blueprint_ant_cleaner,
    blueprint_crab_water_sampler,
    blueprint_octopus_pipe_repair,
)

__all__ = [
    "Decision",
    "Severity",
    "TaskType",
    "DefensiveMode",
    "HEPHAESTUS_CROSSED_THE_LINE",
    "NonLethalDefenseCharter",
    "SafetyKernel",
    "SafetyViolation",
    "TendonActuator",
    "JointDesign",
    "Blueprint",
    "DefensePolicy",
    "Reviewer",
    "ReviewResult",
    "AjaniStrategist",
    "MinervaEthics",
    "HermesFabrication",
    "HumanGate",
    "RefusalEngine",
    "CauldronLiteFactory",
    "FederatedOrchestrator",
    "blueprint_ant_cleaner",
    "blueprint_crab_water_sampler",
    "blueprint_octopus_pipe_repair",
]
