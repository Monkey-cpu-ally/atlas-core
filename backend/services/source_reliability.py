"""ATLAS Source Reliability Ranking.

Produces transparent, deterministic reliability assessments for records in the
Global Source Library. A score is a routing aid, not a declaration that every
claim from a source is true. Claim-level evidence review remains mandatory.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Optional

TRUST_TIER_BASE = {
    "tier_1_official": 92,
    "tier_2_academic": 84,
    "tier_3_industry": 72,
    "tier_4_community": 56,
    "tier_5_personal": 42,
}

SOURCE_TYPE_ADJUSTMENT = {
    "standards_body": 5,
    "government_agency": 4,
    "research_institute": 4,
    "university": 3,
    "journal_index": 2,
    "patent_database": 1,
    "data_portal": 1,
    "documentation": 0,
    "open_source": -1,
    "media_source": -4,
    "personal_archive": -8,
}

INGESTION_ADJUSTMENT = {
    "approved": 4,
    "reviewed": 3,
    "candidate": 0,
    "paused": -3,
    "rejected": -20,
    "blocked": -25,
}

ACCESS_ADJUSTMENT = {
    "api": 2,
    "dataset_download": 2,
    "rss": 1,
    "website": 0,
    "manual_review": 1,
    "connector": 0,
    "library_import": 0,
    "not_connected": -2,
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _clamp(value: int, low: int = 0, high: int = 100) -> int:
    return max(low, min(high, int(value)))


def _band(score: int) -> str:
    if score >= 90:
        return "verified_priority"
    if score >= 80:
        return "strong"
    if score >= 65:
        return "usable_with_corroboration"
    if score >= 50:
        return "caution"
    return "restricted"


def assess_source(source: Dict[str, Any], *, domain: Optional[str] = None) -> Dict[str, Any]:
    """Return a transparent reliability assessment for one source record."""
    trust_tier = source.get("trust_tier", "")
    source_type = source.get("source_type", "")
    ingestion_status = source.get("ingestion_status", "candidate")
    access_method = source.get("access_method", "not_connected")

    base = TRUST_TIER_BASE.get(trust_tier, 35)
    type_adjustment = SOURCE_TYPE_ADJUSTMENT.get(source_type, -3)
    review_adjustment = INGESTION_ADJUSTMENT.get(ingestion_status, -2)
    access_adjustment = ACCESS_ADJUSTMENT.get(access_method, -1)
    provenance_adjustment = 2 if source.get("website") else -5
    review_evidence_adjustment = 2 if source.get("last_reviewed_at") else 0

    domain_adjustment = 0
    domain_match = None
    if domain:
        domains = {str(item).lower() for item in source.get("domains", [])}
        domain_match = domain.lower() in domains
        domain_adjustment = 3 if domain_match else -6

    score = _clamp(
        base
        + type_adjustment
        + review_adjustment
        + access_adjustment
        + provenance_adjustment
        + review_evidence_adjustment
        + domain_adjustment
    )

    warnings: List[str] = []
    if not source.get("website"):
        warnings.append("No provenance website is registered.")
    if not source.get("last_reviewed_at"):
        warnings.append("Source has not completed an ATLAS review cycle.")
    if ingestion_status in {"rejected", "blocked"}:
        warnings.append("Source is not approved for ingestion.")
    if domain is not None and domain_match is False:
        warnings.append(f"Source is not registered for the requested domain: {domain}.")
    if trust_tier in {"tier_4_community", "tier_5_personal"}:
        warnings.append("Independent corroboration is required before promotion to trusted knowledge.")

    corroboration_required = score < 90 or source_type in {
        "open_source", "media_source", "personal_archive"
    }

    return {
        "source_id": source.get("source_id"),
        "name": source.get("name"),
        "reliability_score": score,
        "reliability_band": _band(score),
        "corroboration_required": corroboration_required,
        "eligible_for_automatic_priority": score >= 90 and ingestion_status not in {"rejected", "blocked"},
        "domain": domain,
        "domain_match": domain_match,
        "factors": {
            "trust_tier_base": base,
            "source_type_adjustment": type_adjustment,
            "ingestion_status_adjustment": review_adjustment,
            "access_method_adjustment": access_adjustment,
            "provenance_adjustment": provenance_adjustment,
            "review_evidence_adjustment": review_evidence_adjustment,
            "domain_adjustment": domain_adjustment,
        },
        "warnings": warnings,
        "rule": "Source reliability ranks provenance and review readiness; it does not prove individual claims.",
        "generated_at": _utc_now(),
    }


def rank_sources(
    sources: Iterable[Dict[str, Any]],
    *,
    domain: Optional[str] = None,
    minimum_score: int = 0,
    limit: int = 100,
) -> Dict[str, Any]:
    assessments = [assess_source(source, domain=domain) for source in sources]
    assessments = [item for item in assessments if item["reliability_score"] >= _clamp(minimum_score)]
    assessments.sort(key=lambda item: (-item["reliability_score"], item.get("name") or ""))
    selected = assessments[: max(1, min(int(limit), 1000))]

    return {
        "title": "ATLAS Source Reliability Ranking",
        "domain": domain,
        "minimum_score": _clamp(minimum_score),
        "count": len(selected),
        "items": selected,
        "policy": {
            "verified_priority": "May be prioritized for discovery review, but claim-level evidence checks still apply.",
            "strong": "Strong source; corroborate high-impact or disputed claims.",
            "usable_with_corroboration": "Use only with at least one stronger independent source.",
            "caution": "Use for leads, context, or comparison—not as sole evidence.",
            "restricted": "Do not promote into trusted knowledge without Council exception and stronger evidence.",
        },
        "generated_at": _utc_now(),
    }
