from fastapi import APIRouter
from pydantic import BaseModel
from typing import Any, Dict, Optional

from .sword_shield import (
    AuditChain, TokenVault, PolicyEngine, ResponseEngine, SwordShieldOrgan,
    HermesRouter, TinyCache, Metrics, TaskRequest,
    Zone, Lane
)

router = APIRouter(prefix="/hermes", tags=["hermes-router"])

audit = AuditChain(secret_key=b"hermes_sword_shield_replit")
tokens = TokenVault()
policy = PolicyEngine(human_required_over=50)
response = ResponseEngine()

sword_shield = SwordShieldOrgan(audit, tokens, policy, response, mode="warrior")

def fast_outline(payload: Dict[str, Any]) -> Dict[str, Any]:
    topic = payload.get("topic", "unknown")
    depth = int(payload.get("depth", 5))
    return {
        "topic": topic,
        "outline": [f"{i+1}. {topic} — key point" for i in range(depth)],
        "next": "Pick one point to expand."
    }

def fast_tag_asset(payload: Dict[str, Any]) -> Dict[str, Any]:
    name = payload.get("name", "asset")
    tags = payload.get("tags", [])
    return {"asset": name, "tags": tags, "status": "tagged"}

def safe_export(payload: Dict[str, Any]) -> Dict[str, Any]:
    return {"exported": True, "where": "sandbox storage", "payload": payload}

def heavy_polish(payload: Dict[str, Any]) -> Dict[str, Any]:
    return {"polished": True, "note": "HEAVY lane stub", "payload": payload}

cache = TinyCache()
metrics = Metrics()

hermes_router = HermesRouter(
    cache=cache,
    metrics=metrics,
    sword_shield=sword_shield,
    fast_handlers={
        "outline": fast_outline,
        "tag_asset": fast_tag_asset,
    },
    safe_handlers={
        "export": safe_export,
    },
    heavy_handlers={
        "polish": heavy_polish,
    }
)

class RunTask(BaseModel):
    name: str
    lane: str
    zone: str
    payload: Dict[str, Any] = {}
    max_ms: int = 600
    allow_cache: bool = True
    cache_ttl_ms: int = 30000
    risk_score: int = 20
    token_id: Optional[str] = None
    approvals: Dict[str, bool] = {}

@router.post("/run")
def run_task(req: RunTask):
    zone_val: Zone = req.zone if req.zone in ("core_memory", "tools_io", "render_forge", "connectors", "ui", "unknown") else "unknown"
    lane_val: Lane = req.lane if req.lane in ("FAST", "SAFE", "HEAVY") else "FAST"
    out = hermes_router.run(TaskRequest(
        name=req.name,
        zone=zone_val,
        lane=lane_val,
        payload=req.payload,
        max_ms=req.max_ms,
        allow_cache=req.allow_cache,
        cache_ttl_ms=req.cache_ttl_ms,
        risk_score=req.risk_score,
        token_id=req.token_id,
        approvals=req.approvals,
    ))
    return out.__dict__

@router.get("/metrics")
def get_metrics():
    return metrics.summary()

@router.get("/audit")
def get_audit():
    return audit.export()

@router.post("/token/issue")
def issue_token(issued_to: str = "hermes", caps: str = "tools_call", ttl_ms: int = 300000, max_risk: int = 40):
    cap_list = [c.strip() for c in caps.split(",")]
    token_id = tokens.issue(issued_to, cap_list, ttl_ms, max_risk)
    return {"token_id": token_id, "ttl_ms": ttl_ms, "caps": cap_list, "max_risk": max_risk}

@router.get("/status")
def router_status():
    return {
        "mode": sword_shield.mode,
        "strike_counts": dict(sword_shield.strike_count),
        "zone_states": dict(sword_shield.response.zone_state),
        "cache_size": len(cache.store),
        "metrics_count": len(metrics.events),
        "audit_count": len(audit._events),
    }
