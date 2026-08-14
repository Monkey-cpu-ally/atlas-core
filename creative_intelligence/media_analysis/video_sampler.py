"""Video frame sampling primitives for ATLAS media study.

Frame extraction is injected so the core package does not hard-depend on
OpenCV/ffmpeg. A deployment can supply either implementation.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Sequence


@dataclass(frozen=True)
class SampledFrame:
    timestamp_seconds: float
    image_path: str


class VideoFrameSampler:
    def __init__(self, extractor: Callable[[str, Sequence[float], str], Sequence[str]]) -> None:
        self.extractor = extractor

    @staticmethod
    def uniform_timestamps(duration_seconds: float, count: int = 12) -> list[float]:
        if duration_seconds <= 0:
            raise ValueError("duration_seconds must be positive")
        if count < 1:
            raise ValueError("count must be at least 1")
        if count == 1:
            return [duration_seconds / 2]
        margin = duration_seconds * 0.02
        usable = max(0.0, duration_seconds - 2 * margin)
        return [margin + usable * i / (count - 1) for i in range(count)]

    def sample(self, video_path: str, duration_seconds: float, output_dir: str, count: int = 12) -> list[SampledFrame]:
        if not Path(video_path).is_file():
            raise FileNotFoundError(video_path)
        timestamps = self.uniform_timestamps(duration_seconds, count)
        paths = list(self.extractor(video_path, timestamps, output_dir))
        if len(paths) != len(timestamps):
            raise ValueError("extractor returned a different number of frames than requested")
        return [SampledFrame(ts, path) for ts, path in zip(timestamps, paths)]
