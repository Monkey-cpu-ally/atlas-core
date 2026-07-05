"""ATLAS Project Intelligence Engine.

Turns ATLAS projects into living workspaces with mission links, knowledge links,
risks, recommendations, council decisions, and cross-project reuse signals.
V1 is deterministic in-memory with optional MongoDB persistence.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4

VALID_STATUSES = {"idea", "research", "design", "prototype", "testing", "paused", "archived", "active"}
VALID_AI_OWNERS = {"Ajani", "Hermes", "Minerva", "Council"}

_PROJECTS: Dict[str, Dict[str, Any]] = {}
_DB: Any = None


class ProjectIntelligenceError(RuntimeError):
    """Raised when a Project Intelligence operation is invalid."""


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _slug(value: str) -> str:
    return "".join(ch.lower() if ch.isalnum() else "_" for ch in value).strip("_")


def attach_mongo(db: Any) -> None:
    global _DB
    _DB = db


def persistence_enabled() -> bool:
    return _DB is not None


def create_project(
    *,
    name: str,
    purpose: str,
    owner_ai: str = "Council",
    status: str = "idea",
    subject_tags: Optional[List[str]] = None,
    related_projects: Optional[List[str]] = None,
    project_id: Optional[str] = None,
) -> Dict[str, Any]:
    if owner_ai not in VALID_AI_OWNERS:
        raise ProjectIntelligenceError(f"invalid owner_ai: {owner_ai}")
    if status not in VALID_STATUSES:
        raise ProjectIntelligenceError(f"invalid status: {status}")

    pid = project_id or f"project:{_slug(name)}"
    if pid in _PROJECTS:
        raise ProjectIntelligenceError(f"project already exists: {pid}")

    project = {
        "project_id": pid,
        "name": name,
        "purpose": purpose,
        "owner_ai": owner_ai,
        "status": status,
        "priority": "normal",
        "subject_tags": subject_tags or [],
        "related_projects": related_projects or [],
        "missions": [],
        "discoveries": [],
        "knowledge_records": [],
        "blueprints": [],
        "materials": [],
        "components": [],
        "risks": [],
        "tests": [],
        "recommendations": [],
        "council_decisions": [],
        "chronicle_events": [],
        "open_questions": [],
        "next_actions": [],
        "created_at": _utc_now(),
        "updated_at": _utc_now(),
    }
    _PROJECTS[pid] = project
    return project


def upsert_project(**kwargs: Any) -> Dict[str, Any]:
    project_id = kwargs.get("project_id") or f"project:{_slug(kwargs.get('name', 'untitled'))}"
    if project_id in _PROJECTS:
        project = _PROJECTS[project_id]
        for key in ("name", "purpose", "owner_ai", "status", "priority", "subject_tags", "related_projects"):
            if key in kwargs and kwargs[key] is not None:
                project[key] = kwargs[key]
        project["updated_at"] = _utc_now()
        return project
    kwargs["project_id"] = project_id
    return create_project(**kwargs)


def get_project(project_id: str) -> Optional[Dict[str, Any]]:
    return _PROJECTS.get(project_id)


def list_projects(owner_ai: Optional[str] = None, status: Optional[str] = None, tag: Optional[str] = None) -> List[Dict[str, Any]]:
    projects = list(_PROJECTS.values())
    if owner_ai:
        projects = [p for p in projects if p["owner_ai"].lower() == owner_ai.lower()]
    if status:
        projects = [p for p in projects if p["status"] == status]
    if tag:
        projects = [p for p in projects if tag in p.get("subject_tags", [])]
    return sorted(projects, key=lambda p: p["updated_at"], reverse=True)


def add_project_item(project_id: str, section: str, item: Dict[str, Any]) -> Dict[str, Any]:
    project = get_project(project_id)
    if not project:
        raise ProjectIntelligenceError(f"unknown project_id: {project_id}")
    if section not in {
        "missions", "discoveries", "knowledge_records", "blueprints", "materials",
        "components", "risks", "tests", "recommendations", "council_decisions",
        "chronicle_events", "open_questions", "next_actions",
    }:
        raise ProjectIntelligenceError(f"invalid project section: {section}")
    entry = dict(item)
    entry.setdefault("item_id", f"{section}:{str(uuid4())[:8]}")
    entry.setdefault("created_at", _utc_now())
    project[section].append(entry)
    project["updated_at"] = _utc_now()
    return project


def link_mission(project_id: str, mission_id: str, title: str = "", owner_ai: str = "Council") -> Dict[str, Any]:
    return add_project_item(project_id, "missions", {"mission_id": mission_id, "title": title, "owner_ai": owner_ai})


def link_discovery(project_id: str, discovery_id: str, title: str = "", confidence_score: int = 50) -> Dict[str, Any]:
    return add_project_item(project_id, "discoveries", {
        "discovery_id": discovery_id,
        "title": title,
        "confidence_score": max(0, min(100, int(confidence_score))),
    })


def add_risk(project_id: str, title: str, severity: str = "medium", mitigation: str = "") -> Dict[str, Any]:
    return add_project_item(project_id, "risks", {"title": title, "severity": severity, "mitigation": mitigation, "status": "open"})


def add_recommendation(project_id: str, title: str, owner_ai: str, rationale: str, confidence_score: int = 50) -> Dict[str, Any]:
    if owner_ai not in VALID_AI_OWNERS:
        raise ProjectIntelligenceError(f"invalid owner_ai: {owner_ai}")
    return add_project_item(project_id, "recommendations", {
        "title": title,
        "owner_ai": owner_ai,
        "rationale": rationale,
        "confidence_score": max(0, min(100, int(confidence_score))),
        "status": "proposed",
    })


def project_brief(project_id: str) -> Dict[str, Any]:
    project = get_project(project_id)
    if not project:
        raise ProjectIntelligenceError(f"unknown project_id: {project_id}")
    return {
        "project_id": project_id,
        "name": project["name"],
        "status": project["status"],
        "owner_ai": project["owner_ai"],
        "priority": project.get("priority"),
        "counts": {
            "missions": len(project["missions"]),
            "discoveries": len(project["discoveries"]),
            "knowledge_records": len(project["knowledge_records"]),
            "blueprints": len(project["blueprints"]),
            "risks": len(project["risks"]),
            "recommendations": len(project["recommendations"]),
            "council_decisions": len(project["council_decisions"]),
        },
        "top_risks": project["risks"][-5:],
        "latest_recommendations": project["recommendations"][-5:],
        "next_actions": project["next_actions"][-5:],
        "updated_at": project["updated_at"],
    }


def cross_project_matches(project_id: str) -> Dict[str, Any]:
    project = get_project(project_id)
    if not project:
        raise ProjectIntelligenceError(f"unknown project_id: {project_id}")
    tags = set(project.get("subject_tags", []))
    matches = []
    for other_id, other in _PROJECTS.items():
        if other_id == project_id:
            continue
        overlap = sorted(tags.intersection(set(other.get("subject_tags", []))))
        explicit = other_id in project.get("related_projects", []) or project_id in other.get("related_projects", [])
        if overlap or explicit:
            matches.append({
                "project_id": other_id,
                "name": other["name"],
                "shared_tags": overlap,
                "explicit_relation": explicit,
                "reuse_hint": "Review this project for reusable materials, risks, tests, or design decisions.",
            })
    return {"project": project, "matches": matches}


async def persist_project(project: Dict[str, Any]) -> None:
    if _DB is None:
        return
    await _DB.project_intelligence.update_one({"project_id": project["project_id"]}, {"$set": project}, upsert=True)


async def hydrate_from_mongo() -> Dict[str, int]:
    if _DB is None:
        return {"projects": 0}
    projects = await _DB.project_intelligence.find({}, {"_id": 0}).to_list(5000)
    _PROJECTS.clear()
    for project in projects:
        _PROJECTS[project["project_id"]] = project
    return {"projects": len(_PROJECTS)}


async def create_indexes() -> None:
    if _DB is None:
        return
    await _DB.project_intelligence.create_index("project_id", unique=True)
    await _DB.project_intelligence.create_index([("owner_ai", 1), ("status", 1)])
    await _DB.project_intelligence.create_index("subject_tags")


def reset_in_memory_state() -> None:
    _PROJECTS.clear()
