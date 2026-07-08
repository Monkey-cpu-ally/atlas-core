"""Ollama adapter scaffold for ATLAS Tool Bus."""

from __future__ import annotations

from ..contracts import ToolCapability, ToolSafetyLevel
from .base import PlaceholderToolAdapter


class OllamaAdapter(PlaceholderToolAdapter):
    """Placeholder adapter for future local model routing."""

    def __init__(self) -> None:
        super().__init__(
            name="ollama",
            capabilities=[
                ToolCapability(
                    name="list_models",
                    description="List locally available Ollama models when configured.",
                    safety_level=ToolSafetyLevel.READ_ONLY,
                    enabled_by_default=False,
                ),
                ToolCapability(
                    name="generate_response",
                    description="Route a safe local-model prompt through Ollama when configured.",
                    safety_level=ToolSafetyLevel.GENERATE_ONLY,
                    enabled_by_default=False,
                ),
            ],
        )
