"""
Digital Twin — Phase 5 Pydantic models.

Twins are simulation-only avatars of real-world projects, robots, devices,
buildings, or environments. They never drive hardware (the Robot Control
Layer in Phase 7 will). Their job in Phase 5 is to (a) hold structured
state, (b) feed the six simulation engines, and (c) accumulate council
deliberations into the Memory Bank.

Forward-compat hooks are deliberate: `integrations`, `cad_refs`, and
`hardware_binding` are placeholders that Weaver / Robot Control / CAD
ingest will populate in later phases.
"""
from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4

from pydantic import BaseModel, Field


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


# --- Enums ------------------------------------------------------------------
class TwinCategory(str, Enum):
    DEVICE = "device"
    ROBOT = "robot"
    VEHICLE = "vehicle"
    ENVIRONMENT = "environment"
    BUILDING = "building"
    MANUFACTURING_SYSTEM = "manufacturing_system"
    POWER_SYSTEM = "power_system"


class TwinStatus(str, Enum):
    DRAFT = "draft"           # registered, no state yet
    SPEC = "spec"             # state defined, no simulation run
    SIMULATED = "simulated"   # at least one simulation has run
    APPROVED = "approved"     # council deliberated and approved for build
    DEPRECATED = "deprecated"


class SimulationKind(str, Enum):
    BLUEPRINT = "blueprint"   # structural completeness
    ASSEMBLY = "assembly"     # ordering + step plan
    RESOURCE = "resource"     # BoM + energy budget
    FAILURE = "failure"       # single-points-of-failure, risk
    TIMELINE = "timeline"     # critical-path schedule
    COST = "cost"             # rolled-up cost estimate


# --- Sub-documents ----------------------------------------------------------
class Component(BaseModel):
    """A part of the twin. Components can themselves reference other twins,
    enabling composition (e.g. a robot twin uses a power_system twin).
    """
    id: str = Field(default_factory=lambda: uuid4().hex[:10])
    name: str
    quantity: float = 1.0
    unit: str = "unit"
    material: Optional[str] = None
    mass_kg: Optional[float] = None
    cost_per_unit: Optional[float] = None
    lead_time_days: Optional[float] = None
    twin_ref: Optional[str] = None     # forward-compat: composes another twin
    notes: Optional[str] = None


class Dimensions(BaseModel):
    length_m: Optional[float] = None
    width_m: Optional[float] = None
    height_m: Optional[float] = None
    volume_m3: Optional[float] = None
    mass_kg: Optional[float] = None


class EnergyProfile(BaseModel):
    peak_w: Optional[float] = None
    average_w: Optional[float] = None
    daily_wh: Optional[float] = None
    source: Optional[str] = None        # 'solar', 'grid', 'battery', etc.


class Dependency(BaseModel):
    from_component: str                 # component.id
    to_component: str                   # component.id
    kind: str = "requires"              # 'requires' | 'powers' | 'signals' | 'mounts'


class SensorInput(BaseModel):
    name: str
    kind: str                            # 'temperature' | 'pressure' | ...
    unit: str
    min_value: Optional[float] = None
    max_value: Optional[float] = None


class TwinOutput(BaseModel):
    name: str
    kind: str                            # 'data' | 'motion' | 'force' | 'media'
    unit: Optional[str] = None
    description: Optional[str] = None


class TwinState(BaseModel):
    """Versioned snapshot of the twin's specification."""
    status: TwinStatus = TwinStatus.SPEC
    components: List[Component] = Field(default_factory=list)
    materials: List[str] = Field(default_factory=list)
    dimensions: Optional[Dimensions] = None
    energy: Optional[EnergyProfile] = None
    dependencies: List[Dependency] = Field(default_factory=list)
    sensor_inputs: List[SensorInput] = Field(default_factory=list)
    outputs: List[TwinOutput] = Field(default_factory=list)
    # Future-compat — empty in Phase 5.
    integrations: Dict[str, Any] = Field(default_factory=dict)
    cad_refs: List[str] = Field(default_factory=list)
    hardware_binding: Optional[Dict[str, Any]] = None
    revision: int = 1
    updated_at: str = Field(default_factory=_utc_now)


class DigitalTwin(BaseModel):
    """Registry entry."""
    id: str = Field(default_factory=lambda: uuid4().hex)
    name: str
    category: TwinCategory
    owner_agent: str = "council"            # 'ajani' | 'minerva' | 'hermes' | 'council'
    related_project_id: Optional[str] = None
    description: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    state: TwinState = Field(default_factory=TwinState)
    last_simulation_id: Optional[str] = None
    last_deliberation_id: Optional[str] = None
    created_at: str = Field(default_factory=_utc_now)
    updated_at: str = Field(default_factory=_utc_now)


# --- Simulation result ------------------------------------------------------
class SimulationResult(BaseModel):
    """The structured output every simulator returns."""
    id: str = Field(default_factory=lambda: uuid4().hex)
    twin_id: str
    revision: int                       # of the state at sim time
    kind: SimulationKind
    ok: bool
    score: float = 0.0                  # 0..1 — higher is better
    findings: List[str] = Field(default_factory=list)     # human-readable
    warnings: List[str] = Field(default_factory=list)
    failures: List[str] = Field(default_factory=list)
    metrics: Dict[str, Any] = Field(default_factory=dict)
    timeline: Optional[List[Dict[str, Any]]] = None        # for ASSEMBLY/TIMELINE
    bom: Optional[List[Dict[str, Any]]] = None             # for RESOURCE/COST
    created_at: str = Field(default_factory=_utc_now)


class DeliberationVoice(BaseModel):
    persona: str                # ajani | minerva | hermes | council
    role: str                   # 'engineering' | 'science' | 'validation' | 'verdict'
    text: str
    flags: List[str] = Field(default_factory=list)


class CouncilDeliberation(BaseModel):
    id: str = Field(default_factory=lambda: uuid4().hex)
    twin_id: str
    simulation_id: Optional[str] = None
    voices: List[DeliberationVoice] = Field(default_factory=list)
    verdict: str = "pending"     # 'approve' | 'revise' | 'reject' | 'pending'
    final_text: str = ""
    created_at: str = Field(default_factory=_utc_now)
