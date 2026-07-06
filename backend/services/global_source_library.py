"""ATLAS Global Source Library.

Curated catalog of trusted global knowledge sources. This service does not
scrape sources; it registers source metadata, trust tier, domain coverage,
access method, region/country, owner AI, and ingestion readiness so the Source
Hub can later connect only approved sources with provenance.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4

_DB: Any = None
_SOURCES: Dict[str, Dict[str, Any]] = {}

TRUST_TIERS = {"tier_1_official", "tier_2_academic", "tier_3_industry", "tier_4_community", "tier_5_personal"}
SOURCE_TYPES = {"standards_body", "government_agency", "university", "research_institute", "journal_index", "data_portal", "documentation", "patent_database", "open_source", "personal_archive", "media_source"}
ACCESS_METHODS = {"manual_review", "website", "api", "rss", "dataset_download", "connector", "library_import", "not_connected"}
AI_OWNERS = {"Ajani", "Hermes", "Minerva", "Council"}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def attach_mongo(db: Any) -> None:
    global _DB
    _DB = db


def persistence_enabled() -> bool:
    return _DB is not None


def register_source(
    *,
    name: str,
    source_type: str,
    trust_tier: str,
    domains: List[str],
    country: str = "International",
    region: str = "International",
    website: Optional[str] = None,
    access_method: str = "website",
    owner_ai: str = "Council",
    ingestion_status: str = "candidate",
    notes: Optional[str] = None,
) -> Dict[str, Any]:
    if trust_tier not in TRUST_TIERS:
        raise ValueError(f"invalid trust_tier: {trust_tier}")
    if source_type not in SOURCE_TYPES:
        raise ValueError(f"invalid source_type: {source_type}")
    if access_method not in ACCESS_METHODS:
        raise ValueError(f"invalid access_method: {access_method}")
    if owner_ai not in AI_OWNERS:
        raise ValueError(f"invalid owner_ai: {owner_ai}")
    source_id = _source_id(name, country)
    now = _utc_now()
    source = {
        "source_id": source_id,
        "name": name,
        "source_type": source_type,
        "trust_tier": trust_tier,
        "domains": sorted(set(domains)),
        "country": country,
        "region": region,
        "website": website,
        "access_method": access_method,
        "owner_ai": owner_ai,
        "ingestion_status": ingestion_status,
        "last_reviewed_at": None,
        "notes": notes,
        "created_at": now,
        "updated_at": now,
    }
    _SOURCES[source_id] = source
    return source


def list_sources(*, domain: Optional[str] = None, country: Optional[str] = None, region: Optional[str] = None, trust_tier: Optional[str] = None, source_type: Optional[str] = None, owner_ai: Optional[str] = None, ingestion_status: Optional[str] = None, limit: int = 500) -> List[Dict[str, Any]]:
    items = list(_SOURCES.values())
    if domain:
        d = domain.lower()
        items = [item for item in items if d in {x.lower() for x in item.get("domains", [])}]
    if country:
        items = [item for item in items if item["country"].lower() == country.lower()]
    if region:
        items = [item for item in items if item["region"].lower() == region.lower()]
    if trust_tier:
        items = [item for item in items if item["trust_tier"] == trust_tier]
    if source_type:
        items = [item for item in items if item["source_type"] == source_type]
    if owner_ai:
        items = [item for item in items if item["owner_ai"].lower() == owner_ai.lower()]
    if ingestion_status:
        items = [item for item in items if item["ingestion_status"] == ingestion_status]
    return sorted(items, key=lambda item: (item["trust_tier"], item["region"], item["country"], item["name"]))[:limit]


def get_source(source_id: str) -> Optional[Dict[str, Any]]:
    return _SOURCES.get(source_id)


def mark_reviewed(*, source_id: str, reviewer: str, ingestion_status: str, notes: str) -> Dict[str, Any]:
    source = _SOURCES.get(source_id)
    if not source:
        raise ValueError(f"unknown source_id: {source_id}")
    source["ingestion_status"] = ingestion_status
    source["last_reviewed_at"] = _utc_now()
    source["reviewer"] = reviewer
    source["notes"] = notes
    source["updated_at"] = _utc_now()
    return source


def source_summary() -> Dict[str, Any]:
    by_tier = {tier: 0 for tier in sorted(TRUST_TIERS)}
    by_type = {typ: 0 for typ in sorted(SOURCE_TYPES)}
    by_owner = {owner: 0 for owner in sorted(AI_OWNERS)}
    countries = set()
    domains = set()
    for item in _SOURCES.values():
        by_tier[item["trust_tier"]] += 1
        by_type[item["source_type"]] += 1
        by_owner[item["owner_ai"]] += 1
        countries.add(item["country"])
        domains.update(item.get("domains", []))
    return {
        "title": "ATLAS Global Source Library Summary",
        "generated_at": _utc_now(),
        "source_count": len(_SOURCES),
        "country_count": len(countries),
        "domain_count": len(domains),
        "trust_tiers": by_tier,
        "source_types": by_type,
        "owner_ai": by_owner,
    }


def seed_foundation_sources() -> Dict[str, Any]:
    created = 0
    for seed in _foundation_sources():
        register_source(**seed)
        created += 1
    return {"created_or_updated": created, "items": list_sources(limit=10000)}


def reset_in_memory_state() -> None:
    _SOURCES.clear()


async def persist_all(items: Optional[List[Dict[str, Any]]] = None) -> None:
    if _DB is None:
        return
    for item in items or list(_SOURCES.values()):
        await _DB.global_source_library.update_one({"source_id": item["source_id"]}, {"$set": item}, upsert=True)


async def hydrate_from_mongo() -> Dict[str, int]:
    if _DB is None:
        return {"global_source_library": 0}
    items = await _DB.global_source_library.find({}, {"_id": 0}).to_list(20000)
    _SOURCES.clear()
    for item in items:
        _SOURCES[item["source_id"]] = item
    return {"global_source_library": len(_SOURCES)}


async def create_indexes() -> None:
    if _DB is None:
        return
    await _DB.global_source_library.create_index("source_id", unique=True)
    await _DB.global_source_library.create_index("trust_tier")
    await _DB.global_source_library.create_index("source_type")
    await _DB.global_source_library.create_index("owner_ai")
    await _DB.global_source_library.create_index([("region", 1), ("country", 1)])


def _source_id(name: str, country: str) -> str:
    safe = "-".join(f"{country}-{name}".lower().replace("&", "and").replace("/", " ").replace("*", "star").split())
    return f"SRC-{safe[:72]}-{str(uuid4())[:6]}"


def _foundation_sources() -> List[Dict[str, Any]]:
    return [
        {"name": "NASA", "source_type": "government_agency", "trust_tier": "tier_1_official", "domains": ["Aerospace", "Robotics", "Earth Science"], "country": "United States", "region": "North America", "website": "https://www.nasa.gov", "owner_ai": "Hermes"},
        {"name": "NIST", "source_type": "government_agency", "trust_tier": "tier_1_official", "domains": ["Standards", "Cybersecurity", "Materials", "Measurement Science"], "country": "United States", "region": "North America", "website": "https://www.nist.gov", "owner_ai": "Ajani"},
        {"name": "NIH", "source_type": "government_agency", "trust_tier": "tier_1_official", "domains": ["Medicine", "Biology", "Genetics", "Neuroscience"], "country": "United States", "region": "North America", "website": "https://www.nih.gov", "owner_ai": "Minerva"},
        {"name": "NOAA", "source_type": "government_agency", "trust_tier": "tier_1_official", "domains": ["Climate", "Oceanography", "Weather", "Earth Science"], "country": "United States", "region": "North America", "website": "https://www.noaa.gov", "owner_ai": "Minerva"},
        {"name": "USGS", "source_type": "government_agency", "trust_tier": "tier_1_official", "domains": ["Geology", "Water", "Earth Science", "Maps"], "country": "United States", "region": "North America", "website": "https://www.usgs.gov", "owner_ai": "Minerva"},
        {"name": "IEEE", "source_type": "standards_body", "trust_tier": "tier_1_official", "domains": ["Electrical Engineering", "Electronics", "AI", "Robotics", "Standards"], "country": "International", "region": "International", "website": "https://www.ieee.org", "owner_ai": "Ajani"},
        {"name": "ISO", "source_type": "standards_body", "trust_tier": "tier_1_official", "domains": ["Standards", "Manufacturing", "Quality", "Safety"], "country": "International", "region": "International", "website": "https://www.iso.org", "owner_ai": "Council"},
        {"name": "IEC", "source_type": "standards_body", "trust_tier": "tier_1_official", "domains": ["Electrical Engineering", "Electronics", "Energy", "Standards"], "country": "International", "region": "International", "website": "https://www.iec.ch", "owner_ai": "Council"},
        {"name": "ASTM International", "source_type": "standards_body", "trust_tier": "tier_1_official", "domains": ["Materials", "Manufacturing", "Testing", "Standards"], "country": "International", "region": "International", "website": "https://www.astm.org", "owner_ai": "Hermes"},
        {"name": "ASME", "source_type": "standards_body", "trust_tier": "tier_1_official", "domains": ["Mechanical Engineering", "Manufacturing", "Safety", "Standards"], "country": "International", "region": "International", "website": "https://www.asme.org", "owner_ai": "Hermes"},
        {"name": "arXiv", "source_type": "journal_index", "trust_tier": "tier_2_academic", "domains": ["Physics", "Mathematics", "Computer Science", "AI", "Robotics"], "country": "International", "region": "International", "website": "https://arxiv.org", "owner_ai": "Minerva"},
        {"name": "PubMed", "source_type": "journal_index", "trust_tier": "tier_1_official", "domains": ["Medicine", "Biology", "Public Health", "Genetics"], "country": "United States", "region": "North America", "website": "https://pubmed.ncbi.nlm.nih.gov", "owner_ai": "Minerva"},
        {"name": "Google Scholar", "source_type": "journal_index", "trust_tier": "tier_2_academic", "domains": ["Academic Search", "Research"], "country": "International", "region": "International", "website": "https://scholar.google.com", "owner_ai": "Council"},
        {"name": "MIT OpenCourseWare", "source_type": "university", "trust_tier": "tier_2_academic", "domains": ["Engineering", "Computer Science", "Physics", "Mathematics"], "country": "United States", "region": "North America", "website": "https://ocw.mit.edu", "owner_ai": "Ajani"},
        {"name": "ETH Zurich", "source_type": "university", "trust_tier": "tier_2_academic", "domains": ["Engineering", "Robotics", "AI", "Architecture"], "country": "Switzerland", "region": "Europe", "website": "https://ethz.ch", "owner_ai": "Hermes"},
        {"name": "Fraunhofer Society", "source_type": "research_institute", "trust_tier": "tier_1_official", "domains": ["Manufacturing", "Materials", "Robotics", "Energy"], "country": "Germany", "region": "Europe", "website": "https://www.fraunhofer.de", "owner_ai": "Hermes"},
        {"name": "Max Planck Society", "source_type": "research_institute", "trust_tier": "tier_1_official", "domains": ["Physics", "Chemistry", "Biology", "Materials"], "country": "Germany", "region": "Europe", "website": "https://www.mpg.de", "owner_ai": "Minerva"},
        {"name": "ESA", "source_type": "government_agency", "trust_tier": "tier_1_official", "domains": ["Aerospace", "Earth Science", "Robotics"], "country": "International", "region": "Europe", "website": "https://www.esa.int", "owner_ai": "Hermes"},
        {"name": "JAXA", "source_type": "government_agency", "trust_tier": "tier_1_official", "domains": ["Aerospace", "Robotics", "Materials"], "country": "Japan", "region": "Asia", "website": "https://global.jaxa.jp", "owner_ai": "Hermes"},
        {"name": "RIKEN", "source_type": "research_institute", "trust_tier": "tier_1_official", "domains": ["Biology", "Physics", "AI", "Materials"], "country": "Japan", "region": "Asia", "website": "https://www.riken.jp/en", "owner_ai": "Minerva"},
        {"name": "KAIST", "source_type": "university", "trust_tier": "tier_2_academic", "domains": ["AI", "Robotics", "Electronics", "Semiconductors"], "country": "South Korea", "region": "Asia", "website": "https://www.kaist.ac.kr/en", "owner_ai": "Hermes"},
        {"name": "A*STAR", "source_type": "research_institute", "trust_tier": "tier_1_official", "domains": ["Biotechnology", "Materials", "AI", "Manufacturing"], "country": "Singapore", "region": "Asia", "website": "https://www.a-star.edu.sg", "owner_ai": "Minerva"},
        {"name": "ISRO", "source_type": "government_agency", "trust_tier": "tier_1_official", "domains": ["Aerospace", "Remote Sensing", "Systems Engineering"], "country": "India", "region": "Asia", "website": "https://www.isro.gov.in", "owner_ai": "Ajani"},
        {"name": "CSIRO", "source_type": "government_agency", "trust_tier": "tier_1_official", "domains": ["Agriculture", "Materials", "Energy", "Environmental Science"], "country": "Australia", "region": "Oceania", "website": "https://www.csiro.au", "owner_ai": "Minerva"},
        {"name": "EMBRAPA", "source_type": "government_agency", "trust_tier": "tier_1_official", "domains": ["Agriculture", "Biology", "Environmental Science"], "country": "Brazil", "region": "South America", "website": "https://www.embrapa.br/en", "owner_ai": "Minerva"},
        {"name": "CSIR South Africa", "source_type": "research_institute", "trust_tier": "tier_1_official", "domains": ["Engineering", "Water", "Materials", "Environmental Science"], "country": "South Africa", "region": "Africa", "website": "https://www.csir.co.za", "owner_ai": "Hermes"},
        {"name": "WIPO Patentscope", "source_type": "patent_database", "trust_tier": "tier_1_official", "domains": ["Patents", "Innovation", "Technology"], "country": "International", "region": "International", "website": "https://patentscope.wipo.int", "owner_ai": "Ajani"},
        {"name": "USPTO", "source_type": "patent_database", "trust_tier": "tier_1_official", "domains": ["Patents", "Trademarks", "Technology"], "country": "United States", "region": "North America", "website": "https://www.uspto.gov", "owner_ai": "Ajani"},
        {"name": "Python Documentation", "source_type": "documentation", "trust_tier": "tier_1_official", "domains": ["Software Engineering", "Programming"], "country": "International", "region": "International", "website": "https://docs.python.org", "owner_ai": "Ajani"},
        {"name": "ROS Documentation", "source_type": "documentation", "trust_tier": "tier_1_official", "domains": ["Robotics", "Software Engineering"], "country": "International", "region": "International", "website": "https://docs.ros.org", "owner_ai": "Hermes"},
        {"name": "ATLAS YouTube via Windsor", "source_type": "media_source", "trust_tier": "tier_5_personal", "domains": ["User Approved Videos", "Learning", "Research Leads"], "country": "Personal", "region": "Personal", "access_method": "connector", "owner_ai": "Council", "ingestion_status": "connected", "notes": "Connected through Windsor.ai; use as learning leads that require verification."},
        {"name": "Frazier GitHub Archive", "source_type": "personal_archive", "trust_tier": "tier_5_personal", "domains": ["ATLAS", "Code", "Project History"], "country": "Personal", "region": "Personal", "access_method": "connector", "owner_ai": "Ajani", "ingestion_status": "connected"},
    ]
