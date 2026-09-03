"""ATLAS Discovery Engine routes."""
from __future__ import annotations
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from services import discovery_approval_pipeline as approval
from services import discovery_engine as engine
router=APIRouter(prefix="/api/discovery-engine",tags=["ATLAS Discovery Engine"])
class InvestigationRequest(BaseModel):
 title:str=Field(min_length=3,max_length=300); question:str=Field(min_length=5,max_length=5000); knowledge_layer:str="FRONTIER"; owner_ai:str="Council"; subjects:List[str]=Field(default_factory=list); related_projects:List[str]=Field(default_factory=list); mission_id:Optional[str]=None
class HypothesisRequest(BaseModel): statement:str=Field(min_length=5); rationale:str=Field(min_length=5); falsification_criteria:List[str]=Field(min_length=1); assumptions:List[str]=Field(default_factory=list)
class AnalogyRequest(BaseModel): source_subject:str=Field(min_length=2); target_subject:str=Field(min_length=2); source_concept:str=Field(min_length=3); mechanism:str=Field(min_length=3); transferable_principle:str=Field(min_length=3); constraints:List[str]=Field(default_factory=list); source_refs:List[Dict[str,Any]]=Field(default_factory=list)
class CandidateHypothesisRequest(BaseModel): analogy_id:str; statement:str=Field(min_length=5); rationale:str=Field(min_length=5); assumptions:List[str]=Field(default_factory=list); falsification_criteria:List[str]=Field(min_length=1); expected_observations:List[str]=Field(default_factory=list); target_measurements:List[str]=Field(min_length=1)
class ChallengeRequest(BaseModel): hypothesis_id:str; supporting_claims:List[Dict[str,Any]]=Field(default_factory=list); conflicting_claims:List[Dict[str,Any]]=Field(default_factory=list)
class PriorArtAssessmentRequest(BaseModel): candidate_id:str; search_queries:List[str]=Field(min_length=1); matches:List[Dict[str,Any]]=Field(default_factory=list)
class EvidenceRequest(BaseModel): evidence:List[Dict[str,Any]]=Field(min_length=1)
class EvidenceEvaluationRequest(BaseModel): conflicts:List[Dict[str,Any]]=Field(default_factory=list)
class ExperimentPlanRequest(BaseModel): objective:str=Field(min_length=3); method:List[str]=Field(min_length=1); measurements:List[str]=Field(min_length=1); pass_fail_criteria:List[str]=Field(min_length=1); safety_constraints:List[str]=Field(default_factory=list)
class ExperimentDesignRequest(BaseModel): hypothesis_id:str; independent_variables:List[str]=Field(min_length=1); dependent_variables:List[str]=Field(min_length=1); controls:List[str]=Field(min_length=1); procedure:List[str]=Field(min_length=1); pass_fail_criteria:List[str]=Field(min_length=1); safety_constraints:List[str]=Field(default_factory=list); replication_target:int=2
class ResultRequest(BaseModel): result_type:str=Field(min_length=2); summary:str=Field(min_length=3); measurements:Dict[str,Any]=Field(default_factory=dict); resulting_status:str
class ReplicationRequest(BaseModel): original_result_id:str; replication_runs:List[Dict[str,Any]]=Field(default_factory=list); required_successes:int=2; independent_required:bool=True; verification_context:str="generic"
@router.get("/health")
async def health(): return {"status":"ok","engine":"discovery_engine","persistence_enabled":engine.persistence_enabled(),"investigations":len(engine.list_investigations()),"knowledge_layers":sorted(engine.LAYERS),"statuses":sorted(engine.STATUSES),"rule":"Discovery candidates are hypotheses until evidence and Council review support promotion."}
@router.get("/frontier-map")
async def frontier_map(subject:List[str]=Query(default=[])): return engine.map_frontier(subjects=subject)
@router.post("/investigations")
async def create_investigation(req:InvestigationRequest):
 try: r=engine.create_investigation(**req.model_dump()); await engine.persist(r); return r
 except engine.DiscoveryEngineError as exc: raise HTTPException(422,str(exc)) from exc
@router.get("/investigations")
async def list_investigations(status:Optional[str]=None,knowledge_layer:Optional[str]=None):
 items=engine.list_investigations(status=status,knowledge_layer=knowledge_layer); return {"count":len(items),"items":items}
@router.get("/investigations/{iid}")
async def get_investigation(iid:str):
 r=engine.get_investigation(iid)
 if not r: raise HTTPException(404,f"investigation not found: {iid}")
 return r
@router.get("/investigations/{iid}/gaps")
async def gaps(iid:str):
 try:return engine.detect_gaps(iid)
 except engine.DiscoveryEngineError as exc:raise HTTPException(404,str(exc)) from exc
@router.get("/investigations/{iid}/ledger")
async def ledger(iid:str):
 try:return engine.get_invention_ledger(iid)
 except engine.DiscoveryEngineError as exc:raise HTTPException(404,str(exc)) from exc
@router.get("/investigations/{iid}/ledger/verify")
async def verify_ledger(iid:str):
 try:return engine.verify_invention_ledger(iid)
 except engine.DiscoveryEngineError as exc:raise HTTPException(404,str(exc)) from exc
@router.post("/investigations/{iid}/analogies")
async def add_analogy(iid:str,req:AnalogyRequest):
 try:x=engine.add_analogy(iid,**req.model_dump());await engine.persist(engine.get_investigation(iid));return x
 except engine.DiscoveryEngineError as exc:raise HTTPException(422,str(exc)) from exc
@router.post("/investigations/{iid}/candidate-hypotheses")
async def candidate(iid:str,req:CandidateHypothesisRequest):
 try:x=engine.generate_candidate_hypothesis(iid,**req.model_dump());await engine.persist(engine.get_investigation(iid));return x
 except engine.DiscoveryEngineError as exc:raise HTTPException(422,str(exc)) from exc
@router.post("/investigations/{iid}/candidate-hypotheses/{cid}/accept")
async def accept(iid:str,cid:str):
 try:x=engine.accept_candidate_hypothesis(iid,cid);await engine.persist(engine.get_investigation(iid));return x
 except engine.DiscoveryEngineError as exc:raise HTTPException(422,str(exc)) from exc
@router.post("/investigations/{iid}/hypotheses")
async def hypothesis(iid:str,req:HypothesisRequest):
 try:x=engine.add_hypothesis(iid,**req.model_dump());await engine.persist(engine.get_investigation(iid));return x
 except engine.DiscoveryEngineError as exc:raise HTTPException(422,str(exc)) from exc
@router.post("/investigations/{iid}/challenges")
async def challenge(iid:str,req:ChallengeRequest):
 try:x=engine.challenge_active_hypothesis(iid,**req.model_dump());await engine.persist(engine.get_investigation(iid));return x
 except engine.DiscoveryEngineError as exc:raise HTTPException(422,str(exc)) from exc
@router.post("/investigations/{iid}/prior-art-assessments")
async def prior_assess(iid:str,req:PriorArtAssessmentRequest):
 try:x=engine.assess_candidate_prior_art(iid,**req.model_dump());await engine.persist(engine.get_investigation(iid));return x
 except engine.DiscoveryEngineError as exc:raise HTTPException(422,str(exc)) from exc
@router.post("/investigations/{iid}/evidence")
async def evidence(iid:str,req:EvidenceRequest):
 try:r=engine.add_evidence(iid,evidence=req.evidence);await engine.persist(r);return r
 except engine.DiscoveryEngineError as exc:raise HTTPException(422,str(exc)) from exc
@router.post("/investigations/{iid}/evidence-evaluations")
async def evaluate(iid:str,req:EvidenceEvaluationRequest):
 try:x=engine.evaluate_investigation_evidence(iid,conflicts=req.conflicts);await engine.persist(engine.get_investigation(iid));return x
 except engine.DiscoveryEngineError as exc:raise HTTPException(422,str(exc)) from exc
@router.post("/investigations/{iid}/experiment-designs")
async def design(iid:str,req:ExperimentDesignRequest):
 try:x=engine.design_investigation_experiment(iid,**req.model_dump());await engine.persist(engine.get_investigation(iid));return x
 except engine.DiscoveryEngineError as exc:raise HTTPException(422,str(exc)) from exc
@router.put("/investigations/{iid}/experiment-plan")
async def plan(iid:str,req:ExperimentPlanRequest):
 try:r=engine.set_experiment_plan(iid,**req.model_dump());await engine.persist(r);return r
 except engine.DiscoveryEngineError as exc:raise HTTPException(422,str(exc)) from exc
@router.post("/investigations/{iid}/results")
async def result(iid:str,req:ResultRequest):
 try:x=engine.record_result(iid,**req.model_dump());await engine.persist(engine.get_investigation(iid));return x
 except engine.DiscoveryEngineError as exc:raise HTTPException(422,str(exc)) from exc
@router.post("/investigations/{iid}/replications")
async def replicate(iid:str,req:ReplicationRequest):
 try:x=engine.record_replication(iid,**req.model_dump());await engine.persist(engine.get_investigation(iid));return x
 except engine.DiscoveryEngineError as exc:raise HTTPException(422,str(exc)) from exc
@router.post("/investigations/{iid}/promote")
async def promote(iid:str):
 try:
  draft=engine.promote_to_approval(iid);r=engine.get_investigation(iid)
  if r:await engine.persist(r)
  await approval.persist_draft(draft);return {"investigation_id":iid,"approval_discovery_id":draft["discovery_id"],"approval_status":draft["status"],"draft":draft}
 except engine.DiscoveryEngineError as exc:raise HTTPException(422,str(exc)) from exc
