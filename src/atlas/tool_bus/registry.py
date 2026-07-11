"""Default Tool Bus registry for ATLAS."""

from __future__ import annotations

from .adapters.blender import BlenderAdapter
from .adapters.cadquery import CadQueryAdapter
from .adapters.isaac_sim import IsaacSimAdapter
from .adapters.kicad import KiCadAdapter
from .adapters.neo4j import Neo4jAdapter
from .adapters.ollama import OllamaAdapter
from .adapters.opencv import OpenCVAdapter
from .adapters.ros2 import ROS2Adapter
from .bus import ToolBus


def create_default_tool_bus() -> ToolBus:
    """Create the default Tool Bus.

    OpenCV, CadQuery, and KiCad adapters perform local availability checks.
    Other adapters remain disabled scaffolds until their runtimes are configured.
    """
    bus = ToolBus()
    bus.register(BlenderAdapter())
    bus.register(Neo4jAdapter())
    bus.register(OllamaAdapter())
    bus.register(OpenCVAdapter())
    bus.register(CadQueryAdapter())
    bus.register(KiCadAdapter())
    bus.register(ROS2Adapter())
    bus.register(IsaacSimAdapter())
    return bus
