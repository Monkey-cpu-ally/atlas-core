"""End-to-end ATLAS creative production orchestration.

Coordinates Story Foundry, Visual Development, and Animation Studio while preserving
one Creative Intelligence context path through the production pipeline.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List

from story_foundry.mini_screenplay_engine import MiniScreenplayEngine, MiniScreenplayPlan
from academy.school_of_visual_development.visual_development_engine import (
    VisualDevelopmentEngine,
    VisualDevelopmentPlan,
)
from atlas_animation_studio.storyboard_engine import StoryboardEngine, StoryboardSequence


@dataclass(frozen=True)
class CreativeProductionRequest:
    project: str
    idea: str
    emotion: str
    visual_subject: str
    visual_purpose: str
    beat_goals: List[str]
    scene_number: int = 1


@dataclass
class CreativeProductionPackage:
    request: CreativeProductionRequest
    screenplay: MiniScreenplayPlan
    visual_development: VisualDevelopmentPlan
    storyboard: StoryboardSequence

    @property
    def has_creative_intelligence(self) -> bool:
        return all((
            bool(self.screenplay.creative_context),
            bool(self.visual_development.creative_context),
            bool(self.storyboard.creative_context),
        ))

    def to_markdown(self) -> str:
        return "\n\n---\n\n".join([
            f"# ATLAS Creative Production Package — {self.request.project}",
            self.screenplay.to_markdown(),
            self.visual_development.to_markdown(),
            self.storyboard.to_markdown(),
        ])


class CreativeProductionOrchestrator:
    """Runs a project through the verified creative production consumers."""

    def __init__(self, *, creative_bridge=None) -> None:
        self.screenplay_engine = MiniScreenplayEngine(creative_bridge=creative_bridge)
        self.visual_engine = VisualDevelopmentEngine(creative_bridge=creative_bridge)
        self.storyboard_engine = StoryboardEngine(creative_bridge=creative_bridge)

    def produce(self, request: CreativeProductionRequest) -> CreativeProductionPackage:
        screenplay = self.screenplay_engine.build_plan(
            request.project, request.idea, request.emotion
        )
        visual_development = self.visual_engine.build_plan(
            project=request.project,
            subject=request.visual_subject,
            purpose=request.visual_purpose,
        )
        storyboard = self.storyboard_engine.build_sequence(
            request.project,
            request.scene_number,
            request.beat_goals,
        )
        return CreativeProductionPackage(
            request=request,
            screenplay=screenplay,
            visual_development=visual_development,
            storyboard=storyboard,
        )
