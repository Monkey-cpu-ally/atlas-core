"""Tests for ATLAS Tool Bus event records."""

from __future__ import annotations

import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from atlas.tool_bus.events import InMemoryEventLog, ToolEvent, ToolEventType


def test_event_log_appends_and_filters_by_job() -> None:
    log = InMemoryEventLog()
    first = ToolEvent(
        event_type=ToolEventType.JOB_RECEIVED,
        job_id="job-1",
        tool_name="blender",
    )
    second = ToolEvent(
        event_type=ToolEventType.SAFETY_ALLOWED,
        job_id="job-1",
        tool_name="blender",
    )
    third = ToolEvent(
        event_type=ToolEventType.JOB_RECEIVED,
        job_id="job-2",
        tool_name="ollama",
    )

    log.extend([first, second, third])

    assert len(log) == 3
    assert log.for_job("job-1") == [first, second]
    assert log.for_tool("ollama") == [third]


def test_event_serializes_enum_value() -> None:
    event = ToolEvent(
        event_type=ToolEventType.JOB_FAILED,
        job_id="job-3",
        tool_name="neo4j",
        message="Adapter verification failed.",
    )

    data = event.to_dict()

    assert data["event_type"] == "job_failed"
    assert data["job_id"] == "job-3"
    assert data["tool_name"] == "neo4j"


def test_latest_returns_requested_tail() -> None:
    log = InMemoryEventLog()
    for index in range(5):
        log.append(
            ToolEvent(
                event_type=ToolEventType.JOB_RECEIVED,
                job_id=f"job-{index}",
                tool_name="blender",
            )
        )

    latest = log.latest(2)

    assert [event.job_id for event in latest] == ["job-3", "job-4"]
