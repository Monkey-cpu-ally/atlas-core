"""End-to-end ATLAS creative production orchestration."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import List, Optional

from story_foundry.mini_screenplay_engine import MiniScreenplayEngine, MiniScreenplayPlan
from academy.school_of_visual_development.visual_development_engine import VisualDevelopmentEngine, VisualDevelopmentPlan
from atlas_animation_studio.storyboard_engine import StoryboardEngine, StoryboardSequence
from .continuity import ContinuityEngine, ContinuityIssue, ContinuityState
from .design_sheets import CharacterSheet, DesignSheetEngine, EnvironmentSheet, PropSheet
from .manifest import ProductionAsset, ProductionManifest, ProductionScene, ProductionStatus
from .project_store import CreativeProjectStore, ProjectRevision
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
    continuity_state: Optional[ContinuityState] = None
    continuity_issues: List[ContinuityIssue] = None

    def __post_init__(self) -> None:
        if self.continuity_issues is None:
            self.continuity_issues = []

    @property
    def has_creative_intelligence(self) -> bool:
        return all(bool(context) for context in (
            self.screenplay.creative_context, self.visual_development.creative_context,
            self.storyboard.creative_context, self.character_sheet.creative_context,
            self.environment_sheet.creative_context, self.prop_sheet.creative_context,
        ))

    def snapshot(self) -> dict:
        return {
            "request": asdict(self.request),
            "character_sheet": asdict(self.character_sheet),
            "environment_sheet": asdict(self.environment_sheet),
            "prop_sheet": asdict(self.prop_sheet),
            "timing": {"scene_number": self.timing.scene_number, "total_frames": self.timing.total_frames,
                       "total_seconds": self.timing.total_seconds, "shots": [asdict(s) for s in self.timing.shots]},
            "continuity_state": asdict(self.continuity_state) if self.continuity_state else None,
            "continuity_issues": [asdict(issue) for issue in self.continuity_issues],
            "manifest": self.manifest.summary(),
            "screenplay_markdown": self.screenplay.to_markdown(),
            "visual_development_markdown": self.visual_development.to_markdown(),
            "storyboard_markdown": self.storyboard.to_markdown(),
        }

    def to_markdown(self) -> str:
        summary = self.manifest.summary()
        manifest_text = "\n".join([
            "# Production Manifest", f"- Assets: {summary['asset_count']}", f"- Scenes: {summary['scene_count']}",
            f"- Total Frames: {summary['total_frames']}", f"- Total Seconds: {summary['total_seconds']}",
            f"- Ready: {summary['ready_for_production']}",
        ])
        return "\n\n---\n\n".join([
            f"# ATLAS Creative Production Package — {self.request.project}", self.screenplay.to_markdown(),
            self.visual_development.to_markdown(), self.storyboard.to_markdown(), manifest_text,
        ])


class CreativeProductionOrchestrator:
    """Generates, validates, continuity-checks, and versions a creative production package."""

    def __init__(self, *, creative_bridge=None, project_store: CreativeProjectStore | None = None) -> None:
        self.creative_bridge = creative_bridge
        self.project_store = project_store
        self.continuity_engine = ContinuityEngine()
        self.screenplay_engine = MiniScreenplayEngine(creative_bridge=creative_bridge)
        self.visual_engine = VisualDevelopmentEngine(creative_bridge=creative_bridge)
        self.storyboard_engine = StoryboardEngine(creative_bridge=creative_bridge)
        self.design_sheet_engine = DesignSheetEngine(creative_bridge=creative_bridge)

    @staticmethod
    def _issue_id(issue: ContinuityIssue) -> str:
        return f"{issue.category}:{issue.subject}:{issue.previous_scene}-{issue.current_scene}"

    def produce_and_save(self, request: CreativeProductionRequest, *, message: str = "creative production revision", continuity_state: ContinuityState | None = None) -> tuple[CreativeProductionPackage, ProjectRevision]:
        if self.project_store is None:
            raise RuntimeError("project_store is required for produce_and_save")
        package = self.produce(request, continuity_state=continuity_state)
        previous = self.project_store.latest(request.project)
        if previous is not None and continuity_state is not None:
            issues = self.continuity_engine.compare_revisions(previous.payload, {"continuity_state": asdict(continuity_state)})
            package.continuity_issues.extend(issues)
            scene = package.manifest.scenes[request.scene_number]
            scene.continuity_issue_ids.extend(self._issue_id(issue) for issue in issues)
        revision = self.project_store.save_revision(project=request.project, payload=package.snapshot(), message=message)
        return package, revision

    def produce(self, request: CreativeProductionRequest, *, continuity_state: ContinuityState | None = None) -> CreativeProductionPackage:
        screenplay = self.screenplay_engine.build_plan(request.project, request.idea, request.emotion)
        visual_development = self.visual_engine.build_plan(project=request.project, subject=request.visual_subject, purpose=request.visual_purpose)
        storyboard = self.storyboard_engine.build_sequence(request.project, request.scene_number, request.beat_goals)
        character_sheet = self.design_sheet_engine.character(project=request.project, name=request.character_name, role=request.character_role)
        environment_sheet = self.design_sheet_engine.environment(project=request.project, name=request.environment_name, story_function=request.environment_function)
        prop_sheet = self.design_sheet_engine.prop(project=request.project, name=request.prop_name, story_function=request.prop_function)
        timing = ShotPlanningEngine(self.creative_bridge, fps=request.fps).plan_scene(
            project=request.project, scene_number=request.scene_number, beat_goals=request.beat_goals,
            seconds_per_beat=request.seconds_per_beat,
        )
        manifest = ProductionManifest(
            project=request.project, screenplay_status=ProductionStatus.APPROVED,
            visual_development_status=ProductionStatus.APPROVED, storyboard_status=ProductionStatus.APPROVED,
        )
        character_id = f"character-{request.character_name.lower().replace(' ', '-')}"
        environment_id = f"environment-{request.environment_name.lower().replace(' ', '-')}"
        prop_id = f"prop-{request.prop_name.lower().replace(' ', '-')}"
        manifest.add_asset(ProductionAsset(character_id, request.character_name, "character", ProductionStatus.APPROVED))
        manifest.add_asset(ProductionAsset(environment_id, request.environment_name, "environment", ProductionStatus.APPROVED))
        manifest.add_asset(ProductionAsset(prop_id, request.prop_name, "prop", ProductionStatus.APPROVED))
        manifest.add_scene(ProductionScene(
            scene_number=request.scene_number, status=ProductionStatus.PLANNED, character_assets=[character_id],
            environment_assets=[environment_id], prop_assets=[prop_id], shot_count=len(timing.shots),
            total_frames=timing.total_frames, total_seconds=timing.total_seconds,
        ))
        return CreativeProductionPackage(
            request=request, screenplay=screenplay, visual_development=visual_development, storyboard=storyboard,
            character_sheet=character_sheet, environment_sheet=environment_sheet, prop_sheet=prop_sheet,
            timing=timing, manifest=manifest, continuity_state=continuity_state,
        )
