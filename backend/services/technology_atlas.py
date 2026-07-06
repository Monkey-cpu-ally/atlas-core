"""ATLAS Technology Atlas.

Concept and technology registry for the Global Knowledge Network. V1 links
technologies to institutions, disciplines, ATLAS projects, standards needs, and
AI ownership without ingesting external content.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4

_DB: Any = None
_TECHNOLOGIES: Dict[str, Dict[str, Any]] = {}
_RELATIONSHIPS: Dict[str, Dict[str, Any]] = {}

AI_OWNERS = {"Ajani", "Hermes", "Minerva", "Council"}
MATURITY_LEVELS = {"concept", "research", "prototype", "fielded", "industrial", "standardized"}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def attach_mongo(db: Any) -> None:
    global _DB
    _DB = db


def persistence_enabled() -> bool:
    return _DB is not None


def create_technology(
    *,
    name: str,
    category: str,
    description: str,
    disciplines: List[str],
    primary_ai_owner: str,
    maturity_level: str = "research",
    related_atlas_projects: Optional[List[str]] = None,
    safety_considerations: Optional[List[str]] = None,
    standards_needed: Optional[List[str]] = None,
) -> Dict[str, Any]:
    if primary_ai_owner not in AI_OWNERS:
        raise ValueError(f"invalid primary_ai_owner: {primary_ai_owner}")
    if maturity_level not in MATURITY_LEVELS:
        raise ValueError(f"invalid maturity_level: {maturity_level}")
    tech_id = _technology_id(name)
    technology = {
        "technology_id": tech_id,
        "name": name,
        "category": category,
        "description": description,
        "disciplines": sorted(set(disciplines)),
        "primary_ai_owner": primary_ai_owner,
        "maturity_level": maturity_level,
        "related_atlas_projects": related_atlas_projects or [],
        "safety_considerations": safety_considerations or [],
        "standards_needed": standards_needed or [],
        "status": "registered",
        "created_at": _utc_now(),
        "updated_at": _utc_now(),
    }
    _TECHNOLOGIES[tech_id] = technology
    return technology


def get_technology(technology_id: str) -> Optional[Dict[str, Any]]:
    return _TECHNOLOGIES.get(technology_id)


def list_technologies(
    *,
    category: Optional[str] = None,
    discipline: Optional[str] = None,
    owner: Optional[str] = None,
    maturity_level: Optional[str] = None,
    project: Optional[str] = None,
    limit: int = 250,
) -> List[Dict[str, Any]]:
    items = list(_TECHNOLOGIES.values())
    if category:
        items = [item for item in items if item["category"].lower() == category.lower()]
    if discipline:
        d = discipline.lower()
        items = [item for item in items if d in {x.lower() for x in item["disciplines"]}]
    if owner:
        items = [item for item in items if item["primary_ai_owner"].lower() == owner.lower()]
    if maturity_level:
        items = [item for item in items if item["maturity_level"] == maturity_level]
    if project:
        items = [item for item in items if project in item.get("related_atlas_projects", [])]
    return sorted(items, key=lambda item: (item["category"], item["name"]))[:limit]


def link_institution_to_technology(
    *,
    institution_id: str,
    technology_id: str,
    relationship_type: str,
    evidence_note: str,
    confidence_score: int = 50,
) -> Dict[str, Any]:
    if technology_id not in _TECHNOLOGIES:
        raise ValueError(f"unknown technology_id: {technology_id}")
    relationship_id = f"GKN-REL-{str(uuid4())[:8]}"
    relationship = {
        "relationship_id": relationship_id,
        "institution_id": institution_id,
        "technology_id": technology_id,
        "relationship_type": relationship_type,
        "evidence_note": evidence_note,
        "confidence_score": max(0, min(100, int(confidence_score))),
        "created_at": _utc_now(),
    }
    _RELATIONSHIPS[relationship_id] = relationship
    return relationship


def list_relationships(*, technology_id: Optional[str] = None, institution_id: Optional[str] = None, limit: int = 250) -> List[Dict[str, Any]]:
    items = list(_RELATIONSHIPS.values())
    if technology_id:
        items = [item for item in items if item["technology_id"] == technology_id]
    if institution_id:
        items = [item for item in items if item["institution_id"] == institution_id]
    return sorted(items, key=lambda item: item["created_at"], reverse=True)[:limit]


def technology_summary() -> Dict[str, Any]:
    by_category: Dict[str, int] = {}
    by_owner: Dict[str, int] = {owner: 0 for owner in sorted(AI_OWNERS)}
    by_maturity: Dict[str, int] = {level: 0 for level in sorted(MATURITY_LEVELS)}
    projects = set()
    for item in _TECHNOLOGIES.values():
        by_category[item["category"]] = by_category.get(item["category"], 0) + 1
        by_owner[item["primary_ai_owner"]] = by_owner.get(item["primary_ai_owner"], 0) + 1
        by_maturity[item["maturity_level"]] = by_maturity.get(item["maturity_level"], 0) + 1
        projects.update(item.get("related_atlas_projects", []))
    return {
        "title": "ATLAS Technology Atlas Summary",
        "status": "active_registry",
        "generated_at": _utc_now(),
        "technology_count": len(_TECHNOLOGIES),
        "relationship_count": len(_RELATIONSHIPS),
        "project_count": len(projects),
        "categories": by_category,
        "ai_owners": by_owner,
        "maturity_levels": by_maturity,
    }


def seed_foundation_technologies() -> Dict[str, Any]:
    created = 0
    for seed in _foundation_technology_seed_data():
        tech = create_technology(**seed)
        if tech["technology_id"]:
            created += 1
    return {"created_or_updated": created, "items": list_technologies(limit=1000)}


def reset_in_memory_state() -> None:
    _TECHNOLOGIES.clear()
    _RELATIONSHIPS.clear()


async def persist_technologies(items: List[Dict[str, Any]]) -> None:
    if _DB is None:
        return
    for item in items:
        await _DB.global_technologies.update_one({"technology_id": item["technology_id"]}, {"$set": item}, upsert=True)


async def persist_relationships(items: List[Dict[str, Any]]) -> None:
    if _DB is None:
        return
    for item in items:
        await _DB.global_knowledge_relationships.update_one({"relationship_id": item["relationship_id"]}, {"$set": item}, upsert=True)


async def hydrate_from_mongo() -> Dict[str, int]:
    if _DB is None:
        return {"global_technologies": 0, "global_knowledge_relationships": 0}
    techs = await _DB.global_technologies.find({}, {"_id": 0}).to_list(10000)
    rels = await _DB.global_knowledge_relationships.find({}, {"_id": 0}).to_list(10000)
    _TECHNOLOGIES.clear(); _RELATIONSHIPS.clear()
    for item in techs:
        _TECHNOLOGIES[item["technology_id"]] = item
    for item in rels:
        _RELATIONSHIPS[item["relationship_id"]] = item
    return {"global_technologies": len(_TECHNOLOGIES), "global_knowledge_relationships": len(_RELATIONSHIPS)}


async def create_indexes() -> None:
    if _DB is None:
        return
    await _DB.global_technologies.create_index("technology_id", unique=True)
    await _DB.global_technologies.create_index("category")
    await _DB.global_technologies.create_index("primary_ai_owner")
    await _DB.global_knowledge_relationships.create_index("relationship_id", unique=True)
    await _DB.global_knowledge_relationships.create_index("technology_id")
    await _DB.global_knowledge_relationships.create_index("institution_id")


def _technology_id(name: str) -> str:
    safe = "-".join(name.lower().replace("&", "and").replace("/", " ").split())
    return f"TECH-{safe[:72]}-{str(uuid4())[:6]}"


def _foundation_technology_seed_data() -> List[Dict[str, Any]]:
    return [
        {"name": "Hydrogen Energy Systems", "category": "Energy", "description": "Hydrogen production, storage, safety, fuel cells, and industrial energy applications.", "disciplines": ["Chemistry", "Materials", "Energy", "Manufacturing"], "primary_ai_owner": "Hermes", "maturity_level": "industrial", "related_atlas_projects": ["project:hydrogen_engine", "project:power_cell"], "safety_considerations": ["flammability", "storage pressure", "leak detection"], "standards_needed": ["ISO", "IEC", "NIST"]},
        {"name": "Advanced Robotics", "category": "Robotics", "description": "Robotic systems including manipulation, mobility, autonomy, sensing, and field operations.", "disciplines": ["Robotics", "AI", "Mechanical Engineering", "Electronics"], "primary_ai_owner": "Hermes", "maturity_level": "industrial", "related_atlas_projects": ["project:weaver", "project:green_robotics"], "safety_considerations": ["human safety", "actuator limits", "sensor failure"], "standards_needed": ["ISO", "IEC"]},
        {"name": "Digital Twins", "category": "Simulation", "description": "Virtual representations of physical systems used for simulation, monitoring, and engineering decisions.", "disciplines": ["Software Engineering", "Control Systems", "Simulation", "Robotics"], "primary_ai_owner": "Ajani", "maturity_level": "fielded", "related_atlas_projects": ["project:digital_twin", "project:weaver"], "safety_considerations": ["model drift", "sensor quality", "incorrect assumptions"], "standards_needed": ["NIST", "ISO"]},
        {"name": "Battery Materials", "category": "Energy", "description": "Electrochemical materials, solid-state batteries, separators, safety, and lifecycle analysis.", "disciplines": ["Chemistry", "Materials", "Energy", "Environmental Science"], "primary_ai_owner": "Minerva", "maturity_level": "research", "related_atlas_projects": ["project:power_cell"], "safety_considerations": ["thermal runaway", "toxicity", "recycling"], "standards_needed": ["IEC", "NIST"]},
        {"name": "Precision Manufacturing", "category": "Manufacturing", "description": "High-accuracy manufacturing, metrology, process control, automation, and quality systems.", "disciplines": ["Manufacturing", "Mechanical Engineering", "Materials", "Metrology"], "primary_ai_owner": "Hermes", "maturity_level": "industrial", "related_atlas_projects": ["project:weaver", "project:blueprint_vault"], "safety_considerations": ["machine guarding", "calibration", "process repeatability"], "standards_needed": ["ISO", "NIST"]},
        {"name": "Sustainable Agriculture", "category": "Nature", "description": "Agricultural systems focused on soil health, water efficiency, crop resilience, and ecological restoration.", "disciplines": ["Agriculture", "Biology", "Environmental Science", "Botany"], "primary_ai_owner": "Minerva", "maturity_level": "industrial", "related_atlas_projects": ["project:green_robotics", "project:minerva_plant_library"], "safety_considerations": ["ecosystem impact", "invasive species", "soil chemistry"], "standards_needed": ["USDA", "FAO"]},
        {"name": "Semiconductor Engineering", "category": "Electronics", "description": "Chip design, fabrication, packaging, lithography, process control, and reliability.", "disciplines": ["Electronics", "Materials", "Physics", "Manufacturing"], "primary_ai_owner": "Ajani", "maturity_level": "industrial", "related_atlas_projects": ["project:atlas_compute", "project:sensor_platforms"], "safety_considerations": ["cleanroom safety", "chemical exposure", "supply chain risk"], "standards_needed": ["SEMI", "IEC"]},
        {"name": "Medical Biotechnology", "category": "Medicine", "description": "Biomedical research, diagnostics, tissue engineering, genetics, and clinical translation.", "disciplines": ["Medicine", "Biology", "Genetics", "Neuroscience"], "primary_ai_owner": "Minerva", "maturity_level": "fielded", "related_atlas_projects": ["project:biological_augmentation_research"], "safety_considerations": ["clinical safety", "ethics", "human subject protection"], "standards_needed": ["WHO", "NIH"]},
    ]
