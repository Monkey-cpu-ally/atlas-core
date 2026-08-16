"""Adversarial multi-perspective critic council for ATLAS creative work."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple

from .craft_rubrics import CraftRubric


@dataclass(frozen=True)
class CriticReview:
    critic: str
    focus: str
    scores: Dict[str, int]
    findings: Tuple[str, ...]
    revision_requests: Tuple[str, ...]

    @property
    def average(self) -> float:
        return sum(self.scores.values()) / len(self.scores) if self.scores else 0.0


@dataclass(frozen=True)
class CouncilDecision:
    reviews: Tuple[CriticReview, ...]
    blockers: Tuple[str, ...]
    revision_plan: Tuple[str, ...]

    @property
    def approved(self) -> bool:
        return not self.blockers


class CreativeCriticCouncil:
    """Fail-closed council: disagreement exposes weaknesses instead of averaging them away."""

    CRITIC_FOCUS = {
        "minerva": "theme, research, emotional truth, cultural/artistic context, meaning",
        "hermes": "construction, continuity, internal logic, anatomy, perspective, composition, technical execution",
        "ajani": "impact, clarity, pacing, tension, character decisions, audience experience",
    }

    def review(self, *, rubric: CraftRubric, critic_scores: Dict[str, Dict[str, int]],
               findings: Dict[str, List[str]] | None = None,
               revision_requests: Dict[str, List[str]] | None = None) -> CouncilDecision:
        findings = findings or {}
        revision_requests = revision_requests or {}
        reviews: List[CriticReview] = []
        blockers: List[str] = []
        revisions: List[str] = []

        for critic, focus in self.CRITIC_FOCUS.items():
            if critic not in critic_scores:
                blockers.append(f"missing_critic:{critic}")
                continue
            scores = rubric.validate_scores(critic_scores[critic])
            review = CriticReview(
                critic=critic,
                focus=focus,
                scores=scores,
                findings=tuple(findings.get(critic, [])),
                revision_requests=tuple(revision_requests.get(critic, [])),
            )
            reviews.append(review)
            weak = sorted(name for name, score in scores.items() if score < rubric.passing_score)
            if weak:
                blockers.extend(f"{critic}:{name}" for name in weak)
            revisions.extend(review.revision_requests)

        # No averaging away a specialist objection: any sub-threshold dimension blocks approval.
        return CouncilDecision(
            reviews=tuple(reviews),
            blockers=tuple(dict.fromkeys(blockers)),
            revision_plan=tuple(dict.fromkeys(item for item in revisions if item.strip())),
        )
