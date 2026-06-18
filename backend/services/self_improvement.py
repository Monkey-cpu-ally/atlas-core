"""
Self-Improvement Watcher.

Tracks proposals to improve ATLAS based on observed patterns and stores
them for human approval. By design this watcher NEVER applies a change on
its own — every proposal is stored with `status="pending"` until an explicit
approve/reject call is made via the routes layer.

Collections:
  * self_improvements   — proposal records

Categories:
  prompt | lesson_format | memory_retrieval | hud_layout |
  code_architecture | research_source | agent_personality | workflow

Risk levels:
  low | medium | high   (high = touches architecture; approval mandatory)

A "weekly report" is a deterministic roll-up computed from the last 7 days
of records. No background thread is started — call the route on demand.
"""
from __future__ import annotations

import logging
import os
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional
from uuid import uuid4

from motor.motor_asyncio import AsyncIOMotorClient

logger = logging.getLogger("atlas.self_improvement")

MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.environ.get("DB_NAME", "test_database")
_client: Optional[AsyncIOMotorClient] = None


def _db():
    global _client
    if _client is None:
        _client = AsyncIOMotorClient(MONGO_URL)
    return _client[DB_NAME]


def _col(): return _db()["self_improvements"]


def _utc(): return datetime.now(timezone.utc).isoformat()


VALID_CATEGORIES = {
    "prompt", "lesson_format", "memory_retrieval", "hud_layout",
    "code_architecture", "research_source", "agent_personality", "workflow",
}
VALID_RISK = {"low", "medium", "high"}


async def propose(
    *, observed_pattern: str, evidence: List[Dict[str, Any]],
    affected_system: str, proposed_change: str,
    category: str = "workflow", risk_level: str = "low",
    confidence_score: float = 0.5, source: str = "atlas",
) -> Dict[str, Any]:
    """Create a new improvement proposal."""
    if category not in VALID_CATEGORIES:
        raise ValueError(f"invalid category: {category}")
    if risk_level not in VALID_RISK:
        raise ValueError(f"invalid risk_level: {risk_level}")
    approval_required = risk_level in {"medium", "high"} or category in {
        "code_architecture", "agent_personality",
    }
    doc = {
        "id": uuid4().hex,
        "improvement_id": uuid4().hex,
        "observed_pattern": observed_pattern,
        "evidence": evidence,
        "affected_system": affected_system,
        "proposed_change": proposed_change,
        "category": category,
        "risk_level": risk_level,
        "confidence_score": max(0.0, min(1.0, float(confidence_score))),
        "approval_required": approval_required,
        "source": source,                 # who/what generated the proposal
        "status": "pending",
        "decision_note": None,
        "created_at": _utc(),
        "updated_at": _utc(),
    }
    doc["improvement_id"] = doc["id"]
    await _col().insert_one(doc)
    return _strip(doc)


async def list_proposals(
    status: Optional[str] = None, category: Optional[str] = None, limit: int = 100,
) -> List[Dict[str, Any]]:
    q: Dict[str, Any] = {}
    if status:
        q["status"] = status
    if category:
        q["category"] = category
    cur = _col().find(q, {"_id": 0}).sort("created_at", -1).limit(limit)
    return [d async for d in cur]


async def get(improvement_id: str) -> Optional[Dict[str, Any]]:
    return await _col().find_one({"id": improvement_id}, {"_id": 0})


async def decide(improvement_id: str, *, status: str, note: Optional[str] = None) -> Optional[Dict[str, Any]]:
    if status not in {"approved", "rejected", "applied"}:
        raise ValueError(f"invalid status: {status}")
    res = await _col().find_one_and_update(
        {"id": improvement_id},
        {"$set": {
            "status": status,
            "decision_note": note,
            "updated_at": _utc(),
        }},
        return_document=True,
    )
    if not res:
        return None
    return _strip(res)


async def history(limit: int = 200) -> List[Dict[str, Any]]:
    cur = _col().find({}, {"_id": 0}).sort("created_at", -1).limit(limit)
    return [d async for d in cur]


async def weekly_report() -> Dict[str, Any]:
    """Deterministic roll-up of the last 7 days. Computed live, no cron."""
    week_ago = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
    cur = _col().find(
        {"created_at": {"$gte": week_ago}}, {"_id": 0},
    ).sort("created_at", -1)
    items = [d async for d in cur]

    by_cat: Dict[str, int] = {}
    by_status: Dict[str, int] = {}
    by_risk: Dict[str, int] = {}
    for d in items:
        by_cat[d.get("category", "workflow")] = by_cat.get(d.get("category", "workflow"), 0) + 1
        by_status[d.get("status", "pending")] = by_status.get(d.get("status", "pending"), 0) + 1
        by_risk[d.get("risk_level", "low")] = by_risk.get(d.get("risk_level", "low"), 0) + 1

    pending_high = [d for d in items if d.get("status") == "pending" and d.get("risk_level") == "high"]

    # Pull the most-referenced affected_system in the week
    affected_counter: Dict[str, int] = {}
    for d in items:
        a = d.get("affected_system") or "unknown"
        affected_counter[a] = affected_counter.get(a, 0) + 1
    top_affected = sorted(
        affected_counter.items(), key=lambda kv: -kv[1],
    )[:5]

    return {
        "window_days": 7,
        "total_proposals": len(items),
        "by_category": by_cat,
        "by_status": by_status,
        "by_risk": by_risk,
        "needs_user_approval": [
            {"id": d["id"], "title": d.get("observed_pattern", "")[:80],
             "risk": d.get("risk_level"), "category": d.get("category")}
            for d in pending_high
        ],
        "top_affected_systems": [{"system": s, "count": c} for s, c in top_affected],
        "recent": [_strip(d) for d in items[:10]],
        "generated_at": _utc(),
    }


def _strip(d: Dict[str, Any]) -> Dict[str, Any]:
    return {k: v for k, v in d.items() if k != "_id"}
