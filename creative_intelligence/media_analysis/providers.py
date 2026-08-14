"""Live-provider implementations for ATLAS reference-media analysis.

The provider is deliberately dependency-light: callers inject a callable that
accepts an analysis request and returns a mapping. This lets ATLAS use an
OpenAI-compatible vision service, a local multimodal model, or another approved
backend without coupling the creative library to one vendor SDK.
"""

from __future__ import annotations

import base64
import mimetypes
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Mapping


VISION_FIELDS = (
    "silhouette", "shape_language", "proportion", "line", "color", "value",
    "lighting", "materials", "composition", "perspective", "costume", "movement", "notes",
)


@dataclass(frozen=True)
class VisionRequest:
    source_name: str
    mime_type: str
    data_url: str
    instruction: str


class CallableVisionProvider:
    """Adapter around a live multimodal callable.

    ``analyze_call`` receives a VisionRequest and must return a mapping whose
    values for VISION_FIELDS are strings or lists of strings. The optional
    ``instructions`` argument keeps this provider compatible with the
    ``VisionProvider`` protocol used by ``ObservationAdapter``.
    """

    def __init__(self, analyze_call: Callable[[VisionRequest], Mapping[str, Any]]) -> None:
        self._analyze_call = analyze_call

    def analyze_image(self, image_path: str, instructions: str = "") -> Mapping[str, Any]:
        path = Path(image_path)
        if not path.is_file():
            raise FileNotFoundError(path)
        mime_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        encoded = base64.b64encode(path.read_bytes()).decode("ascii")
        base_instruction = (
            "Analyze observable visual craft only. Return concise observations for "
            "silhouette, shape_language, proportion, line, color, value, lighting, "
            "materials, composition, perspective, costume, movement, and notes. "
            "Describe techniques and visual properties; do not instruct imitation "
            "of a creator's distinctive style."
        )
        request = VisionRequest(
            source_name=path.name,
            mime_type=mime_type,
            data_url=f"data:{mime_type};base64,{encoded}",
            instruction=f"{base_instruction}\n{instructions}".strip(),
        )
        raw = self._analyze_call(request)
        return self._normalize(raw)

    @staticmethod
    def _normalize(raw: Mapping[str, Any]) -> dict[str, list[str]]:
        normalized: dict[str, list[str]] = {}
        for field in VISION_FIELDS:
            value = raw.get(field, [])
            if isinstance(value, str):
                value = [value]
            elif not isinstance(value, (list, tuple)):
                value = [str(value)] if value else []
            normalized[field] = [str(item).strip() for item in value if str(item).strip()]
        return normalized
