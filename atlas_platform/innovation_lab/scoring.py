"""Deterministic Innovation Lab scoring engine."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Mapping


CRITERIA = (
    "novelty",
    "feasibility",
    "manufacturing",
    "cost",
    "sustainability",
    "safety",
    "user_experience",
    "long_term_value",
    "competitive_advantage",
)


@dataclass(frozen=True)
class InnovationScore:
    """Normalized Innovation Lab score and decision band."""

    criteria: Dict[str, float]
    total: float
    maximum: float
    percentage: float
    recommendation: str


def score_innovation(scores: Mapping[str, float]) -> InnovationScore:
    """Score all required criteria on a 0-10 scale.

    The engine refuses partial rubrics so Council never receives a misleading
    total based on missing criteria.
    """

    missing = set(CRITERIA) - set(scores)
    extra = set(scores) - set(CRITERIA)
    if missing:
        raise ValueError(f"missing scoring criteria: {', '.join(sorted(missing))}")
    if extra:
        raise ValueError(f"unknown scoring criteria: {', '.join(sorted(extra))}")

    normalized: Dict[str, float] = {}
    for criterion in CRITERIA:
        value = float(scores[criterion])
        if value < 0 or value > 10:
            raise ValueError(f"{criterion} score must be between 0 and 10")
        normalized[criterion] = value

    total = round(sum(normalized.values()), 2)
    maximum = float(len(CRITERIA) * 10)
    percentage = round((total / maximum) * 100, 2)

    if percentage >= 80:
        recommendation = "advance"
    elif percentage >= 60:
        recommendation = "revise_or_validate"
    else:
        recommendation = "hold"

    return InnovationScore(
        criteria=normalized,
        total=total,
        maximum=maximum,
        percentage=percentage,
        recommendation=recommendation,
    )
