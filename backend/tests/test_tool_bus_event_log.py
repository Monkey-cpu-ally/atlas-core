"""Tests for ATLAS Tool Bus event logging."""

from __future__ import annotations

import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from atlas.tool_bus import (
    InMemoryEventLog,
    SafetyPolicy,
    ToolEvent,
    ToolEventType,
    ToolJob,
    ToolSafetyLevel,
    create_default_tool_bus,
)


def test_event_log_appends_and_filters() -> None:
    log = InMemoryEventLog()
    first = ToolEvent(ToolEventType.JOB_RECEIVED, "job-1", "blender")
    second = ToolEvent(ToolEventType.SAFETY_ALLOWED, "job-1", "blender")
    third = ToolEvent(ToolEventType.JOB_RECEIVED, "job-2", "ollama")
    log.extend([first, second, third])

    assert len(log) == 3
    assert log.for_job("job-1") == [first, second]
    assert log.for_tool("ollama") == [third]
    assert third.to_dict()["event_type"] == "job_received"


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
    assert event_types == [ToolEventType.JOB_RECEIVED, ToolEventType.SAFETY_DENIED]


def test_allowed_placeholder_records_verification_failure() -> None:
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
    assert bus.get_status()["event_count"] == 3
