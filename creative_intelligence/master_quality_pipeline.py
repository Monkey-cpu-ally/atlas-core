"""Master ATLAS creative quality pipeline.

Separates creative approval from production readiness:
1) reference/originality/critique/revision approval
2) final story/art/visual/continuity production gate
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Generic, Tuple, TypeVar

from creative_production.art_style import ArtStyleAssessment
from creative_production.quality_gate import ProductionQualityDecision, ProductionQualityGate
from creative_production.story_quality import StoryQualityReport
from creative_production.visual_quality import VisualQualityAssessment
from .critic_council import CouncilDecision
from .quality_pipeline import CreativeQualityPipeline, CreativeQualityResult
from creative_production.reference_provenance import OriginalityAssessment

T = TypeVar("T")


@dataclass(frozen=True)
class MasterCreativeQualityResult(Generic[T]):
    creative: CreativeQualityResult[T]
    production: ProductionQualityDecision | None
    blockers: Tuple[str, ...]

    @property
    def production_ready(self) -> bool:
        return (
            self.creative.approved
            and self.production is not None
            and self.production.production_ready
            and not self.blockers
        )


class MasterCreativeQualityPipeline(Generic[T]):
    """Fail-closed orchestration from creative critique through master-asset approval."""

    def __init__(self, creative_pipeline: CreativeQualityPipeline[T] | None = None):
        self.creative_pipeline = creative_pipeline or CreativeQualityPipeline[T]()
        self.production_gate = ProductionQualityGate()

    def run(self, *, artifact: T, reference_queries: Tuple[str, ...],
            originality: OriginalityAssessment,
            evaluate: Callable[[T], CouncilDecision],
            revise: Callable[[T, Tuple[str, ...]], T],
            production_assessments: Callable[[T], tuple[StoryQualityReport, ArtStyleAssessment, VisualQualityAssessment, bool]]) -> MasterCreativeQualityResult[T]:
        creative = self.creative_pipeline.run(
            artifact=artifact,
            reference_queries=reference_queries,
            originality=originality,
            evaluate=evaluate,
            revise=revise,
        )
        blockers = list(creative.blockers)
        if not creative.approved or creative.revision is None:
            blockers.append("creative_quality_not_approved")
            return MasterCreativeQualityResult(creative, None, tuple(dict.fromkeys(blockers)))

        final_artifact = creative.revision.final_artifact
        story, art_style, visual, continuity_ready = production_assessments(final_artifact)
        production = self.production_gate.evaluate(
            story_assessment=story,
            art_style_assessment=art_style,
            visual_assessment=visual,
            continuity_ready=continuity_ready,
        )
        if not production.production_ready:
            blockers.extend(f"production:{item}" for item in production.blockers)

        return MasterCreativeQualityResult(
            creative=creative,
            production=production,
            blockers=tuple(dict.fromkeys(blockers)),
        )
