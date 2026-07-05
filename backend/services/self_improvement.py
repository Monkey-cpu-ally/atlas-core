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
  code_architecture | research_source | agent_personality | workflow |
  dependency | testing | security | performance | ai_capability

Risk levels:
  low | medium | high   (high = touches architecture; approval mandatory)

A "weekly report" is a deterministic roll-up computed from the last 7 days
of records. No background thread is started — call the route on demand.
"""
from __future__ import annotations

import logging
import os
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4

from motor.motor_asyncio import AsyncIOMotorClient

logger = logging.getLogger("atlas.self_improvement")

MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.environ.get("DB_NAME", "test_database")
ROOT_DIR = Path(__file__).resolve().parents[2]
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
    "dependency", "testing", "security", "performance", "ai_capability",
}
VALID_RISK = {"low", "medium", "high"}
VALID_AI_ROLES = {"Ajani", "Hermes", "Minerva", "Council", "ATLAS"}


async def propose(
    *, observed_pattern: str, evidence: List[Dict[str, Any]],
    affected_system: str, proposed_change: str,
    category: str = "workflow", risk_level: str = "low",
    confidence_score: float = 0.5, source: str = "atlas",
    owner_ai: str = "Council", update_plan: Optional[List[str]] = None,
    rollback_plan: Optional[str] = None,
) -> Dict[str, Any]:
    """Create a new improvement proposal.

    Self-improvement proposals are recommendations, not automatic patches.
    High-risk or architecture/personality changes require explicit approval.
    """
    if category not in VALID_CATEGORIES:
        raise ValueError(f"invalid category: {category}")
    if risk_level not in VALID_RISK:
        raise ValueError(f"invalid risk_level: {risk_level}")
    if owner_ai not in VALID_AI_ROLES:
        raise ValueError(f"invalid owner_ai: {owner_ai}")
    approval_required = risk_level in {"medium", "high"} or category in {
        "code_architecture", "agent_personality", "security", "dependency",
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
        "owner_ai": owner_ai,
        "source": source,                 # who/what generated the proposal
        "status": "pending",
        "decision_note": None,
        "update_plan": update_plan or [],
        "rollback_plan": rollback_plan or "Revert the related commit or disable the changed subsystem flag.",
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


def analyze_repository_health() -> Dict[str, Any]:
    """Deterministic local repository scan for improvement opportunities.

    This scan is intentionally lightweight. It does not execute code or mutate
    files. It finds missing tests, oversized modules, TODO/FIXME markers, and
    recently added ATLAS service patterns that should receive tests.
    """
    backend = ROOT_DIR / "backend"
    services = backend / "services"
    routes = backend / "routes"
    tests = backend / "tests"

    service_files = sorted(services.glob("*.py")) if services.exists() else []
    route_files = sorted(routes.glob("*.py")) if routes.exists() else []
    test_files = sorted(tests.glob("test_*.py")) if tests.exists() else []
    test_names = {p.name for p in test_files}

    missing_tests = []
    large_modules = []
    todo_markers = []

    for path in service_files:
        if path.name.startswith("__"):
            continue
        expected = f"test_{path.stem}.py"
        if expected not in test_names:
            missing_tests.append(str(path.relative_to(ROOT_DIR)))
        try:
            lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            continue
        if len(lines) > 350:
            large_modules.append({"path": str(path.relative_to(ROOT_DIR)), "lines": len(lines)})
        for idx, line in enumerate(lines, start=1):
            if "TODO" in line or "FIXME" in line:
                todo_markers.append({"path": str(path.relative_to(ROOT_DIR)), "line": idx, "text": line.strip()[:160]})

    core_new_systems = [
        "autonomous_knowledge_engine.py", "source_sync_engine.py", "mission_scheduler.py",
        "project_intelligence.py", "knowledge_graph_engine.py", "source_code_connector.py",
    ]
    priority_missing = [
        f"backend/services/{name}" for name in core_new_systems
        if (services / name).exists() and f"test_{Path(name).stem}.py" not in test_names
    ]

    return {
        "generated_at": _utc(),
        "service_count": len(service_files),
        "route_count": len(route_files),
        "test_count": len(test_files),
        "missing_service_tests": missing_tests[:80],
        "priority_missing_tests": priority_missing,
        "large_modules": large_modules[:25],
        "todo_markers": todo_markers[:50],
        "recommendations": [
            "Add tests for every ATLAS service before adding more major features.",
            "Keep self-improvement proposal-only unless a human explicitly approves changes.",
            "Use CI failure artifacts as evidence for repair proposals.",
        ],
    }


async def propose_from_health_scan(source: str = "atlas-health-scan") -> Dict[str, Any]:
    """Run the health scan and create improvement proposals from its findings."""
    scan = analyze_repository_health()
    created: List[Dict[str, Any]] = []

    if scan["priority_missing_tests"]:
        created.append(await propose(
            observed_pattern="Critical ATLAS services are missing dedicated tests.",
            evidence=[{"type": "health_scan", "priority_missing_tests": scan["priority_missing_tests"]}],
            affected_system="backend/tests",
            proposed_change="Add unit tests for the newest ATLAS engines before expanding the roadmap further.",
            category="testing",
            risk_level="low",
            confidence_score=0.95,
            source=source,
            owner_ai="Ajani",
            update_plan=[
                "Create focused unit tests for each missing service.",
                "Run pytest locally and through GitHub Actions.",
                "Only continue roadmap development after failures are fixed.",
            ],
            rollback_plan="Remove only the new failing test file if it blocks urgent repair work, then recreate it correctly.",
        ))

    if scan["large_modules"]:
        created.append(await propose(
            observed_pattern="Some backend service modules are becoming large enough to risk maintenance problems.",
            evidence=[{"type": "health_scan", "large_modules": scan["large_modules"][:10]}],
            affected_system="backend/services",
            proposed_change="Review large modules and split them into smaller focused helpers when the split lowers complexity.",
            category="code_architecture",
            risk_level="medium",
            confidence_score=0.75,
            source=source,
            owner_ai="Council",
            update_plan=[
                "Identify oversized modules with multiple responsibilities.",
                "Split only when tests exist and behavior stays unchanged.",
                "Update imports and run CI after each refactor.",
            ],
        ))

    if scan["todo_markers"]:
        created.append(await propose(
            observed_pattern="TODO/FIXME markers exist in backend services.",
            evidence=[{"type": "health_scan", "todo_markers": scan["todo_markers"][:10]}],
            affected_system="backend/services",
            proposed_change="Convert TODO/FIXME markers into tracked ATLAS improvement tasks or resolve them.",
            category="workflow",
            risk_level="low",
            confidence_score=0.8,
            source=source,
            owner_ai="Hermes",
            update_plan=[
                "Review each TODO/FIXME marker.",
                "Resolve simple ones immediately.",
                "Create proposals for risky ones.",
            ],
        ))

    return {"scan": scan, "created_count": len(created), "created": created}


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
    by_owner: Dict[str, int] = {}
    for d in items:
        by_cat[d.get("category", "workflow")] = by_cat.get(d.get("category", "workflow"), 0) + 1
        by_status[d.get("status", "pending")] = by_status.get(d.get("status", "pending"), 0) + 1
        by_risk[d.get("risk_level", "low")] = by_risk.get(d.get("risk_level", "low"), 0) + 1
        by_owner[d.get("owner_ai", "Council")] = by_owner.get(d.get("owner_ai", "Council"), 0) + 1

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
        "by_owner_ai": by_owner,
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
