"""Creative Studio contracts, jobs, and fail-closed execution for the ATLAS HUD."""
from dataclasses import asdict

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from creative_intelligence.craft_rubrics import MEDIUMS, QUALITY_PRINCIPLES, STORY, VISUAL_ART
from creative_intelligence.critic_council import CreativeCriticCouncil
from creative_intelligence.executor_registry import ExecutionRequest, ExecutorUnavailable, registry
from creative_intelligence.job_store import CreativeJobStore, VALID_STAGES
from creative_intelligence.reference_library.loader import CreativeReferenceLibrary
from services.creative_story_executor import register_story_executor
from services.creative_critique_executor import register_critique_executor
from services.creative_revision_executor import register_revision_executor
from services.creative_master_executor import register_master_executor

register_story_executor()
register_critique_executor()
register_revision_executor()
register_master_executor()

router = APIRouter(prefix="/api/creative-studio", tags=["creative-studio"])
job_store = CreativeJobStore()


class CreativeJobCreate(BaseModel):
    project_id: str = Field(min_length=1, max_length=160)
    stage: str
    artifact_id: str | None = Field(default=None, max_length=200)
    parent_job_id: str | None = Field(default=None, max_length=200)


class CreativeJobExecute(BaseModel):
    payload: dict = Field(default_factory=dict)


def _rubric_payload(rubric):
    return {"name": rubric.name, "passing_score": rubric.passing_score, "dimensions": [{"name": d.name, "question": d.question, "failure_signals": list(d.failure_signals)} for d in rubric.dimensions]}


def _reference_payload(reference):
    return {
        "id": reference.reference_id,
        "title": reference.title,
        "kind": reference.kind,
        "category": reference.category,
        "study": list(reference.study),
        "disciplines": list(reference.disciplines),
        "techniques": list(reference.techniques),
        "strengths": list(reference.strengths),
        "study_targets": list(reference.study_targets),
        "limitations": list(reference.limitations),
        "provenance": list(reference.provenance),
        "relationships": list(reference.relationships),
    }


@router.get("/references")
async def list_references(q: str = Query(default="", max_length=120)):
    library = CreativeReferenceLibrary.load_default()
    references = library.search(q)
    return {"query": q, "stats": library.stats(), "items": [_reference_payload(r) for r in references]}


@router.get("/references/retrieve")
async def retrieve_references(
    q: str = Query(min_length=1, max_length=240),
    limit: int = Query(default=12, ge=1, le=50),
    kind: str | None = Query(default=None),
):
    """Rank creative references with explainable matching evidence."""
    library = CreativeReferenceLibrary.load_default()
    try:
        matches = library.retrieve(q, limit=limit, kind=kind)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return {
        "query": q,
        "kind": kind,
        "limit": limit,
        "stats": library.stats(),
        "items": [
            {**_reference_payload(match.reference), "score": match.score, "matched_terms": list(match.matched_terms)}
            for match in matches
        ],
        "retrieval_contract": {
            "ranked": True,
            "explainable": True,
            "vector_ready": True,
            "principle_only": True,
        },
    }


@router.get("/references/synthesize")
async def synthesize_references(
    q: str = Query(min_length=1, max_length=240),
    limit: int = Query(default=4, ge=2, le=12),
    minimum_references: int = Query(default=2, ge=2, le=6),
):
    """Combine transferable principles from several references while preserving provenance and anti-imitation boundaries."""
    library = CreativeReferenceLibrary.load_default()
    try:
        synthesis = library.synthesize(q, limit=limit, minimum_references=minimum_references)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return {
        "query": synthesis.query,
        "references": [
            {
                **_reference_payload(match.reference),
                "score": match.score,
                "matched_terms": list(match.matched_terms),
            }
            for match in synthesis.references
        ],
        "principles": list(synthesis.principles),
        "study_targets": list(synthesis.study_targets),
        "limitations": list(synthesis.limitations),
        "provenance": list(synthesis.provenance),
        "synthesis_contract": {
            "multi_reference": True,
            "deterministic": True,
            "principle_only": True,
            "provenance_preserved": True,
            "anti_imitation_boundaries_preserved": True,
            "project_identity_overrides_reference_influence": True,
        },
    }


@router.get("/rubrics")
async def get_rubrics():
    return {"quality_principles": list(QUALITY_PRINCIPLES), "story": _rubric_payload(STORY), "visual_art": _rubric_payload(VISUAL_ART), "mediums": {n: _rubric_payload(r) for n, r in MEDIUMS.items()}}


@router.get("/critic-council")
async def get_critic_council_contract():
    return {"critics": [{"id": c, "focus": f} for c, f in CreativeCriticCouncil.CRITIC_FOCUS.items()], "policy": {"fail_closed": True, "specialist_objection_blocks": True, "missing_critic_blocks": True, "revision_required_for_failed_dimensions": True}}


@router.get("/quality-contract")
async def get_quality_contract():
    capabilities = registry.capabilities()
    return {"stages": ["brief", "references", "create", "critique", "revision", "master"], "creative_gate": ["reference_context", "originality", "critic_council", "revision_re_evaluation"], "master_gate": ["creative_approval", "story_quality", "art_style", "visual_quality", "continuity", "originality"], "job_api_enabled": True, "executor_capabilities": capabilities, "generation_enabled": capabilities["create"], "reason": "Only explicitly registered real executors can advance queued jobs."}


@router.post("/jobs", status_code=201)
async def create_job(payload: CreativeJobCreate):
    if payload.stage not in VALID_STAGES:
        raise HTTPException(status_code=422, detail=f"stage must be one of: {', '.join(VALID_STAGES)}")
    if payload.parent_job_id and job_store.get(payload.parent_job_id) is None:
        raise HTTPException(status_code=404, detail="parent creative job not found")
    return asdict(job_store.create(project_id=payload.project_id, stage=payload.stage, artifact_id=payload.artifact_id, parent_job_id=payload.parent_job_id))


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


@router.post("/jobs/{job_id}/execute")
async def execute_job(job_id: str, body: CreativeJobExecute):
    job = job_store.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="creative job not found")
    if job.status != "queued":
        raise HTTPException(status_code=409, detail=f"creative job is {job.status}, not queued")
    if not registry.available(job.stage):
        blocked = job_store.transition(job.id, status="blocked", blockers=[f"executor_unavailable:{job.stage}"])
        return asdict(blocked)
    running = job_store.transition(job.id, status="running")
    try:
        result = await registry.execute(ExecutionRequest(job_id=running.id, project_id=running.project_id, stage=running.stage, artifact_id=running.artifact_id, payload=body.payload))
    except ExecutorUnavailable as exc:
        blocked = job_store.transition(job.id, status="blocked", blockers=[str(exc)])
        return asdict(blocked)
    except Exception as exc:
        failed = job_store.transition(job.id, status="failed", blockers=[f"executor_error:{type(exc).__name__}"], result={"error": str(exc)})
        return asdict(failed)
    completed = job_store.transition(job.id, status="completed", result={"artifact_id": result.artifact_id, "executor": result.executor, "output": dict(result.output)})
    return asdict(completed)
