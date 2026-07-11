"""Contract tests for ATLAS engineering tool adapters."""
from src.atlas.tool_bus.adapters.cadquery import CadQueryAdapter
from src.atlas.tool_bus.adapters.kicad import KiCadAdapter
from src.atlas.tool_bus.adapters.opencv import OpenCVAdapter
from src.atlas.tool_bus.registry import create_default_tool_bus


def _capability_names(adapter):
    return {capability.name for capability in adapter.get_capabilities()}


def test_opencv_adapter_contract():
    adapter = OpenCVAdapter()
    assert adapter.name == "opencv"
    assert "inspect_image" in _capability_names(adapter)
    assert isinstance(adapter.verify(), bool)


def test_cadquery_adapter_contract():
    adapter = CadQueryAdapter()
    assert adapter.name == "cadquery"
    assert "generate_box" in _capability_names(adapter)
    assert isinstance(adapter.verify(), bool)


def test_kicad_adapter_contract():
    adapter = KiCadAdapter()
    assert adapter.name == "kicad"
    assert {"version", "validate_schematic", "validate_pcb"}.issubset(_capability_names(adapter))
    assert isinstance(adapter.verify(), bool)


def test_registry_contains_engineering_adapters():
    bus = create_default_tool_bus()
    statuses = bus.get_status()
    names = set(statuses.get("tools", {}).keys()) if isinstance(statuses, dict) else set()
    if not names:
        names = {adapter.name for adapter in getattr(bus, "_adapters", {}).values()}
    assert {"opencv", "cadquery", "kicad"}.issubset(names)
