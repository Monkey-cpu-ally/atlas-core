"""Creative Studio contracts and persistent job lifecycle for the ATLAS HUD.

Job creation records workflow intent only. Jobs remain queued until a real production
service explicitly starts and completes them; this API never fabricates generation.
"""
from dataclasses import asdict

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from creative_intelligence.craft_rubrics import MEDIUMS, QUALITY_PRINCIPLES, STORY, VISUAL_ART
from creative_intelligence.critic_council import CreativeCriticCouncil
from creative_intelligence.job_store import CreativeJobStore, VALID_STAGES
from creative_intelligence.reference_library.loader import CreativeReferenceLibrary

router = APIRouter(prefix="/api/creative-studio", tags=["creative-studio"])
job_store = CreativeJobStore()


class CreativeJobCreate(BaseModel):
    project_id: str = Field(min_length=1, max_length=160)
    stage: str
    artifact_id: str | None = Field(default=None, max_length=200)
    parent_job_id: str | None = Field(default=None, max_length=200)


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
        "job_api_enabled": True,
        "generation_enabled": False,
        "reason": "Persistent workflow jobs are live; production executors are enabled only when real generation/review services are connected.",
    }


@router.post("/jobs", status_code=201)
async def create_job(payload: CreativeJobCreate):
    if payload.stage not in VALID_STAGES:
        raise HTTPException(status_code=422, detail=f"stage must be one of: {', '.join(VALID_STAGES)}")
    if payload.parent_job_id and job_store.get(payload.parent_job_id) is None:
        raise HTTPException(status_code=404, detail="parent creative job not found")
    job = job_store.create(
        project_id=payload.project_id,
        stage=payload.stage,
        artifact_id=payload.artifact_id,
        parent_job_id=payload.parent_job_id,
    )
    return asdict(job)


@router.get("/jobs")
async def list_jobs(project_id: str | None = Query(default=None, max_length=160)):
    jobs = job_store.list(project_id=project_id)
    return {"total": len(jobs), "items": [asdict(job) for job in jobs]}


@router.get("/jobs/{job_id}")
async def get_job(job_id: str):
    job = job_store.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="creative job not found")
    return asdict(job)
