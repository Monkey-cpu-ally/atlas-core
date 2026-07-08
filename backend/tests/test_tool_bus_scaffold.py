"""Tests for the ATLAS Tool Bus scaffold."""

from __future__ import annotations

import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from atlas.tool_bus import ToolJob, ToolJobStatus, ToolSafetyLevel, create_default_tool_bus
from atlas.tool_bus.adapters.blender import BlenderAdapter
from atlas.tool_bus.bus import ToolBus, ToolBusError


def test_default_tool_bus_registers_expected_scaffold_adapters() -> None:
    bus = create_default_tool_bus()

    assert bus.list_tools() == [
        "blender",
        "isaac_sim",
        "kicad",
        "neo4j",
        "ollama",
        "ros2",
    ]


def test_placeholder_adapter_reports_scaffold_only_status() -> None:
    adapter = BlenderAdapter()
    adapter.initialize()

    status = adapter.get_status()

    assert status["name"] == "blender"
    assert status["initialized"] is True
    assert status["connected"] is False
    assert status["enabled"] is False
    assert "generate_scene_script" in status["capabilities"]


def test_tool_bus_skips_placeholder_execution_safely() -> None:
    bus = create_default_tool_bus()
    job = ToolJob(
        tool_name="blender",
        capability="generate_scene_script",
        payload={"prompt": "Create a simple concept scene."},
        requested_by="hermes",
        safety_level=ToolSafetyLevel.GENERATE_ONLY,
    )

    result = bus.execute(job)

    assert result.success is False
    assert result.status == ToolJobStatus.FAILED
    assert result.tool_name == "blender"
    assert result.errors


def test_tool_bus_rejects_unknown_tool() -> None:
    bus = ToolBus()

    try:
        bus.get_adapter("unknown_tool")
    except ToolBusError as exc:
        assert "No adapter registered" in str(exc)
    else:
        raise AssertionError("Expected ToolBusError for unknown adapter")
