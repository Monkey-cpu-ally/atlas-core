"""FastAPI endpoints for modular persona suggestion and validation."""

from fastapi import APIRouter
from pydantic import BaseModel, Field

from atlas_core_new.ai_routing.personas import PersonaName
from atlas_core_new.ai_routing.service import PersonaRoutingService


router = APIRouter(tags=["ai-routing"])
routing_service = PersonaRoutingService()


class SuggestRequest(BaseModel):
    goal: str = Field(..., min_length=1, max_length=4000)
    constraints: list[str] = Field(default_factory=list)
    persona: PersonaName | None = None


class SuggestResponse(BaseModel):
    persona: PersonaName
    route_reason: str
    route_scores: dict[str, int]
    suggestion: str
    checklist: list[str]


class ValidateRequest(BaseModel):
    goal: str = Field(..., min_length=1, max_length=4000)
    proposal: str = Field(..., min_length=1, max_length=8000)
    persona: PersonaName | None = None


class ValidateResponse(BaseModel):
    persona: PersonaName
    route_reason: str
    route_scores: dict[str, int]
    valid: bool
    score: float
    strengths: list[str]
    issues: list[str]
    next_steps: list[str]


@router.post("/suggest", response_model=SuggestResponse)
def suggest(req: SuggestRequest) -> SuggestResponse:
    persona_name, decision, suggestion_text, checklist = routing_service.suggest(
        goal=req.goal,
        constraints=req.constraints,
        persona=req.persona,
    )
    return SuggestResponse(
        persona=persona_name,
        route_reason=decision.reason,
        route_scores=dict(decision.scores),
        suggestion=suggestion_text,
        checklist=checklist,
    )


@router.post("/validate", response_model=ValidateResponse)
def validate(req: ValidateRequest) -> ValidateResponse:
    persona_name, decision, report, is_valid = routing_service.validate(
        goal=req.goal,
        proposal=req.proposal,
        persona=req.persona,
    )
    return ValidateResponse(
        persona=persona_name,
        route_reason=decision.reason,
        route_scores=dict(decision.scores),
        valid=is_valid,
        score=report.score,
        strengths=report.strengths,
        issues=report.issues,
        next_steps=report.next_steps,
    )
