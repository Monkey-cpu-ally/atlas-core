"""KiCad adapter scaffold for ATLAS Tool Bus."""

from __future__ import annotations

from ..contracts import ToolCapability, ToolSafetyLevel
from .base import PlaceholderToolAdapter


class KiCadAdapter(PlaceholderToolAdapter):
    """Placeholder adapter for future electronics design workflows."""

    def __init__(self) -> None:
        super().__init__(
            name="kicad",
            capabilities=[
                ToolCapability(
                    name="create_pcb_project_plan",
                    description="Create a structured PCB project plan for later KiCad implementation.",
                    safety_level=ToolSafetyLevel.GENERATE_ONLY,
                    enabled_by_default=False,
                ),
                ToolCapability(
                    name="validate_pcb_files",
                    description="Validate KiCad project files when a local runner is configured.",
                    safety_level=ToolSafetyLevel.READ_ONLY,
                    enabled_by_default=False,
                ),
            ],
        )
