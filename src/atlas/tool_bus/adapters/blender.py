"""Blender adapter scaffold for ATLAS Tool Bus."""

from __future__ import annotations

from ..contracts import ToolCapability, ToolSafetyLevel
from .base import PlaceholderToolAdapter


class BlenderAdapter(PlaceholderToolAdapter):
    """Placeholder adapter for future Blender automation."""

    def __init__(self) -> None:
        super().__init__(
            name="blender",
            capabilities=[
                ToolCapability(
                    name="generate_scene_script",
                    description="Create a Blender Python script from a structured ATLAS design request.",
                    safety_level=ToolSafetyLevel.GENERATE_ONLY,
                    enabled_by_default=False,
                ),
                ToolCapability(
                    name="render_scene",
                    description="Render a Blender scene when a local Blender runner is configured.",
                    safety_level=ToolSafetyLevel.WRITE_LOCAL,
                    enabled_by_default=False,
                ),
            ],
        )
