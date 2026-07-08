"""ATLAS Engineering Playbook Engine.

Living engineering manuals for ATLAS technologies and projects. V1 stores
playbooks, sections, components, materials, failures, patterns, and revisions.
It is registry-driven and does not perform external scraping or unsafe build
automation.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4

_DB: Any = None
_PLAYBOOKS: Dict[str, Dict[str, Any]] = {}
_SECTIONS: Dict[str, Dict[str, Any]] = {}
_COMPONENTS: Dict[str, Dict[str, Any]] = {}
_MATERIALS: Dict[str, Dict[str, Any]] = {}
_FAILURES: Dict[str, Dict[str, Any]] = {}
_PATTERNS: Dict[str, Dict[str, Any]] = {}
_REVISIONS: Dict[str, Dict[str, Any]] = {}

AI_OWNERS = {"Ajani", "Hermes", "Minerva", "Council"}
PLAYBOOK_TYPES = {"technology", "project", "discipline", "component", "material", "process"}
SECTION_TYPES = {
    "overview", "science", "math", "materials", "components", "manufacturing", "assembly",
    "electronics", "software", "safety", "standards", "testing", "failure_analysis",
    "maintenance", "environmental_impact", "costs", "suppliers", "research_timeline",
    "prototype_history", "future_improvements", "atlas_notes",
}
STATUS_VALUES = {"draft", "active", "review", "approved", "superseded", "archived"}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def attach_mongo(db: Any) -> None:
    global _DB
    _DB = db


def persistence_enabled() -> bool:
    return _DB is not None


def create_playbook(
    *,
    title: str,
    playbook_type: str,
    owner_ai: str,
    domains: List[str],
    summary: str,
    related_project_ids: Optional[List[str]] = None,
    related_technology_ids: Optional[List[str]] = None,
    status: str = "draft",
) -> Dict[str, Any]:
    if playbook_type not in PLAYBOOK_TYPES:
        raise ValueError(f"invalid playbook_type: {playbook_type}")
    if owner_ai not in AI_OWNERS:
        raise ValueError(f"invalid owner_ai: {owner_ai}")
    if status not in STATUS_VALUES:
        raise ValueError(f"invalid status: {status}")
    playbook_id = f"EPB-{str(uuid4())[:8]}"
    now = _utc_now()
    playbook = {
        "playbook_id": playbook_id,
        "title": title,
        "playbook_type": playbook_type,
        "owner_ai": owner_ai,
        "domains": sorted(set(domains)),
        "summary": summary,
        "related_project_ids": sorted(set(related_project_ids or [])),
        "related_technology_ids": sorted(set(related_technology_ids or [])),
        "status": status,
        "version": 1,
        "section_count": 0,
        "component_count": 0,
        "material_count": 0,
        "failure_count": 0,
        "pattern_count": 0,
        "created_at": now,
        "updated_at": now,
    }
    _PLAYBOOKS[playbook_id] = playbook
    _revision(playbook_id=playbook_id, change_type="created", note="Playbook created.", actor=owner_ai)
    return playbook


def add_section(*, playbook_id: str, section_type: str, title: str, content: str, evidence_level: str = "internal", confidence_score: int = 50) -> Dict[str, Any]:
    _require_playbook(playbook_id)
    if section_type not in SECTION_TYPES:
        raise ValueError(f"invalid section_type: {section_type}")
    section_id = f"EPS-{str(uuid4())[:8]}"
    section = {
        "section_id": section_id,
        "playbook_id": playbook_id,
        "section_type": section_type,
        "title": title,
        "content": content,
        "evidence_level": evidence_level,
        "confidence_score": max(0, min(100, int(confidence_score))),
        "created_at": _utc_now(),
        "updated_at": _utc_now(),
    }
    _SECTIONS[section_id] = section
    _touch_counts(playbook_id)
    _revision(playbook_id=playbook_id, change_type="section_added", note=title, actor="system")
    return section


def add_component(*, playbook_id: str, name: str, component_type: str, function: str, key_specs: Optional[Dict[str, Any]] = None, risks: Optional[List[str]] = None) -> Dict[str, Any]:
    _require_playbook(playbook_id)
    component_id = f"EPC-{str(uuid4())[:8]}"
    component = {
        "component_id": component_id,
        "playbook_id": playbook_id,
        "name": name,
        "component_type": component_type,
        "function": function,
        "key_specs": key_specs or {},
        "risks": risks or [],
        "created_at": _utc_now(),
    }
    _COMPONENTS[component_id] = component
    _touch_counts(playbook_id)
    _revision(playbook_id=playbook_id, change_type="component_added", note=name, actor="Hermes")
    return component


def add_material(*, playbook_id: str, name: str, material_family: str, properties: Optional[Dict[str, Any]] = None, applications: Optional[List[str]] = None, sustainability_notes: Optional[str] = None) -> Dict[str, Any]:
    _require_playbook(playbook_id)
    material_id = f"EPM-{str(uuid4())[:8]}"
    material = {
        "material_id": material_id,
        "playbook_id": playbook_id,
        "name": name,
        "material_family": material_family,
        "properties": properties or {},
        "applications": applications or [],
        "sustainability_notes": sustainability_notes,
        "created_at": _utc_now(),
    }
    _MATERIALS[material_id] = material
    _touch_counts(playbook_id)
    _revision(playbook_id=playbook_id, change_type="material_added", note=name, actor="Minerva")
    return material


def add_failure(*, playbook_id: str, title: str, root_cause: str, severity: str, corrective_action: str, preventive_action: str, evidence: Optional[str] = None) -> Dict[str, Any]:
    _require_playbook(playbook_id)
    failure_id = f"EPF-{str(uuid4())[:8]}"
    failure = {
        "failure_id": failure_id,
        "playbook_id": playbook_id,
        "title": title,
        "root_cause": root_cause,
        "severity": severity,
        "corrective_action": corrective_action,
        "preventive_action": preventive_action,
        "evidence": evidence,
        "created_at": _utc_now(),
    }
    _FAILURES[failure_id] = failure
    _touch_counts(playbook_id)
    _revision(playbook_id=playbook_id, change_type="failure_added", note=title, actor="Council")
    return failure


def add_design_pattern(*, playbook_id: str, name: str, pattern_type: str, intent: str, structure: List[str], tradeoffs: Optional[List[str]] = None) -> Dict[str, Any]:
    _require_playbook(playbook_id)
    pattern_id = f"EPP-{str(uuid4())[:8]}"
    pattern = {
        "pattern_id": pattern_id,
        "playbook_id": playbook_id,
        "name": name,
        "pattern_type": pattern_type,
        "intent": intent,
        "structure": structure,
        "tradeoffs": tradeoffs or [],
        "created_at": _utc_now(),
    }
    _PATTERNS[pattern_id] = pattern
    _touch_counts(playbook_id)
    _revision(playbook_id=playbook_id, change_type="pattern_added", note=name, actor="Hermes")
    return pattern


def get_playbook(playbook_id: str) -> Optional[Dict[str, Any]]:
    return _PLAYBOOKS.get(playbook_id)


def list_playbooks(*, playbook_type: Optional[str] = None, owner_ai: Optional[str] = None, domain: Optional[str] = None, status: Optional[str] = None, project_id: Optional[str] = None, limit: int = 500) -> List[Dict[str, Any]]:
    items = list(_PLAYBOOKS.values())
    if playbook_type:
        items = [item for item in items if item["playbook_type"] == playbook_type]
    if owner_ai:
        items = [item for item in items if item["owner_ai"].lower() == owner_ai.lower()]
    if domain:
        d = domain.lower()
        items = [item for item in items if d in {x.lower() for x in item.get("domains", [])}]
    if status:
        items = [item for item in items if item["status"] == status]
    if project_id:
        items = [item for item in items if project_id in item.get("related_project_ids", [])]
    return sorted(items, key=lambda item: item["updated_at"], reverse=True)[:limit]


def list_sections(playbook_id: str) -> List[Dict[str, Any]]:
    return sorted([s for s in _SECTIONS.values() if s["playbook_id"] == playbook_id], key=lambda s: s["section_type"])


def playbook_detail(playbook_id: str) -> Dict[str, Any]:
    playbook = _require_playbook(playbook_id)
    return {
        "playbook": playbook,
        "sections": list_sections(playbook_id),
        "components": [x for x in _COMPONENTS.values() if x["playbook_id"] == playbook_id],
        "materials": [x for x in _MATERIALS.values() if x["playbook_id"] == playbook_id],
        "failures": [x for x in _FAILURES.values() if x["playbook_id"] == playbook_id],
        "patterns": [x for x in _PATTERNS.values() if x["playbook_id"] == playbook_id],
        "revisions": [x for x in _REVISIONS.values() if x["playbook_id"] == playbook_id],
    }


def playbook_summary() -> Dict[str, Any]:
    by_type = {typ: 0 for typ in sorted(PLAYBOOK_TYPES)}
    by_ai = {owner: 0 for owner in sorted(AI_OWNERS)}
    domains = set()
    for item in _PLAYBOOKS.values():
        by_type[item["playbook_type"]] += 1
        by_ai[item["owner_ai"]] += 1
        domains.update(item.get("domains", []))
    return {
        "title": "ATLAS Engineering Playbook Engine Summary",
        "generated_at": _utc_now(),
        "playbook_count": len(_PLAYBOOKS),
        "section_count": len(_SECTIONS),
        "component_count": len(_COMPONENTS),
        "material_count": len(_MATERIALS),
        "failure_count": len(_FAILURES),
        "pattern_count": len(_PATTERNS),
        "revision_count": len(_REVISIONS),
        "domain_count": len(domains),
        "playbook_types": by_type,
        "owner_ai": by_ai,
    }


def seed_foundation_playbooks() -> Dict[str, Any]:
    created = []
    robotics = create_playbook(title="Advanced Robotics Engineering Playbook", playbook_type="technology", owner_ai="Hermes", domains=["Robotics", "Manufacturing", "AI"], summary="Core engineering playbook for robot mechanisms, sensors, control, safety, testing, and manufacturing.", related_project_ids=["project:weaver", "project:green_robotics"])
    add_section(playbook_id=robotics["playbook_id"], section_type="overview", title="Robotics overview", content="Robotics combines mechanisms, actuators, sensors, controls, software, power systems, safety, and manufacturing discipline.", confidence_score=80)
    add_component(playbook_id=robotics["playbook_id"], name="Actuator", component_type="motion", function="Converts energy into controlled motion.", risks=["overheating", "torque overload", "control instability"])
    add_design_pattern(playbook_id=robotics["playbook_id"], name="Redundant Sensor Architecture", pattern_type="safety", intent="Reduce single sensor failure risk.", structure=["primary sensor", "secondary sensor", "health monitor", "fallback mode"], tradeoffs=["higher cost", "more wiring"])
    created.append(robotics)

    energy = create_playbook(title="Power Cell Engineering Playbook", playbook_type="project", owner_ai="Hermes", domains=["Energy", "Chemistry", "Materials"], summary="Safety-first playbook for ATLAS power cell research, materials, containment, tests, and failure modes.", related_project_ids=["project:power_cell"])
    add_section(playbook_id=energy["playbook_id"], section_type="safety", title="Energy safety baseline", content="Energy systems require containment, thermal review, electrical isolation, test limits, and documented failure handling before prototype work.", confidence_score=85)
    add_material(playbook_id=energy["playbook_id"], name="Copper", material_family="metal", properties={"conductivity": "high"}, applications=["conductors", "bus bars", "coils"], sustainability_notes="Recyclable but mining impact must be considered.")
    add_failure(playbook_id=energy["playbook_id"], title="Thermal runaway risk", root_cause="Uncontrolled heat generation or inadequate containment.", severity="critical", corrective_action="Stop test and isolate system.", preventive_action="Use current limits, thermal monitoring, and safe enclosure.")
    created.append(energy)

    ecology = create_playbook(title="Minerva Ecological Restoration Playbook", playbook_type="discipline", owner_ai="Minerva", domains=["Botany", "Agriculture", "Environmental Science"], summary="Playbook for plant profiles, ecological safety, toxicity, invasive risk, soil context, and restoration decisions.", related_project_ids=["project:minerva_plant_library", "project:green_robotics"])
    add_section(playbook_id=ecology["playbook_id"], section_type="environmental_impact", title="Ecological context rule", content="Plant recommendations must account for local climate, soil, toxicity, invasive risk, water needs, and ecosystem impact.", confidence_score=88)
    created.append(ecology)
    return {"created_or_updated": len(created), "items": list_playbooks(limit=1000)}


def reset_in_memory_state() -> None:
    _PLAYBOOKS.clear(); _SECTIONS.clear(); _COMPONENTS.clear(); _MATERIALS.clear(); _FAILURES.clear(); _PATTERNS.clear(); _REVISIONS.clear()


async def persist_all() -> None:
    if _DB is None:
        return
    collections = [
        ("engineering_playbooks", _PLAYBOOKS, "playbook_id"),
        ("engineering_playbook_sections", _SECTIONS, "section_id"),
        ("engineering_components", _COMPONENTS, "component_id"),
        ("engineering_materials", _MATERIALS, "material_id"),
        ("engineering_failures", _FAILURES, "failure_id"),
        ("engineering_patterns", _PATTERNS, "pattern_id"),
        ("engineering_playbook_revisions", _REVISIONS, "revision_id"),
    ]
    for collection_name, store, key in collections:
        collection = getattr(_DB, collection_name)
        for item in store.values():
            await collection.update_one({key: item[key]}, {"$set": item}, upsert=True)


async def hydrate_from_mongo() -> Dict[str, int]:
    if _DB is None:
        return {"engineering_playbooks": 0}
    reset_in_memory_state()
    for item in await _DB.engineering_playbooks.find({}, {"_id": 0}).to_list(50000):
        _PLAYBOOKS[item["playbook_id"]] = item
    for item in await _DB.engineering_playbook_sections.find({}, {"_id": 0}).to_list(100000):
        _SECTIONS[item["section_id"]] = item
    for item in await _DB.engineering_components.find({}, {"_id": 0}).to_list(100000):
        _COMPONENTS[item["component_id"]] = item
    for item in await _DB.engineering_materials.find({}, {"_id": 0}).to_list(100000):
        _MATERIALS[item["material_id"]] = item
    for item in await _DB.engineering_failures.find({}, {"_id": 0}).to_list(100000):
        _FAILURES[item["failure_id"]] = item
    for item in await _DB.engineering_patterns.find({}, {"_id": 0}).to_list(100000):
        _PATTERNS[item["pattern_id"]] = item
    for item in await _DB.engineering_playbook_revisions.find({}, {"_id": 0}).to_list(100000):
        _REVISIONS[item["revision_id"]] = item
    return {"engineering_playbooks": len(_PLAYBOOKS), "engineering_playbook_sections": len(_SECTIONS)}


async def create_indexes() -> None:
    if _DB is None:
        return
    await _DB.engineering_playbooks.create_index("playbook_id", unique=True)
    await _DB.engineering_playbooks.create_index("owner_ai")
    await _DB.engineering_playbooks.create_index("playbook_type")
    await _DB.engineering_playbook_sections.create_index("section_id", unique=True)
    await _DB.engineering_playbook_sections.create_index("playbook_id")
    await _DB.engineering_components.create_index("playbook_id")
    await _DB.engineering_materials.create_index("playbook_id")
    await _DB.engineering_failures.create_index("playbook_id")
    await _DB.engineering_patterns.create_index("playbook_id")
    await _DB.engineering_playbook_revisions.create_index("playbook_id")


def _require_playbook(playbook_id: str) -> Dict[str, Any]:
    playbook = _PLAYBOOKS.get(playbook_id)
    if not playbook:
        raise ValueError(f"unknown playbook_id: {playbook_id}")
    return playbook


def _touch_counts(playbook_id: str) -> None:
    playbook = _require_playbook(playbook_id)
    playbook["section_count"] = len([x for x in _SECTIONS.values() if x["playbook_id"] == playbook_id])
    playbook["component_count"] = len([x for x in _COMPONENTS.values() if x["playbook_id"] == playbook_id])
    playbook["material_count"] = len([x for x in _MATERIALS.values() if x["playbook_id"] == playbook_id])
    playbook["failure_count"] = len([x for x in _FAILURES.values() if x["playbook_id"] == playbook_id])
    playbook["pattern_count"] = len([x for x in _PATTERNS.values() if x["playbook_id"] == playbook_id])
    playbook["updated_at"] = _utc_now()


def _revision(*, playbook_id: str, change_type: str, note: str, actor: str) -> Dict[str, Any]:
    revision_id = f"EPR-{str(uuid4())[:8]}"
    revision = {"revision_id": revision_id, "playbook_id": playbook_id, "change_type": change_type, "note": note, "actor": actor, "timestamp": _utc_now()}
    _REVISIONS[revision_id] = revision
    return revision
