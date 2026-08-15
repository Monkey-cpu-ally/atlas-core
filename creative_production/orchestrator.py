"""End-to-end ATLAS creative production orchestration."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List

from story_foundry.mini_screenplay_engine import MiniScreenplayEngine, MiniScreenplayPlan
from academy.school_of_visual_development.visual_development_engine import VisualDevelopmentEngine, VisualDevelopmentPlan
from atlas_animation_studio.storyboard_engine import StoryboardEngine, StoryboardSequence
from .design_sheets import CharacterSheet, DesignSheetEngine, EnvironmentSheet, PropSheet
from .manifest import ProductionAsset, ProductionManifest, ProductionScene, ProductionStatus
from .shot_planning import SceneTimingPlan, ShotPlanningEngine


@dataclass(frozen=True)
class CreativeProductionRequest:
    project: str
    idea: str
    emotion: str
    visual_subject: str
    visual_purpose: str
    beat_goals: List[str]
    scene_number: int = 1
    character_name: str = "PROTAGONIST"
    character_role: str = "emotional center"
    environment_name: str = "Primary Environment"
    environment_function: str = "stage the scene conflict"
    prop_name: str = "Key Prop"
    prop_function: str = "carry story information"
    fps: int = 24
    seconds_per_beat: float = 3.0


@dataclass
class CreativeProductionPackage:
    request: CreativeProductionRequest
    screenplay: MiniScreenplayPlan
    visual_development: VisualDevelopmentPlan
    storyboard: StoryboardSequence
    character_sheet: CharacterSheet
    environment_sheet: EnvironmentSheet
    prop_sheet: PropSheet
    timing: SceneTimingPlan
    manifest: ProductionManifest

    @property
    def has_creative_intelligence(self) -> bool:
        contexts = (
            self.screenplay.creative_context,
            self.visual_development.creative_context,
            self.storyboard.creative_context,
            self.character_sheet.creative_context,
            self.environment_sheet.creative_context,
            self.prop_sheet.creative_context,
        )
        return all(bool(context) for context in contexts)

    def to_markdown(self) -> str:
        summary = self.manifest.summary()
        manifest_text = "\n".join([
            "# Production Manifest",
            f"- Assets: {summary['asset_count']}",
            f"- Scenes: {summary['scene_count']}",
            f"- Total Frames: {summary['total_frames']}",
            f"- Total Seconds: {summary['total_seconds']}",
            f"- Ready: {summary['ready_for_production']}",
        ])
        return "\n\n---\n\n".join([
            f"# ATLAS Creative Production Package — {self.request.project}",
            self.screenplay.to_markdown(),
            self.visual_development.to_markdown(),
            self.storyboard.to_markdown(),
            manifest_text,
        ])


class CreativeProductionOrchestrator:
    """Generates and registers one coherent creative production package."""

    def __init__(self, *, creative_bridge=None) -> None:
        self.creative_bridge = creative_bridge
        self.screenplay_engine = MiniScreenplayEngine(creative_bridge=creative_bridge)
        self.visual_engine = VisualDevelopmentEngine(creative_bridge=creative_bridge)
        self.storyboard_engine = StoryboardEngine(creative_bridge=creative_bridge)
        self.design_sheet_engine = DesignSheetEngine(creative_bridge=creative_bridge)

    def produce(self, request: CreativeProductionRequest) -> CreativeProductionPackage:
        screenplay = self.screenplay_engine.build_plan(request.project, request.idea, request.emotion)
        visual_development = self.visual_engine.build_plan(
            project=request.project, subject=request.visual_subject, purpose=request.visual_purpose
        )
        storyboard = self.storyboard_engine.build_sequence(
            request.project, request.scene_number, request.beat_goals
        )
        character_sheet = self.design_sheet_engine.character(
            project=request.project, name=request.character_name, role=request.character_role
        )
        environment_sheet = self.design_sheet_engine.environment(
            project=request.project, name=request.environment_name, story_function=request.environment_function
        )
        prop_sheet = self.design_sheet_engine.prop(
            project=request.project, name=request.prop_name, story_function=request.prop_function
        )
        timing = ShotPlanningEngine(self.creative_bridge, fps=request.fps).plan_scene(
            project=request.project,
            scene_number=request.scene_number,
            beat_goals=request.beat_goals,
            seconds_per_beat=request.seconds_per_beat,
        )

        manifest = ProductionManifest(
            project=request.project,
            screenplay_status=ProductionStatus.APPROVED,
            visual_development_status=ProductionStatus.APPROVED,
            storyboard_status=ProductionStatus.APPROVED,
        )
        character_id = f"character-{request.character_name.lower().replace(' ', '-')}"
        environment_id = f"environment-{request.environment_name.lower().replace(' ', '-')}"
        prop_id = f"prop-{request.prop_name.lower().replace(' ', '-')}"
        manifest.add_asset(ProductionAsset(character_id, request.character_name, "character", ProductionStatus.APPROVED))
        manifest.add_asset(ProductionAsset(environment_id, request.environment_name, "environment", ProductionStatus.APPROVED))
        manifest.add_asset(ProductionAsset(prop_id, request.prop_name, "prop", ProductionStatus.APPROVED))
        manifest.add_scene(ProductionScene(
            scene_number=request.scene_number,
            status=ProductionStatus.PLANNED,
            character_assets=[character_id],
            environment_assets=[environment_id],
            prop_assets=[prop_id],
            shot_count=len(timing.shots),
            total_frames=timing.total_frames,
            total_seconds=timing.total_seconds,
        ))

        return CreativeProductionPackage(
            request=request,
            screenplay=screenplay,
            visual_development=visual_development,
            storyboard=storyboard,
            character_sheet=character_sheet,
            environment_sheet=environment_sheet,
            prop_sheet=prop_sheet,
            timing=timing,
            manifest=manifest,
        )
