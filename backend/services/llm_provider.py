"""
LLM Provider abstraction — Phase 1.

Routes persona prompts to Emergent, Ollama, or LM Studio. In ATLAS_TEST_MODE
only, a deterministic local provider is used so CI verifies orchestration,
persistence, persona differentiation, and memory wiring without pretending a
cloud model was contacted.
"""
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
        sanitised[p] = {"provider": provider, "model": str(cfg.get("model", "gpt-5.2"))}
    if not sanitised:
        return {"updated": 0}
    await _get_settings_collection().update_one(
        {"_id": "persona_models"}, {"$set": sanitised}, upsert=True
    )
    return {"updated": len(sanitised), "personas": sanitised}


async def _send_emergent(system_msg: str, user_text: str, model: str, session_id: str) -> str:
    if not EMERGENT_LLM_KEY:
        raise RuntimeError("LLM API key is not configured")
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


def _test_reply(persona: str, user_text: str) -> str:
    """Deterministic CI-only response; never used outside ATLAS_TEST_MODE."""
    p = (persona or "council").lower()
    if p == "ajani":
        return "Engineering first: define the mechanism, load, tolerance, materials, and failure mode before we build or test it."
    if p == "minerva":
        return "Evidence first: define the hypothesis, measurement, controls, uncertainty, and reproducibility before calling a result true."
    if p == "hermes":
        return "Systems first: state the assumptions, invariants, constraints, edge cases, and trade-offs before optimizing the design."
    return "Council synthesis: engineering feasibility, scientific evidence, and logical constraints must agree before ATLAS advances the decision."


async def send(
    persona: str,
    system_msg: str,
    user_text: str,
    *,
    provider_override: Optional[str] = None,
    model_override: Optional[str] = None,
    session_id: Optional[str] = None,
) -> Dict[str, Any]:
    sid = session_id or f"{persona}-{uuid4().hex[:12]}"

    # CI must exercise the real orchestration/persistence path without making
    # an external LLM call or misreporting a fake cloud provider as successful.
    if os.environ.get("ATLAS_TEST_MODE") == "1":
        return {
            "text": _test_reply(persona, user_text),
            "provider_used": "test",
            "model_used": "atlas-deterministic-ci-v1",
            "fallback_reason": "ATLAS_TEST_MODE",
        }

    provider, model = await get_persona_model(persona)
    if provider_override:
        provider = provider_override.lower()
    if model_override:
        model = model_override

    fallback_reason: Optional[str] = None
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
        provider, model = "emergent", "gpt-5.2"

    if not isinstance(text, str) or not text.strip():
        logger.warning("Empty LLM response for persona=%s provider=%s", persona, provider)
        text = await _send_emergent(system_msg, user_text, "gpt-5.2", f"{sid}-retry")
        provider, model = "emergent", "gpt-5.2"
        fallback_reason = fallback_reason or "empty_response_retry"

    return {"text": text, "provider_used": provider, "model_used": model, "fallback_reason": fallback_reason}


async def health() -> Dict[str, Any]:
    out: Dict[str, Any] = {
        "emergent": {"configured": bool(EMERGENT_LLM_KEY), "ok": bool(EMERGENT_LLM_KEY)},
        "ollama": {"host": OLLAMA_HOST, "ok": False, "models": [], "error": None},
        "lmstudio": {"host": LMSTUDIO_BASE_URL, "ok": False, "models": [], "error": None},
    }
    if os.environ.get("ATLAS_TEST_MODE") == "1":
        out["test"] = {"configured": True, "ok": True, "model": "atlas-deterministic-ci-v1"}
    async with httpx.AsyncClient(timeout=3.0) as client:
        try:
            r = await client.get(f"{OLLAMA_HOST.rstrip('/')}/api/tags")
            if r.status_code < 400:
                out["ollama"]["ok"] = True
                out["ollama"]["models"] = [m.get("name") for m in r.json().get("models", [])][:20]
        except Exception as exc:
            out["ollama"]["error"] = str(exc)[:120]
        try:
            r = await client.get(f"{LMSTUDIO_BASE_URL.rstrip('/')}/models")
            if r.status_code < 400:
                out["lmstudio"]["ok"] = True
                data = r.json()
                out["lmstudio"]["models"] = [m.get("id") for m in data.get("data", [])][:20] if isinstance(data, dict) else []
        except Exception as exc:
            out["lmstudio"]["error"] = str(exc)[:120]
    return out
