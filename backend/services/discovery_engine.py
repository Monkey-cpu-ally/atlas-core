"""Canonical ATLAS Discovery Engine with tamper-evident process provenance."""
from __future__ import annotations
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4
from services import discovery_approval_pipeline as approval
from services import discovery_challenge, discovery_verification, evidence_scoring, invention_ledger

LAYERS={"FOUNDATION","FRONTIER","UNKNOWN"}
STATUSES={"CONCEPT","HYPOTHESIS","PRIOR_ART_CHECKED","TEST_DESIGNED","SIMULATED","EXPERIMENTALLY_SUPPORTED","REPLICATED","INDEPENDENTLY_VERIFIED","INVALIDATED","INCONCLUSIVE","BLOCKED_BY_EVIDENCE","BLOCKED_BY_SAFETY","BLOCKED_BY_CAPABILITY","NOT_NOVEL"}
PROMOTABLE_STATUSES={"PRIOR_ART_CHECKED","TEST_DESIGNED","SIMULATED","EXPERIMENTALLY_SUPPORTED","REPLICATED","INDEPENDENTLY_VERIFIED"}
_RECORDS: Dict[str,Dict[str,Any]]={}; _DB: Any=None
class DiscoveryEngineError(RuntimeError): pass
def _now(): return datetime.now(timezone.utc).isoformat()
def attach_mongo(db):
 global _DB; _DB=db
def persistence_enabled(): return _DB is not None

def _ledger(record):
 ledger=invention_ledger.get_ledger(record.get("ledger_id")) if record.get("ledger_id") else invention_ledger.get_for_investigation(record["investigation_id"])
 if ledger and not record.get("ledger_id"): record["ledger_id"]=ledger["ledger_id"]
 return ledger

def _event(record,event_type,payload,source_refs=None):
 ledger=_ledger(record)
 if not ledger: raise DiscoveryEngineError("investigation provenance ledger is unavailable")
 try: return invention_ledger.append_event(ledger["ledger_id"],event_type=event_type,payload=payload,actor=record["owner_ai"],source_refs=source_refs or [])
 except invention_ledger.InventionLedgerError as exc: raise DiscoveryEngineError(str(exc)) from exc

def create_investigation(*,title:str,question:str,knowledge_layer:str="FRONTIER",owner_ai:str="Council",subjects:Optional[List[str]]=None,related_projects:Optional[List[str]]=None,mission_id:Optional[str]=None):
 layer=knowledge_layer.upper()
 if layer not in LAYERS: raise DiscoveryEngineError(f"invalid knowledge_layer: {knowledge_layer}")
 if owner_ai not in approval.VALID_OWNER_AI: raise DiscoveryEngineError(f"invalid owner_ai: {owner_ai}")
 if not title.strip() or not question.strip(): raise DiscoveryEngineError("title and question are required")
 iid=f"DX-{str(uuid4())[:8]}"; ledger=invention_ledger.create_ledger(title=title,investigation_id=iid,subjects=subjects or [])
 record={"investigation_id":iid,"ledger_id":ledger["ledger_id"],"title":title.strip(),"question":question.strip(),"knowledge_layer":layer,"owner_ai":owner_ai,"status":"CONCEPT","subjects":subjects or [],"related_projects":related_projects or [],"mission_id":mission_id,"known_facts":[],"unknowns":[],"assumptions":[],"analogies":[],"candidate_hypotheses":[],"hypotheses":[],"challenges":[],"prior_art":[],"prior_art_assessments":[],"evidence":[],"evidence_evaluations":[],"evidence_score":evidence_scoring.score_evidence([]),"experiment_plan":None,"experiment_designs":[],"results":[],"replications":[],"approval_discovery_id":None,"created_at":_now(),"updated_at":_now()}
 _RECORDS[iid]=record; _event(record,"QUESTION",{"question":record["question"],"knowledge_layer":layer}); return record
def get_investigation(iid): return _RECORDS.get(iid)
def list_investigations(*,status=None,knowledge_layer=None):
 items=list(_RECORDS.values())
 if status: items=[x for x in items if x["status"]==status.upper()]
 if knowledge_layer: items=[x for x in items if x["knowledge_layer"]==knowledge_layer.upper()]
 return sorted(items,key=lambda x:x["updated_at"],reverse=True)
def map_frontier(*,subjects=None):
 wanted={s.casefold() for s in (subjects or [])}; records=list(_RECORDS.values())
 if wanted: records=[r for r in records if wanted.intersection({s.casefold() for s in r.get("subjects",[])})]
 layers={x:[] for x in sorted(LAYERS)}
 for r in records: layers[r["knowledge_layer"]].append({"investigation_id":r["investigation_id"],"title":r["title"],"question":r["question"],"status":r["status"],"subjects":r.get("subjects",[]),"evidence_score":r.get("evidence_score",{}).get("score",0)})
 return {"generated_at":_now(),"scope_subjects":subjects or [],"layers":layers,"counts":{k:len(v) for k,v in layers.items()},"rule":"FRONTIER and UNKNOWN are ATLAS tracking labels, not claims that the literature contains no answer."}
def detect_gaps(iid):
 r=_require(iid); gaps=[]
 if not r.get("known_facts"): gaps.append({"kind":"foundation","severity":"medium","message":"No known facts have been recorded."})
 if not r.get("unknowns"): gaps.append({"kind":"question_decomposition","severity":"medium","message":"The main question has not been decomposed into explicit unknowns."})
 if not r.get("hypotheses"): gaps.append({"kind":"hypothesis","severity":"high","message":"No accepted falsifiable hypothesis exists."})
 if not r.get("prior_art"): gaps.append({"kind":"prior_art","severity":"high","message":"No prior-art or literature items are recorded."})
 if r.get("evidence_score",{}).get("score",0)<60: gaps.append({"kind":"evidence","severity":"high","message":"Evidence score is below the moderate threshold of 60."})
 if not r.get("experiment_plan") and not r.get("experiment_designs"): gaps.append({"kind":"experiment","severity":"high","message":"No measurable experiment or simulation plan exists."})
 if r["status"]=="SIMULATED": gaps.append({"kind":"physical_validation","severity":"high","message":"Simulation has not established physical or independent verification."})
 if r["status"] in {"EXPERIMENTALLY_SUPPORTED","REPLICATED"}: gaps.append({"kind":"independent_verification","severity":"medium","message":"Independent verification has not been recorded."})
 return {"investigation_id":iid,"status":r["status"],"gap_count":len(gaps),"gaps":gaps,"ready_for_approval_review":r["status"] in PROMOTABLE_STATUSES and bool(r.get("hypotheses")),"ready_for_verified_claim":r["status"]=="INDEPENDENTLY_VERIFIED","generated_at":_now()}
def add_analogy(iid,*,source_subject,target_subject,source_concept,mechanism,transferable_principle,constraints,source_refs=None):
 r=_require(iid); vals=[source_subject,target_subject,source_concept,mechanism,transferable_principle]
 if any(not x.strip() for x in vals): raise DiscoveryEngineError("analogy requires source/target subjects, source concept, mechanism, and transferable principle")
 if source_subject.casefold()==target_subject.casefold(): raise DiscoveryEngineError("cross-disciplinary analogy requires different source and target subjects")
 a={"analogy_id":f"ANA-{str(uuid4())[:8]}","source_subject":source_subject.strip(),"target_subject":target_subject.strip(),"source_concept":source_concept.strip(),"mechanism":mechanism.strip(),"transferable_principle":transferable_principle.strip(),"constraints":constraints,"source_refs":source_refs or [],"status":"candidate","proves_feasibility":False,"created_at":_now()}; r["analogies"].append(a); _event(r,"ANALOGY",a); r["updated_at"]=_now(); return a
def generate_candidate_hypothesis(iid,*,analogy_id,statement,rationale,assumptions,falsification_criteria,expected_observations,target_measurements):
 r=_require(iid)
 if not any(x["analogy_id"]==analogy_id for x in r["analogies"]): raise DiscoveryEngineError(f"unknown analogy_id: {analogy_id}")
 if not statement.strip() or not rationale.strip() or not falsification_criteria or not target_measurements: raise DiscoveryEngineError("candidate hypothesis requires statement, rationale, falsification criteria, and target measurements")
 c={"candidate_id":f"CHY-{str(uuid4())[:8]}","analogy_id":analogy_id,"statement":statement.strip(),"rationale":rationale.strip(),"assumptions":assumptions,"falsification_criteria":falsification_criteria,"expected_observations":expected_observations,"target_measurements":target_measurements,"status":"pending_review","origin":"structured_candidate","created_at":_now()}; r["candidate_hypotheses"].append(c); r["updated_at"]=_now(); return c
def accept_candidate_hypothesis(iid,candidate_id):
 r=_require(iid); c=next((x for x in r["candidate_hypotheses"] if x["candidate_id"]==candidate_id),None)
 if not c: raise DiscoveryEngineError(f"unknown candidate_id: {candidate_id}")
 if c["status"]!="pending_review": raise DiscoveryEngineError(f"candidate is already {c['status']}")
 if c.get("novelty_status")=="blocked_by_direct_prior_art": raise DiscoveryEngineError("candidate is blocked by direct prior art")
 h=add_hypothesis(iid,statement=c["statement"],rationale=c["rationale"],falsification_criteria=c["falsification_criteria"],assumptions=c["assumptions"]); h["origin_candidate_id"]=candidate_id; h["analogy_id"]=c["analogy_id"]; c["status"]="accepted"; c["accepted_hypothesis_id"]=h["hypothesis_id"]; c["reviewed_at"]=_now(); return h
def add_hypothesis(iid,*,statement,rationale,falsification_criteria,assumptions=None):
 r=_require(iid)
 if not statement.strip() or not rationale.strip(): raise DiscoveryEngineError("hypothesis statement and rationale are required")
 if not falsification_criteria: raise DiscoveryEngineError("a hypothesis requires falsification criteria")
 h={"hypothesis_id":f"HYP-{str(uuid4())[:8]}","statement":statement.strip(),"rationale":rationale.strip(),"falsification_criteria":falsification_criteria,"assumptions":assumptions or [],"status":"active","created_at":_now()}; r["hypotheses"].append(h); r["status"]="HYPOTHESIS"; _event(r,"HYPOTHESIS",h); r["updated_at"]=_now(); return h
def challenge_active_hypothesis(iid,*,hypothesis_id,supporting_claims,conflicting_claims):
 r=_require(iid); h=next((x for x in r["hypotheses"] if x["hypothesis_id"]==hypothesis_id),None)
 if not h: raise DiscoveryEngineError(f"unknown hypothesis_id: {hypothesis_id}")
 try: c=discovery_challenge.challenge_hypothesis(statement=h["statement"],assumptions=h.get("assumptions",[]),supporting_claims=supporting_claims,conflicting_claims=conflicting_claims)
 except discovery_challenge.DiscoveryChallengeError as exc: raise DiscoveryEngineError(str(exc)) from exc
 c["hypothesis_id"]=hypothesis_id; c["created_at"]=_now(); r["challenges"].append(c); _event(r,"CONTRADICTION" if c.get("conflict_count",0) else "ASSUMPTION_CHALLENGE",c); r["updated_at"]=_now(); return c
def assess_candidate_prior_art(iid,*,candidate_id,search_queries,matches):
 r=_require(iid); c=next((x for x in r["candidate_hypotheses"] if x["candidate_id"]==candidate_id),None)
 if not c: raise DiscoveryEngineError(f"unknown candidate_id: {candidate_id}")
 try: a=discovery_challenge.assess_prior_art(candidate_statement=c["statement"],search_queries=search_queries,matches=matches)
 except discovery_challenge.DiscoveryChallengeError as exc: raise DiscoveryEngineError(str(exc)) from exc
 a["candidate_id"]=candidate_id; a["created_at"]=_now(); r["prior_art_assessments"].append(a); c["novelty_status"]="blocked_by_direct_prior_art" if a["disposition"]=="NOT_NOVEL_CANDIDATE" else ("unresolved" if a["disposition"]=="NOVELTY_UNRESOLVED" else "unproven"); _event(r,"PRIOR_ART",a); r["updated_at"]=_now(); return a
def add_prior_art(iid,*,items,conclusion):
 r=_require(iid); r["prior_art"].extend(items); r["prior_art_conclusion"]=conclusion.strip(); r["status"]="PRIOR_ART_CHECKED"; _event(r,"PRIOR_ART",{"items":items,"conclusion":conclusion}); r["updated_at"]=_now(); return r
def add_evidence(iid,*,evidence):
 r=_require(iid); r["evidence"].extend(evidence); r["evidence_score"]=evidence_scoring.score_evidence(r["evidence"]); _event(r,"SOURCE",{"evidence":evidence,"score":r["evidence_score"]}); r["updated_at"]=_now(); return r
def evaluate_investigation_evidence(iid,*,conflicts=None):
 r=_require(iid); e=discovery_verification.evaluate_evidence(evidence=r["evidence"],conflicts=conflicts); e["created_at"]=_now(); r["evidence_evaluations"].append(e); r["evidence_score"]=e["evidence_score"]
 if e["disposition"]=="INSUFFICIENT_EVIDENCE": r["status"]="BLOCKED_BY_EVIDENCE"
 r["updated_at"]=_now(); return e
def design_investigation_experiment(iid,*,hypothesis_id,independent_variables,dependent_variables,controls,procedure,pass_fail_criteria,safety_constraints=None,replication_target=2):
 r=_require(iid); h=next((x for x in r["hypotheses"] if x["hypothesis_id"]==hypothesis_id),None)
 if not h: raise DiscoveryEngineError(f"unknown hypothesis_id: {hypothesis_id}")
 if any(c.get("hypothesis_id")==hypothesis_id and c.get("conflict_count",0)>0 for c in r["challenges"]): raise DiscoveryEngineError("hypothesis has unresolved contradiction review")
 try: d=discovery_verification.design_experiment(hypothesis=h["statement"],independent_variables=independent_variables,dependent_variables=dependent_variables,controls=controls,procedure=procedure,pass_fail_criteria=pass_fail_criteria,safety_constraints=safety_constraints,replication_target=replication_target)
 except discovery_verification.DiscoveryVerificationError as exc: raise DiscoveryEngineError(str(exc)) from exc
 d["hypothesis_id"]=hypothesis_id; d["created_at"]=_now(); r["experiment_designs"].append(d); r["experiment_plan"]=d; r["status"]="TEST_DESIGNED"; _event(r,"EXPERIMENT_PLAN",d); r["updated_at"]=_now(); return d
def set_experiment_plan(iid,*,objective,method,measurements,pass_fail_criteria,safety_constraints=None):
 r=_require(iid)
 if not method or not measurements or not pass_fail_criteria: raise DiscoveryEngineError("experiment plan requires method, measurements, and pass/fail criteria")
 p={"objective":objective.strip(),"method":method,"measurements":measurements,"pass_fail_criteria":pass_fail_criteria,"safety_constraints":safety_constraints or [],"created_at":_now()}; r["experiment_plan"]=p; r["status"]="TEST_DESIGNED"; _event(r,"EXPERIMENT_PLAN",p); r["updated_at"]=_now(); return r
def record_result(iid,*,result_type,summary,measurements=None,resulting_status):
 r=_require(iid); status=resulting_status.upper()
 if status not in STATUSES: raise DiscoveryEngineError(f"invalid resulting_status: {resulting_status}")
 if status in {"REPLICATED","INDEPENDENTLY_VERIFIED"}: raise DiscoveryEngineError("replication states must be produced by the replication manager")
 if status in {"SIMULATED","EXPERIMENTALLY_SUPPORTED"} and not r.get("experiment_plan"): raise DiscoveryEngineError("validated result states require an experiment plan")
 sim=str(result_type).lower() in {"simulation","simulated","model"}
 if sim and status=="EXPERIMENTALLY_SUPPORTED": raise DiscoveryEngineError("simulation cannot be recorded as experimental support")
 x={"result_id":f"RES-{str(uuid4())[:8]}","result_type":result_type,"summary":summary,"measurements":measurements or {},"status":status,"created_at":_now()}; r["results"].append(x); r["status"]=status; _event(r,"SIMULATION_RESULT" if sim else ("FAILURE" if status in {"INVALIDATED","INCONCLUSIVE"} else "EXPERIMENT_RESULT"),x); r["updated_at"]=_now(); return x
def record_replication(iid,*,original_result_id,replication_runs,required_successes=2,independent_required=True,verification_context="generic"):
 r=_require(iid); original=next((x for x in r["results"] if x["result_id"]==original_result_id),None)
 if not original: raise DiscoveryEngineError(f"unknown original_result_id: {original_result_id}")
 try: rep=discovery_verification.evaluate_replication(original_result=original,replication_runs=replication_runs,required_successes=required_successes,independent_required=independent_required,verification_context=verification_context)
 except discovery_verification.DiscoveryVerificationError as exc: raise DiscoveryEngineError(str(exc)) from exc
 rep["original_result_id"]=original_result_id; rep["created_at"]=_now(); r["replications"].append(rep); _event(r,"INDEPENDENT_VERIFICATION" if rep["status"]=="INDEPENDENTLY_VERIFIED" else "REPLICATION",rep)
 if rep["status"] in {"REPLICATED","INDEPENDENTLY_VERIFIED","INCONCLUSIVE"}: r["status"]=rep["status"]
 r["updated_at"]=_now(); return rep
def promote_to_approval(iid):
 r=_require(iid)
 if r["status"] not in PROMOTABLE_STATUSES: raise DiscoveryEngineError(f"status {r['status']} is not ready for approval review")
 if not r["hypotheses"]: raise DiscoveryEngineError("at least one hypothesis is required before approval review")
 if r.get("approval_discovery_id"):
  existing=approval.get_draft(r["approval_discovery_id"])
  if existing: return existing
 draft=approval.create_draft(title=r["title"],summary=r["question"],owner_ai=r["owner_ai"],evidence=r["evidence"],source_refs=[x for x in r["prior_art"] if isinstance(x,dict)],related_subjects=r["subjects"],related_projects=r["related_projects"],mission_id=r["mission_id"]); draft["discovery_engine_investigation_id"]=iid; draft["discovery_engine_status"]=r["status"]; r["approval_discovery_id"]=draft["discovery_id"]; _event(r,"COUNCIL_DECISION",{"action":"promoted_to_approval_review","approval_discovery_id":draft["discovery_id"],"status_at_promotion":r["status"]}); r["updated_at"]=_now(); return draft
def get_invention_ledger(iid):
 r=_require(iid); ledger=_ledger(r)
 if not ledger: raise DiscoveryEngineError("investigation provenance ledger is unavailable")
 return ledger
def verify_invention_ledger(iid):
 ledger=get_invention_ledger(iid)
 try: return invention_ledger.verify_chain(ledger["ledger_id"])
 except invention_ledger.InventionLedgerError as exc: raise DiscoveryEngineError(str(exc)) from exc
def _require(iid):
 r=get_investigation(iid)
 if not r: raise DiscoveryEngineError(f"unknown investigation_id: {iid}")
 return r
async def persist(record):
 if _DB is not None: await _DB.discovery_investigations.update_one({"investigation_id":record["investigation_id"]},{"$set":record},upsert=True)
 ledger=_ledger(record)
 if ledger: await invention_ledger.persist(ledger)
async def hydrate_from_mongo():
 if _DB is None: return {"investigations":0}
 items=await _DB.discovery_investigations.find({}, {"_id":0}).to_list(10000); _RECORDS.clear()
 for x in items:
  for key in ("analogies","candidate_hypotheses","hypotheses","challenges","prior_art","prior_art_assessments","evidence","evidence_evaluations","experiment_designs","results","replications"): x.setdefault(key,[])
  ledger=invention_ledger.get_for_investigation(x["investigation_id"])
  if ledger: x.setdefault("ledger_id",ledger["ledger_id"])
  _RECORDS[x["investigation_id"]]=x
 return {"investigations":len(_RECORDS)}
async def create_indexes():
 if _DB is not None:
  await _DB.discovery_investigations.create_index("investigation_id",unique=True); await _DB.discovery_investigations.create_index([("knowledge_layer",1),("status",1)]); await _DB.discovery_investigations.create_index("mission_id")
def reset_in_memory_state(): _RECORDS.clear()
