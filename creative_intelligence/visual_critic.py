"""Fail-closed visual production gate for ATLAS-directed work."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple

from creative_intelligence.craft_rubrics import VISUAL_ART
from creative_intelligence.critic_council import CouncilDecision, CreativeCriticCouncil
from creative_intelligence.visual_direction import VisualDirectionSpec

PRODUCTION_GATES = (
    "anatomy",
    "silhouette",
    "materials",
    "lighting",
    "continuity",
    "character_consistency",
    "camera_language",
    "animation_quality",
    "originality",
    "project_constraints",
)


@dataclass(frozen=True)
class VisualProductionDecision:
    council: CouncilDecision
    production_scores: Dict[str, int]
    blockers: Tuple[str, ...]

    @property
    def approved(self) -> bool:
        return self.council.approved and not self.blockers


def review_visual_production(
    spec: VisualDirectionSpec,
    *,
    critic_scores: Dict[str, Dict[str, int]],
    production_scores: Dict[str, int],
    findings=None,
    revision_requests=None,
) -> VisualProductionDecision:
    if not isinstance(spec, VisualDirectionSpec):
        raise ValueError("VisualDirectionSpec is required")
    if not spec.project_identity_authoritative or not spec.direct_imitation_forbidden:
        raise ValueError("unsafe visual direction cannot enter Critic Council")

    missing = set(PRODUCTION_GATES) - set(production_scores)
    if missing:
        raise ValueError(f"missing visual production gates: {sorted(missing)}")
    clean = {gate: max(0, min(100, int(production_scores[gate]))) for gate in PRODUCTION_GATES}
    blockers = []
    for gate, score in clean.items():
        if score < VISUAL_ART.passing_score:
            blockers.append(f"visual:{gate}")
    if not spec.project_constraints:
        blockers.append("visual:project_constraints_missing")

    council = CreativeCriticCouncil().review(
        rubric=VISUAL_ART,
        critic_scores=critic_scores,
        findings=findings,
        revision_requests=revision_requests,
    )
    return VisualProductionDecision(council=council, production_scores=clean, blockers=tuple(blockers))
