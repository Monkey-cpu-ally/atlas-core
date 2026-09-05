"""Runtime registry for explicitly configured Art Study vision providers."""
from __future__ import annotations

from creative_intelligence.vision_provider import VisionProvider

_provider: VisionProvider | None = None


def register(provider: VisionProvider) -> None:
    global _provider
    if not isinstance(provider, VisionProvider):
        raise ValueError("provider must implement VisionProvider")
    _provider = provider


def clear() -> None:
    global _provider
    _provider = None


def get() -> VisionProvider | None:
    return _provider


def contract() -> dict:
    return {
        "configured": _provider is not None,
        "fail_closed_when_unconfigured": True,
        "provider_id": _provider.provider_id if _provider is not None else None,
    }
