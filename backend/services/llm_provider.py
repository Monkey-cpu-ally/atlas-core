"""
LLM Provider abstraction — Phase 1.

Wraps the existing `emergentintegrations.LlmChat` (cloud) and adds:
  - Ollama provider (local, OpenAI-compatible HTTP API)
  - LM Studio provider (local, OpenAI-compatible HTTP API)
  - Per-persona model preference from `atlas_settings.persona_models`
  - Graceful fallback to Emergent on local-provider connection errors

The Emergent SDK is optional at import time. If it is not installed, the
module remains importable for local providers and tests, while an actual
Emergent request fails explicitly instead of reporting a false success.
"""
import logging
import os
from typing import Any, Dict, Optional, Tuple
from uuid import uuid4

import httpx
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

try:
    from emergentintegrations.llm.chat import LlmChat, UserMessage
except ImportError:  # Optional/private runtime dependency.
    LlmChat = None
    UserMessage = None

load_dotenv()
logger = logging.getLogger("atlas.llm_provider")

EMERGENT_LLM_KEY = os.environ.get("EMERGENT_LLM_KEY", "")
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
LMSTUDIO_BASE_URL = os.environ.get("LMSTUDIO_BASE_URL", "http://localhost:1234/v1")
MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.environ.get("DB_NAME", "test_database")

DEFAULT_PERSONA_MODELS = {
    "ajani": {"provider": "emergent", "model": "gpt-5.2"},
    "minerva": {"provider": "emergent", "model": "gpt-5.2"},
    "hermes": {"provider": "emergent", "model": "gpt-5.2"},
    "council": {"provider": "emergent", "model": "gpt-5.2"},
    "trinity": {"provider": "emergent", "model": "gpt-5.2"},
}

EMERGENT_MODEL_MAP = {
    "gpt-5.2": ("openai", "gpt-5.2"),
    "gpt-4.1-mini": ("openai", "gpt-4.1-mini"),
    "claude-sonnet-4-5-20250929": ("anthropic", "claude-sonnet-4-5-20250929"),
    "claude-haiku-4-5": ("anthropic", "claude-haiku-4-5"),
    "gemini-3-flash": ("gemini", "gemini-3-flash"),
    "gemini-3-pro": ("gemini", "gemini-3-pro"),
}

_mongo_client: Optional[AsyncIOMotorClient] = None


def _get_settings_collection():
    global _mongo_client
    if _mongo_client is None:
        _mongo_client = AsyncIOMotorClient(MONGO_URL)
    return _mongo_client[DB_NAME]["atlas_settings"]


async def get_persona_model(persona: str) -> Tuple[str, str]:
    persona = (persona or "council").lower()
    col = _get_settings_collection()
    doc = await col.find_one({"_id": "persona_models"}, {"_id": 0})
    settings = (doc or {}).get(persona) or DEFAULT_PERSONA_MODELS.get(persona) or DEFAULT_PERSONA_MODELS["council"]
    return settings.get("provider", "emergent"), settings.get("model", "gpt-5.2")


async def set_persona_models(updates: Dict[str, Dict[str, str]]) -> Dict[str, Any]:
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
    await col.update_one({"_id": "persona_models"}, {"$set": sanitised}, upsert=True)
    return {"updated": len(sanitised), "personas": sanitised}


async def _send_emergent(system_msg: str, user_text: str, model: str, session_id: str) -> str:
    if LlmChat is None or UserMessage is None:
        raise RuntimeError("Emergent LLM SDK is not installed")
    if not EMERGENT_LLM_KEY:
        raise RuntimeError("EMERGENT_LLM_KEY is not configured")
    provider_pair = EMERGENT_MODEL_MAP.get(model)
    if not provider_pair:
        if model.startswith("claude"):
            provider_pair = ("anthropic", model)
        elif model.startswith("gemini"):
            provider_pair = ("gemini", model)
        else:
            provider_pair = ("openai", model)
    chat = LlmChat(api_key=EMERGENT_LLM_KEY, session_id=session_id, system_message=system_msg).with_model(*provider_pair)
    raw = await chat.send_message(UserMessage(text=user_text))
    return raw if isinstance(raw, str) else ""


async def _send_ollama(system_msg: str, user_text: str, model: str) -> str:
    url = f"{OLLAMA_HOST.rstrip('/')}/v1/chat/completions"
    payload = {"model": model, "messages": [{"role": "system", "content": system_msg}, {"role": "user", "content": user_text}], "stream": False}
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
    url = f"{LMSTUDIO_BASE_URL.rstrip('/')}/chat/completions"
    payload = {"model": model, "messages": [{"role": "system", "content": system_msg}, {"role": "user", "content": user_text}], "stream": False}
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


class OllamaUnreachable(Exception):
    pass


class OllamaError(Exception):
    pass


class LMStudioUnreachable(Exception):
    pass


class LMStudioError(Exception):
    pass


async def send(persona: str, system_msg: str, user_text: str, *, provider_override: Optional[str] = None, model_override: Optional[str] = None, session_id: Optional[str] = None) -> Dict[str, Any]:
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
    except Exception as exc:
        logger.exception("LLM send failed for persona=%s: %s", persona, exc)
        raise
    if not isinstance(text, str) or not text.strip():
        logger.warning("Empty LLM response for persona=%s provider=%s", persona, provider)
        text = await _send_emergent(system_msg, user_text, "gpt-5.2", f"{sid}-retry")
        provider = "emergent"
        model = "gpt-5.2"
        fallback_reason = fallback_reason or "empty_response_retry"
    return {"text": text, "provider_used": provider, "model_used": model, "fallback_reason": fallback_reason}


async def health() -> Dict[str, Any]:
    out: Dict[str, Any] = {
        "emergent": {"configured": bool(EMERGENT_LLM_KEY), "sdk_installed": LlmChat is not None and UserMessage is not None, "ok": bool(EMERGENT_LLM_KEY) and LlmChat is not None and UserMessage is not None},
        "ollama": {"host": OLLAMA_HOST, "ok": False, "models": [], "error": None},
        "lmstudio": {"host": LMSTUDIO_BASE_URL, "ok": False, "models": [], "error": None},
    }
    async with httpx.AsyncClient(timeout=3.0) as client:
        try:
            r = await client.get(f"{OLLAMA_HOST.rstrip('/')}/api/tags")
            if r.status_code < 400:
                out["ollama"]["ok"] = True
                data = r.json()
                out["ollama"]["models"] = [m.get("name") for m in data.get("models", [])][:20]
        except Exception as exc:
            out["ollama"]["error"] = str(exc)[:120]
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
