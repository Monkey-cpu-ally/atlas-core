"""Runtime wiring for ATLAS Creative Intelligence media analysis.

This module turns environment settings into concrete provider and memory
implementations without coupling the creative pipeline to a vendor SDK.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any, Callable, Mapping
from urllib.request import Request, urlopen

from creative_intelligence.creative_memory import CreativeMemory
from creative_intelligence.creative_memory_sqlite import SQLiteCreativeMemory
from .config import MediaAnalysisSettings
from .providers import CallableVisionProvider, VisionRequest


OpenURL = Callable[[Request, float], Any]


@dataclass
class HTTPJSONVisionTransport:
    """Send a normalized vision request to an approved JSON HTTP endpoint.

    Expected response is either the visual-analysis mapping itself or
    ``{"analysis": {...}}``. The endpoint contract is intentionally vendor
    neutral so ATLAS can use a local service or approved cloud gateway.
    """

    api_base: str
    model: str = ""
    api_key: str = ""
    timeout_seconds: float = 60.0
    opener: OpenURL | None = None

    def __call__(self, request: VisionRequest) -> Mapping[str, Any]:
        if not self.api_base:
            raise ValueError("ATLAS_VISION_API_BASE is required for http-json provider")
        payload = {
            "model": self.model,
            "instruction": request.instruction,
            "image": {
                "source_name": request.source_name,
                "mime_type": request.mime_type,
                "data_url": request.data_url,
            },
        }
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        http_request = Request(
            self.api_base,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST",
        )
        opener = self.opener or (lambda req, timeout: urlopen(req, timeout=timeout))
        with opener(http_request, self.timeout_seconds) as response:
            decoded = json.loads(response.read().decode("utf-8"))
        analysis = decoded.get("analysis", decoded) if isinstance(decoded, dict) else None
        if not isinstance(analysis, dict):
            raise ValueError("vision endpoint must return a JSON object")
        return analysis


def build_memory(settings: MediaAnalysisSettings):
    settings.validate()
    if settings.creative_memory_backend == "memory":
        return CreativeMemory()
    return SQLiteCreativeMemory(settings.creative_memory_path)


def build_vision_provider(
    settings: MediaAnalysisSettings,
    *,
    callable_backend: Callable[[VisionRequest], Mapping[str, Any]] | None = None,
) -> CallableVisionProvider:
    settings.validate()
    provider = settings.provider.casefold()
    if provider == "callable":
        if callable_backend is None:
            raise ValueError("callable vision provider requires callable_backend")
        return CallableVisionProvider(callable_backend)
    if provider == "http-json":
        api_key = os.getenv(settings.api_key_env, "") if settings.api_key_env else ""
        return CallableVisionProvider(
            HTTPJSONVisionTransport(
                api_base=settings.api_base,
                model=settings.model,
                api_key=api_key,
            )
        )
    raise ValueError(f"unsupported ATLAS_VISION_PROVIDER: {settings.provider}")
