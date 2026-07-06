"""ATLAS Engineering Operating System.

Mission manager and readiness engine for ATLAS engineering work.
V1 provides deterministic mission creation, workflow advancement, task/risk
tracking, ERL scoring, and dashboard summaries. It coordinates projects without
performing unsafe autonomous implementation.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4

_DB: Any = None
_MISSIONS: Dict[str, Dict[str, Any]] = {}
_TASKS: Dict[str, Dict[str, Any]] = {}
_RISKS: Dict[str, Dict[str, Any]] = {}
_EVENTS: Dict[str, Dict[str, Any]] = {}

AI_OWNERS = {"Ajani", "Hermes", "Minerva", "Council"}
MISSION_STATUSES = {"planned", "active", "blocked", "review", "paused", "completed", "archived"}
TASK_STATUSES = {"todo", "in_progress", "blocked", "review", "done", "cancelled"}
WORKFLOW_PHASES = [
    "idea",
    "research",
    "architecture",
    "engineering_review",
    "simulation",
    "prototype",
    "validation",
    "council_approval",
    "production_candidate",
    "maintained",
]
ERL_LABELS = {
    1: "Concept",
    2: "Research",
    3: "Initial Architecture",
    4: "Simulation",
    5: "Prototype Design",
    6: "Functional Prototype",
    7: "Validation",
    8: "Production Candidate",
    9: "Production Ready",
    10: "Continuous Improvement",
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def attach_mongo(db: Any) -> None:
    global _DB
    _DB = db


def persistence_enabled() -> bool:
    return _DB is not None


def create_mission(
    *,
    title: str,
    project_id: str,
    objective: str,
    lead_ai: str,
    council_members: Optional[List[str]] = None,
    domains: Optional[List[str]] = None,
    status: str = "planned",
    workflow_phase: str = "idea",
    constraints: Optional[List[str]] = None,
    success_criteria: Optional[List[str]] = None,
) -> Dict[str, Any]:
    if lead_ai not in AI_OWNERS:
        raise ValueError(f"invalid lead_ai: {lead_ai}")
    if status not in MISSION_STATUSES:
        raise ValueError(f"invalid status: {status}")
    if workflow_phase not in WORKFLOW_PHASES:
        raise ValueError(f"invalid workflow_phase: {workflow_phase}")

    mission_id = f"AEOS-MSN-{str(uuid4())[:8]}"
    now = _utc_now()
    mission = {
        "mission_id": mission_id,
        "title": title,
        "project_id": project_id,
        "objective": objective,
        "lead_ai": lead_ai,
        "council_members": sorted(set(council_members or ["Council"])),
        "domains": sorted(set(domains or [])),
        "status": status,
        "workflow_phase": workflow_phase,
        "engineering_readiness_level": _phase_to_erl(workflow_phase),
        "engineering_readiness_label": ERL_LABELS[_phase_to_erl(workflow_phase)],
        "completion_percent": _phase_completion(workflow_phase),
        "constraints": sorted(set(constraints or [])),
        "success_criteria": sorted(set(success_criteria or [])),
        "current_blockers": [],
        "next_action": "Define research targets and engineering requirements.",
        "created_at": now,
        "updated_at": now,
    }
    _MISSIONS[mission_id] = mission
    _event(mission_id=mission_id, event_type="mission_created", note="Engineering mission created.")
    return mission


def get_mission(mission_id: str) -> Optional[Dict[str, Any]]:
    return _MISSIONS.get(mission_id)


def list_missions(*, project_id: Optional[str] = None, lead_ai: Optional[str] = None, status: Optional[str] = None, phase: Optional[str] = None, limit: int = 250) -> List[Dict[str, Any]]:
    items = list(_MISSIONS.values())
    if project_id:
        items = [item for item in items if item["project_id"] == project_id]
    if lead_ai:
        items = [item for item in items if item["lead_ai"].lower() == lead_ai.lower()]
    if status:
        items = [item for item in items if item["status"] == status]
    if phase:
        items = [item for item in items if item["workflow_phase"] == phase]
    return sorted(items, key=lambda item: item["updated_at"], reverse=True)[:limit]


def advance_mission(*, mission_id: str, workflow_phase: str, note: str, actor: str = "system") -> Dict[str, Any]:
    mission = _require_mission(mission_id)
    if workflow_phase not in WORKFLOW_PHASES:
        raise ValueError(f"invalid workflow_phase: {workflow_phase}")
    mission["workflow_phase"] = workflow_phase
    mission["engineering_readiness_level"] = _phase_to_erl(workflow_phase)
    mission["engineering_readiness_label"] = ERL_LABELS[mission["engineering_readiness_level"]]
    mission["completion_percent"] = _phase_completion(workflow_phase)
    mission["status"] = "active" if mission["status"] == "planned" else mission["status"]
    mission["next_action"] = _next_action_for_phase(workflow_phase)
    mission["updated_at"] = _utc_now()
    _event(mission_id=mission_id, event_type="mission_advanced", note=note, actor=actor)
    return mission


def create_task(*, mission_id: str, title: str, owner_ai: str, phase: str, priority: str = "medium", status: str = "todo", evidence_required: bool = True) -> Dict[str, Any]:
    _require_mission(mission_id)
    if owner_ai not in AI_OWNERS:
        raise ValueError(f"invalid owner_ai: {owner_ai}")
    if phase not in WORKFLOW_PHASES:
        raise ValueError(f"invalid phase: {phase}")
    if status not in TASK_STATUSES:
        raise ValueError(f"invalid status: {status}")
    task_id = f"AEOS-TSK-{str(uuid4())[:8]}"
    task = {
        "task_id": task_id,
        "mission_id": mission_id,
        "title": title,
        "owner_ai": owner_ai,
        "phase": phase,
        "priority": priority,
        "status": status,
        "evidence_required": evidence_required,
        "created_at": _utc_now(),
        "updated_at": _utc_now(),
    }
    _TASKS[task_id] = task
    _event(mission_id=mission_id, event_type="task_created", note=title, actor=owner_ai)
    _recalculate_mission(mission_id)
    return task


def update_task_status(*, task_id: str, status: str, note: str, actor: str = "system") -> Dict[str, Any]:
    task = _TASKS.get(task_id)
    if not task:
        raise ValueError(f"unknown task_id: {task_id}")
    if status not in TASK_STATUSES:
        raise ValueError(f"invalid status: {status}")
    task["status"] = status
    task["updated_at"] = _utc_now()
    _event(mission_id=task["mission_id"], event_type="task_status_changed", note=note, actor=actor)
    _recalculate_mission(task["mission_id"])
    return task


def create_risk(*, mission_id: str, title: str, severity: str, mitigation: str, owner_ai: str, status: str = "open") -> Dict[str, Any]:
    _require_mission(mission_id)
    if owner_ai not in AI_OWNERS:
        raise ValueError(f"invalid owner_ai: {owner_ai}")
    risk_id = f"AEOS-RSK-{str(uuid4())[:8]}"
    risk = {
        "risk_id": risk_id,
        "mission_id": mission_id,
        "title": title,
        "severity": severity,
        "mitigation": mitigation,
        "owner_ai": owner_ai,
        "status": status,
        "created_at": _utc_now(),
        "updated_at": _utc_now(),
    }
    _RISKS[risk_id] = risk
    _event(mission_id=mission_id, event_type="risk_created", note=title, actor=owner_ai)
    _recalculate_mission(mission_id)
    return risk


def list_tasks(*, mission_id: Optional[str] = None, status: Optional[str] = None, owner_ai: Optional[str] = None, limit: int = 250) -> List[Dict[str, Any]]:
    items = list(_TASKS.values())
    if mission_id:
        items = [item for item in items if item["mission_id"] == mission_id]
    if status:
        items = [item for item in items if item["status"] == status]
    if owner_ai:
        items = [item for item in items if item["owner_ai"].lower() == owner_ai.lower()]
    return sorted(items, key=lambda item: item["updated_at"], reverse=True)[:limit]


def list_risks(*, mission_id: Optional[str] = None, status: Optional[str] = None, limit: int = 250) -> List[Dict[str, Any]]:
    items = list(_RISKS.values())
    if mission_id:
        items = [item for item in items if item["mission_id"] == mission_id]
    if status:
        items = [item for item in items if item["status"] == status]
    return sorted(items, key=lambda item: item["updated_at"], reverse=True)[:limit]


def dashboard_summary() -> Dict[str, Any]:
    by_status = {status: 0 for status in sorted(MISSION_STATUSES)}
    by_ai = {owner: 0 for owner in sorted(AI_OWNERS)}
    by_phase = {phase: 0 for phase in WORKFLOW_PHASES}
    for mission in _MISSIONS.values():
        by_status[mission["status"]] = by_status.get(mission["status"], 0) + 1
        by_ai[mission["lead_ai"]] = by_ai.get(mission["lead_ai"], 0) + 1
        by_phase[mission["workflow_phase"]] = by_phase.get(mission["workflow_phase"], 0) + 1
    avg_erl = round(sum(m["engineering_readiness_level"] for m in _MISSIONS.values()) / len(_MISSIONS), 2) if _MISSIONS else 0
    return {
        "title": "ATLAS Engineering Operating System Dashboard",
        "generated_at": _utc_now(),
        "mission_count": len(_MISSIONS),
        "task_count": len(_TASKS),
        "risk_count": len(_RISKS),
        "event_count": len(_EVENTS),
        "average_erl": avg_erl,
        "missions_by_status": by_status,
        "missions_by_ai": by_ai,
        "missions_by_phase": by_phase,
        "open_blockers": [r for r in list_risks(status="open", limit=25) if r["severity"].lower() in {"high", "critical"}],
    }


def list_events(*, mission_id: Optional[str] = None, event_type: Optional[str] = None, limit: int = 250) -> List[Dict[str, Any]]:
    items = list(_EVENTS.values())
    if mission_id:
        items = [item for item in items if item["mission_id"] == mission_id]
    if event_type:
        items = [item for item in items if item["event_type"] == event_type]
    return sorted(items, key=lambda item: item["timestamp"], reverse=True)[:limit]


def seed_foundation_missions() -> Dict[str, Any]:
    created = 0
    for seed in _foundation_mission_seed_data():
        mission = create_mission(**seed)
        created += 1
        create_task(mission_id=mission["mission_id"], title="Build knowledge brief", owner_ai=mission["lead_ai"], phase="research", priority="high")
        create_task(mission_id=mission["mission_id"], title="Define engineering acceptance criteria", owner_ai="Ajani", phase="architecture", priority="high")
    return {"created_or_updated": created, "items": list_missions(limit=1000)}


def reset_in_memory_state() -> None:
    _MISSIONS.clear(); _TASKS.clear(); _RISKS.clear(); _EVENTS.clear()


async def persist_all() -> None:
    if _DB is None:
        return
    for item in _MISSIONS.values():
        await _DB.engineering_missions.update_one({"mission_id": item["mission_id"]}, {"$set": item}, upsert=True)
    for item in _TASKS.values():
        await _DB.engineering_tasks.update_one({"task_id": item["task_id"]}, {"$set": item}, upsert=True)
    for item in _RISKS.values():
        await _DB.engineering_risks.update_one({"risk_id": item["risk_id"]}, {"$set": item}, upsert=True)
    for item in _EVENTS.values():
        await _DB.engineering_activity_log.update_one({"event_id": item["event_id"]}, {"$set": item}, upsert=True)


async def hydrate_from_mongo() -> Dict[str, int]:
    if _DB is None:
        return {"engineering_missions": 0, "engineering_tasks": 0, "engineering_risks": 0, "engineering_activity_log": 0}
    missions = await _DB.engineering_missions.find({}, {"_id": 0}).to_list(10000)
    tasks = await _DB.engineering_tasks.find({}, {"_id": 0}).to_list(10000)
    risks = await _DB.engineering_risks.find({}, {"_id": 0}).to_list(10000)
    events = await _DB.engineering_activity_log.find({}, {"_id": 0}).to_list(10000)
    reset_in_memory_state()
    for item in missions:
        _MISSIONS[item["mission_id"]] = item
    for item in tasks:
        _TASKS[item["task_id"]] = item
    for item in risks:
        _RISKS[item["risk_id"]] = item
    for item in events:
        _EVENTS[item["event_id"]] = item
    return {"engineering_missions": len(_MISSIONS), "engineering_tasks": len(_TASKS), "engineering_risks": len(_RISKS), "engineering_activity_log": len(_EVENTS)}


async def create_indexes() -> None:
    if _DB is None:
        return
    await _DB.engineering_missions.create_index("mission_id", unique=True)
    await _DB.engineering_missions.create_index("project_id")
    await _DB.engineering_missions.create_index("lead_ai")
    await _DB.engineering_tasks.create_index("task_id", unique=True)
    await _DB.engineering_tasks.create_index("mission_id")
    await _DB.engineering_risks.create_index("risk_id", unique=True)
    await _DB.engineering_risks.create_index("mission_id")
    await _DB.engineering_activity_log.create_index("event_id", unique=True)
    await _DB.engineering_activity_log.create_index("mission_id")


def _require_mission(mission_id: str) -> Dict[str, Any]:
    mission = _MISSIONS.get(mission_id)
    if not mission:
        raise ValueError(f"unknown mission_id: {mission_id}")
    return mission


def _phase_to_erl(phase: str) -> int:
    mapping = {
        "idea": 1,
        "research": 2,
        "architecture": 3,
        "engineering_review": 3,
        "simulation": 4,
        "prototype": 5,
        "validation": 7,
        "council_approval": 8,
        "production_candidate": 8,
        "maintained": 10,
    }
    return mapping[phase]


def _phase_completion(phase: str) -> int:
    return int((WORKFLOW_PHASES.index(phase) + 1) / len(WORKFLOW_PHASES) * 100)


def _next_action_for_phase(phase: str) -> str:
    return {
        "idea": "Define mission objective and core constraints.",
        "research": "Build project knowledge brief and evidence map.",
        "architecture": "Create system architecture and acceptance criteria.",
        "engineering_review": "Run structured engineering review.",
        "simulation": "Connect digital twin or simulation checks.",
        "prototype": "Prepare prototype design package.",
        "validation": "Collect test evidence and failure notes.",
        "council_approval": "Prepare Council decision packet.",
        "production_candidate": "Complete production readiness checklist.",
        "maintained": "Monitor performance and continuous improvement.",
    }[phase]


def _recalculate_mission(mission_id: str) -> None:
    mission = _require_mission(mission_id)
    tasks = list_tasks(mission_id=mission_id, limit=10000)
    risks = list_risks(mission_id=mission_id, status="open", limit=10000)
    blocked = [task["title"] for task in tasks if task["status"] == "blocked"]
    mission["current_blockers"] = blocked + [risk["title"] for risk in risks if risk["severity"].lower() in {"high", "critical"}]
    if tasks:
        done = len([task for task in tasks if task["status"] == "done"])
        task_completion = int(done / len(tasks) * 100)
        mission["completion_percent"] = max(mission["completion_percent"], task_completion)
    if mission["current_blockers"]:
        mission["status"] = "blocked"
    mission["updated_at"] = _utc_now()


def _event(*, mission_id: str, event_type: str, note: str, actor: str = "system") -> Dict[str, Any]:
    event_id = f"AEOS-EVT-{str(uuid4())[:8]}"
    event = {"event_id": event_id, "mission_id": mission_id, "event_type": event_type, "note": note, "actor": actor, "timestamp": _utc_now()}
    _EVENTS[event_id] = event
    return event


def _foundation_mission_seed_data() -> List[Dict[str, Any]]:
    return [
        {"title": "Weaver Engineering Mission", "project_id": "project:weaver", "objective": "Move The Weaver from architecture to validated prototype planning with traceable robotics, manufacturing, and safety evidence.", "lead_ai": "Hermes", "domains": ["Robotics", "Manufacturing", "Digital Twins"], "constraints": ["human safety", "verified materials", "maintainable design"], "success_criteria": ["knowledge brief", "risk register", "prototype readiness criteria"]},
        {"title": "Power Cell Engineering Mission", "project_id": "project:power_cell", "objective": "Organize safe energy-cell research into evidence-backed design, testing, and validation stages.", "lead_ai": "Hermes", "domains": ["Energy", "Chemistry", "Materials"], "constraints": ["safety first", "no unsupported performance claims"], "success_criteria": ["safety review", "materials review", "test plan"]},
        {"title": "Minerva Plant Library Mission", "project_id": "project:minerva_plant_library", "objective": "Build a curated botany and ecological restoration knowledge foundation with safety and evidence controls.", "lead_ai": "Minerva", "domains": ["Botany", "Ecology", "Agriculture"], "constraints": ["ecological safety", "source traceability"], "success_criteria": ["plant profile schema", "toxicity review", "environmental context rules"]},
    ]
