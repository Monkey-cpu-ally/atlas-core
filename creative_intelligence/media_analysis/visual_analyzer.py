from __future__ import annotations

from typing import Iterable

from .schemas import VisualObservation


class VisualCraftAnalyzer:
    """Builds structured visual observations from supplied frame/art notes.

    A future vision adapter can populate these fields directly from images.
    This class keeps the craft vocabulary and normalization logic stable.
    """

    def analyze(
        self,
        *,
        subject: str,
        silhouette: Iterable[str] = (),
        shape_language: Iterable[str] = (),
        proportion: Iterable[str] = (),
        line: Iterable[str] = (),
        color: Iterable[str] = (),
        value: Iterable[str] = (),
        lighting: Iterable[str] = (),
        materials: Iterable[str] = (),
        composition: Iterable[str] = (),
        perspective: Iterable[str] = (),
        costume: Iterable[str] = (),
        movement: Iterable[str] = (),
        notes: Iterable[str] = (),
    ) -> VisualObservation:
        return VisualObservation(
            subject=subject,
            silhouette=self._clean(silhouette),
            shape_language=self._clean(shape_language),
            proportion=self._clean(proportion),
            line=self._clean(line),
            color=self._clean(color),
            value=self._clean(value),
            lighting=self._clean(lighting),
            materials=self._clean(materials),
            composition=self._clean(composition),
            perspective=self._clean(perspective),
            costume=self._clean(costume),
            movement=self._clean(movement),
            notes=self._clean(notes),
        )

    def principle_candidates(self, observation: VisualObservation) -> list[str]:
        candidates: list[str] = []
        if observation.silhouette:
            candidates.append("Silhouette carries identity before surface detail.")
        if observation.shape_language:
            candidates.append("Repeated shape language creates visual cohesion.")
        if observation.color and observation.value:
            candidates.append("Color works best when value structure remains readable.")
        if observation.lighting:
            candidates.append("Lighting should direct attention and reinforce emotion.")
        if observation.materials:
            candidates.append("Material choices should support function, age, and world history.")
        if observation.movement:
            candidates.append("Motion should reveal weight, intention, and character.")
        if observation.composition:
            candidates.append("Composition should control what the audience notices first.")
        return candidates

    @staticmethod
    def _clean(values: Iterable[str]) -> list[str]:
        return [value.strip() for value in values if value and value.strip()]
