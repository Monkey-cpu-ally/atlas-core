"""End-to-end orchestration for approved creative reference study."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from creative_intelligence.creative_memory import CreativeMemory
from .adapters import ObservationAdapter
from .memory_bridge import MediaStudyMemoryBridge
from .pipeline import ReferenceMediaAnalyzer
from .providers import CallableVisionProvider
from .video_sampler import SampledFrame


@dataclass
class StudyResult:
    source_name: str
    report_markdown: str
    learned_lessons: int


class CreativeReferenceStudyService:
    def __init__(self, vision_provider: CallableVisionProvider, memory: CreativeMemory) -> None:
        self.vision_provider = vision_provider
        self.memory = memory
        self.analyzer = ReferenceMediaAnalyzer()
        self.memory_bridge = MediaStudyMemoryBridge(memory)

    def study_frames(self, *, project: str, source_name: str, frames: Sequence[SampledFrame]) -> StudyResult:
        observations = []
        for frame in frames:
            raw = self.vision_provider.analyze_image(frame.image_path)
            obs = ObservationAdapter.visual_from_mapping(
                subject=f"{source_name} @ {frame.timestamp_seconds:.2f}s",
                payload=raw,
            )
            observations.append(obs)

        merged = ObservationAdapter.merge_visuals(source_name, observations)
        report = self.analyzer.study(source_name=source_name, source_type="video", visual=merged)
        lessons = self.memory_bridge.remember_report(project=project, report=report)
        return StudyResult(source_name, report.to_markdown(), len(lessons))
