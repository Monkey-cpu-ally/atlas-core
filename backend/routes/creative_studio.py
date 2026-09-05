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
from services.art_study_runtime import run_art_study
from services import art_study_provider_registry
register_story_executor(); register_critique_executor(); register_revision_executor(); register_master_executor()
router=APIRouter(prefix="/api/creative-studio",tags=["creative-studio"]); job_store=CreativeJobStore()
class CreativeJobCreate(BaseModel):
    project_id:str=Field(min_length=1,max_length=160); stage:str; artifact_id:str|None=Field(default=None,max_length=200); parent_job_id:str|None=Field(default=None,max_length=200)
class CreativeJobExecute(BaseModel): payload:dict=Field(default_factory=dict)
class ArtStudyRequest(BaseModel):
    source_reference:str=Field(min_length=1,max_length=500)
    source:dict
    request:dict=Field(default_factory=dict)
    project_identity:str=Field(min_length=1,max_length=240)
    project_constraints:list[str]=Field(min_length=1)
    minimum_confidence:float=Field(default=0.60,ge=0.0,le=1.0)
def _rubric_payload(r): return {"name":r.name,"passing_score":r.passing_score,"dimensions":[{"name":d.name,"question":d.question,"failure_signals":list(d.failure_signals)} for d in r.dimensions]}
def _reference_payload(r): return {"id":r.reference_id,"title":r.title,"kind":r.kind,"category":r.category,"study":list(r.study),"disciplines":list(r.disciplines),"techniques":list(r.techniques),"strengths":list(r.strengths),"study_targets":list(r.study_targets),"limitations":list(r.limitations),"provenance":list(r.provenance),"relationships":list(r.relationships)}
@router.get("/references")
async def list_references(q:str=Query(default="",max_length=120)):
    library=CreativeReferenceLibrary.load_default(); references=library.search(q); return {"query":q,"stats":library.stats(),"items":[_reference_payload(r) for r in references]}
@router.get("/references/retrieve")
async def retrieve_references(q:str=Query(min_length=1,max_length=240),limit:int=Query(default=12,ge=1,le=50),kind:str|None=Query(default=None)):
    library=CreativeReferenceLibrary.load_default()
    try: matches=library.retrieve(q,limit=limit,kind=kind)
    except ValueError as exc: raise HTTPException(status_code=422,detail=str(exc)) from exc
    return {"query":q,"kind":kind,"limit":limit,"stats":library.stats(),"items":[{**_reference_payload(m.reference),"score":m.score,"matched_terms":list(m.matched_terms)} for m in matches],"retrieval_contract":{"ranked":True,"explainable":True,"vector_ready":True,"principle_only":True}}
@router.get("/references/synthesize")
async def synthesize_references(q:str=Query(min_length=1,max_length=240),limit:int=Query(default=4,ge=2,le=12),minimum_references:int=Query(default=2,ge=2,le=6),project_identity:str=Query(default="",max_length=240),project_constraints:list[str]|None=Query(default=None)):
    """Synthesize references from creative intent; preserve project constraints strictly as boundaries."""
    library=CreativeReferenceLibrary.load_default()
    try: synthesis=library.synthesize(q,limit=limit,minimum_references=minimum_references,project_identity=project_identity,project_constraints=project_constraints or ())
    except ValueError as exc: raise HTTPException(status_code=422,detail=str(exc)) from exc
    return {"query":synthesis.query,"project_identity":synthesis.project_identity,"project_constraints":list(synthesis.project_constraints),"diversity_dimensions":list(synthesis.diversity_dimensions),"references":[{**_reference_payload(m.reference),"score":m.score,"matched_terms":list(m.matched_terms)} for m in synthesis.references],"principles":list(synthesis.principles),"study_targets":list(synthesis.study_targets),"limitations":list(synthesis.limitations),"provenance":list(synthesis.provenance),"synthesis_contract":{"multi_reference":True,"deterministic":True,"principle_only":True,"provenance_preserved":True,"anti_imitation_boundaries_preserved":True,"project_identity_overrides_reference_influence":True,"project_constraints_preserved":True,"constraints_are_not_inspiration":True,"diversity_aware_selection":True}}
@router.get("/art-study/contract")
async def get_art_study_contract():
    return {"provider":art_study_provider_registry.contract(),"principles_only":True,"direct_imitation_forbidden":True,"project_identity_authoritative":True,"rights_declaration_required":True,"validated_evidence_required":True}
@router.post("/art-study/analyze")
async def analyze_art_study(body:ArtStudyRequest):
    provider=art_study_provider_registry.get()
    if provider is None: raise HTTPException(status_code=503,detail="Art Study vision provider is not configured")
    try:
        return run_art_study(provider=provider,source_reference=body.source_reference,request=body.request,source=body.source,project_identity=body.project_identity,project_constraints=body.project_constraints,minimum_confidence=body.minimum_confidence)
    except ValueError as exc: raise HTTPException(status_code=422,detail=str(exc)) from exc
@router.get("/rubrics")
async def get_rubrics(): return {"quality_principles":list(QUALITY_PRINCIPLES),"story":_rubric_payload(STORY),"visual_art":_rubric_payload(VISUAL_ART),"mediums":{n:_rubric_payload(r) for n,r in MEDIUMS.items()}}
@router.get("/critic-council")
async def get_critic_council_contract(): return {"critics":[{"id":c,"focus":f} for c,f in CreativeCriticCouncil.CRITIC_FOCUS.items()],"policy":{"fail_closed":True,"specialist_objection_blocks":True,"missing_critic_blocks":True,"revision_required_for_failed_dimensions":True}}
@router.get("/quality-contract")
async def get_quality_contract():
    capabilities=registry.capabilities(); return {"stages":["brief","references","create","critique","revision","master"],"creative_gate":["reference_context","originality","critic_council","revision_re_evaluation"],"master_gate":["creative_approval","story_quality","art_style","visual_quality","continuity","originality"],"job_api_enabled":True,"executor_capabilities":capabilities,"generation_enabled":capabilities["create"],"reason":"Only explicitly registered real executors can advance queued jobs."}
@router.post("/jobs",status_code=201)
async def create_job(payload:CreativeJobCreate):
    if payload.stage not in VALID_STAGES: raise HTTPException(status_code=422,detail=f"stage must be one of: {', '.join(VALID_STAGES)}")
    if payload.parent_job_id and job_store.get(payload.parent_job_id) is None: raise HTTPException(status_code=404,detail="parent creative job not found")
    return asdict(job_store.create(project_id=payload.project_id,stage=payload.stage,artifact_id=payload.artifact_id,parent_job_id=payload.parent_job_id))
@router.get("/jobs")
async def list_jobs(project_id:str|None=Query(default=None,max_length=160)):
    jobs=job_store.list(project_id=project_id); return {"total":len(jobs),"items":[asdict(j) for j in jobs]}
@router.get("/jobs/{job_id}")
async def get_job(job_id:str):
    job=job_store.get(job_id)
    if job is None: raise HTTPException(status_code=404,detail="creative job not found")
    return asdict(job)
@router.post("/jobs/{job_id}/execute")
async def execute_job(job_id:str,body:CreativeJobExecute):
    job=job_store.get(job_id)
    if job is None: raise HTTPException(status_code=404,detail="creative job not found")
    if job.status!="queued": raise HTTPException(status_code=409,detail=f"creative job is {job.status}, not queued")
    if not registry.available(job.stage): return asdict(job_store.transition(job.id,status="blocked",blockers=[f"executor_unavailable:{job.stage}"]))
    running=job_store.transition(job.id,status="running")
    try: result=await registry.execute(ExecutionRequest(job_id=running.id,project_id=running.project_id,stage=running.stage,artifact_id=running.artifact_id,payload=body.payload))
    except ExecutorUnavailable as exc: return asdict(job_store.transition(job.id,status="blocked",blockers=[str(exc)]))
    except Exception as exc: return asdict(job_store.transition(job.id,status="failed",blockers=[f"executor_error:{type(exc).__name__}"],result={"error":str(exc)}))
    return asdict(job_store.transition(job.id,status="completed",result={"artifact_id":result.artifact_id,"executor":result.executor,"output":dict(result.output)}))
