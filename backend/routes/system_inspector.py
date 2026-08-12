"""ATLAS System Inspector routes + runtime bootstrap."""
from __future__ import annotations

import asyncio
import importlib.util
import os
from typing import Any, Dict

from fastapi import APIRouter

from services import system_inspector

router = APIRouter(prefix="/api/system-inspector", tags=["ATLAS System Inspector"])

_runtime: Dict[str, Any] = {
    "bootstrapped": False,
    "memory": {"provider": "unknown", "model": None, "reason": None},
    "mqtt": {"uplink_enabled": False, "reason": "not_started"},
}

_ST_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


@router.on_event("startup")
async def _bootstrap_atlas_runtime() -> None:
    """Wire optional runtime services without making app startup brittle.

    Memory preference order:
      1. ATLAS_EMBED_PROVIDER / ATLAS_EMBED_MODEL when explicitly configured.
      2. Local sentence-transformers when installed (real semantic vectors).
      3. Existing hash backend as a deterministic last-resort fallback.

    MQTT is also attached to the FastAPI event loop here so the paho network
    thread can forward device telemetry into the async robot pipeline.
    """
    global _runtime

    # ---- Memory Bank semantic embeddings ---------------------------------
    try:
        from services import memory_bank as mb

        explicit_provider = (os.environ.get("ATLAS_EMBED_PROVIDER") or "").strip().lower()
        explicit_model = (os.environ.get("ATLAS_EMBED_MODEL") or "").strip()

        if explicit_provider:
            provider = explicit_provider
            model = explicit_model or {
                "st": _ST_MODEL,
                "ollama": mb.DEFAULT_OLLAMA_EMBED,
                "emergent": mb.DEFAULT_OPENAI_EMBED,
                "hash": mb.DEFAULT_EMBED_MODEL,
            }.get(provider, mb.DEFAULT_EMBED_MODEL)
            reason = "explicit_environment_configuration"
        elif importlib.util.find_spec("sentence_transformers") is not None:
            provider = "st"
            model = _ST_MODEL
            reason = "local_semantic_embeddings_available"
        else:
            provider = "hash"
            model = mb.DEFAULT_EMBED_MODEL
            reason = "sentence_transformers_unavailable_fallback"

        updates = {
            persona: {"provider": provider, "model": model}
            for persona in mb.DEFAULT_EMBED_SETTINGS
        }
        result = await mb.set_embed_settings(updates)
        _runtime["memory"] = {
            "provider": provider,
            "model": model,
            "reason": reason,
            "settings_updated": result.get("updated", 0),
        }
    except Exception as exc:  # noqa: BLE001
        _runtime["memory"] = {
            "provider": "existing",
            "model": None,
            "reason": f"bootstrap_failed: {str(exc)[:180]}",
        }

    # ---- MQTT bidirectional bridge ---------------------------------------
    try:
        from services import mqtt_bridge

        mqtt_bridge.set_loop(asyncio.get_running_loop())
        _runtime["mqtt"] = mqtt_bridge.enable_uplink()
        _runtime["mqtt"]["status"] = mqtt_bridge.status()
    except Exception as exc:  # noqa: BLE001
        _runtime["mqtt"] = {
            "uplink_enabled": False,
            "reason": f"bootstrap_failed: {str(exc)[:180]}",
        }

    _runtime["bootstrapped"] = True


@router.on_event("shutdown")
async def _shutdown_atlas_runtime() -> None:
    try:
        from services import mqtt_bridge
        mqtt_bridge.shutdown()
    except Exception:  # noqa: BLE001
        pass


@router.get("/health")
async def health():
    return {
        "status": "ok",
        "engine": "system_inspector",
        "purpose": "Repository and engineering quality inspection.",
        "runtime_bootstrapped": _runtime.get("bootstrapped", False),
    }


@router.get("/runtime")
async def runtime():
    """Return honest live readiness for memory, LLM providers and MQTT."""
    out = dict(_runtime)
    try:
        from services import mqtt_bridge
        out["mqtt_status"] = mqtt_bridge.status()
    except Exception as exc:  # noqa: BLE001
        out["mqtt_status"] = {"error": str(exc)[:180]}

    try:
        from services import llm_provider
        out["llm"] = await llm_provider.health()
    except Exception as exc:  # noqa: BLE001
        out["llm"] = {"error": str(exc)[:180]}
    return out


@router.get("/report")
async def report():
    return system_inspector.inspect_repository()


@router.get("/technical-debt")
async def technical_debt():
    return system_inspector.technical_debt_register()


@router.get("/certification")
async def certification():
    return system_inspector.certification_report()
