"""Isaac Sim adapter scaffold for ATLAS Tool Bus."""

from __future__ import annotations

from ..contracts import ToolCapability, ToolSafetyLevel
from .base import PlaceholderToolAdapter


class IsaacSimAdapter(PlaceholderToolAdapter):
    """Placeholder adapter for future robotics simulation workflows."""

    def __init__(self) -> None:
        super().__init__(
            name="isaac_sim",
            capabilities=[
                ToolCapability(
                    name="create_simulation_plan",
                    description="Create a robotics simulation plan for later Isaac Sim execution.",
                    safety_level=ToolSafetyLevel.GENERATE_ONLY,
                    enabled_by_default=False,
                ),
                ToolCapability(
                    name="run_simulation",
                    description="Run a simulation when a local Isaac Sim runner is configured.",
                    safety_level=ToolSafetyLevel.SIMULATION_ONLY,
                    enabled_by_default=False,
                ),
            ],
        )
