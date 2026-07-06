"""ATLAS Project Knowledge Linker.

Connects ATLAS projects to the Global Knowledge Network and Technology Atlas.
V1 is deterministic and registry-driven: it does not fetch external content;
it recommends relevant technologies and institution categories from existing
ATLAS registries.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4

from services import global_knowledge_network as gkn
from services import technology_atlas

_DB: Any = None
_PROJECT_PROFILES: Dict[str, Dict[str, Any]] = {}
_PROJECT_LINKS: Dict[str, Dict[str, Any]] = {}

PROJECT_STATUSES = {"concept", "research", "architecture", "prototype", "validation", "production_candidate", "maintained"}
AI_OWNERS = {"Ajani", "Hermes", "Minerva", "Council"}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def attach_mongo(db: Any) -> None:
    global _DB
    _DB = db


def persistence_enabled() -> bool:
    return _DB is not None


def create_project_profile(
    *,
    project_id: str,
    name: str,
    mission: str,
    domains: List[str],
    lead_ai: str,
    status: str = "research",
    required_capabilities: Optional[List[str]] = None,
    safety_focus: Optional[List[str]] = None,
) -> Dict[str, Any]:
    if lead_ai not in AI_OWNERS:
        raise ValueError(f"invalid lead_ai: {lead_ai}")
    if status not in PROJECT_STATUSES:
        raise ValueError(f"invalid status: {status}")
    profile = {
        "project_id": project_id,
        "name": name,
        "mission": mission,
        "domains": sorted(set(domains)),
        "lead_ai": lead_ai,
        "status": status,
        "required_capabilities": sorted(set(required_capabilities or [])),
        "safety_focus": sorted(set(safety_focus or [])),
        "created_at": _utc_now(),
        "updated_at": _utc_now(),
    }
    _PROJECT_PROFILES[project_id] = profile
    return profile


def get_project_profile(project_id: str) -> Optional[Dict[str, Any]]:
    return _PROJECT_PROFILES.get(project_id)


def list_project_profiles(*, lead_ai: Optional[str] = None, domain: Optional[str] = None, status: Optional[str] = None, limit: int = 250) -> List[Dict[str, Any]]:
    items = list(_PROJECT_PROFILES.values())
    if lead_ai:
        items = [item for item in items if item["lead_ai"].lower() == lead_ai.lower()]
    if domain:
        d = domain.lower()
        items = [item for item in items if d in {x.lower() for x in item["domains"]}]
    if status:
        items = [item for item in items if item["status"] == status]
    return sorted(items, key=lambda item: item["name"])[:limit]


def build_project_brief(project_id: str) -> Dict[str, Any]:
    profile = get_project_profile(project_id)
    if not profile:
        raise ValueError(f"unknown project_id: {project_id}")

    technologies = _rank_technologies_for_project(profile)
    institutions = _rank_institutions_for_project(profile, technologies)
    standards = sorted({standard for tech in technologies for standard in tech.get("standards_needed", [])})
    safety = sorted(set(profile.get("safety_focus", [])) | {s for tech in technologies for s in tech.get("safety_considerations", [])})

    brief = {
        "title": "ATLAS Project Knowledge Brief",
        "generated_at": _utc_now(),
        "project": profile,
        "recommended_technologies": technologies[:12],
        "recommended_institutions": institutions[:12],
        "standards_to_review": standards,
        "safety_review_topics": safety,
        "council_note": "This brief recommends research targets only. Adoption still requires evidence review, engineering review, and Council approval.",
    }
    return brief


def link_project_to_target(
    *,
    project_id: str,
    target_type: str,
    target_id: str,
    relationship_type: str,
    rationale: str,
    confidence_score: int = 50,
) -> Dict[str, Any]:
    if project_id not in _PROJECT_PROFILES:
        raise ValueError(f"unknown project_id: {project_id}")
    if target_type not in {"technology", "institution", "standard", "source"}:
        raise ValueError(f"invalid target_type: {target_type}")
    link_id = f"PKL-{str(uuid4())[:8]}"
    link = {
        "link_id": link_id,
        "project_id": project_id,
        "target_type": target_type,
        "target_id": target_id,
        "relationship_type": relationship_type,
        "rationale": rationale,
        "confidence_score": max(0, min(100, int(confidence_score))),
        "status": "candidate",
        "created_at": _utc_now(),
    }
    _PROJECT_LINKS[link_id] = link
    return link


def list_project_links(*, project_id: Optional[str] = None, target_type: Optional[str] = None, limit: int = 250) -> List[Dict[str, Any]]:
    items = list(_PROJECT_LINKS.values())
    if project_id:
        items = [item for item in items if item["project_id"] == project_id]
    if target_type:
        items = [item for item in items if item["target_type"] == target_type]
    return sorted(items, key=lambda item: item["created_at"], reverse=True)[:limit]


def seed_project_profiles() -> Dict[str, Any]:
    created = 0
    for seed in _foundation_project_seed_data():
        profile = create_project_profile(**seed)
        if profile["project_id"]:
            created += 1
    return {"created_or_updated": created, "items": list_project_profiles(limit=1000)}


def project_knowledge_summary() -> Dict[str, Any]:
    by_ai = {owner: 0 for owner in sorted(AI_OWNERS)}
    by_status = {status: 0 for status in sorted(PROJECT_STATUSES)}
    domains = set()
    for profile in _PROJECT_PROFILES.values():
        by_ai[profile["lead_ai"]] = by_ai.get(profile["lead_ai"], 0) + 1
        by_status[profile["status"]] = by_status.get(profile["status"], 0) + 1
        domains.update(profile["domains"])
    return {
        "title": "ATLAS Project Knowledge Linker Summary",
        "generated_at": _utc_now(),
        "project_count": len(_PROJECT_PROFILES),
        "link_count": len(_PROJECT_LINKS),
        "domain_count": len(domains),
        "lead_ai": by_ai,
        "statuses": by_status,
    }


def reset_in_memory_state() -> None:
    _PROJECT_PROFILES.clear()
    _PROJECT_LINKS.clear()


async def persist_projects(items: List[Dict[str, Any]]) -> None:
    if _DB is None:
        return
    for item in items:
        await _DB.project_knowledge_profiles.update_one({"project_id": item["project_id"]}, {"$set": item}, upsert=True)


async def persist_links(items: List[Dict[str, Any]]) -> None:
    if _DB is None:
        return
    for item in items:
        await _DB.project_knowledge_links.update_one({"link_id": item["link_id"]}, {"$set": item}, upsert=True)


async def hydrate_from_mongo() -> Dict[str, int]:
    if _DB is None:
        return {"project_knowledge_profiles": 0, "project_knowledge_links": 0}
    profiles = await _DB.project_knowledge_profiles.find({}, {"_id": 0}).to_list(10000)
    links = await _DB.project_knowledge_links.find({}, {"_id": 0}).to_list(10000)
    _PROJECT_PROFILES.clear(); _PROJECT_LINKS.clear()
    for profile in profiles:
        _PROJECT_PROFILES[profile["project_id"]] = profile
    for link in links:
        _PROJECT_LINKS[link["link_id"]] = link
    return {"project_knowledge_profiles": len(_PROJECT_PROFILES), "project_knowledge_links": len(_PROJECT_LINKS)}


async def create_indexes() -> None:
    if _DB is None:
        return
    await _DB.project_knowledge_profiles.create_index("project_id", unique=True)
    await _DB.project_knowledge_profiles.create_index("lead_ai")
    await _DB.project_knowledge_profiles.create_index("status")
    await _DB.project_knowledge_links.create_index("link_id", unique=True)
    await _DB.project_knowledge_links.create_index("project_id")
    await _DB.project_knowledge_links.create_index("target_type")


def _rank_technologies_for_project(profile: Dict[str, Any]) -> List[Dict[str, Any]]:
    query_terms = {x.lower() for x in profile.get("domains", []) + profile.get("required_capabilities", [])}
    scored: List[Dict[str, Any]] = []
    for tech in technology_atlas.list_technologies(limit=1000):
        haystack = {tech["category"].lower(), tech["name"].lower(), tech["primary_ai_owner"].lower()}
        haystack.update(x.lower() for x in tech.get("disciplines", []))
        haystack.update(x.lower().replace("project:", "") for x in tech.get("related_atlas_projects", []))
        score = len(query_terms & haystack) * 20
        score += 15 if profile["project_id"] in tech.get("related_atlas_projects", []) else 0
        score += 5 if profile["lead_ai"] == tech.get("primary_ai_owner") else 0
        if score > 0:
            item = dict(tech)
            item["match_score"] = min(100, score)
            scored.append(item)
    return sorted(scored, key=lambda item: item["match_score"], reverse=True)


def _rank_institutions_for_project(profile: Dict[str, Any], technologies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    query_terms = {x.lower() for x in profile.get("domains", []) + profile.get("required_capabilities", [])}
    query_terms.update(x.lower() for tech in technologies for x in tech.get("disciplines", []))
    scored: List[Dict[str, Any]] = []
    for inst in gkn.list_institutions(limit=1000):
        haystack = {inst["primary_ai_owner"].lower(), inst["organization_type"].lower(), inst["country"].lower(), inst["region"].lower()}
        haystack.update(x.lower() for x in inst.get("primary_disciplines", []))
        haystack.update(x.lower() for x in inst.get("research_strengths", []))
        score = len(query_terms & haystack) * 15
        score += 10 if profile["lead_ai"] == inst.get("primary_ai_owner") else 0
        score += 8 if inst.get("trust_tier") == "tier_1_official" else 0
        if score > 0:
            item = dict(inst)
            item["match_score"] = min(100, score)
            scored.append(item)
    return sorted(scored, key=lambda item: item["match_score"], reverse=True)


def _foundation_project_seed_data() -> List[Dict[str, Any]]:
    return [
        {"project_id": "project:weaver", "name": "The Weaver", "mission": "Multi-arm engineering and manufacturing robot ecosystem for assembly, sensing, fabrication, and research support.", "domains": ["Robotics", "Manufacturing", "Digital Twins", "Materials"], "lead_ai": "Hermes", "status": "architecture", "required_capabilities": ["Advanced Robotics", "Precision Manufacturing", "Digital Twins"], "safety_focus": ["human proximity safety", "tooling safety", "sensor redundancy"]},
        {"project_id": "project:green_robotics", "name": "Green Robotics", "mission": "Sustainable environmental robots for repair, restoration, agriculture, and clean materials handling.", "domains": ["Robotics", "Environmental Science", "Agriculture", "Botany"], "lead_ai": "Minerva", "status": "research", "required_capabilities": ["Sustainable Agriculture", "Advanced Robotics"], "safety_focus": ["ecosystem impact", "non-lethal operations", "soil and water safety"]},
        {"project_id": "project:power_cell", "name": "Power Cell", "mission": "Modular energy cell research for safe, durable, scalable power systems.", "domains": ["Energy", "Chemistry", "Materials", "Electronics"], "lead_ai": "Hermes", "status": "research", "required_capabilities": ["Battery Materials", "Hydrogen Energy Systems"], "safety_focus": ["thermal safety", "electrochemical safety", "containment"]},
        {"project_id": "project:digital_twin", "name": "Digital Twin Engine", "mission": "Simulation and monitoring layer for ATLAS projects, robots, environments, and engineering decisions.", "domains": ["Simulation", "Software Engineering", "Control Systems", "Robotics"], "lead_ai": "Ajani", "status": "architecture", "required_capabilities": ["Digital Twins", "Advanced Robotics"], "safety_focus": ["model drift", "incorrect assumptions", "data quality"]},
        {"project_id": "project:minerva_plant_library", "name": "Minerva Plant Library", "mission": "Curated plant, botany, medicinal, ecological, and restoration knowledge base for ATLAS nature projects.", "domains": ["Botany", "Agriculture", "Biology", "Environmental Science"], "lead_ai": "Minerva", "status": "research", "required_capabilities": ["Sustainable Agriculture"], "safety_focus": ["toxicity", "invasive species", "ecological context"]},
    ]
