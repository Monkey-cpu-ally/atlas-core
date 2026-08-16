"""Unified ATLAS production approval gate."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List

from .art_style import ArtStyleAssessment
from .visual_quality import VisualQualityAssessment


@dataclass(frozen=True)
class ProductionQualityDecision:
    story_ready: bool
    art_style_ready: bool
    visual_ready: bool
    continuity_ready: bool
    blockers: List[str]

    @property
    def production_ready(self) -> bool:
        return all((self.story_ready, self.art_style_ready, self.visual_ready, self.continuity_ready)) and not self.blockers


class ProductionQualityGate:
    """Fail-closed gate: every creative quality director must approve production."""

    def evaluate(self, *, story_assessment, art_style_assessment: ArtStyleAssessment,
                 visual_assessment: VisualQualityAssessment, continuity_ready: bool) -> ProductionQualityDecision:
        story_ready = bool(getattr(story_assessment, "production_ready", False))
        art_ready = art_style_assessment.production_ready
        visual_ready = visual_assessment.production_ready
        blockers: List[str] = []

        if not story_ready:
            blockers.append("story_quality")
        if not art_ready:
            blockers.append("art_style_quality")
        if not visual_ready:
            blockers.append("visual_quality")
        if not continuity_ready:
            blockers.append("continuity")

        return ProductionQualityDecision(
            story_ready=story_ready,
            art_style_ready=art_ready,
            visual_ready=visual_ready,
            continuity_ready=continuity_ready,
            blockers=blockers,
        )
