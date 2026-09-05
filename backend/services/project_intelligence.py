"""ATLAS Project Intelligence Engine.

Turns ATLAS projects into living engineering threads: mission, knowledge, digital
Twin, requirements, decisions, tests, simulations, revisions, and audit events.
V1 is deterministic in-memory with optional MongoDB persistence.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4

VALID_STATUSES = {"idea", "research", "design", "prototype", "testing", "paused", "archived", "active"}
VALID_AI_OWNERS = {"Ajani", "Hermes", "Minerva", "Council"}
THREAD_SECTIONS = {
    "requirements", "missions", "discoveries", "knowledge_records", "digital_twins",
    "blueprints", "materials", "components", "risks", "tests", "simulations",
    "recommendations", "engineering_decisions", "council_decisions", "code_changes",
    "manufacturing_events", "maintenance_events", "chronicle_events", "open_questions",
    "next_actions",
}

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


def _timeline_event(project: Dict[str, Any], event_type: str, title: str, *, actor: str = "system", ref_id: str | None = None, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    event = {
        "event_id": f"event:{str(uuid4())[:12]}",
        "event_type": event_type,
        "title": title,
        "actor": actor,
        "ref_id": ref_id,
        "metadata": metadata or {},
        "created_at": _utc_now(),
    }
    project.setdefault("engineering_timeline", []).append(event)
    return event


def create_project(*, name: str, purpose: str, owner_ai: str = "Council", status: str = "idea", subject_tags: Optional[List[str]] = None, related_projects: Optional[List[str]] = None, project_id: Optional[str] = None) -> Dict[str, Any]:
    if owner_ai not in VALID_AI_OWNERS:
        raise ProjectIntelligenceError(f"invalid owner_ai: {owner_ai}")
    if status not in VALID_STATUSES:
        raise ProjectIntelligenceError(f"invalid status: {status}")
    pid = project_id or f"project:{_slug(name)}"
    if pid in _PROJECTS:
        raise ProjectIntelligenceError(f"project already exists: {pid}")
    now = _utc_now()
    project = {
        "project_id": pid, "name": name, "purpose": purpose, "owner_ai": owner_ai,
        "status": status, "priority": "normal", "subject_tags": subject_tags or [],
        "related_projects": related_projects or [], "engineering_dna": {
            "creator": "Founder", "responsible_ai": owner_ai, "hardware_version": None,
            "software_version": None, "primary_twin_id": None, "revision": 1,
        },
        "engineering_timeline": [],
        "created_at": now, "updated_at": now,
    }
    for section in THREAD_SECTIONS:
        project[section] = []
    _timeline_event(project, "project.created", f"Project created: {name}", actor=owner_ai, ref_id=pid)
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
    items = list(_PROJECTS.values())
    if owner_ai:
        items = [p for p in items if p["owner_ai"].lower() == owner_ai.lower()]
    if status:
        items = [p for p in items if p["status"] == status]
    if tag:
        items = [p for p in items if tag in p.get("subject_tags", [])]
    return sorted(items, key=lambda p: p["updated_at"], reverse=True)


def add_project_item(project_id: str, section: str, item: Dict[str, Any]) -> Dict[str, Any]:
    project = get_project(project_id)
    if not project:
        raise ProjectIntelligenceError(f"unknown project_id: {project_id}")
    if section not in THREAD_SECTIONS:
        raise ProjectIntelligenceError(f"invalid project section: {section}")
    entry = dict(item)
    entry.setdefault("item_id", f"{section}:{str(uuid4())[:8]}")
    entry.setdefault("created_at", _utc_now())
    project.setdefault(section, []).append(entry)
    _timeline_event(project, f"project.{section}.added", entry.get("title") or entry.get("name") or f"Added {section} item", actor=entry.get("owner_ai", "system"), ref_id=entry["item_id"], metadata={"section": section})
    project["updated_at"] = _utc_now()
    return project


def link_knowledge_record(project_id: str, record_id: str, title: str = "", validation_status: str = "unknown") -> Dict[str, Any]:
    return add_project_item(project_id, "knowledge_records", {"record_id": record_id, "title": title, "validation_status": validation_status})


def link_digital_twin(project_id: str, twin_id: str, name: str = "", twin_version: str | None = None, primary: bool = False) -> Dict[str, Any]:
    project = get_project(project_id)
    if not project:
        raise ProjectIntelligenceError(f"unknown project_id: {project_id}")
    if any(item.get("twin_id") == twin_id for item in project.get("digital_twins", [])):
        raise ProjectIntelligenceError(f"digital twin already linked: {twin_id}")
    result = add_project_item(project_id, "digital_twins", {"twin_id": twin_id, "name": name, "twin_version": twin_version, "primary": primary})
    if primary or not project["engineering_dna"].get("primary_twin_id"):
        project["engineering_dna"]["primary_twin_id"] = twin_id
    return result


def set_versions(project_id: str, *, software_version: str | None = None, hardware_version: str | None = None, actor: str = "Hermes") -> Dict[str, Any]:
    project = get_project(project_id)
    if not project:
        raise ProjectIntelligenceError(f"unknown project_id: {project_id}")
    dna = project["engineering_dna"]
    if software_version is not None:
        dna["software_version"] = software_version
    if hardware_version is not None:
        dna["hardware_version"] = hardware_version
    dna["revision"] = int(dna.get("revision", 1)) + 1
    _timeline_event(project, "project.version.updated", "Engineering version updated", actor=actor, metadata={"software_version": software_version, "hardware_version": hardware_version, "revision": dna["revision"]})
    project["updated_at"] = _utc_now()
    return project


def link_mission(project_id: str, mission_id: str, title: str = "", owner_ai: str = "Council") -> Dict[str, Any]:
    return add_project_item(project_id, "missions", {"mission_id": mission_id, "title": title, "owner_ai": owner_ai})


def link_discovery(project_id: str, discovery_id: str, title: str = "", confidence_score: int = 50) -> Dict[str, Any]:
    return add_project_item(project_id, "discoveries", {"discovery_id": discovery_id, "title": title, "confidence_score": max(0, min(100, int(confidence_score)))})


def add_risk(project_id: str, title: str, severity: str = "medium", mitigation: str = "") -> Dict[str, Any]:
    return add_project_item(project_id, "risks", {"title": title, "severity": severity, "mitigation": mitigation, "status": "open"})


def add_recommendation(project_id: str, title: str, owner_ai: str, rationale: str, confidence_score: int = 50) -> Dict[str, Any]:
    if owner_ai not in VALID_AI_OWNERS:
        raise ProjectIntelligenceError(f"invalid owner_ai: {owner_ai}")
    return add_project_item(project_id, "recommendations", {"title": title, "owner_ai": owner_ai, "rationale": rationale, "confidence_score": max(0, min(100, int(confidence_score))), "status": "proposed"})


def engineering_thread(project_id: str) -> Dict[str, Any]:
    project = get_project(project_id)
    if not project:
        raise ProjectIntelligenceError(f"unknown project_id: {project_id}")
    return {
        "project_id": project_id, "name": project["name"], "status": project["status"],
        "owner_ai": project["owner_ai"], "engineering_dna": project["engineering_dna"],
        "timeline": project["engineering_timeline"],
        "links": {section: project.get(section, []) for section in THREAD_SECTIONS},
        "updated_at": project["updated_at"],
    }


def project_brief(project_id: str) -> Dict[str, Any]:
    project = get_project(project_id)
    if not project:
        raise ProjectIntelligenceError(f"unknown project_id: {project_id}")
    return {"project_id": project_id, "name": project["name"], "status": project["status"], "owner_ai": project["owner_ai"], "priority": project.get("priority"), "engineering_dna": project["engineering_dna"], "counts": {section: len(project.get(section, [])) for section in THREAD_SECTIONS}, "top_risks": project["risks"][-5:], "latest_recommendations": project["recommendations"][-5:], "next_actions": project["next_actions"][-5:], "updated_at": project["updated_at"]}


def cross_project_matches(project_id: str) -> Dict[str, Any]:
    project = get_project(project_id)
    if not project:
        raise ProjectIntelligenceError(f"unknown project_id: {project_id}")
    tags = set(project.get("subject_tags", [])); matches = []
    for other_id, other in _PROJECTS.items():
        if other_id == project_id: continue
        overlap = sorted(tags.intersection(set(other.get("subject_tags", []))))
        explicit = other_id in project.get("related_projects", []) or project_id in other.get("related_projects", [])
        if overlap or explicit:
            matches.append({"project_id": other_id, "name": other["name"], "shared_tags": overlap, "explicit_relation": explicit, "reuse_hint": "Review this project for reusable materials, risks, tests, or design decisions."})
    return {"project": project, "matches": matches}


async def persist_project(project: Dict[str, Any]) -> None:
    if _DB is not None:
        await _DB.project_intelligence.update_one({"project_id": project["project_id"]}, {"$set": project}, upsert=True)


async def hydrate_from_mongo() -> Dict[str, int]:
    if _DB is None: return {"projects": 0}
    items = await _DB.project_intelligence.find({}, {"_id": 0}).to_list(5000)
    _PROJECTS.clear()
    for project in items:
        for section in THREAD_SECTIONS: project.setdefault(section, [])
        project.setdefault("engineering_timeline", [])
        project.setdefault("engineering_dna", {"creator": "Founder", "responsible_ai": project.get("owner_ai", "Council"), "hardware_version": None, "software_version": None, "primary_twin_id": None, "revision": 1})
        _PROJECTS[project["project_id"]] = project
    return {"projects": len(_PROJECTS)}


async def create_indexes() -> None:
    if _DB is None: return
    await _DB.project_intelligence.create_index("project_id", unique=True)
    await _DB.project_intelligence.create_index([("owner_ai", 1), ("status", 1)])
    await _DB.project_intelligence.create_index("subject_tags")
    await _DB.project_intelligence.create_index("digital_twins.twin_id")
    await _DB.project_intelligence.create_index("knowledge_records.record_id")


def reset_in_memory_state() -> None:
    _PROJECTS.clear()
