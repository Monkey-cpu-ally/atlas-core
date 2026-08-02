"""ATLAS Evidence Scoring.

Deterministic scoring helpers for discovery review. Evidence strength is scored
from citations, source types, recency signals, review agreement, and registered
source reliability. No claim is treated as truth without Council approval.
"""
from __future__ import annotations

from typing import Any, Dict, List

from services import global_source_library, source_reliability

SOURCE_TYPE_WEIGHTS = {
    "peer_reviewed": 30,
    "government": 28,
    "standards_body": 26,
    "university": 24,
    "patent": 20,
    "technical_documentation": 18,
    "open_source": 16,
    "news": 10,
    "video": 8,
    "unknown": 4,
}


def clamp_score(value: int) -> int:
    return max(0, min(100, int(value)))


def _reliability_adjustment(score: int) -> int:
    """Convert a 0-100 source score into a bounded -8 to +8 evidence modifier."""
    return max(-8, min(8, round((int(score) - 50) / 6.25)))


def score_evidence(evidence: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Score evidence items using clear, auditable rules."""
    if not evidence:
        return {
            "score": 0,
            "level": "none",
            "reasons": ["No evidence supplied."],
            "items_count": 0,
            "source_reliability": {
                "registered_items": 0,
                "unregistered_items": 0,
                "average_score": None,
                "corroboration_required_count": 0,
                "assessments": [],
            },
        }

    score = 0
    reasons: List[str] = []
    cited = 0
    source_types = set()
    reliability_assessments: List[Dict[str, Any]] = []
    unregistered_source_ids: List[str] = []

    for index, item in enumerate(evidence):
        source_type = str(item.get("source_type", "unknown")).lower()
        source_types.add(source_type)
        score += SOURCE_TYPE_WEIGHTS.get(source_type, SOURCE_TYPE_WEIGHTS["unknown"])

        if item.get("citation") or item.get("url") or item.get("source_id"):
            cited += 1
            score += 8
        if item.get("published_at") or item.get("accessed_at"):
            score += 4
        if item.get("conflict") is True:
            score -= 15
        if item.get("direct_support") is True:
            score += 8

        source_id = item.get("source_id")
        if source_id:
            registered_source = global_source_library.get_source(str(source_id))
            if registered_source:
                assessment = source_reliability.assess_source(
                    registered_source,
                    domain=item.get("domain"),
                )
                adjustment = _reliability_adjustment(assessment["reliability_score"])
                score += adjustment
                reliability_assessments.append(
                    {
                        "evidence_index": index,
                        "source_id": source_id,
                        "source_name": assessment["name"],
                        "reliability_score": assessment["reliability_score"],
                        "reliability_band": assessment["reliability_band"],
                        "evidence_adjustment": adjustment,
                        "corroboration_required": assessment["corroboration_required"],
                        "domain_match": assessment["domain_match"],
                        "warnings": assessment["warnings"],
                    }
                )
            else:
                score -= 4
                unregistered_source_ids.append(str(source_id))

    if len(source_types) >= 2:
        score += 10
        reasons.append("Evidence comes from multiple source types.")
    if cited == len(evidence):
        score += 10
        reasons.append("All evidence items include citation/origin metadata.")
    elif cited > 0:
        reasons.append("Some evidence items include citation/origin metadata.")
    else:
        reasons.append("Evidence lacks citation/origin metadata.")

    if reliability_assessments:
        average_reliability = sum(item["reliability_score"] for item in reliability_assessments) // len(reliability_assessments)
        reasons.append(
            f"{len(reliability_assessments)} evidence item(s) were checked against the Global Source Library; average source reliability was {average_reliability}."
        )
    else:
        average_reliability = None

    if unregistered_source_ids:
        reasons.append(
            f"{len(unregistered_source_ids)} cited source ID(s) were not registered in the Global Source Library."
        )

    corroboration_required_count = sum(
        1 for item in reliability_assessments if item["corroboration_required"]
    )
    if corroboration_required_count:
        reasons.append(
            f"{corroboration_required_count} registered source assessment(s) require independent corroboration."
        )

    final = clamp_score(score // max(1, len(evidence)))
    if final >= 80:
        level = "strong"
    elif final >= 60:
        level = "moderate"
    elif final >= 35:
        level = "weak"
    else:
        level = "insufficient"

    return {
        "score": final,
        "level": level,
        "reasons": reasons,
        "items_count": len(evidence),
        "cited_items": cited,
        "source_types": sorted(source_types),
        "source_reliability": {
            "registered_items": len(reliability_assessments),
            "unregistered_items": len(unregistered_source_ids),
            "unregistered_source_ids": sorted(set(unregistered_source_ids)),
            "average_score": average_reliability,
            "corroboration_required_count": corroboration_required_count,
            "assessments": reliability_assessments,
            "rule": "Source reliability adjusts evidence routing only; Council approval and claim-level review remain required.",
        },
    }


def score_reviews(reviews: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Score agreement among Ajani, Hermes, Minerva, and Council-style reviews."""
    if not reviews:
        return {"score": 0, "level": "none", "approve_count": 0, "review_count": 0}
    approve_count = sum(1 for review in reviews if review.get("recommendation") == "approve")
    needs_more = sum(1 for review in reviews if review.get("recommendation") == "needs_more_evidence")
    reject_count = sum(1 for review in reviews if review.get("recommendation") == "reject")
    confidence = sum(int(review.get("confidence_score", 50)) for review in reviews) // len(reviews)
    score = confidence + approve_count * 8 - needs_more * 6 - reject_count * 12
    final = clamp_score(score)
    return {
        "score": final,
        "level": "aligned" if approve_count >= 2 and reject_count == 0 else "mixed",
        "approve_count": approve_count,
        "needs_more_evidence_count": needs_more,
        "reject_count": reject_count,
        "review_count": len(reviews),
    }
