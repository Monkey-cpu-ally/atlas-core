"""Append-only provenance ledger for ATLAS Discovery Intelligence."""
from __future__ import annotations
from datetime import datetime, timezone
from hashlib import sha256
import json
from typing import Any, Dict, List, Optional
from uuid import uuid4
LEDGERS: Dict[str, Dict[str, Any]]={}; _DB: Any=None
ALLOWED_EVENTS={"QUESTION","SOURCE","ANALOGY","HYPOTHESIS","ASSUMPTION_CHALLENGE","CONTRADICTION","PRIOR_ART","EXPERIMENT_PLAN","SIMULATION_RESULT","EXPERIMENT_RESULT","FAILURE","REVISION","REPLICATION","INDEPENDENT_VERIFICATION","COUNCIL_DECISION"}
class InventionLedgerError(RuntimeError): pass
def _now(): return datetime.now(timezone.utc).isoformat()
def _hash(payload): return sha256(json.dumps(payload,sort_keys=True,separators=(",",":"),default=str).encode()).hexdigest()
def attach_mongo(db):
 global _DB; _DB=db
def persistence_enabled(): return _DB is not None
def create_ledger(*,title:str,investigation_id:str,subjects:Optional[List[str]]=None):
 if not title.strip() or not investigation_id.strip(): raise InventionLedgerError("title and investigation_id are required")
 ledger_id=f"INV-{str(uuid4())[:8]}"; item={"ledger_id":ledger_id,"title":title.strip(),"investigation_id":investigation_id.strip(),"subjects":subjects or [],"events":[],"created_at":_now(),"claim_rule":"Ledger provenance documents process; it does not prove novelty, patentability, safety, efficacy, or scientific truth."}; LEDGERS[ledger_id]=item; return item
def append_event(ledger_id:str,*,event_type:str,payload:Dict[str,Any],actor:str,source_refs:Optional[List[str]]=None):
 item=LEDGERS.get(ledger_id)
 if not item: raise InventionLedgerError(f"unknown ledger_id: {ledger_id}")
 kind=event_type.upper()
 if kind not in ALLOWED_EVENTS: raise InventionLedgerError(f"invalid event_type: {event_type}")
 previous=item["events"][-1]["event_hash"] if item["events"] else None; core={"event_id":f"EVT-{str(uuid4())[:8]}","event_type":kind,"payload":payload,"actor":actor,"source_refs":source_refs or [],"created_at":_now(),"previous_hash":previous}; event={**core,"event_hash":_hash(core)}; item["events"].append(event); return event
def verify_chain(ledger_id:str):
 item=LEDGERS.get(ledger_id)
 if not item: raise InventionLedgerError(f"unknown ledger_id: {ledger_id}")
 previous=None
 for index,event in enumerate(item["events"]):
  core={k:event[k] for k in ("event_id","event_type","payload","actor","source_refs","created_at","previous_hash")}
  if event["previous_hash"]!=previous or _hash(core)!=event["event_hash"]: return {"ledger_id":ledger_id,"valid":False,"broken_at":index}
  previous=event["event_hash"]
 return {"ledger_id":ledger_id,"valid":True,"event_count":len(item["events"]),"head_hash":previous}
def get_ledger(ledger_id): return LEDGERS.get(ledger_id)
def get_for_investigation(investigation_id):
 return next((x for x in LEDGERS.values() if x["investigation_id"]==investigation_id),None)
async def persist(item):
 if _DB is not None: await _DB.invention_ledgers.update_one({"ledger_id":item["ledger_id"]},{"$set":item},upsert=True)
async def hydrate_from_mongo():
 if _DB is None: return {"ledgers":0}
 rows=await _DB.invention_ledgers.find({}, {"_id":0}).to_list(10000); LEDGERS.clear()
 for row in rows: LEDGERS[row["ledger_id"]]=row
 return {"ledgers":len(LEDGERS)}
async def create_indexes():
 if _DB is not None:
  await _DB.invention_ledgers.create_index("ledger_id",unique=True); await _DB.invention_ledgers.create_index("investigation_id",unique=True)
def reset_in_memory_state(): LEDGERS.clear()
