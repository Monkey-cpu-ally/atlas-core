"""ATLAS Discovery Engine routes."""
from __future__ import annotations
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from services import discovery_approval_pipeline as approval
from services import discovery_engine as engine

router = APIRouter(prefix="/api/discovery-engine", tags=["ATLAS Discovery Engine"])

class InvestigationRequest(BaseModel):
    title: str = Field(min_length=3,max_length=300); question: str = Field(min_length=5,max_length=5000)
    knowledge_layer: str="FRONTIER"; owner_ai: str="Council"; subjects: List[str]=Field(default_factory=list)
    related_projects: List[str]=Field(default_factory=list); mission_id: Optional[str]=None
class HypothesisRequest(BaseModel):
    statement: str=Field(min_length=5,max_length=5000); rationale: str=Field(min_length=5,max_length=5000)
    falsification_criteria: List[str]=Field(min_length=1); assumptions: List[str]=Field(default_factory=list)
class AnalogyRequest(BaseModel):
    source_subject: str=Field(min_length=2); target_subject: str=Field(min_length=2); source_concept: str=Field(min_length=3)
    mechanism: str=Field(min_length=3); transferable_principle: str=Field(min_length=3); constraints: List[str]=Field(default_factory=list)
    source_refs: List[Dict[str,Any]]=Field(default_factory=list)
class CandidateHypothesisRequest(BaseModel):
    analogy_id: str; statement: str=Field(min_length=5); rationale: str=Field(min_length=5); assumptions: List[str]=Field(default_factory=list)
    falsification_criteria: List[str]=Field(min_length=1); expected_observations: List[str]=Field(default_factory=list); target_measurements: List[str]=Field(min_length=1)
class PriorArtRequest(BaseModel):
    items: List[Dict[str,Any]]=Field(default_factory=list); conclusion: str=Field(min_length=3,max_length=5000)
class EvidenceRequest(BaseModel): evidence: List[Dict[str,Any]]=Field(min_length=1)
class ExperimentPlanRequest(BaseModel):
    objective: str=Field(min_length=3,max_length=5000); method: List[str]=Field(min_length=1); measurements: List[str]=Field(min_length=1)
    pass_fail_criteria: List[str]=Field(min_length=1); safety_constraints: List[str]=Field(default_factory=list)
class ResultRequest(BaseModel):
    result_type: str=Field(min_length=2,max_length=100); summary: str=Field(min_length=3,max_length=8000); measurements: Dict[str,Any]=Field(default_factory=dict); resulting_status: str

@router.get("/health")
async def health():
    return {"status":"ok","engine":"discovery_engine","persistence_enabled":engine.persistence_enabled(),"investigations":len(engine.list_investigations()),"knowledge_layers":sorted(engine.LAYERS),"statuses":sorted(engine.STATUSES),"rule":"Discovery candidates are hypotheses until evidence and Council review support promotion."}

@router.get("/frontier-map")
async def frontier_map(subject: List[str]=Query(default=[])): return engine.map_frontier(subjects=subject)

@router.post("/investigations")
async def create_investigation(req: InvestigationRequest):
    try:
        record=engine.create_investigation(**req.model_dump()); await engine.persist(record); return record
    except engine.DiscoveryEngineError as exc: raise HTTPException(422,str(exc)) from exc

@router.get("/investigations")
async def list_investigations(status: Optional[str]=None,knowledge_layer: Optional[str]=None):
    items=engine.list_investigations(status=status,knowledge_layer=knowledge_layer); return {"count":len(items),"items":items}

@router.get("/investigations/{investigation_id}")
async def get_investigation(investigation_id: str):
    record=engine.get_investigation(investigation_id)
    if not record: raise HTTPException(404,f"investigation not found: {investigation_id}")
    return record

@router.get("/investigations/{investigation_id}/gaps")
async def gaps(investigation_id: str):
    try: return engine.detect_gaps(investigation_id)
    except engine.DiscoveryEngineError as exc: raise HTTPException(404,str(exc)) from exc

@router.post("/investigations/{investigation_id}/analogies")
async def add_analogy(investigation_id: str,req: AnalogyRequest):
    try:
        item=engine.add_analogy(investigation_id,**req.model_dump()); await engine.persist(engine.get_investigation(investigation_id)); return item
    except engine.DiscoveryEngineError as exc: raise HTTPException(422,str(exc)) from exc

@router.post("/investigations/{investigation_id}/candidate-hypotheses")
async def generate_candidate(investigation_id: str,req: CandidateHypothesisRequest):
    try:
        item=engine.generate_candidate_hypothesis(investigation_id,**req.model_dump()); await engine.persist(engine.get_investigation(investigation_id)); return item
    except engine.DiscoveryEngineError as exc: raise HTTPException(422,str(exc)) from exc

@router.post("/investigations/{investigation_id}/candidate-hypotheses/{candidate_id}/accept")
async def accept_candidate(investigation_id: str,candidate_id: str):
    try:
        item=engine.accept_candidate_hypothesis(investigation_id,candidate_id); await engine.persist(engine.get_investigation(investigation_id)); return item
    except engine.DiscoveryEngineError as exc: raise HTTPException(422,str(exc)) from exc

@router.post("/investigations/{investigation_id}/hypotheses")
async def add_hypothesis(investigation_id: str,req: HypothesisRequest):
    try:
        item=engine.add_hypothesis(investigation_id,**req.model_dump()); await engine.persist(engine.get_investigation(investigation_id)); return item
    except engine.DiscoveryEngineError as exc: raise HTTPException(422,str(exc)) from exc

@router.post("/investigations/{investigation_id}/prior-art")
async def add_prior_art(investigation_id: str,req: PriorArtRequest):
    try:
        record=engine.add_prior_art(investigation_id,**req.model_dump()); await engine.persist(record); return record
    except engine.DiscoveryEngineError as exc: raise HTTPException(422,str(exc)) from exc

@router.post("/investigations/{investigation_id}/evidence")
async def add_evidence(investigation_id: str,req: EvidenceRequest):
    try:
        record=engine.add_evidence(investigation_id,evidence=req.evidence); await engine.persist(record); return record
    except engine.DiscoveryEngineError as exc: raise HTTPException(422,str(exc)) from exc

@router.put("/investigations/{investigation_id}/experiment-plan")
async def set_experiment_plan(investigation_id: str,req: ExperimentPlanRequest):
    try:
        record=engine.set_experiment_plan(investigation_id,**req.model_dump()); await engine.persist(record); return record
    except engine.DiscoveryEngineError as exc: raise HTTPException(422,str(exc)) from exc

@router.post("/investigations/{investigation_id}/results")
async def record_result(investigation_id: str,req: ResultRequest):
    try:
        item=engine.record_result(investigation_id,**req.model_dump()); await engine.persist(engine.get_investigation(investigation_id)); return item
    except engine.DiscoveryEngineError as exc: raise HTTPException(422,str(exc)) from exc

@router.post("/investigations/{investigation_id}/promote")
async def promote(investigation_id: str):
    try:
        draft=engine.promote_to_approval(investigation_id); record=engine.get_investigation(investigation_id)
        if record: await engine.persist(record)
        await approval.persist_draft(draft)
        return {"investigation_id":investigation_id,"approval_discovery_id":draft["discovery_id"],"approval_status":draft["status"],"draft":draft}
    except engine.DiscoveryEngineError as exc: raise HTTPException(422,str(exc)) from exc
