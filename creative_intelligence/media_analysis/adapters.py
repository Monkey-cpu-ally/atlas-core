"""Adapters that normalize external image/video analysis into ATLAS observations.

These adapters do not bundle a vision model. They define the contract that any
approved vision provider, local model, or frame-analysis service must satisfy.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable, Mapping, Protocol

from .schemas import StoryObservation, VisualObservation


class VisionProvider(Protocol):
    def analyze_image(self, image_ref: str, instructions: str) -> Mapping[str, Any]: ...


class VideoProvider(Protocol):
    def sample_frames(self, video_ref: str, *, max_frames: int = 12) -> Iterable[str]: ...


@dataclass(frozen=True)
class MediaInput:
    source_name: str
    media_ref: str
    source_type: str
    context: str = ""
    allowed_for_study: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)


class ObservationAdapter:
    VISUAL_INSTRUCTIONS = (
        "Analyze craft characteristics, not creator identity. Return concise observations for: "
        "subject, silhouette, shape_language, proportion, line, color, value, lighting, "
        "materials, composition, perspective, costume, movement, notes."
    )

    def __init__(self, vision_provider: VisionProvider) -> None:
        self.vision_provider = vision_provider

    def from_image(self, media: MediaInput) -> VisualObservation:
        if not media.allowed_for_study:
            raise PermissionError("media is not approved for ATLAS study")
        raw = self.vision_provider.analyze_image(
            media.media_ref,
            f"{self.VISUAL_INSTRUCTIONS}\nContext: {media.context}",
        )
        return self._visual_from_mapping(raw, fallback_subject=media.source_name)

    @staticmethod
    def _items(raw: Mapping[str, Any], key: str) -> list[str]:
        value = raw.get(key, [])
        if value is None:
            return []
        if isinstance(value, str):
            return [value]
        if isinstance(value, Iterable):
            return [str(item) for item in value if str(item).strip()]
        return [str(value)]

    @classmethod
    def _visual_from_mapping(
        cls, raw: Mapping[str, Any], *, fallback_subject: str
    ) -> VisualObservation:
        return VisualObservation(
            subject=str(raw.get("subject") or fallback_subject),
            silhouette=cls._items(raw, "silhouette"),
            shape_language=cls._items(raw, "shape_language"),
            proportion=cls._items(raw, "proportion"),
            line=cls._items(raw, "line"),
            color=cls._items(raw, "color"),
            value=cls._items(raw, "value"),
            lighting=cls._items(raw, "lighting"),
            materials=cls._items(raw, "materials"),
            composition=cls._items(raw, "composition"),
            perspective=cls._items(raw, "perspective"),
            costume=cls._items(raw, "costume"),
            movement=cls._items(raw, "movement"),
            notes=cls._items(raw, "notes"),
        )


class VideoObservationAdapter:
    """Samples frames and merges recurring visual observations from a clip."""

    def __init__(self, video_provider: VideoProvider, image_adapter: ObservationAdapter) -> None:
        self.video_provider = video_provider
        self.image_adapter = image_adapter

    def from_video(self, media: MediaInput, *, max_frames: int = 12) -> VisualObservation:
        if not media.allowed_for_study:
            raise PermissionError("media is not approved for ATLAS study")

        frames = list(self.video_provider.sample_frames(media.media_ref, max_frames=max_frames))
        if not frames:
            raise ValueError("video provider returned no frames")

        observations = [
            self.image_adapter.from_image(
                MediaInput(
                    source_name=f"{media.source_name} frame {index + 1}",
                    media_ref=frame,
                    source_type="frame",
                    context=media.context,
                    allowed_for_study=True,
                    metadata={"parent": media.source_name, "frame_index": index},
                )
            )
            for index, frame in enumerate(frames)
        ]
        return self._merge_visual(media.source_name, observations)

    @staticmethod
    def _merge_visual(subject: str, observations: list[VisualObservation]) -> VisualObservation:
        def merge(attribute: str) -> list[str]:
            seen: set[str] = set()
            output: list[str] = []
            for observation in observations:
                for item in getattr(observation, attribute):
                    normalized = item.strip().casefold()
                    if normalized and normalized not in seen:
                        seen.add(normalized)
                        output.append(item)
            return output

        return VisualObservation(
            subject=subject,
            silhouette=merge("silhouette"),
            shape_language=merge("shape_language"),
            proportion=merge("proportion"),
            line=merge("line"),
            color=merge("color"),
            value=merge("value"),
            lighting=merge("lighting"),
            materials=merge("materials"),
            composition=merge("composition"),
            perspective=merge("perspective"),
            costume=merge("costume"),
            movement=merge("movement"),
            notes=merge("notes"),
        )


class StoryObservationAdapter:
    """Normalizes externally generated scene/story notes into StoryObservation."""

    @staticmethod
    def from_mapping(raw: Mapping[str, Any], *, title: str) -> StoryObservation:
        items = ObservationAdapter._items
        return StoryObservation(
            title=title,
            premise=str(raw.get("premise") or ""),
            character_goals=items(raw, "character_goals"),
            conflicts=items(raw, "conflicts"),
            reveals=items(raw, "reveals"),
            pacing_notes=items(raw, "pacing_notes"),
            visual_storytelling=items(raw, "visual_storytelling"),
            themes=items(raw, "themes"),
            scene_changes=items(raw, "scene_changes"),
        )
