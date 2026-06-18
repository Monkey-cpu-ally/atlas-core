"""
Sentinel Anomaly Detection — Phase 8b.

Learn a rolling mean + standard deviation per (device, telemetry-key) using
Welford's online algorithm. Each incoming telemetry burst is scored against
the learned envelope; if any numeric reading drifts beyond N standard
deviations from its rolling mean, the device gains a transient `anomaly`
status and a list of triggering keys is surfaced to the HUD.

Why Welford's?
  - One pass, constant memory per key (n, mean, m2).
  - No need to keep the raw stream — telemetry already lives in
    `robot_telemetry` if anyone wants to recompute.

Storage:
  envelopes are persisted on the device document:
    device.state.envelopes[<key>] = {n, mean, m2, last_value, last_z}
  device.state.anomaly = {
    "drifting_keys": ["co2", "pm2_5"],
    "since": "<iso ts>",
    "z_scores": {"co2": 3.7, "pm2_5": 4.1},
  }
  device.state.anomaly is removed when the next reading falls back inside
  the envelope.

Warm-up:
  envelopes ignore the first N_WARMUP samples (default 10) — no anomaly
  scoring until enough data has accrued. This avoids screaming on the very
  first 2-3 readings.

Sigma threshold:
  default 3.0 — standard "outside 3 sigma" convention. Override per-device
  via device.state.anomaly_sigma.
"""
from __future__ import annotations

import math
import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from motor.motor_asyncio import AsyncIOMotorClient

_DEFAULT_SIGMA  = 3.0
_DEFAULT_WARMUP = 10

_client: Optional[AsyncIOMotorClient] = None


def _db():
    global _client
    if _client is None:
        _client = AsyncIOMotorClient(os.environ['MONGO_URL'])
    return _client[os.environ['DB_NAME']]


def _devices():
    return _db()["robot_devices"]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _welford_update(envelope: Dict[str, Any], value: float) -> Dict[str, Any]:
    """Online mean + variance update. Returns the updated envelope (mutated
    in-place too)."""
    n = int(envelope.get("n", 0)) + 1
    mean = float(envelope.get("mean", 0.0))
    m2 = float(envelope.get("m2", 0.0))
    delta = value - mean
    mean += delta / n
    delta2 = value - mean
    m2 += delta * delta2
    envelope["n"] = n
    envelope["mean"] = mean
    envelope["m2"] = m2
    envelope["last_value"] = value
    return envelope


def _stddev(envelope: Dict[str, Any]) -> float:
    n = int(envelope.get("n", 0))
    if n < 2:
        return 0.0
    return math.sqrt(envelope["m2"] / (n - 1))


def _z_score(envelope: Dict[str, Any], value: float) -> float:
    sd = _stddev(envelope)
    if sd == 0.0:
        return 0.0
    return (value - envelope["mean"]) / sd


async def update_and_score(
    device_id: str, payload: Dict[str, Any],
) -> Tuple[Dict[str, Any], List[str], Dict[str, float]]:
    """Update the device's envelopes from this telemetry burst and return:
        (updated_device_doc, drifting_keys, z_scores_for_drifting)

    Only numeric values are tracked. Non-numeric keys are silently skipped.
    Boolean values are NOT tracked (they're not anomalies in the statistical sense).
    """
    dev = await _devices().find_one({"id": device_id}, {"_id": 0})
    if not dev:
        return {}, [], {}

    state = dict(dev.get("state") or {})
    envelopes: Dict[str, Dict[str, Any]] = dict(state.get("envelopes") or {})

    sigma = float(state.get("anomaly_sigma", _DEFAULT_SIGMA))
    warmup = int(state.get("anomaly_warmup", _DEFAULT_WARMUP))

    drifting: List[str] = []
    z_scores: Dict[str, float] = {}

    for key, raw in payload.items():
        # Only track real numbers; booleans are falsey for isinstance(int).
        if isinstance(raw, bool) or not isinstance(raw, (int, float)):
            continue
        value = float(raw)
        if math.isnan(value) or math.isinf(value):
            continue
        env = envelopes.get(key) or {}
        prev_n = int(env.get("n", 0))
        # Score BEFORE update — that's how anomaly detection works (you
        # compare the new value to the previously learned distribution).
        if prev_n >= warmup:
            z = _z_score(env, value)
            env["last_z"] = z
            if abs(z) >= sigma:
                drifting.append(key)
                z_scores[key] = round(z, 3)
        # Always update the envelope so it keeps learning.
        envelopes[key] = _welford_update(env, value)

    state["envelopes"] = envelopes

    if drifting:
        state["anomaly"] = {
            "drifting_keys": drifting,
            "since": (state.get("anomaly") or {}).get("since") or _now(),
            "z_scores": z_scores,
            "sigma_threshold": sigma,
            "last_seen": _now(),
        }
    elif "anomaly" in state:
        # All readings are back inside the envelope — clear the flag.
        state.pop("anomaly", None)

    await _devices().update_one(
        {"id": device_id},
        {"$set": {"state": state, "updated_at": _now()}},
    )
    dev["state"] = state
    return dev, drifting, z_scores


async def envelope_summary(device_id: str) -> Dict[str, Any]:
    """Return the current envelope per key for inspection / debugging."""
    dev = await _devices().find_one({"id": device_id}, {"_id": 0, "state": 1, "name": 1})
    if not dev:
        return {}
    state = dev.get("state") or {}
    envs = state.get("envelopes") or {}
    out = {}
    for k, env in envs.items():
        out[k] = {
            "n": env.get("n", 0),
            "mean": env.get("mean", 0.0),
            "stddev": _stddev(env),
            "last_value": env.get("last_value"),
            "last_z": env.get("last_z"),
        }
    return {
        "device_id": device_id,
        "name": dev.get("name"),
        "anomaly": state.get("anomaly"),
        "envelopes": out,
    }


async def reset_envelope(device_id: str) -> bool:
    """Owner-only — wipe the learned envelopes and any current anomaly
    flag (e.g. after a known intentional change to the device)."""
    res = await _devices().update_one(
        {"id": device_id},
        {"$unset": {"state.envelopes": "", "state.anomaly": ""},
         "$set": {"updated_at": _now()}},
    )
    return res.matched_count > 0
