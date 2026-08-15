"""Shot planning and animation timing for ATLAS Creative Production."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Protocol


class CreativeBriefProvider(Protocol):
    def build_brief(self, *, project: str, task: str): ...


@dataclass(frozen=True)
class ShotPlan:
    shot_number: int
    beat: str
    framing: str
    camera: str
    staging: str
    focal_priority: str
    transition: str
    duration_seconds: float
    fps: int
    frame_count: int
    key_poses: List[int]
    creative_context: str = ""


@dataclass
class SceneTimingPlan:
    project: str
    scene_number: int
    shots: List[ShotPlan]

    @property
    def total_seconds(self) -> float:
        return round(sum(shot.duration_seconds for shot in self.shots), 3)

    @property
    def total_frames(self) -> int:
        return sum(shot.frame_count for shot in self.shots)


class ShotPlanningEngine:
    def __init__(self, creative_bridge: CreativeBriefProvider | None = None, *, fps: int = 24) -> None:
        if fps <= 0:
            raise ValueError("fps must be positive")
        self.creative_bridge = creative_bridge
        self.fps = fps

    def _context(self, project: str, scene_number: int, beat: str) -> str:
        if self.creative_bridge is None:
            return ""
        return self.creative_bridge.build_brief(
            project=project,
            task=f"shot planning scene {scene_number}: {beat}",
        ).to_prompt_context()

    def plan_scene(self, *, project: str, scene_number: int, beat_goals: List[str], seconds_per_beat: float = 3.0) -> SceneTimingPlan:
        if seconds_per_beat <= 0:
            raise ValueError("seconds_per_beat must be positive")
        shots: List[ShotPlan] = []
        for index, beat in enumerate(beat_goals, start=1):
            frames = max(1, round(seconds_per_beat * self.fps))
            midpoint = max(1, frames // 2)
            shots.append(ShotPlan(
                shot_number=index,
                beat=beat,
                framing="Choose shot size from emotional distance and required information",
                camera="Move only when movement reveals, tracks, contrasts, or intensifies story information",
                staging="Keep action readable in silhouette and preserve screen direction",
                focal_priority="One dominant read per shot; secondary detail must support it",
                transition="Cut on completed information, changed emotion, or motivated movement",
                duration_seconds=seconds_per_beat,
                fps=self.fps,
                frame_count=frames,
                key_poses=[1, midpoint, frames],
                creative_context=self._context(project, scene_number, beat),
            ))
        return SceneTimingPlan(project=project, scene_number=scene_number, shots=shots)
