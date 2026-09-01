"""Append-only provenance ledger for ATLAS Discovery Intelligence.

The ledger records how an idea evolved. It is not a patent determination and
never upgrades scientific verification merely because an event was recorded.
"""
from __future__ import annotations
from datetime import datetime, timezone
from hashlib import sha256
import json
from typing import Any, Dict, List, Optional
from uuid import uuid4

LEDGERS: Dict[str, Dict[str, Any]] = {}
ALLOWED_EVENTS={"QUESTION","SOURCE","ANALOGY","HYPOTHESIS","ASSUMPTION_CHALLENGE","CONTRADICTION","PRIOR_ART","EXPERIMENT_PLAN","SIMULATION_RESULT","EXPERIMENT_RESULT","FAILURE","REVISION","REPLICATION","INDEPENDENT_VERIFICATION","COUNCIL_DECISION"}
class InventionLedgerError(RuntimeError): pass

def _now(): return datetime.now(timezone.utc).isoformat()
def _hash(payload: Dict[str, Any]) -> str: return sha256(json.dumps(payload,sort_keys=True,separators=(",",":"),default=str).encode()).hexdigest()

def create_ledger(*, title: str, investigation_id: str, subjects: Optional[List[str]]=None) -> Dict[str, Any]:
    if not title.strip() or not investigation_id.strip(): raise InventionLedgerError("title and investigation_id are required")
    ledger_id=f"INV-{str(uuid4())[:8]}"; ledger={"ledger_id":ledger_id,"title":title.strip(),"investigation_id":investigation_id.strip(),"subjects":subjects or [],"events":[],"created_at":_now(),"claim_rule":"Ledger provenance documents process; it does not prove novelty, patentability, safety, efficacy, or scientific truth."}; LEDGERS[ledger_id]=ledger; return ledger

def append_event(ledger_id: str, *, event_type: str, payload: Dict[str, Any], actor: str, source_refs: Optional[List[str]]=None) -> Dict[str, Any]:
    ledger=LEDGERS.get(ledger_id)
    if not ledger: raise InventionLedgerError(f"unknown ledger_id: {ledger_id}")
    kind=event_type.upper()
    if kind not in ALLOWED_EVENTS: raise InventionLedgerError(f"invalid event_type: {event_type}")
    previous_hash=ledger["events"][-1]["event_hash"] if ledger["events"] else None
    core={"event_id":f"EVT-{str(uuid4())[:8]}","event_type":kind,"payload":payload,"actor":actor,"source_refs":source_refs or [],"created_at":_now(),"previous_hash":previous_hash}
    event={**core,"event_hash":_hash(core)}; ledger["events"].append(event); return event

def verify_chain(ledger_id: str) -> Dict[str, Any]:
    ledger=LEDGERS.get(ledger_id)
    if not ledger: raise InventionLedgerError(f"unknown ledger_id: {ledger_id}")
    previous=None
    for index,event in enumerate(ledger["events"]):
        core={k:event[k] for k in ("event_id","event_type","payload","actor","source_refs","created_at","previous_hash")}
        if event["previous_hash"]!=previous or _hash(core)!=event["event_hash"]: return {"ledger_id":ledger_id,"valid":False,"broken_at":index}
        previous=event["event_hash"]
    return {"ledger_id":ledger_id,"valid":True,"event_count":len(ledger["events"]),"head_hash":previous}

def get_ledger(ledger_id: str): return LEDGERS.get(ledger_id)
def reset_in_memory_state(): LEDGERS.clear()
