"""Reference ingestion entry points for ATLAS Creative Intelligence."""
from __future__ import annotations

import tempfile
from dataclasses import dataclass

from creative_intelligence.creative_memory import CreativeMemory
from .adapters import ObservationAdapter
from .ffmpeg_extractor import extract_frames_ffmpeg
from .memory_bridge import MediaStudyMemoryBridge
from .pipeline import ReferenceMediaAnalyzer
from .providers import CallableVisionProvider
from .study_service import CreativeReferenceStudyService, StudyResult
from .video_sampler import VideoFrameSampler


@dataclass
class ImageStudyResult:
    source_name: str
    report_markdown: str
    learned_lessons: int


class ReferenceIngestionService:
    """Study approved local media and persist reusable craft principles."""

    def __init__(self, vision_provider: CallableVisionProvider, memory: CreativeMemory) -> None:
        self.vision_provider = vision_provider
        self.memory = memory
        self.analyzer = ReferenceMediaAnalyzer()
        self.memory_bridge = MediaStudyMemoryBridge(memory)

    def study_image(self, *, project: str, source_name: str, image_path: str) -> ImageStudyResult:
        raw = self.vision_provider.analyze_image(image_path)
        visual = ObservationAdapter._visual_from_mapping(raw, fallback_subject=source_name)
        report = self.analyzer.build_report(
            source_name=source_name,
            source_type="image",
            visual=visual,
        )
        lessons = self.memory_bridge.remember_report(
            project=project,
            task=f"reference image study: {source_name}",
            report=report,
        )
        return ImageStudyResult(source_name, report.to_markdown(), len(lessons))

    def study_video(
        self,
        *,
        project: str,
        source_name: str,
        video_path: str,
        duration_seconds: float,
        frame_count: int = 12,
    ) -> StudyResult:
        sampler = VideoFrameSampler(extract_frames_ffmpeg)
        with tempfile.TemporaryDirectory(prefix="atlas-reference-frames-") as output_dir:
            frames = sampler.sample(
                video_path,
                duration_seconds,
                output_dir,
                count=frame_count,
            )
            return CreativeReferenceStudyService(self.vision_provider, self.memory).study_frames(
                project=project,
                source_name=source_name,
                frames=frames,
            )
