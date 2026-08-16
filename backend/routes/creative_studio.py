"""Read-only Creative Studio contracts for the ATLAS HUD.

Mutation/generation endpoints are intentionally deferred until their production
services have durable project persistence. These routes expose real reference,
critic, rubric, and quality-gate metadata without pretending to generate work.
"""
from fastapi import APIRouter, Query

from creative_intelligence.craft_rubrics import MEDIUMS, QUALITY_PRINCIPLES, STORY, VISUAL_ART
from creative_intelligence.critic_council import CreativeCriticCouncil
from creative_intelligence.reference_library.loader import CreativeReferenceLibrary

router = APIRouter(prefix="/api/creative-studio", tags=["creative-studio"])


def _rubric_payload(rubric):
    return {
        "name": rubric.name,
        "passing_score": rubric.passing_score,
        "dimensions": [
            {
                "name": dimension.name,
                "question": dimension.question,
                "failure_signals": list(dimension.failure_signals),
            }
            for dimension in rubric.dimensions
        ],
    }


@router.get("/references")
async def list_references(q: str = Query(default="", max_length=120)):
    library = CreativeReferenceLibrary.load_default()
    references = library.search(q)
    return {
        "query": q,
        "stats": library.stats(),
        "items": [
            {
                "id": ref.reference_id,
                "title": ref.title,
                "kind": ref.kind,
                "category": ref.category,
                "study": list(ref.study),
            }
            for ref in references
        ],
    }


@router.get("/rubrics")
async def get_rubrics():
    return {
        "quality_principles": list(QUALITY_PRINCIPLES),
        "story": _rubric_payload(STORY),
        "visual_art": _rubric_payload(VISUAL_ART),
        "mediums": {name: _rubric_payload(rubric) for name, rubric in MEDIUMS.items()},
    }


@router.get("/critic-council")
async def get_critic_council_contract():
    return {
        "critics": [
            {"id": critic, "focus": focus}
            for critic, focus in CreativeCriticCouncil.CRITIC_FOCUS.items()
        ],
        "policy": {
            "fail_closed": True,
            "specialist_objection_blocks": True,
            "missing_critic_blocks": True,
            "revision_required_for_failed_dimensions": True,
        },
    }


@router.get("/quality-contract")
async def get_quality_contract():
    return {
        "stages": ["brief", "references", "create", "critique", "revision", "master"],
        "creative_gate": ["reference_context", "originality", "critic_council", "revision_re_evaluation"],
        "master_gate": ["creative_approval", "story_quality", "art_style", "visual_quality", "continuity", "originality"],
        "generation_enabled": False,
        "reason": "Production mutation endpoints require durable Creative Studio project persistence before HUD activation.",
    }
