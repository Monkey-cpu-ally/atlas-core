"""FFmpeg implementation for ATLAS video-frame extraction."""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import Sequence


def extract_frames_ffmpeg(video_path: str, timestamps: Sequence[float], output_dir: str) -> list[str]:
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise RuntimeError("ffmpeg is required for video reference analysis")
    source = Path(video_path)
    if not source.is_file():
        raise FileNotFoundError(video_path)
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    results: list[str] = []
    for index, timestamp in enumerate(timestamps):
        target = destination / f"frame_{index:04d}_{timestamp:.3f}.jpg"
        command = [
            ffmpeg, "-hide_banner", "-loglevel", "error", "-y",
            "-ss", f"{timestamp:.3f}", "-i", str(source),
            "-frames:v", "1", "-q:v", "2", str(target),
        ]
        completed = subprocess.run(command, capture_output=True, text=True, timeout=60)
        if completed.returncode != 0 or not target.is_file():
            raise RuntimeError(f"ffmpeg frame extraction failed at {timestamp:.3f}s: {completed.stderr.strip()}")
        results.append(str(target))
    return results
