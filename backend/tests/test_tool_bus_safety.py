"""Tests for ATLAS Tool Bus safety gates."""

from __future__ import annotations

import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from atlas.tool_bus import SafetyDecision, SafetyPolicy, ToolJob, ToolSafetyLevel


def make_job(
    *,
    tool_name: str = "blender",
    capability: str = "generate_scene_script",
    safety_level: ToolSafetyLevel = ToolSafetyLevel.GENERATE_ONLY,
    requested_by: str = "hermes",
) -> ToolJob:
    return ToolJob(
        tool_name=tool_name,
        capability=capability,
        payload={"prompt": "test"},
        requested_by=requested_by,
        safety_level=safety_level,
    )


def test_disabled_tool_is_denied() -> None:
    policy = SafetyPolicy()

    review = policy.review(make_job())

    assert review.decision == SafetyDecision.DENY
    assert "Tool is not enabled" in review.reasons[0]


def test_enabled_generate_only_job_is_allowed() -> None:
    policy = SafetyPolicy()
    policy.enable_tool("blender", ["generate_scene_script"])

    review = policy.review(make_job())

    assert review.decision == SafetyDecision.ALLOW
    assert review.allowed is True


def test_unlisted_capability_is_denied() -> None:
    policy = SafetyPolicy()
    policy.enable_tool("blender", ["generate_scene_script"])

    review = policy.review(make_job(capability="render_scene"))

    assert review.decision == SafetyDecision.DENY
    assert "Capability is not enabled" in review.reasons[0]


def test_local_write_requires_approval_by_default() -> None:
    policy = SafetyPolicy()
    policy.enable_tool("blender", ["render_scene"])
    job = make_job(
        capability="render_scene",
        safety_level=ToolSafetyLevel.WRITE_LOCAL,
    )

    review = policy.review(job)

    assert review.decision == SafetyDecision.REQUIRE_APPROVAL


def test_specific_job_approval_allows_local_write() -> None:
    policy = SafetyPolicy()
    policy.enable_tool("blender", ["render_scene"])
    job = make_job(
        capability="render_scene",
        safety_level=ToolSafetyLevel.WRITE_LOCAL,
    )
    policy.approve_job(job.job_id)

    review = policy.review(job)

    assert review.decision == SafetyDecision.ALLOW


def test_destructive_action_is_denied_by_default() -> None:
    policy = SafetyPolicy()
    policy.enable_tool("example", ["delete_output"])
    job = make_job(
        tool_name="example",
        capability="delete_output",
        safety_level=ToolSafetyLevel.DESTRUCTIVE,
    )

    review = policy.review(job)

    assert review.decision == SafetyDecision.DENY
    assert "Destructive actions are disabled" in review.reasons[0]


def test_blocked_requester_is_denied() -> None:
    policy = SafetyPolicy(denied_requesters={"unknown-agent"})
    policy.enable_tool("blender", ["generate_scene_script"])

    review = policy.review(make_job(requested_by="unknown-agent"))

    assert review.decision == SafetyDecision.DENY
    assert "Requester is blocked" in review.reasons[0]
