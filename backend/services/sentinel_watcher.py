"""
Sentinel Autonomic Watcher — Phase 8h.

Background task that fires `/api/persona/council/chat` automatically whenever
a device's anomaly block changes (new anomaly tripped OR drifting_keys
changed). Closes the gap between Phase 8b (anomaly detection trips a flag)
and Council reasoning (architect previously needed to click "ask the council"
in the Sentinel popover).

Architectural choices (env-only, fail-quiet):
  * Off by default. Set SENTINEL_AUTONOMIC=true to enable.
  * 60-second poll interval (overridable via SENTINEL_AUTONOMIC_INTERVAL_S).
  * De-duplication via the anomaly's `since` timestamp + sorted drifting_keys:
    we only fire ONCE per unique anomaly signature, not every minute. The
    dedupe key is persisted in MongoDB collection `sentinel_autonomic_fires`
    so restarts don't re-fire.
  * The Council reply is written to Memory Bank as `category=council`
    (permanent), tagged with `autonomic_council`, the device name, and
    every drifting key — Hermes / Ajani / Minerva can recall it later.
  * Cooldown: after firing, the same device cannot trip another autonomic
    council call for SENTINEL_AUTONOMIC_COOLDOWN_S (default 5 min) — keeps
    the LLM budget sane during oscillating telemetry.

Operational surface:
  GET /api/robot/sentinel/watcher/status  — running? last_fire? counters?
  POST /api/robot/sentinel/watcher/fire-now  — owner-only manual tick

Failure mode: if Council fails, we log it and STILL record the dedupe key
so we don't loop forever on a broken LLM provider.
"""
from __future__ import annotations

import asyncio
import logging
import os
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, Optional

from motor.motor_asyncio import AsyncIOMotorClient

import services.memory_bank as mb

logger = logging.getLogger("atlas.sentinel.watcher")


def _enabled() -> bool:
    return os.environ.get("SENTINEL_AUTONOMIC", "").lower() in ("1", "true", "yes")


def _interval_s() -> int:
    try:
        return max(5, int(os.environ.get("SENTINEL_AUTONOMIC_INTERVAL_S", "60")))
    except ValueError:
        return 60


def _cooldown_s() -> int:
    try:
        return max(0, int(os.environ.get("SENTINEL_AUTONOMIC_COOLDOWN_S", "300")))
    except ValueError:
        return 300


_client: Optional[AsyncIOMotorClient] = None


def _db():
    global _client
    if _client is None:
        _client = AsyncIOMotorClient(os.environ['MONGO_URL'])
    return _client[os.environ['DB_NAME']]


def _devices():
    return _db()["robot_devices"]


def _fires():
    return _db()["sentinel_autonomic_fires"]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _dedupe_key(device_id: str, anomaly: Dict[str, Any]) -> str:
    """Same anomaly signature → same key. Changes only when drifting_keys
    change or a new `since` timestamp is recorded (which happens on a fresh
    trip after a clean reading)."""
    keys = ",".join(sorted(anomaly.get("drifting_keys") or []))
    return f"{device_id}::{anomaly.get('since', '')}::{keys}"


# ---------------------------------------------------------------------------
# State (in-process — survives across requests, reset on backend restart)
# ---------------------------------------------------------------------------
_state: Dict[str, Any] = {
    "running": False,
    "started_at": None,
    "last_tick_at": None,
    "last_fire_at": None,
    "ticks": 0,
    "fires_total": 0,
    "errors_total": 0,
    "last_error": None,
}
_task: Optional[asyncio.Task] = None


def status() -> Dict[str, Any]:
    return {
        "enabled_env": _enabled(),
        "interval_s": _interval_s(),
        "cooldown_s": _cooldown_s(),
        **_state,
    }


# ---------------------------------------------------------------------------
# Core tick
# ---------------------------------------------------------------------------
async def _fire_council(device: Dict[str, Any], anomaly: Dict[str, Any]) -> None:
    """Auto-call the council with an anomaly-framed question. Writes the
    reply to MemoryBank tagged `autonomic_council` so future Council /
    persona chats can recall it."""
    # Lazy imports so this module never crashes app startup if persona_chat
    # has a transient issue.
    from services import persona_chat
    from models.persona_models import ChatRequest

    name = device.get("name") or device.get("id")
    drifting = anomaly.get("drifting_keys") or []
    z_desc = ", ".join(
        f"{k} (z={anomaly.get('z_scores', {}).get(k, '?'):.2f})"
        for k in drifting
    )
    question = (
        f"AUTONOMIC ALERT — Sentinel just tripped on device {name} "
        f"({device.get('kind')}). Drifting keys: {z_desc}. "
        f"Last telemetry: {device.get('last_seen')}. "
        f"State block: {anomaly}. "
        f"This is unsolicited — no human asked. Decide in two sentences: "
        f"investigate, recalibrate, or take protective action?"
    )
    try:
        res = await persona_chat.chat_any(
            "council",
            ChatRequest(message=question, memory_top_k=3, knowledge_top_k=3),
        )
        # Permanent council memory — tagged so it shows up in future Council
        # chats and in /api/membank/by-tag?tag=autonomic_council searches.
        await mb.auto_store(
            f"[AUTONOMIC COUNCIL] {name} :: {','.join(drifting)}\nQ: {question[:300]}\nA: {res.reply[:1200]}",
            persona="council", category="council",
            source_type="sentinel_autonomic",
            source_id=res.message_id,
            tags=["autonomic_council", "sentinel", "robot", name] + drifting,
        )
        _state["last_fire_at"] = _now()
        _state["fires_total"] += 1
        logger.info("[sentinel.autonomic] fired council for %s (drift=%s)", name, drifting)
    except Exception as exc:    # noqa: BLE001
        _state["errors_total"] += 1
        _state["last_error"] = f"{type(exc).__name__}: {exc}"[:240]
        logger.exception("[sentinel.autonomic] council fan-out failed for %s: %s", name, exc)


async def _in_cooldown(device_id: str) -> bool:
    if _cooldown_s() <= 0:
        return False
    last = await _fires().find_one(
        {"device_id": device_id}, {"fired_at": 1, "_id": 0},
        sort=[("fired_at", -1)],
    )
    if not last:
        return False
    try:
        fired_at = datetime.fromisoformat(last["fired_at"])
    except Exception:    # noqa: BLE001
        return False
    delta = datetime.now(timezone.utc) - fired_at
    return delta < timedelta(seconds=_cooldown_s())


async def tick() -> Dict[str, Any]:
    """One pass over every device with an active anomaly. Idempotent —
    safe to call from a cron OR from the manual fire-now endpoint."""
    _state["last_tick_at"] = _now()
    _state["ticks"] += 1
    fired = 0
    skipped = 0
    examined = 0

    # Stream devices that are currently flagged.
    cursor = _devices().find(
        {"state.anomaly": {"$exists": True, "$ne": None}},
        {"_id": 0, "id": 1, "name": 1, "kind": 1, "last_seen": 1, "state": 1},
    )
    async for dev in cursor:
        examined += 1
        anomaly = dev.get("state", {}).get("anomaly")
        if not anomaly:
            continue
        key = _dedupe_key(dev["id"], anomaly)
        # Dedup — fired before for this exact signature?
        already = await _fires().find_one({"key": key}, {"_id": 1})
        if already:
            skipped += 1
            continue
        if await _in_cooldown(dev["id"]):
            skipped += 1
            continue
        # Record FIRST (so a crash mid-LLM doesn't loop us)
        await _fires().insert_one({
            "key": key,
            "device_id": dev["id"],
            "device_name": dev.get("name"),
            "drifting_keys": anomaly.get("drifting_keys"),
            "fired_at": _now(),
        })
        await _fire_council(dev, anomaly)
        fired += 1

    return {"examined": examined, "fired": fired, "skipped": skipped}


async def _loop():
    """Forever loop — runs while the FastAPI process is alive."""
    while True:
        try:
            if _enabled():
                await tick()
        except asyncio.CancelledError:
            break
        except Exception as exc:    # noqa: BLE001
            _state["errors_total"] += 1
            _state["last_error"] = f"loop: {type(exc).__name__}: {exc}"[:240]
            logger.exception("[sentinel.autonomic] tick failed: %s", exc)
        try:
            await asyncio.sleep(_interval_s())
        except asyncio.CancelledError:
            break


async def start() -> bool:
    """Idempotent startup hook. Spawns the background task on first call;
    subsequent calls are no-ops. Returns True if the task is running."""
    global _task
    if _task is not None and not _task.done():
        return True
    _state["running"] = True
    _state["started_at"] = _now()
    _task = asyncio.create_task(_loop(), name="sentinel-autonomic-loop")
    logger.info(
        "[sentinel.autonomic] started · enabled=%s · interval=%ds · cooldown=%ds",
        _enabled(), _interval_s(), _cooldown_s(),
    )
    return True


async def stop() -> None:
    """Clean shutdown hook."""
    global _task
    _state["running"] = False
    if _task is not None and not _task.done():
        _task.cancel()
        try:
            await _task
        except (asyncio.CancelledError, Exception):    # noqa: BLE001
            pass
    _task = None
