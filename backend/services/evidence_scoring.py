"""ATLAS Evidence Scoring.

Deterministic scoring helpers for discovery review. V1 is intentionally simple
and transparent: it scores evidence strength from citations, source types,
recency signals, and review agreement. No claims are treated as truth without
Council approval.
"""
from __future__ import annotations

from typing import Any, Dict, List

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


def score_evidence(evidence: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Score evidence items using clear, auditable rules."""
    if not evidence:
        return {
            "score": 0,
            "level": "none",
            "reasons": ["No evidence supplied."],
            "items_count": 0,
        }

    score = 0
    reasons: List[str] = []
    cited = 0
    source_types = set()

    for item in evidence:
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
