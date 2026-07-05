"""
Self-Improvement routes (prefix /api/self-improve).

GET   /api/self-improve/proposals           → list (filter: status, category)
POST  /api/self-improve/propose             → create a new proposal
POST  /api/self-improve/approve/{id}        → approve a proposal
POST  /api/self-improve/reject/{id}         → reject a proposal
GET   /api/self-improve/history             → full history
GET   /api/self-improve/weekly-report       → deterministic 7-day roll-up
GET   /api/self-improve/health-scan         → repository self-improvement scan
POST  /api/self-improve/health-scan/propose → create proposals from scan
"""
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from services import self_improvement as si

router = APIRouter(prefix="/api/self-improve", tags=["SelfImprovement"])


class ProposeReq(BaseModel):
    observed_pattern: str
    evidence: List[Dict[str, Any]] = Field(default_factory=list)
    affected_system: str
    proposed_change: str
    category: str = "workflow"
    risk_level: str = "low"
    confidence_score: float = 0.5
    source: str = "atlas"
    owner_ai: str = "Council"
    update_plan: List[str] = Field(default_factory=list)
    rollback_plan: Optional[str] = None


class DecideReq(BaseModel):
    note: Optional[str] = None


@router.get("/proposals")
async def proposals(
    status: Optional[str] = None,
    category: Optional[str] = None,
    limit: int = Query(100, ge=1, le=500),
):
    items = await si.list_proposals(status=status, category=category, limit=limit)
    return {"count": len(items), "items": items}


@router.post("/propose")
async def create(req: ProposeReq):
    try:
        return await si.propose(
            observed_pattern=req.observed_pattern,
            evidence=req.evidence,
            affected_system=req.affected_system,
            proposed_change=req.proposed_change,
            category=req.category,
            risk_level=req.risk_level,
            confidence_score=req.confidence_score,
            source=req.source,
            owner_ai=req.owner_ai,
            update_plan=req.update_plan,
            rollback_plan=req.rollback_plan,
        )
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc


@router.post("/approve/{improvement_id}")
async def approve(improvement_id: str, req: Optional[DecideReq] = None):
    note = (req.note if req else None) or "approved by user"
    res = await si.decide(improvement_id, status="approved", note=note)
    if not res:
        raise HTTPException(404, "proposal not found")
    return res


@router.post("/reject/{improvement_id}")
async def reject(improvement_id: str, req: Optional[DecideReq] = None):
    note = (req.note if req else None) or "rejected by user"
    res = await si.decide(improvement_id, status="rejected", note=note)
    if not res:
        raise HTTPException(404, "proposal not found")
    return res


@router.get("/history")
async def history(limit: int = Query(200, ge=1, le=1000)):
    items = await si.history(limit=limit)
    return {"count": len(items), "items": items}


@router.get("/weekly-report")
async def weekly_report():
    return await si.weekly_report()


@router.get("/health-scan")
async def health_scan():
    return si.analyze_repository_health()


@router.post("/health-scan/propose")
async def health_scan_propose():
    return await si.propose_from_health_scan()
