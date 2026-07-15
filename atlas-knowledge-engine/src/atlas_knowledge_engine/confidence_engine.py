"""Evidence-aware confidence scoring for ATLAS learning sources."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from .learning_adapter import ExtractedContent


@dataclass(frozen=True, slots=True)
class ConfidenceAssessment:
    """Transparent source assessment stored with every learned record."""

    score: float
    label: str
    source_class: str
    requires_verification: bool
    reasons: tuple[str, ...]

    def as_metadata(self) -> dict[str, Any]:
        return {
            "confidence_score": self.score,
            "confidence_label": self.label,
            "source_class": self.source_class,
            "requires_verification": self.requires_verification,
            "confidence_reasons": list(self.reasons),
        }


class ConfidenceEngine:
    """Score source reliability without pretending content has been verified.

    The score measures source quality and traceability, not whether every claim in
    the content is true. Independent corroboration can raise confidence later.
    """

    _BASE_SCORES: Mapping[str, float] = {
        "peer_reviewed": 0.90,
        "government": 0.86,
        "university": 0.84,
        "official_documentation": 0.82,
        "standards_body": 0.88,
        "patent": 0.68,
        "industry": 0.64,
        "educational_video": 0.55,
        "news": 0.52,
        "community": 0.40,
        "opinion": 0.30,
        "unknown": 0.35,
    }

    def assess(self, content: ExtractedContent) -> ConfidenceAssessment:
        metadata = dict(content.metadata)
        source_class = self._source_class(content.source_type, metadata)
        score = self._BASE_SCORES[source_class]
        reasons = [f"base source class: {source_class}"]

        if content.creator and content.creator.strip():
            score += 0.04
            reasons.append("creator identified")
        else:
            score -= 0.04
            reasons.append("creator not identified")

        if content.canonical_url and content.canonical_url.strip():
            score += 0.03
            reasons.append("canonical source URL available")
        else:
            score -= 0.03
            reasons.append("canonical source URL missing")

        citations = metadata.get("citations") or metadata.get("references")
        if isinstance(citations, (list, tuple)) and citations:
            score += min(0.08, 0.02 * len(citations))
            reasons.append("supporting references supplied")

        if metadata.get("peer_reviewed") is True:
            score = max(score, 0.90)
            reasons.append("marked peer reviewed")

        if metadata.get("official_source") is True:
            score += 0.08
            reasons.append("official source marker")

        if metadata.get("requires_verification") is True:
            score -= 0.05
            reasons.append("adapter requires independent verification")

        if metadata.get("user_supplied") is True:
            score -= 0.03
            reasons.append("user-supplied classification not independently confirmed")

        score = round(max(0.0, min(1.0, score)), 3)
        requires_verification = score < 0.80 or metadata.get("requires_verification") is True
        return ConfidenceAssessment(
            score=score,
            label=self._label(score),
            source_class=source_class,
            requires_verification=requires_verification,
            reasons=tuple(reasons),
        )

    @classmethod
    def _source_class(cls, source_type: str, metadata: Mapping[str, Any]) -> str:
        explicit = str(metadata.get("source_class", "")).strip().lower()
        if explicit in cls._BASE_SCORES:
            return explicit

        normalized = source_type.strip().lower()
        defaults = {
            "youtube": "educational_video",
            "github": "official_documentation",
            "pdf": "unknown",
            "paper": "peer_reviewed" if metadata.get("peer_reviewed") is True else "unknown",
            "patent": "patent",
            "documentation": "official_documentation",
            "news": "news",
            "note": "community",
        }
        return defaults.get(normalized, "unknown")

    @staticmethod
    def _label(score: float) -> str:
        if score >= 0.90:
            return "verified"
        if score >= 0.80:
            return "high"
        if score >= 0.65:
            return "moderate"
        if score >= 0.45:
            return "limited"
        return "unverified"

    def health(self) -> dict[str, object]:
        return {
            "status": "healthy",
            "source_classes": tuple(sorted(self._BASE_SCORES)),
            "scoring_version": 1,
        }
