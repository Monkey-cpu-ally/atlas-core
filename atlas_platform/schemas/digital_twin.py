"""
ATLAS Digital Twin schemas.

These models represent projects as structured systems with subsystems,
components, materials, sensors, simulation questions, and test records.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from atlas_platform.schemas.base import ConfidenceLevel


class ComponentType(str, Enum):
    STRUCTURE = "structure"
    SENSOR = "sensor"
    ACTUATOR = "actuator"
    CONTROLLER = "controller"
    POWER = "power"
    MATERIAL = "material"
    SOFTWARE = "software"
    INTERFACE = "interface"


class MaterialType(str, Enum):
    METAL = "metal"
    POLYMER = "polymer"
    CERAMIC = "ceramic"
    COMPOSITE = "composite"
    BIOLOGICAL = "biological"
    ELECTRONIC = "electronic"
    UNKNOWN = "unknown"


class SimulationType(str, Enum):
    MASS = "mass"
    POWER = "power"
    HEAT = "heat"
    LOAD = "load"
    MOTION = "motion"
    ELECTRICAL = "electrical"
    CONTROL = "control"
    FLUID = "fluid"
    MANUFACTURING = "manufacturing"
    RISK = "risk"


class TestResult(str, Enum):
    PASS = "pass"
    FAIL = "fail"
    INCONCLUSIVE = "inconclusive"


@dataclass
class DigitalTwinSubsystem:
    subsystem_id: str
    project_id: str
    name: str
    function: str
    component_ids: List[str] = field(default_factory=list)


@dataclass
class DigitalTwinComponent:
    component_id: str
    subsystem_id: str
    name: str
    component_type: ComponentType
    function: str
    material: Optional[str] = None
    estimated_mass_g: Optional[float] = None
    estimated_cost_usd: Optional[float] = None
    power_draw_watts: Optional[float] = None
    failure_modes: List[str] = field(default_factory=list)


@dataclass
class DigitalTwinMaterial:
    material_id: str
    name: str
    material_type: MaterialType
    properties_known: List[str] = field(default_factory=list)
    properties_unknown: List[str] = field(default_factory=list)
    risks: List[str] = field(default_factory=list)
    sustainability_notes: Optional[str] = None


@dataclass
class SimulationQuestion:
    question_id: str
    project_id: str
    question: str
    simulation_type: SimulationType
    required_data: List[str] = field(default_factory=list)
    confidence: ConfidenceLevel = ConfidenceLevel.LOW


@dataclass
class SimulationResult:
    simulation_id: str
    project_id: str
    simulation_type: SimulationType
    inputs: Dict[str, Any]
    outputs: Dict[str, Any]
    assumptions: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    confidence: ConfidenceLevel = ConfidenceLevel.LOW
    recommended_next_step: Optional[str] = None


@dataclass
class DigitalTwinTestRecord:
    test_id: str
    project_id: str
    test_name: str
    purpose: str
    prototype_level: int
    result: TestResult
    data_recorded: Dict[str, Any] = field(default_factory=dict)
    lessons_learned: Optional[str] = None
    model_updates_needed: List[str] = field(default_factory=list)
