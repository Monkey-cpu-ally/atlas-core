from __future__ import annotations
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Literal

SafetyTier = Literal["LOW", "MEDIUM", "HIGH"]
ProjectDomain = Literal["ROBOTICS", "ENERGY", "MATERIALS", "UI_SYSTEM", "BIOMED_SIM_ONLY"]

class Requirement(BaseModel):
    id: str
    statement: str
    metric: Optional[str] = None
    target: Optional[str] = None

class MaterialSpec(BaseModel):
    name: str
    use: str
    justification: str

class ComponentSpec(BaseModel):
    name: str
    qty: int = 1
    role: str
    notes: Optional[str] = None

class ToolSpec(BaseModel):
    name: str
    purpose: str

class FailureMode(BaseModel):
    mode: str
    cause: str
    effect: str
    mitigation: str
    severity: Literal["LOW", "MED", "HIGH"]

class ModuleBlock(BaseModel):
    name: str
    purpose: str
    inputs: List[str] = Field(default_factory=list)
    outputs: List[str] = Field(default_factory=list)
    components: List[ComponentSpec] = Field(default_factory=list)

class BuildStep(BaseModel):
    step: int
    title: str
    instructions: List[str]
    verification: List[str]

class BlueprintPacket(BaseModel):
    blueprint_id: str
    version: str
    title: str
    domain: ProjectDomain
    safety_tier: SafetyTier
    created_at: str

    objective: str
    assumptions: List[str] = Field(default_factory=list)

    requirements: List[Requirement] = Field(default_factory=list)
    architecture: List[ModuleBlock] = Field(default_factory=list)

    materials: List[MaterialSpec] = Field(default_factory=list)
    components: List[ComponentSpec] = Field(default_factory=list)
    tools: List[ToolSpec] = Field(default_factory=list)

    power_flow: List[str] = Field(default_factory=list)
    control_logic: List[str] = Field(default_factory=list)

    fabrication_steps: List[BuildStep] = Field(default_factory=list)
    test_plan: List[str] = Field(default_factory=list)

    failure_modes: List[FailureMode] = Field(default_factory=list)
    revision_notes: List[str] = Field(default_factory=list)

class BlueprintRequest(BaseModel):
    project_key: Literal["GREEN_BOT", "MEDUSA_ARMS", "METAL_FLOWERS", "HYDROGEN_POWER", "MORPHING_STRUCTURES", "ATOMIC_UI"]
    constraints: Dict[str, str] = Field(default_factory=dict)
    version: str = "0.1"
