"""ATLAS World Knowledge Connector Engine.

This service is the first backend layer for the World Knowledge Network.
It does not scrape or ingest full source content yet. It safely loads the
approved source registry, exposes source metadata, creates dry-run sync jobs,
and defines the shape of future knowledge records.

Design rule: ATLAS stores understanding, citations, and traceable metadata —
not copyrighted works wholesale.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4

ROOT_DIR = Path(__file__).resolve().parents[2]
WORLD_SOURCES_DIR = ROOT_DIR / "knowledge_bank" / "world_sources"
SOURCE_REGISTRY_PATH = WORLD_SOURCES_DIR / "source_registry.json"
TRUST_LEVELS_PATH = WORLD_SOURCES_DIR / "trust_levels.json"


class WorldKnowledgeError(RuntimeError):
    """Raised when the World Knowledge Network cannot complete a request."""


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _read_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise WorldKnowledgeError(f"missing world knowledge file: {path}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise WorldKnowledgeError(f"invalid JSON in {path}: {exc}") from exc


def load_source_registry() -> Dict[str, Any]:
    """Load the approved source registry from the Knowledge Bank."""
    return _read_json(SOURCE_REGISTRY_PATH)


def load_trust_levels() -> Dict[str, Any]:
    """Load trust tier rules used by the connector engine."""
    return _read_json(TRUST_LEVELS_PATH)


def list_sources(
    *,
    ai_owner: Optional[str] = None,
    country: Optional[str] = None,
    region: Optional[str] = None,
    subject: Optional[str] = None,
    trust_tier: Optional[str] = None,
    auto_sync: Optional[bool] = None,
) -> List[Dict[str, Any]]:
    """Return approved source records filtered by common dashboard fields."""
    registry = load_source_registry()
    sources: List[Dict[str, Any]] = list(registry.get("sources", []))

    def keep(src: Dict[str, Any]) -> bool:
        if ai_owner and str(src.get("ai_owner", "")).lower() != ai_owner.lower():
            return False
        if country and str(src.get("country", "")).lower() != country.lower():
            return False
        if region and str(src.get("region", "")).lower() != region.lower():
            return False
        if trust_tier and str(src.get("trust_tier", "")).lower() != trust_tier.lower():
            return False
        if auto_sync is not None and bool(src.get("auto_sync")) is not auto_sync:
            return False
        if subject:
            subjects = [str(s).lower() for s in src.get("subjects", [])]
            if subject.lower() not in subjects:
                return False
        return True

    return [src for src in sources if keep(src)]


def get_source(source_id: str) -> Optional[Dict[str, Any]]:
    """Find one source by registry id."""
    for source in list_sources():
        if source.get("id") == source_id:
            return source
    return None


def stats() -> Dict[str, Any]:
    """Return dashboard-friendly World Knowledge Network statistics."""
    sources = list_sources()
    by_owner: Dict[str, int] = {}
    by_region: Dict[str, int] = {}
    by_tier: Dict[str, int] = {}
    by_type: Dict[str, int] = {}
    auto_sync_count = 0

    for source in sources:
        owner = source.get("ai_owner") or "unknown"
        region = source.get("region") or "unknown"
        tier = source.get("trust_tier") or "unknown"
        source_type = source.get("source_type") or "unknown"
        by_owner[owner] = by_owner.get(owner, 0) + 1
        by_region[region] = by_region.get(region, 0) + 1
        by_tier[tier] = by_tier.get(tier, 0) + 1
        by_type[source_type] = by_type.get(source_type, 0) + 1
        if source.get("auto_sync"):
            auto_sync_count += 1

    return {
        "status": "registered_not_live_synced",
        "total_sources": len(sources),
        "auto_sync_enabled": auto_sync_count,
        "by_owner": by_owner,
        "by_region": by_region,
        "by_trust_tier": by_tier,
        "by_source_type": by_type,
        "notes": "Sources are registered. Live web/API/RSS extraction is the next implementation layer.",
    }


def plan_sync_job(source_id: str, mission: Optional[str] = None) -> Dict[str, Any]:
    """Create a dry-run sync job plan for an approved source.

    This does not contact the source yet. It returns the exact job shape that
    future scheduler/connectors should persist and execute.
    """
    source = get_source(source_id)
    if not source:
        raise WorldKnowledgeError(f"unknown source_id: {source_id}")

    access_method = str(source.get("access_method", "web"))
    connector_type = "web_metadata"
    if "rss" in access_method:
        connector_type = "rss"
    elif "api" in access_method:
        connector_type = "api"
    elif source.get("source_type") == "open_source_code_repository":
        connector_type = "github"
    elif "youtube" in str(source.get("source_type", "")):
        connector_type = "youtube"
    elif "patent" in str(source.get("source_type", "")):
        connector_type = "patent"

    return {
        "job_id": str(uuid4()),
        "source_id": source["id"],
        "source_name": source.get("name"),
        "ai_owner": source.get("ai_owner"),
        "mission": mission or f"Check {source.get('name')} for useful ATLAS knowledge updates.",
        "connector_type": connector_type,
        "status": "planned",
        "priority": "normal",
        "created_at": _utc_now(),
        "started_at": None,
        "completed_at": None,
        "items_found": 0,
        "items_processed": 0,
        "knowledge_records_created": 0,
        "knowledge_records_updated": 0,
        "errors": [],
        "requires_council_review": source.get("trust_tier") not in ("S", "A"),
        "related_projects": [],
        "dry_run": True,
        "next_step": "Implement connector execution and Knowledge Bank write-through.",
    }


def build_knowledge_record_template(source_id: str, title: str, summary: str) -> Dict[str, Any]:
    """Create a Knowledge Record template from one approved source.

    This is used by tests and future connector code to keep record shape stable.
    """
    source = get_source(source_id)
    if not source:
        raise WorldKnowledgeError(f"unknown source_id: {source_id}")

    return {
        "record_id": str(uuid4()),
        "title": title,
        "source_id": source["id"],
        "source_name": source.get("name"),
        "original_url": source.get("url"),
        "country": source.get("country"),
        "region": source.get("region"),
        "language": source.get("language"),
        "ai_owner": source.get("ai_owner"),
        "subject_tags": source.get("subjects", []),
        "summary_in_own_words": summary,
        "key_findings": [],
        "evidence_notes": "Initial template. Requires connector extraction and AI review before verification.",
        "confidence_score": source.get("trust_score"),
        "trust_tier": source.get("trust_tier"),
        "verification_status": "single_source",
        "related_projects": [],
        "related_records": [],
        "created_at": _utc_now(),
        "last_verified": None,
        "next_review": None,
        "version": 1,
        "change_reason": "initial knowledge record template",
    }
