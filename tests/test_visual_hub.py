import pytest
from fastapi import HTTPException

from atlas_core.visual import VisualEventCreate, VisualPayload, build_envelope


def test_build_envelope_accepts_valid_persona_state():
    envelope = build_envelope(
        VisualEventCreate(
            event="ai.state.changed",
            source="test-suite",
            payload=VisualPayload(
                persona="minerva",
                state="thinking",
                intensity=0.75,
            ),
        )
    )

    assert envelope["version"] == "1.0"
    assert envelope["event"] == "ai.state.changed"
    assert envelope["source"] == "test-suite"
    assert envelope["payload"]["persona"] == "minerva"
    assert envelope["payload"]["state"] == "thinking"
    assert envelope["correlation_id"]


def test_build_envelope_accepts_genesis_wheel_event():
    envelope = build_envelope(
        VisualEventCreate(
            event="wheel.selection.changed",
            payload=VisualPayload(persona="hermes", node_id="robotics"),
        )
    )
    assert envelope["payload"]["node_id"] == "robotics"


def test_build_envelope_accepts_pulse_items():
    envelope = build_envelope(
        VisualEventCreate(
            event="pulse.updated",
            payload=VisualPayload(
                persona="atlas",
                items=[{"id": "weather", "title": "Storm watch"}],
            ),
        )
    )
    assert envelope["payload"]["items"][0]["id"] == "weather"


def test_build_envelope_accepts_awareness_alert():
    envelope = build_envelope(
        VisualEventCreate(
            event="awareness.alert.raised",
            payload=VisualPayload(
                persona="ajani",
                title="Offer below target",
                reason="The proposal is below the approved floor.",
                urgency="high",
            ),
        )
    )
    assert envelope["payload"]["urgency"] == "high"


def test_build_envelope_rejects_unknown_event():
    with pytest.raises(HTTPException) as error:
        build_envelope(VisualEventCreate(event="unknown.event"))

    assert error.value.status_code == 422


def test_build_envelope_rejects_unknown_urgency():
    with pytest.raises(HTTPException) as error:
        build_envelope(
            VisualEventCreate(
                event="awareness.alert.raised",
                payload=VisualPayload(urgency="wild"),
            )
        )
    assert error.value.status_code == 422


def test_payload_rejects_intensity_over_one():
    with pytest.raises(ValueError):
        VisualPayload(persona="atlas", intensity=1.5)
