from __future__ import annotations

from typing import Dict, Iterable, Mapping

from .models import DesignConcept, DesignGenome, GenomeScore


DEFAULT_CATEGORIES = (
    "beauty",
    "story",
    "engineering",
    "craftsmanship",
    "materials",
    "innovation",
    "originality",
    "repairability",
    "longevity",
    "manufacturability",
    "comfort",
    "emotional_impact",
)


class DesignGenomeEngine:
    """Creates a measurable House of Frazier design profile.

    The engine accepts human- or AI-provided evidence scores and applies small,
    transparent adjustments based on the design record. It deliberately avoids
    pretending that aesthetic judgment can be fully automated.
    """

    def __init__(self, weights: Mapping[str, float] | None = None) -> None:
        self.weights = dict(weights or {category: 1.0 for category in DEFAULT_CATEGORIES})
        missing = set(DEFAULT_CATEGORIES) - self.weights.keys()
        if missing:
            raise ValueError(f"Missing genome weights: {sorted(missing)}")
        if any(weight <= 0 for weight in self.weights.values()):
            raise ValueError("Genome weights must be positive")

    @staticmethod
    def _clamp(value: float) -> float:
        return round(max(0.0, min(100.0, value)), 2)

    def score(
        self,
        concept: DesignConcept,
        evidence_scores: Mapping[str, float],
        reasons: Mapping[str, str] | None = None,
    ) -> DesignGenome:
        reasons = reasons or {}
        unknown = set(evidence_scores) - set(DEFAULT_CATEGORIES)
        if unknown:
            raise ValueError(f"Unknown genome categories: {sorted(unknown)}")

        scores = []
        for category in DEFAULT_CATEGORIES:
            base = float(evidence_scores.get(category, 50.0))
            adjustment = self._concept_adjustment(category, concept)
            final = self._clamp(base + adjustment)
            reason = reasons.get(category, self._default_reason(category, adjustment))
            scores.append(GenomeScore(category=category, score=final, reason=reason))

        return DesignGenome(design_id=concept.design_id, scores=scores)

    def weighted_overall(self, genome: DesignGenome) -> float:
        score_map = genome.as_dict()
        numerator = sum(score_map[category] * self.weights[category] for category in DEFAULT_CATEGORIES)
        denominator = sum(self.weights.values())
        return round(numerator / denominator, 2)

    def weakest_categories(self, genome: DesignGenome, limit: int = 3) -> list[GenomeScore]:
        return sorted(genome.scores, key=lambda item: item.score)[: max(0, limit)]

    def strongest_categories(self, genome: DesignGenome, limit: int = 3) -> list[GenomeScore]:
        return sorted(genome.scores, key=lambda item: item.score, reverse=True)[: max(0, limit)]

    @staticmethod
    def _concept_adjustment(category: str, concept: DesignConcept) -> float:
        adjustment = 0.0
        if category == "story" and concept.story.strip():
            adjustment += 5.0
        if category == "materials" and len(concept.materials) >= 2:
            adjustment += 3.0
        if category == "engineering" and concept.manufacturing_notes.strip():
            adjustment += 4.0
        if category == "repairability" and concept.repair_plan.strip():
            adjustment += 8.0
        if category == "originality" and len(concept.inspirations) > 4:
            adjustment -= 3.0
        if category == "manufacturability" and not concept.manufacturing_notes.strip():
            adjustment -= 8.0
        return adjustment

    @staticmethod
    def _default_reason(category: str, adjustment: float) -> str:
        if adjustment > 0:
            return f"Evidence score adjusted by +{adjustment:g} from documented design details."
        if adjustment < 0:
            return f"Evidence score adjusted by {adjustment:g} because required documentation is weak or risky."
        return f"Evidence score retained for {category}."
