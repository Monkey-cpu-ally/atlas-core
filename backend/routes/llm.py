"""
LLM provider routes — Phase 1.

Exposes:
  GET  /api/llm/health         — which providers are reachable
  GET  /api/llm/persona-models — current per-persona (provider, model) map
  PUT  /api/llm/persona-models — update one or more persona settings
  POST /api/llm/test           — fire a single prompt at the configured
                                  provider for a persona (round-trip test)
"""
import logging
from typing import Dict, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from services.llm_provider import (
    DEFAULT_PERSONA_MODELS,
    EMERGENT_MODEL_MAP,
    get_persona_model,
    health,
    send,
    set_persona_models,
)

logger = logging.getLogger("atlas.llm_routes")
router = APIRouter(prefix="/api/llm", tags=["LLM"])


@router.get("/health")
async def llm_health():
    return await health()


@router.get("/persona-models")
async def list_persona_models():
    """Return the live persona → (provider, model) map.

    Always returns a value for each of the 5 known personas, falling back
    to defaults when the persona has not been customised yet.
    """
    out: Dict[str, Dict[str, str]] = {}
    for persona in DEFAULT_PERSONA_MODELS:
        provider, model = await get_persona_model(persona)
        out[persona] = {"provider": provider, "model": model}
    return {
        "personas": out,
        "providers_available": ["emergent", "ollama", "lmstudio"],
        "emergent_models": sorted(EMERGENT_MODEL_MAP.keys()),
    }


class PersonaModelUpdate(BaseModel):
    """Partial update — only personas present in the payload are changed.

    Example:
      {"ajani": {"provider": "ollama", "model": "llama3.1:70b"},
       "minerva": {"provider": "emergent", "model": "claude-sonnet-4-5-20250929"}}
    """
    updates: Dict[str, Dict[str, str]] = Field(..., min_length=1)


@router.put("/persona-models")
async def update_persona_models(req: PersonaModelUpdate):
    result = await set_persona_models(req.updates)
    if result.get("updated", 0) == 0:
        raise HTTPException(400, "no valid persona updates (check provider + model fields)")
    return result


class TestRequest(BaseModel):
    persona: str = Field(default="council")
    prompt: str = Field(min_length=1, max_length=2000)
    system_msg: Optional[str] = None
    provider_override: Optional[str] = None
    model_override: Optional[str] = None


@router.post("/test")
async def test_llm(req: TestRequest):
    """Round-trip test — sends `prompt` to whatever provider the persona
    resolves to, returns the response plus diagnostic metadata."""
    sys_msg = req.system_msg or "You are a concise assistant. Reply in one short paragraph."
    try:
        result = await send(
            req.persona,
            sys_msg,
            req.prompt,
            provider_override=req.provider_override,
            model_override=req.model_override,
        )
    except Exception as exc:
        raise HTTPException(502, f"LLM call failed: {exc}") from exc
    return result
