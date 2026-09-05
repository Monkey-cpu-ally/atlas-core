"""Versioned contracts for the HUD Intelligence Loop V1."""
from __future__ import annotations

from typing import List, Literal, Optional
from uuid import uuid4

from pydantic import BaseModel, Field

from models.persona_models import CouncilSubVoice, Persona

HudIntent = Literal["chat", "teach", "explain_resource", "deliberate"]
LearningLevel = Literal[
    "foundation", "beginner", "intermediate", "advanced",
    "undergraduate", "graduate", "research",
]
HudRunStatus = Literal[
    "queued", "retrieving", "reasoning", "complete", "partial", "failed", "cancelled",
]


class HudClientContext(BaseModel):
    surface: Literal["core", "persona_chat", "bookshelf", "teaching", "council"]
    reduced_motion: bool = False


class HudIntelligenceRequest(BaseModel):
    request_id: str = Field(default_factory=lambda: uuid4().hex, min_length=8, max_length=128)
    intent: HudIntent = "chat"
    persona: Persona
    message: str = Field(..., min_length=1, max_length=8000)
    session_id: Optional[str] = Field(default=None, max_length=128)
    project_id: Optional[str] = Field(default=None, max_length=128)
    learning_level: LearningLevel = "advanced"
    resource_ids: List[str] = Field(default_factory=list, max_length=20)
    client_context: HudClientContext


class HudEvidence(BaseModel):
    record_id: str
    kind: Literal["knowledge", "memory", "resource", "project"]
    title: str
    verification_status: Literal["verified", "provisional", "unknown"] = "unknown"
    source_url: Optional[str] = None


class HudConfidence(BaseModel):
    label: Literal["high", "medium", "low", "unknown"] = "unknown"
    basis: List[str] = Field(default_factory=list)


class HudMemoryResult(BaseModel):
    turn_saved: bool = False
    learning_state_saved: bool = False


class HudNextStep(BaseModel):
    label: str
    intent: HudIntent
    requires_confirmation: bool = True


class HudProviderAudit(BaseModel):
    name: Optional[str] = None
    model: Optional[str] = None
    fallback_reason: Optional[str] = None


class HudError(BaseModel):
    code: str
    message: str
    retryable: bool = False


class HudIntelligenceResponse(BaseModel):
    request_id: str
    run_id: str
    status: HudRunStatus
    session_id: Optional[str] = None
    message_id: Optional[str] = None
    persona: Persona
    learning_level: LearningLevel
    answer: str = ""
    council_voices: List[CouncilSubVoice] = Field(default_factory=list)
    evidence: List[HudEvidence] = Field(default_factory=list)
    confidence: HudConfidence = Field(default_factory=HudConfidence)
    retrieval_mode: Literal["semantic", "lexical", "hashed_fallback", "none"] = "none"
    memory: HudMemoryResult = Field(default_factory=HudMemoryResult)
    next_step: Optional[HudNextStep] = None
    provider: HudProviderAudit = Field(default_factory=HudProviderAudit)
    error: Optional[HudError] = None

