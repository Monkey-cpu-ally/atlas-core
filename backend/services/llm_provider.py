"""
LLM Provider abstraction — Phase 1.

Wraps the existing `emergentintegrations.LlmChat` (cloud) and adds:
  - Ollama provider (local, OpenAI-compatible HTTP API)
  - LM Studio provider (local, OpenAI-compatible HTTP API)
  - Per-persona model preference from `atlas_settings.persona_models`
  - Graceful fallback to Emergent on local-provider connection errors

This is a NEW module — existing callers in chat.py / council.py /
learning.py / sandbox.py keep working with their direct LlmChat usage.
New code (and refactored callers in Phase 2) should use
`PersonaLLM.send(...)` from this module to opt into the multi-provider
routing.

Design constraints:
  - Same async send() interface so it's a drop-in replacement for
    LlmChat(...).with_model(...).send_message(UserMessage(text=...))
  - Per-call provider/model override (kwargs win over persona settings)
  - No singleton at module import — clients are lazy-instantiated so
    importing this file never hits the network
"""
import asyncio
import logging
import os
from typing import Any, Dict, Optional, Tuple
from uuid import uuid4

import httpx
from dotenv import load_dotenv
from emergentintegrations.llm.chat import LlmChat, UserMessage
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv()
logger = logging.getLogger("atlas.llm_provider")

EMERGENT_LLM_KEY = os.environ.get("EMERGENT_LLM_KEY", "")
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
LMSTUDIO_BASE_URL = os.environ.get("LMSTUDIO_BASE_URL", "http://localhost:1234/v1")
MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.environ.get("DB_NAME", "test_database")

# --- Persona defaults --------------------------------------------------------
# These are the values the seeder writes if `atlas_settings.persona_models`
# is missing. The architect can override per-persona via /api/settings.
DEFAULT_PERSONA_MODELS = {
    "ajani":   {"provider": "emergent", "model": "gpt-5.2"},
    "minerva": {"provider": "emergent", "model": "gpt-5.2"},
    "hermes":  {"provider": "emergent", "model": "gpt-5.2"},
    "council": {"provider": "emergent", "model": "gpt-5.2"},
    "trinity": {"provider": "emergent", "model": "gpt-5.2"},
}

# emergentintegrations -> (provider_id, model_id) used by LlmChat.with_model()
EMERGENT_MODEL_MAP = {
    "gpt-5.2":                       ("openai",    "gpt-5.2"),
    "gpt-4.1-mini":                  ("openai",    "gpt-4.1-mini"),
    "claude-sonnet-4-5-20250929":    ("anthropic", "claude-sonnet-4-5-20250929"),
    "claude-haiku-4-5":              ("anthropic", "claude-haiku-4-5"),
    "gemini-3-flash":                ("gemini",    "gemini-3-flash"),
    "gemini-3-pro":                  ("gemini",    "gemini-3-pro"),
}


# --- Mongo settings access ---------------------------------------------------
_mongo_client: Optional[AsyncIOMotorClient] = None


def _get_settings_collection():
    global _mongo_client
    if _mongo_client is None:
        _mongo_client = AsyncIOMotorClient(MONGO_URL)
    return _mongo_client[DB_NAME]["atlas_settings"]


async def get_persona_model(persona: str) -> Tuple[str, str]:
    """Resolve (provider, model) for a persona. Reads from atlas_settings
    if available, otherwise falls back to DEFAULT_PERSONA_MODELS."""
    persona = (persona or "council").lower()
    col = _get_settings_collection()
    doc = await col.find_one({"_id": "persona_models"}, {"_id": 0})
    settings = (doc or {}).get(persona) or DEFAULT_PERSONA_MODELS.get(persona) or DEFAULT_PERSONA_MODELS["council"]
    return settings.get("provider", "emergent"), settings.get("model", "gpt-5.2")


async def set_persona_models(updates: Dict[str, Dict[str, str]]) -> Dict[str, Any]:
    """Persist a partial map {persona: {provider, model}}. Validates that
    each provider is one of (emergent, ollama, lmstudio)."""
    valid_providers = {"emergent", "ollama", "lmstudio"}
    sanitised: Dict[str, Dict[str, str]] = {}
    for persona, cfg in updates.items():
        p = persona.lower()
        if not isinstance(cfg, dict):
            continue
        provider = str(cfg.get("provider", "emergent")).lower()
        if provider not in valid_providers:
            continue
        model = str(cfg.get("model", "gpt-5.2"))
        sanitised[p] = {"provider": provider, "model": model}
    if not sanitised:
        return {"updated": 0}

    col = _get_settings_collection()
    set_ops = {f"{k}": v for k, v in sanitised.items()}
    await col.update_one(
        {"_id": "persona_models"},
        {"$set": set_ops},
        upsert=True,
    )
    return {"updated": len(sanitised), "personas": sanitised}


# --- Provider implementations -------------------------------------------------
async def _send_emergent(system_msg: str, user_text: str, model: str, session_id: str) -> str:
    """Send via the existing Emergent LlmChat. Maps short model names to
    the (provider, model) tuple expected by with_model()."""
    provider_pair = EMERGENT_MODEL_MAP.get(model)
    if not provider_pair:
        # Heuristic fallback — assume openai-style if unknown
        if model.startswith("claude"):
            provider_pair = ("anthropic", model)
        elif model.startswith("gemini"):
            provider_pair = ("gemini", model)
        else:
            provider_pair = ("openai", model)
    chat = LlmChat(
        api_key=EMERGENT_LLM_KEY,
        session_id=session_id,
        system_message=system_msg,
    ).with_model(*provider_pair)
    raw = await chat.send_message(UserMessage(text=user_text))
    return raw if isinstance(raw, str) else ""


async def _send_ollama(system_msg: str, user_text: str, model: str) -> str:
    """POST to Ollama /v1/chat/completions (OpenAI-compatible)."""
    url = f"{OLLAMA_HOST.rstrip('/')}/v1/chat/completions"
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_text},
        ],
        "stream": False,
    }
    async with httpx.AsyncClient(timeout=120.0) as client:
        try:
            resp = await client.post(url, json=payload)
        except httpx.RequestError as exc:
            raise OllamaUnreachable(f"Cannot reach Ollama at {OLLAMA_HOST}: {exc}") from exc
        if resp.status_code >= 400:
            raise OllamaError(f"Ollama HTTP {resp.status_code}: {resp.text[:200]}")
        data = resp.json()
    try:
        return data["choices"][0]["message"]["content"]
    except (KeyError, IndexError) as exc:
        raise OllamaError(f"Malformed Ollama response: {exc}") from exc


async def _send_lmstudio(system_msg: str, user_text: str, model: str) -> str:
    """POST to LM Studio /v1/chat/completions (OpenAI-compatible)."""
    url = f"{LMSTUDIO_BASE_URL.rstrip('/')}/chat/completions"
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_text},
        ],
        "stream": False,
    }
    async with httpx.AsyncClient(timeout=120.0) as client:
        try:
            resp = await client.post(url, json=payload)
        except httpx.RequestError as exc:
            raise LMStudioUnreachable(f"Cannot reach LM Studio at {LMSTUDIO_BASE_URL}: {exc}") from exc
        if resp.status_code >= 400:
            raise LMStudioError(f"LM Studio HTTP {resp.status_code}: {resp.text[:200]}")
        data = resp.json()
    try:
        return data["choices"][0]["message"]["content"]
    except (KeyError, IndexError) as exc:
        raise LMStudioError(f"Malformed LM Studio response: {exc}") from exc


# --- Exceptions (local-provider unreachable triggers fallback) ---------------
class OllamaUnreachable(Exception): pass    # noqa: E701
class OllamaError(Exception): pass          # noqa: E701
class LMStudioUnreachable(Exception): pass  # noqa: E701
class LMStudioError(Exception): pass        # noqa: E701


# --- Public entry point ------------------------------------------------------
async def send(
    persona: str,
    system_msg: str,
    user_text: str,
    *,
    provider_override: Optional[str] = None,
    model_override: Optional[str] = None,
    session_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Send one prompt to the best LLM for `persona`.

    Returns dict {text, provider_used, model_used, fallback_reason?}.
    Fallback rules:
      - ollama unreachable / error → emergent gpt-5.2
      - lmstudio unreachable / error → emergent gpt-5.2
    """
    sid = session_id or f"{persona}-{uuid4().hex[:12]}"
    provider, model = await get_persona_model(persona)
    if provider_override:
        provider = provider_override.lower()
    if model_override:
        model = model_override

    fallback_reason: Optional[str] = None
    text = ""

    try:
        if provider == "ollama":
            text = await _send_ollama(system_msg, user_text, model)
        elif provider == "lmstudio":
            text = await _send_lmstudio(system_msg, user_text, model)
        else:
            text = await _send_emergent(system_msg, user_text, model, sid)
            provider = "emergent"
    except (OllamaUnreachable, OllamaError, LMStudioUnreachable, LMStudioError) as exc:
        fallback_reason = str(exc)[:200]
        logger.warning("LLM fallback to emergent (%s): %s", provider, fallback_reason)
        text = await _send_emergent(system_msg, user_text, "gpt-5.2", sid)
        provider = "emergent"
        model = "gpt-5.2"
    except Exception as exc:  # pragma: no cover — last-resort
        logger.exception("LLM send failed for persona=%s: %s", persona, exc)
        raise

    if not isinstance(text, str) or not text.strip():
        # Final defensive fallback — never let the caller see None
        logger.warning("Empty LLM response for persona=%s provider=%s", persona, provider)
        text = await _send_emergent(system_msg, user_text, "gpt-5.2", f"{sid}-retry")
        provider = "emergent"
        model = "gpt-5.2"
        fallback_reason = fallback_reason or "empty_response_retry"

    return {
        "text": text,
        "provider_used": provider,
        "model_used": model,
        "fallback_reason": fallback_reason,
    }


# --- Health -----------------------------------------------------------------
async def health() -> Dict[str, Any]:
    """Probe each provider with a tiny prompt to report availability.

    Cheap: skips Emergent (always assumed reachable if key present), just
    pings Ollama /api/tags and LM Studio /v1/models with a 3s timeout.
    """
    out: Dict[str, Any] = {
        "emergent": {"configured": bool(EMERGENT_LLM_KEY), "ok": bool(EMERGENT_LLM_KEY)},
        "ollama":   {"host": OLLAMA_HOST, "ok": False, "models": [], "error": None},
        "lmstudio": {"host": LMSTUDIO_BASE_URL, "ok": False, "models": [], "error": None},
    }
    async with httpx.AsyncClient(timeout=3.0) as client:
        # Ollama
        try:
            r = await client.get(f"{OLLAMA_HOST.rstrip('/')}/api/tags")
            if r.status_code < 400:
                out["ollama"]["ok"] = True
                data = r.json()
                out["ollama"]["models"] = [m.get("name") for m in data.get("models", [])][:20]
        except Exception as exc:
            out["ollama"]["error"] = str(exc)[:120]
        # LM Studio
        try:
            r = await client.get(f"{LMSTUDIO_BASE_URL.rstrip('/')}/models")
            if r.status_code < 400:
                out["lmstudio"]["ok"] = True
                data = r.json()
                models = data.get("data", []) if isinstance(data, dict) else []
                out["lmstudio"]["models"] = [m.get("id") for m in models][:20]
        except Exception as exc:
            out["lmstudio"]["error"] = str(exc)[:120]
    return out
