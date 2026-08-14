from __future__ import annotations

from typing import Iterable

from .schemas import StoryObservation


class StoryStructureAnalyzer:
    """Normalizes scene/story observations into reusable storycraft signals."""

    def analyze(
        self,
        *,
        title: str,
        premise: str,
        character_goals: Iterable[str] = (),
        conflicts: Iterable[str] = (),
        reveals: Iterable[str] = (),
        pacing_notes: Iterable[str] = (),
        visual_storytelling: Iterable[str] = (),
        themes: Iterable[str] = (),
        scene_changes: Iterable[str] = (),
    ) -> StoryObservation:
        return StoryObservation(
            title=title,
            premise=premise.strip(),
            character_goals=self._clean(character_goals),
            conflicts=self._clean(conflicts),
            reveals=self._clean(reveals),
            pacing_notes=self._clean(pacing_notes),
            visual_storytelling=self._clean(visual_storytelling),
            themes=self._clean(themes),
            scene_changes=self._clean(scene_changes),
        )

    def principle_candidates(self, observation: StoryObservation) -> list[str]:
        principles: list[str] = []
        if observation.character_goals and observation.conflicts:
            principles.append("Conflict becomes meaningful when it blocks a specific character goal.")
        if observation.reveals:
            principles.append("A reveal is stronger when earlier information gains new meaning afterward.")
        if observation.pacing_notes:
            principles.append("Pacing should control pressure, recovery, and anticipation rather than remain constant.")
        if observation.visual_storytelling:
            principles.append("Visual information can carry story before dialogue explains it.")
        if observation.scene_changes:
            principles.append("Every scene should change knowledge, emotion, power, risk, or direction.")
        return principles

    @staticmethod
    def _clean(values: Iterable[str]) -> list[str]:
        return [value.strip() for value in values if value and value.strip()]
