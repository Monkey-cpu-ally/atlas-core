"""
Weaver — Phase 6 Pydantic models.

Weaver is ATLAS's manufacturing and assembly planning intelligence. It
turns ideas + blueprints into structured build plans backed by a parts
library and Phase-5 Digital Twins. Weaver does NOT execute anything — it
plans.

Key types:
  * Part            — entry in the parts library
  * BlueprintInput  — parsed-or-raw blueprint payload (text, json, parts list)
  * BuildPlan       — assembly order + tools + difficulty + supplies
  * ManufacturingPlan — cost / timeline / resource roll-up
  * FailurePrediction — missing-parts / weak-designs / risk score
  * WeaverPlan      — the whole result document tying them together
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
class PartCategory(str, Enum):
    COMPONENT  = "component"     # generic mechanical sub-assembly
    MATERIAL   = "material"      # raw stock (sheet, bar, filament)
    FASTENER   = "fastener"      # bolts, nuts, rivets, clips
    ELECTRONIC = "electronic"    # PCBs, ICs, passives
    SENSOR     = "sensor"
    ACTUATOR   = "actuator"      # motors, solenoids, servos
    TOOL       = "tool"          # required to build, not consumed
    CONSUMABLE = "consumable"    # solder, glue, lubricant


class Difficulty(str, Enum):
    TRIVIAL = "trivial"          # < 1h, household tools
    EASY    = "easy"             # 1-4h, common workshop tools
    MEDIUM  = "medium"           # 4-16h, soldering / 3d-print
    HARD    = "hard"             # 16-48h, machining / PCB work
    EXPERT  = "expert"           # > 48h, custom tooling required


class BlueprintFormat(str, Enum):
    TEXT       = "text"          # free-form description
    JSON       = "json"          # structured spec (parts + relations)
    CAD_EXPORT = "cad_export"    # placeholder for future CAD ingest
    DIAGRAM    = "diagram"       # placeholder for image/PDF diagram OCR


# --- Sub-documents ----------------------------------------------------------
class Part(BaseModel):
    id: str = Field(default_factory=lambda: uuid4().hex[:12])
    name: str
    category: PartCategory
    description: Optional[str] = None
    material: Optional[str] = None
    spec: Dict[str, Any] = Field(default_factory=dict)
    unit: str = "unit"
    default_cost: Optional[float] = None
    default_lead_time_days: Optional[float] = None
    suppliers: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    created_at: str = Field(default_factory=_utc_now)
    updated_at: str = Field(default_factory=_utc_now)


class BlueprintRelation(BaseModel):
    from_part: str        # part name or ref id
    to_part: str
    relation: str = "connects_to"   # connects_to | mounts | powers | signals


class BlueprintInput(BaseModel):
    format: BlueprintFormat = BlueprintFormat.TEXT
    title: Optional[str] = None
    description: Optional[str] = None
    text: Optional[str] = None
    parts: List[Dict[str, Any]] = Field(default_factory=list)
    relations: List[BlueprintRelation] = Field(default_factory=list)


class ExtractedPart(BaseModel):
    """A part identified from a blueprint, possibly matched to the library."""
    name: str
    category: PartCategory
    quantity: float = 1.0
    unit: str = "unit"
    library_part_id: Optional[str] = None    # null if unknown to library
    library_match_confidence: float = 0.0
    raw_text: Optional[str] = None
    notes: Optional[str] = None


class AssemblyStep(BaseModel):
    step: int
    description: str
    component_ids: List[str] = Field(default_factory=list)
    tools_required: List[str] = Field(default_factory=list)
    estimated_minutes: float = 0.0
    cautions: List[str] = Field(default_factory=list)


class BuildPlan(BaseModel):
    assembly_order: List[AssemblyStep] = Field(default_factory=list)
    tools_required: List[str] = Field(default_factory=list)
    materials_required: List[Dict[str, Any]] = Field(default_factory=list)
    difficulty: Difficulty = Difficulty.MEDIUM
    total_estimated_minutes: float = 0.0


class ManufacturingPlan(BaseModel):
    total_cost: float = 0.0
    materials_cost: float = 0.0
    labour_cost: float = 0.0
    critical_path_days: float = 0.0
    longest_lead_part: Optional[str] = None
    bom: List[Dict[str, Any]] = Field(default_factory=list)
    resource_notes: List[str] = Field(default_factory=list)


class FailurePrediction(BaseModel):
    risk_score: float = 0.0                  # 0..1 (higher = riskier)
    missing_parts: List[str] = Field(default_factory=list)
    weak_designs: List[str] = Field(default_factory=list)
    single_points_of_failure: List[str] = Field(default_factory=list)
    notes: List[str] = Field(default_factory=list)


class CouncilOutcome(BaseModel):
    verdict: str = "pending"     # approve | revise | reject | pending
    final_text: str = ""
    voices: List[Dict[str, Any]] = Field(default_factory=list)


class WeaverPlan(BaseModel):
    id: str = Field(default_factory=lambda: uuid4().hex)
    title: str
    description: Optional[str] = None
    owner_agent: str = "ajani"
    related_project_id: Optional[str] = None
    blueprint: BlueprintInput
    parts_extracted: List[ExtractedPart] = Field(default_factory=list)
    twin_id: Optional[str] = None                 # the auto-spawned digital twin
    build_plan: BuildPlan = Field(default_factory=BuildPlan)
    manufacturing_plan: ManufacturingPlan = Field(default_factory=ManufacturingPlan)
    failure_prediction: FailurePrediction = Field(default_factory=FailurePrediction)
    council: Optional[CouncilOutcome] = None
    created_at: str = Field(default_factory=_utc_now)
    updated_at: str = Field(default_factory=_utc_now)
