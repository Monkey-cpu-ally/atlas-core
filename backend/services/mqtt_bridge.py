"""
MQTT Bridge — Phase 8c.

Drops a real MQTT publisher behind the existing HTTP-poll command pipeline.
The REST surface (`/api/robot/*`) is UNCHANGED — devices that prefer to
poll `GET /devices/{id}/commands/inbox` keep working exactly as before.
Devices that subscribe to MQTT topics get a live push.

Config (env-only, fail-quiet):
    MQTT_BROKER_HOST   — e.g. mqtt.local OR 192.168.1.5. If unset → adapter
                         is dormant, function is a no-op, HTTP-poll is the
                         only delivery channel.
    MQTT_BROKER_PORT   — default 1883
    MQTT_USERNAME      — optional
    MQTT_PASSWORD      — optional
    MQTT_CLIENT_ID     — default 'atlas-bridge'
    MQTT_TOPIC_PREFIX  — default 'atlas' (topics become
                         '<prefix>/devices/<id>/cmd' down,
                         '<prefix>/devices/<id>/telemetry' up)

Why a thread-runner?
    paho-mqtt is sync. To stay out of the FastAPI event loop, we run the
    network loop on a daemon thread and submit publish() calls from any
    coroutine via the thread-safe client.publish() API (it queues the
    message internally).
"""
from __future__ import annotations

import json
import logging
import os
import threading
from typing import Any, Dict, Optional

logger = logging.getLogger("atlas.mqtt")

_TOPIC_PREFIX = os.environ.get("MQTT_TOPIC_PREFIX", "atlas")

# Single shared client. None = adapter dormant.
_client: Optional[Any] = None
_lock = threading.Lock()
_started = False
_last_error: Optional[str] = None


def is_enabled() -> bool:
    """True when MQTT_BROKER_HOST is configured. Used by HUD/status routes."""
    return bool(os.environ.get("MQTT_BROKER_HOST"))


def status() -> Dict[str, Any]:
    """Operational view — what we tell the HUD's Sentinel popover."""
    host = os.environ.get("MQTT_BROKER_HOST")
    return {
        "enabled": bool(host),
        "broker_host": host or None,
        "broker_port": int(os.environ.get("MQTT_BROKER_PORT", "1883")) if host else None,
        "topic_prefix": _TOPIC_PREFIX,
        "client_id": os.environ.get("MQTT_CLIENT_ID", "atlas-bridge"),
        "connected": _client is not None and getattr(_client, "is_connected", lambda: False)(),
        "last_error": _last_error,
    }


def _ensure_started() -> Optional[Any]:
    """Lazy-connect on first publish. Returns the client or None if MQTT
    is dormant / connection fails."""
    global _client, _started, _last_error

    host = os.environ.get("MQTT_BROKER_HOST")
    if not host:
        return None
    if _client is not None and _started:
        return _client

    with _lock:
        if _client is not None and _started:
            return _client
        try:
            # Imported lazily so a missing paho install never crashes import-time.
            import paho.mqtt.client as mqtt
            cli = mqtt.Client(
                mqtt.CallbackAPIVersion.VERSION2,
                client_id=os.environ.get("MQTT_CLIENT_ID", "atlas-bridge"),
            )
            user = os.environ.get("MQTT_USERNAME")
            pwd = os.environ.get("MQTT_PASSWORD")
            if user:
                cli.username_pw_set(user, pwd or None)
            cli.connect(host, int(os.environ.get("MQTT_BROKER_PORT", "1883")), keepalive=60)
            cli.loop_start()    # network thread
            _client = cli
            _started = True
            _last_error = None
            logger.info("MQTT bridge connected to %s", host)
            return _client
        except Exception as exc:    # noqa: BLE001
            _last_error = str(exc)[:200]
            logger.warning("MQTT bridge connect failed (will stay dormant): %s", exc)
            return None


def publish_command(device: Dict[str, Any], cmd: Dict[str, Any]) -> Dict[str, Any]:
    """Best-effort publish of an executed command to the device's
    downlink topic. Returns {published, topic, error?}. Failure is
    silent at the caller's level — HTTP-poll inbox still works."""
    cli = _ensure_started()
    if cli is None:
        return {"published": False, "reason": "mqtt_dormant"}
    topic = (
        device.get("mqtt_topic")
        or f"{_TOPIC_PREFIX}/devices/{device.get('id')}/cmd"
    )
    try:
        info = cli.publish(
            topic,
            payload=json.dumps({
                "id": cmd.get("id"),
                "kind": cmd.get("kind"),
                "payload": cmd.get("payload", {}),
                "issued_by_role": cmd.get("issued_by_role"),
                "executed_at": cmd.get("executed_at"),
            }, default=str),
            qos=1, retain=False,
        )
        # paho's `info.rc` is 0 on success
        rc = getattr(info, "rc", 0)
        return {"published": rc == 0, "topic": topic, "rc": rc}
    except Exception as exc:    # noqa: BLE001
        logger.warning("MQTT publish failed (topic=%s): %s", topic, exc)
        return {"published": False, "topic": topic, "error": str(exc)[:200]}


def shutdown() -> None:
    """Clean shutdown on FastAPI app stop."""
    global _client, _started
    if _client is not None:
        try:
            _client.loop_stop()
            _client.disconnect()
        except Exception:    # noqa: BLE001
            pass
    _client = None
    _started = False


# ===========================================================================
# Phase 8c.2 — Telemetry UPLINK subscriber
# ---------------------------------------------------------------------------
# When devices publish telemetry to `<prefix>/devices/<id>/telemetry`, the
# bridge ingests them into the same `robot.ingest_telemetry` pipeline that
# HTTP POSTs use. This closes the bidirectional loop:
#   downlink:  Atlas → device  via `<prefix>/devices/<id>/cmd`
#   uplink:    device → Atlas  via `<prefix>/devices/<id>/telemetry`
# ===========================================================================
import asyncio as _asyncio
import re as _re

_UPLINK_RE = _re.compile(r"/devices/([A-Za-z0-9_\-]+)/telemetry$")
_loop_ref: Optional[Any] = None    # main asyncio loop captured at startup


def set_loop(loop: Any) -> None:
    """Capture the FastAPI event loop so the MQTT thread can submit
    coroutine work back via `loop.call_soon_threadsafe`."""
    global _loop_ref
    _loop_ref = loop


def _on_uplink_message(_client_unused, _userdata, msg) -> None:
    """paho callback running on the MQTT network thread. We extract the
    device_id from the topic, parse JSON, and bounce into the asyncio
    loop to call `robot.ingest_telemetry`."""
    try:
        topic = getattr(msg, "topic", "") or ""
        m = _UPLINK_RE.search(topic)
        if not m:
            return
        device_id = m.group(1)
        try:
            payload = json.loads(msg.payload.decode("utf-8") or "{}")
        except Exception:    # noqa: BLE001
            payload = {"raw": (msg.payload or b"").decode("utf-8", "ignore")}
        if not isinstance(payload, dict):
            payload = {"raw": payload}

        if _loop_ref is None:
            logger.warning("MQTT uplink received but no loop captured")
            return
        from services import robot as _robot

        async def _run():
            try:
                await _robot.ingest_telemetry(device_id, payload, source="mqtt")
            except Exception as exc:    # noqa: BLE001
                logger.warning("uplink ingest failed (%s): %s", device_id, exc)

        _asyncio.run_coroutine_threadsafe(_run(), _loop_ref)
    except Exception as exc:    # noqa: BLE001
        logger.warning("MQTT uplink dispatch failed: %s", exc)


def _subscribe_uplink_after_connect(_client_unused, _userdata, _flags, _rc, _props=None) -> None:
    """on_connect callback — subscribe to the wildcard telemetry topic
    so every device's uplink lands here without per-device config."""
    try:
        topic = f"{_TOPIC_PREFIX}/devices/+/telemetry"
        rc, _mid = _client_unused.subscribe(topic, qos=1)
        logger.info("MQTT uplink subscribed: topic=%s rc=%s", topic, rc)
    except Exception as exc:    # noqa: BLE001
        logger.warning("MQTT subscribe failed: %s", exc)


def enable_uplink() -> Dict[str, Any]:
    """Wire the uplink callbacks onto the running client. Idempotent —
    safe to call multiple times. Returns operational status."""
    cli = _ensure_started()
    if cli is None:
        return {"uplink_enabled": False, "reason": "mqtt_dormant"}
    try:
        cli.on_message = _on_uplink_message
        cli.on_connect = _subscribe_uplink_after_connect
        # If already connected, subscribe directly (on_connect won't refire).
        if getattr(cli, "is_connected", lambda: False)():
            topic = f"{_TOPIC_PREFIX}/devices/+/telemetry"
            cli.subscribe(topic, qos=1)
            logger.info("MQTT uplink subscribed (post-connect): %s", topic)
        return {"uplink_enabled": True, "topic": f"{_TOPIC_PREFIX}/devices/+/telemetry"}
    except Exception as exc:    # noqa: BLE001
        return {"uplink_enabled": False, "error": str(exc)[:200]}
