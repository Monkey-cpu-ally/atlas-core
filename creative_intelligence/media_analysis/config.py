"""Environment-driven configuration for ATLAS media analysis."""
from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class MediaAnalysisSettings:
    provider: str = "callable"
    model: str = ""
    api_base: str = ""
    api_key_env: str = ""
    creative_memory_backend: str = "sqlite"
    creative_memory_path: str = "data/creative_memory.sqlite3"
    video_frame_count: int = 12

    @classmethod
    def from_env(cls) -> "MediaAnalysisSettings":
        return cls(
            provider=os.getenv("ATLAS_VISION_PROVIDER", "callable").strip(),
            model=os.getenv("ATLAS_VISION_MODEL", "").strip(),
            api_base=os.getenv("ATLAS_VISION_API_BASE", "").strip(),
            api_key_env=os.getenv("ATLAS_VISION_API_KEY_ENV", "").strip(),
            creative_memory_backend=os.getenv("ATLAS_CREATIVE_MEMORY_BACKEND", "sqlite").strip(),
            creative_memory_path=os.getenv(
                "ATLAS_CREATIVE_MEMORY_PATH", "data/creative_memory.sqlite3"
            ).strip(),
            video_frame_count=int(os.getenv("ATLAS_VIDEO_FRAME_COUNT", "12")),
        )

    def validate(self) -> None:
        if self.video_frame_count < 1:
            raise ValueError("ATLAS_VIDEO_FRAME_COUNT must be at least 1")
        if self.creative_memory_backend not in {"sqlite", "memory"}:
            raise ValueError("ATLAS_CREATIVE_MEMORY_BACKEND must be 'sqlite' or 'memory'")
