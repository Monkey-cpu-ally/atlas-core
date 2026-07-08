"""Default Tool Bus registry for ATLAS."""

from __future__ import annotations

from .adapters.blender import BlenderAdapter
from .adapters.isaac_sim import IsaacSimAdapter
from .adapters.kicad import KiCadAdapter
from .adapters.neo4j import Neo4jAdapter
from .adapters.ollama import OllamaAdapter
from .adapters.ros2 import ROS2Adapter
from .bus import ToolBus


def create_default_tool_bus() -> ToolBus:
    """Create a Tool Bus with scaffold adapters registered.

    The adapters are placeholders and are not live integrations.
    """
    bus = ToolBus()
    bus.register(BlenderAdapter())
    bus.register(Neo4jAdapter())
    bus.register(OllamaAdapter())
    bus.register(KiCadAdapter())
    bus.register(ROS2Adapter())
    bus.register(IsaacSimAdapter())
    return bus
