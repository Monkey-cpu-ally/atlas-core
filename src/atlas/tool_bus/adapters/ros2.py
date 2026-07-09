"""ROS 2 adapter scaffold for ATLAS Tool Bus."""

from __future__ import annotations

from ..contracts import ToolCapability, ToolSafetyLevel
from .base import PlaceholderToolAdapter


class ROS2Adapter(PlaceholderToolAdapter):
    """Placeholder adapter for future robotics workflows."""

    def __init__(self) -> None:
        super().__init__(
            name="ros2",
            capabilities=[
                ToolCapability(
                    name="generate_robot_node_plan",
                    description="Create a ROS 2 node/package plan for a robot subsystem.",
                    safety_level=ToolSafetyLevel.GENERATE_ONLY,
                    enabled_by_default=False,
                ),
                ToolCapability(
                    name="inspect_workspace",
                    description="Inspect a ROS 2 workspace when a local runner is configured.",
                    safety_level=ToolSafetyLevel.READ_ONLY,
                    enabled_by_default=False,
                ),
            ],
        )
