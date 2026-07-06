"""ATLAS Global Knowledge Network.

Curated global source registry for ATLAS. V1 does not scrape or ingest external
content. It defines trusted institutions, regional coverage, discipline mapping,
AI ownership, and reliability metadata so future ingestion flows have a governed
foundation.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4

_DB: Any = None
_INSTITUTIONS: Dict[str, Dict[str, Any]] = {}

REGIONS = [
    "North America",
    "South America",
    "Europe",
    "Africa",
    "Asia",
    "Oceania",
    "International",
    "Polar and Ocean Research",
]

AI_OWNERS = {"Ajani", "Hermes", "Minerva", "Council"}
TRUST_TIERS = {"tier_1_official", "tier_2_academic", "tier_3_industry", "tier_4_community", "tier_5_personal"}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def attach_mongo(db: Any) -> None:
    global _DB
    _DB = db


def persistence_enabled() -> bool:
    return _DB is not None


def create_institution(
    *,
    name: str,
    country: str,
    region: str,
    organization_type: str,
    primary_disciplines: List[str],
    research_strengths: List[str],
    trust_tier: str,
    evidence_level: str,
    primary_ai_owner: str,
    website: Optional[str] = None,
    open_data: bool = False,
    related_atlas_projects: Optional[List[str]] = None,
    notes: Optional[str] = None,
) -> Dict[str, Any]:
    if region not in REGIONS:
        raise ValueError(f"invalid region: {region}")
    if trust_tier not in TRUST_TIERS:
        raise ValueError(f"invalid trust_tier: {trust_tier}")
    if primary_ai_owner not in AI_OWNERS:
        raise ValueError(f"invalid primary_ai_owner: {primary_ai_owner}")

    institution_id = _institution_id(name, country)
    institution = {
        "institution_id": institution_id,
        "name": name,
        "country": country,
        "region": region,
        "organization_type": organization_type,
        "primary_disciplines": sorted(set(primary_disciplines)),
        "research_strengths": sorted(set(research_strengths)),
        "trust_tier": trust_tier,
        "evidence_level": evidence_level,
        "primary_ai_owner": primary_ai_owner,
        "website": website,
        "open_data": open_data,
        "related_atlas_projects": related_atlas_projects or [],
        "notes": notes,
        "status": "registered",
        "created_at": _utc_now(),
        "updated_at": _utc_now(),
    }
    _INSTITUTIONS[institution_id] = institution
    return institution


def get_institution(institution_id: str) -> Optional[Dict[str, Any]]:
    return _INSTITUTIONS.get(institution_id)


def list_institutions(
    *,
    region: Optional[str] = None,
    country: Optional[str] = None,
    discipline: Optional[str] = None,
    owner: Optional[str] = None,
    trust_tier: Optional[str] = None,
    limit: int = 250,
) -> List[Dict[str, Any]]:
    items = list(_INSTITUTIONS.values())
    if region:
        items = [item for item in items if item["region"].lower() == region.lower()]
    if country:
        items = [item for item in items if item["country"].lower() == country.lower()]
    if discipline:
        d = discipline.lower()
        items = [item for item in items if d in {x.lower() for x in item["primary_disciplines"]}]
    if owner:
        items = [item for item in items if item["primary_ai_owner"].lower() == owner.lower()]
    if trust_tier:
        items = [item for item in items if item["trust_tier"] == trust_tier]
    return sorted(items, key=lambda item: (item["region"], item["country"], item["name"]))[:limit]


def global_summary() -> Dict[str, Any]:
    by_region: Dict[str, int] = {region: 0 for region in REGIONS}
    by_owner: Dict[str, int] = {owner: 0 for owner in sorted(AI_OWNERS)}
    by_tier: Dict[str, int] = {tier: 0 for tier in sorted(TRUST_TIERS)}
    countries = set()
    disciplines = set()
    for item in _INSTITUTIONS.values():
        by_region[item["region"]] = by_region.get(item["region"], 0) + 1
        by_owner[item["primary_ai_owner"]] = by_owner.get(item["primary_ai_owner"], 0) + 1
        by_tier[item["trust_tier"]] = by_tier.get(item["trust_tier"], 0) + 1
        countries.add(item["country"])
        disciplines.update(item["primary_disciplines"])
    return {
        "title": "ATLAS Global Knowledge Network Summary",
        "status": "active_registry",
        "generated_at": _utc_now(),
        "institution_count": len(_INSTITUTIONS),
        "country_count": len(countries),
        "discipline_count": len(disciplines),
        "regions": by_region,
        "ai_owners": by_owner,
        "trust_tiers": by_tier,
    }


def seed_foundation_registry() -> Dict[str, Any]:
    seeds = _foundation_seed_data()
    created = 0
    for seed in seeds:
        inst = create_institution(**seed)
        if inst["institution_id"]:
            created += 1
    return {"created_or_updated": created, "items": list_institutions(limit=1000)}


def reset_in_memory_state() -> None:
    _INSTITUTIONS.clear()


async def persist_all(items: List[Dict[str, Any]]) -> None:
    if _DB is None:
        return
    for item in items:
        await _DB.global_institutions.update_one({"institution_id": item["institution_id"]}, {"$set": item}, upsert=True)


async def hydrate_from_mongo() -> Dict[str, int]:
    if _DB is None:
        return {"global_institutions": 0}
    items = await _DB.global_institutions.find({}, {"_id": 0}).to_list(10000)
    _INSTITUTIONS.clear()
    for item in items:
        _INSTITUTIONS[item["institution_id"]] = item
    return {"global_institutions": len(_INSTITUTIONS)}


async def create_indexes() -> None:
    if _DB is None:
        return
    await _DB.global_institutions.create_index("institution_id", unique=True)
    await _DB.global_institutions.create_index([("region", 1), ("country", 1)])
    await _DB.global_institutions.create_index("primary_ai_owner")
    await _DB.global_institutions.create_index("trust_tier")


def _institution_id(name: str, country: str) -> str:
    safe = "-".join(f"{country}-{name}".lower().replace("&", "and").replace("/", " ").split())
    return f"GKN-{safe[:72]}-{str(uuid4())[:6]}"


def _foundation_seed_data() -> List[Dict[str, Any]]:
    return [
        {"name": "NASA", "country": "United States", "region": "North America", "organization_type": "government_science_agency", "primary_disciplines": ["Aerospace", "Robotics", "Earth Science", "Physics"], "research_strengths": ["space systems", "planetary science", "robotic exploration", "earth observation"], "trust_tier": "tier_1_official", "evidence_level": "government scientific agency", "primary_ai_owner": "Hermes", "website": "https://www.nasa.gov", "open_data": True},
        {"name": "NIST", "country": "United States", "region": "North America", "organization_type": "standards_body", "primary_disciplines": ["Standards", "Cybersecurity", "Materials", "Measurement Science"], "research_strengths": ["measurement standards", "cybersecurity frameworks", "materials references"], "trust_tier": "tier_1_official", "evidence_level": "national standards institute", "primary_ai_owner": "Ajani", "website": "https://www.nist.gov", "open_data": True},
        {"name": "NIH", "country": "United States", "region": "North America", "organization_type": "government_health_research", "primary_disciplines": ["Medicine", "Biology", "Genetics", "Neuroscience"], "research_strengths": ["biomedical research", "clinical knowledge", "public health"], "trust_tier": "tier_1_official", "evidence_level": "government biomedical agency", "primary_ai_owner": "Minerva", "website": "https://www.nih.gov", "open_data": True},
        {"name": "Canadian Space Agency", "country": "Canada", "region": "North America", "organization_type": "government_space_agency", "primary_disciplines": ["Aerospace", "Robotics", "Earth Observation"], "research_strengths": ["space robotics", "satellite systems", "exploration"], "trust_tier": "tier_1_official", "evidence_level": "government space agency", "primary_ai_owner": "Hermes", "website": "https://www.asc-csa.gc.ca", "open_data": True},
        {"name": "Fraunhofer Society", "country": "Germany", "region": "Europe", "organization_type": "applied_research_network", "primary_disciplines": ["Manufacturing", "Materials", "Robotics", "Energy"], "research_strengths": ["industrial automation", "applied manufacturing", "production systems"], "trust_tier": "tier_1_official", "evidence_level": "recognized applied research institute", "primary_ai_owner": "Hermes", "website": "https://www.fraunhofer.de", "open_data": False},
        {"name": "Max Planck Society", "country": "Germany", "region": "Europe", "organization_type": "research_institute_network", "primary_disciplines": ["Physics", "Chemistry", "Biology", "Materials"], "research_strengths": ["fundamental science", "materials research", "biology"], "trust_tier": "tier_1_official", "evidence_level": "recognized research institute", "primary_ai_owner": "Minerva", "website": "https://www.mpg.de", "open_data": False},
        {"name": "ETH Zurich", "country": "Switzerland", "region": "Europe", "organization_type": "university", "primary_disciplines": ["Engineering", "Robotics", "AI", "Physics", "Architecture"], "research_strengths": ["robotics", "mechanical engineering", "computer science", "architecture"], "trust_tier": "tier_2_academic", "evidence_level": "leading technical university", "primary_ai_owner": "Hermes", "website": "https://ethz.ch", "open_data": False},
        {"name": "University of Cambridge", "country": "United Kingdom", "region": "Europe", "organization_type": "university", "primary_disciplines": ["Engineering", "Medicine", "Physics", "Computer Science"], "research_strengths": ["science research", "engineering", "biomedical research"], "trust_tier": "tier_2_academic", "evidence_level": "leading research university", "primary_ai_owner": "Minerva", "website": "https://www.cam.ac.uk", "open_data": False},
        {"name": "ESA", "country": "International", "region": "International", "organization_type": "intergovernmental_space_agency", "primary_disciplines": ["Aerospace", "Earth Science", "Robotics", "Telecommunications"], "research_strengths": ["space missions", "earth observation", "launch systems"], "trust_tier": "tier_1_official", "evidence_level": "international space agency", "primary_ai_owner": "Hermes", "website": "https://www.esa.int", "open_data": True},
        {"name": "JAXA", "country": "Japan", "region": "Asia", "organization_type": "government_space_agency", "primary_disciplines": ["Aerospace", "Robotics", "Materials", "Earth Observation"], "research_strengths": ["spacecraft", "robotic exploration", "precision systems"], "trust_tier": "tier_1_official", "evidence_level": "government space agency", "primary_ai_owner": "Hermes", "website": "https://global.jaxa.jp", "open_data": True},
        {"name": "RIKEN", "country": "Japan", "region": "Asia", "organization_type": "research_institute", "primary_disciplines": ["Biology", "Physics", "AI", "Materials"], "research_strengths": ["computational science", "biology", "materials", "brain science"], "trust_tier": "tier_1_official", "evidence_level": "recognized national research institute", "primary_ai_owner": "Minerva", "website": "https://www.riken.jp/en", "open_data": False},
        {"name": "KAIST", "country": "South Korea", "region": "Asia", "organization_type": "university", "primary_disciplines": ["AI", "Robotics", "Electronics", "Semiconductors"], "research_strengths": ["robotics", "AI", "electronics", "advanced engineering"], "trust_tier": "tier_2_academic", "evidence_level": "leading technical university", "primary_ai_owner": "Hermes", "website": "https://www.kaist.ac.kr/en", "open_data": False},
        {"name": "A*STAR", "country": "Singapore", "region": "Asia", "organization_type": "government_research_agency", "primary_disciplines": ["Biotechnology", "Materials", "AI", "Manufacturing"], "research_strengths": ["biomedical science", "advanced manufacturing", "materials"], "trust_tier": "tier_1_official", "evidence_level": "government research agency", "primary_ai_owner": "Minerva", "website": "https://www.a-star.edu.sg", "open_data": False},
        {"name": "ISRO", "country": "India", "region": "Asia", "organization_type": "government_space_agency", "primary_disciplines": ["Aerospace", "Remote Sensing", "Systems Engineering"], "research_strengths": ["space missions", "cost-efficient engineering", "satellites"], "trust_tier": "tier_1_official", "evidence_level": "government space agency", "primary_ai_owner": "Ajani", "website": "https://www.isro.gov.in", "open_data": True},
        {"name": "CSIRO", "country": "Australia", "region": "Oceania", "organization_type": "national_science_agency", "primary_disciplines": ["Agriculture", "Materials", "Energy", "Environmental Science"], "research_strengths": ["applied science", "climate research", "mining technology", "agriculture"], "trust_tier": "tier_1_official", "evidence_level": "national science agency", "primary_ai_owner": "Minerva", "website": "https://www.csiro.au", "open_data": True},
        {"name": "EMBRAPA", "country": "Brazil", "region": "South America", "organization_type": "agricultural_research_agency", "primary_disciplines": ["Agriculture", "Biology", "Environmental Science"], "research_strengths": ["tropical agriculture", "soil science", "bioenergy"], "trust_tier": "tier_1_official", "evidence_level": "government agricultural research agency", "primary_ai_owner": "Minerva", "website": "https://www.embrapa.br/en", "open_data": True},
        {"name": "CSIR South Africa", "country": "South Africa", "region": "Africa", "organization_type": "research_council", "primary_disciplines": ["Engineering", "Water", "Materials", "Environmental Science"], "research_strengths": ["applied science", "water systems", "infrastructure", "materials"], "trust_tier": "tier_1_official", "evidence_level": "national research council", "primary_ai_owner": "Hermes", "website": "https://www.csir.co.za", "open_data": False},
        {"name": "WHO", "country": "International", "region": "International", "organization_type": "international_health_organization", "primary_disciplines": ["Public Health", "Medicine", "Epidemiology"], "research_strengths": ["health guidance", "global disease monitoring", "public health standards"], "trust_tier": "tier_1_official", "evidence_level": "international public health authority", "primary_ai_owner": "Minerva", "website": "https://www.who.int", "open_data": True},
        {"name": "ISO", "country": "International", "region": "International", "organization_type": "standards_body", "primary_disciplines": ["Standards", "Manufacturing", "Quality", "Safety"], "research_strengths": ["international standards", "quality systems", "safety frameworks"], "trust_tier": "tier_1_official", "evidence_level": "international standards body", "primary_ai_owner": "Council", "website": "https://www.iso.org", "open_data": False},
    ]
