"""Integration tests for Tool Bus event flow."""

from __future__ import annotations

import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from atlas.tool_bus import SafetyPolicy, ToolEventType, ToolJob, ToolSafetyLevel, create_default_tool_bus


def test_denied_job_records_received_and_denied_events() -> None:
    bus = create_default_tool_bus()
    job = ToolJob(
        tool_name="blender",
        capability="generate_scene_script",
        payload={"prompt": "test"},
        requested_by="hermes",
        safety_level=ToolSafetyLevel.GENERATE_ONLY,
    )

    result = bus.execute(job)
    event_types = [event.event_type for event in bus.get_job_events(job.job_id)]

    assert result.success is False
    assert event_types == [
        ToolEventType.JOB_RECEIVED,
        ToolEventType.SAFETY_DENIED,
    ]


def test_allowed_placeholder_job_records_verification_failure() -> None:
    policy = SafetyPolicy()
    policy.enable_tool("blender", ["generate_scene_script"])
    bus = create_default_tool_bus()
    bus.safety_policy = policy
    job = ToolJob(
        tool_name="blender",
        capability="generate_scene_script",
        payload={"prompt": "test"},
        requested_by="hermes",
        safety_level=ToolSafetyLevel.GENERATE_ONLY,
    )

    result = bus.execute(job)
    event_types = [event.event_type for event in bus.get_job_events(job.job_id)]

    assert result.success is False
    assert event_types == [
        ToolEventType.JOB_RECEIVED,
        ToolEventType.SAFETY_ALLOWED,
        ToolEventType.ADAPTER_VERIFICATION_FAILED,
    ]


def test_status_reports_event_count() -> None:
    bus = create_default_tool_bus()
    job = ToolJob(
        tool_name="ollama",
        capability="list_models",
        payload={},
        requested_by="minerva",
        safety_level=ToolSafetyLevel.READ_ONLY,
    )

    bus.execute(job)

    assert bus.get_status()["event_count"] == 2
