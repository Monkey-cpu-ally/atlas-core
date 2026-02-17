"""Typed models for Atlas hybrid orchestration flow."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

ModeType = Literal["mentor", "warrior", "builder"]
IntentType = Literal[
    "blueprint_request",
    "learning_request",
    "security_request",
    "general_planning",
    "image_blueprint_extraction",
]
PipelineStage = Literal["blueprint", "build", "modify"]
ValidationStatus = Literal["ok", "flagged", "blocked"]
SafetyMode = Literal["normal", "simulation_only", "blocked"]


class AtlasOrchestrateRequest(BaseModel):
    project: str = Field(..., min_length=1, max_length=128)
    user_input: str = Field(..., min_length=1, max_length=12000)
    mode: ModeType = "mentor"
    context: dict[str, Any] | None = None
    pipeline_stage: PipelineStage | None = None


class AjaniOutput(BaseModel):
    persona: Literal["ajani"] = "ajani"
    summary: str
    structured_plan: list[str]
    component_breakdown: list[str]
    constraints: list[str]
    measurable_requirements: list[str]
    risk_list: list[str]
    test_plan: list[str]
    parts_list: list[str]
    artifacts: dict[str, Any] = Field(default_factory=dict)


class MinervaOutput(BaseModel):
    persona: Literal["minerva"] = "minerva"
    summary: str
    teaching_goal: str
    lego_steps: list[str]
    clarity_notes: list[str]
    teach_back_questions: list[str]
    cultural_context: str | None = None


class HermesOutput(BaseModel):
    persona: Literal["hermes"] = "hermes"
    summary: str
    validation_status: ValidationStatus
    safety_mode: SafetyMode
    checks: list[str]
    flags: list[str]
    blocked_reasons: list[str]
    enforced_constraints: list[str]


class ProjectMemorySnapshot(BaseModel):
    project: str
    current_version: str
    pipeline_stage: PipelineStage
    last_blueprint: dict[str, Any] | None
    parts_list: list[str]
    tasks: list[str]
    decisions: list[str]
    artifacts: dict[str, Any]
    updated_at: str


class AtlasOrchestrateResponse(BaseModel):
    project: str
    mode: ModeType
    intent: IntentType
    intent_reason: str
    pipeline_stage: PipelineStage
    validation_status: ValidationStatus
    ajani: AjaniOutput
    minerva: MinervaOutput
    hermes: HermesOutput
    project_memory: ProjectMemorySnapshot


class ProjectSummary(BaseModel):
    project: str
    current_version: str
    pipeline_stage: PipelineStage
    updated_at: str

