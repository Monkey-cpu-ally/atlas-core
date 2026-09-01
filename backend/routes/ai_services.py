"""AI service endpoints — TTS, Minerva approval, Hermes validation, Blueprint Engine.

LLM-backed review endpoints use the configured Emergent-compatible LLM key.
TTS supports ElevenLabs when configured and otherwise uses the explicit
OpenAI credential. Provider failures are surfaced truthfully; no fake audio is
returned.
"""
import asyncio
import json
import logging
import os
import re
from datetime import datetime, timezone
from typing import List, Optional

from dotenv import load_dotenv
from emergentintegrations.llm.chat import LlmChat, UserMessage
from emergentintegrations.llm.openai import OpenAITextToSpeech
from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel, Field

load_dotenv()

logger = logging.getLogger("atlas.ai_services")
router = APIRouter(prefix="/api/ai", tags=["AI Services"])

EMERGENT_LLM_KEY = os.environ.get("EMERGENT_LLM_KEY", "")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY", "")

_TTS_CLIENT: Optional[OpenAITextToSpeech] = None
_ELEVEN_CLIENT = None
_ELEVEN_TTS_DISABLED = False


def _get_tts_client() -> OpenAITextToSpeech:
    global _TTS_CLIENT
    if _TTS_CLIENT is None:
        _TTS_CLIENT = OpenAITextToSpeech(
            api_key=OPENAI_API_KEY,
            base_url=os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1"),
        )
    return _TTS_CLIENT


def _get_eleven_client():
    global _ELEVEN_CLIENT
    if not ELEVENLABS_API_KEY:
        return None
    if _ELEVEN_CLIENT is None:
        from elevenlabs import ElevenLabs
        _ELEVEN_CLIENT = ElevenLabs(api_key=ELEVENLABS_API_KEY)
    return _ELEVEN_CLIENT


PERSONA_VOICES = {
    "ajani": "onyx",
    "minerva": "nova",
    "hermes": "echo",
    "trinity": "shimmer",
}
ELEVEN_PERSONA_VOICES = {
    "ajani": "pNInz6obpgDQGcFmaJgB",
    "minerva": "EXAVITQu4vr4xnSDxMaL",
    "hermes": "ErXwobaYiN019PkySvjV",
    "trinity": "21m00Tcm4TlvDq8ikWAM",
}
PERSONA_LANGUAGE = {
    "ajani": "zu",
    "minerva": "yo",
    "hermes": "maa",
    "trinity": "en",
}
ELEVEN_MODEL_DEFAULT = "eleven_multilingual_v2"


class TTSRequest(BaseModel):
    text: str
    persona: Optional[str] = None
    voice: Optional[str] = None
    provider: Optional[str] = None
    language: Optional[str] = None
    model: Optional[str] = None
    speed: float = Field(1.0, ge=0.25, le=4.0)


def _resolve_provider(req: TTSRequest) -> str:
    if req.provider:
        return req.provider.lower()
    if ELEVENLABS_API_KEY and not _ELEVEN_TTS_DISABLED:
        return "elevenlabs"
    return "openai"


async def _synthesize_elevenlabs(text: str, voice_id: str, model_id: str) -> bytes:
    client = _get_eleven_client()
    if client is None:
        raise HTTPException(503, "ElevenLabs TTS not configured")

    def _convert():
        audio_iter = client.text_to_speech.convert(
            text=text,
            voice_id=voice_id,
            model_id=model_id,
            output_format="mp3_44100_128",
        )
        return b"".join(audio_iter)

    try:
        return await asyncio.to_thread(_convert)
    except Exception as exc:
        raise HTTPException(502, f"ElevenLabs TTS failed: {exc}") from exc


@router.post("/tts")
async def synthesize_speech(req: TTSRequest):
    if not req.text or not req.text.strip():
        raise HTTPException(400, "text is required")
    if len(req.text) > 4096:
        raise HTTPException(400, "text exceeds 4096 character limit")

    persona = (req.persona or "").lower()
    provider = _resolve_provider(req)
    language = (req.language or PERSONA_LANGUAGE.get(persona) or "en").lower()

    if provider not in {"elevenlabs", "openai"}:
        raise HTTPException(400, f"unsupported TTS provider: {provider}")

    if provider == "elevenlabs":
        if not ELEVENLABS_API_KEY:
            raise HTTPException(503, "ElevenLabs TTS not configured")
        voice_id = req.voice or ELEVEN_PERSONA_VOICES.get(persona) or ELEVEN_PERSONA_VOICES["trinity"]
        model_id = req.model if (req.model and req.model.startswith("eleven_")) else ELEVEN_MODEL_DEFAULT
        try:
            audio_bytes = await _synthesize_elevenlabs(req.text, voice_id, model_id)
            return Response(
                content=audio_bytes,
                media_type="audio/mpeg",
                headers={
                    "X-AI-Voice": voice_id,
                    "X-AI-Provider": "elevenlabs",
                    "X-AI-Language": language,
                    "X-AI-Model": model_id,
                },
            )
        except HTTPException as exc:
            detail = str(getattr(exc, "detail", ""))
            disabled_signals = (
                "missing_permissions", "text_to_speech", "detected_unusual_activity",
                "Unusual activity detected", "Free Tier usage disabled", "status_code: 401",
            )
            if any(sig in detail for sig in disabled_signals):
                global _ELEVEN_TTS_DISABLED
                _ELEVEN_TTS_DISABLED = True
            logger.warning("ElevenLabs TTS failed, falling back to OpenAI: %s", detail[:200])

    if not OPENAI_API_KEY:
        raise HTTPException(503, "OpenAI TTS offline (missing OPENAI_API_KEY)")
    voice = req.voice if (req.voice and req.voice in {"alloy", "echo", "fable", "onyx", "nova", "shimmer"}) else PERSONA_VOICES.get(persona, "alloy")
    model = req.model if (req.model and req.model.startswith("tts-")) else "tts-1"
    try:
        audio_bytes = await _get_tts_client().generate_speech(
            text=req.text, model=model, voice=voice, speed=req.speed
        )
    except Exception as exc:
        raise HTTPException(502, f"OpenAI TTS failed: {exc}") from exc

    return Response(
        content=audio_bytes,
        media_type="audio/mpeg",
        headers={
            "X-AI-Voice": voice,
            "X-AI-Provider": "openai",
            "X-AI-Language": language,
            "X-AI-Model": model,
        },
    )


MINERVA_APPROVAL_PROMPT = """You are Minerva — Yoruba wisdom keeper, ethical reviewer.
Your role is to evaluate proposals against ethical, cultural, and harm-reduction
criteria. You do NOT judge feasibility (that is Hermes' job) — you judge
whether something SHOULD be done and at what cost.

Output ONLY a JSON object with this exact shape:
{
  "verdict": "approve" | "approve_with_conditions" | "reject",
  "summary": "<one-sentence verdict in plain language>",
  "ethical_score": <0-100 integer, higher = more ethically sound>,
  "concerns": ["<concern 1>", "<concern 2>", ...],
  "conditions": ["<condition for approval, if any>", ...],
  "alternatives": ["<more ethical alternative, if reject/conditional>", ...],
  "ancestral_wisdom": "<a short proverb or principle that applies>"
}

Hard rule: if the proposal involves irreversible harm, manipulation without
consent, or undermines human dignity, the verdict MUST be "reject".
"""


class ApprovalRequest(BaseModel):
    proposal: str
    context: Optional[str] = None


def _extract_json_object(text: str) -> dict:
    fence = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if fence:
        text = fence.group(1)
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise HTTPException(502, "AI did not return JSON")
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError as exc:
        raise HTTPException(502, f"AI returned malformed JSON: {exc}") from exc


@router.post("/minerva/approve")
async def minerva_approve(req: ApprovalRequest):
    if not EMERGENT_LLM_KEY:
        raise HTTPException(503, "AI services offline")
    user_text = req.proposal
    if req.context:
        user_text = f"CONTEXT:\n{req.context}\n\nPROPOSAL:\n{req.proposal}"
    try:
        chat = LlmChat(api_key=EMERGENT_LLM_KEY, session_id=f"minerva-{datetime.now(timezone.utc).timestamp()}", system_message=MINERVA_APPROVAL_PROMPT).with_model("openai", "gpt-4.1-mini")
        result = await chat.send_message(UserMessage(text=user_text))
        return _extract_json_object(result)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(502, f"Minerva review failed: {exc}") from exc


HERMES_VALIDATION_PROMPT = """You are Hermes — ATLAS engineering architect and feasibility reviewer.
Evaluate the proposal for engineering feasibility, testability, dependencies,
risks, and verification requirements. Return ONLY JSON with keys verdict,
summary, feasibility_score, risks, dependencies, tests, and alternatives."""


class ValidationRequest(BaseModel):
    proposal: str
    context: Optional[str] = None


@router.post("/hermes/validate")
async def hermes_validate(req: ValidationRequest):
    if not EMERGENT_LLM_KEY:
        raise HTTPException(503, "AI services offline")
    user_text = req.proposal if not req.context else f"CONTEXT:\n{req.context}\n\nPROPOSAL:\n{req.proposal}"
    try:
        chat = LlmChat(api_key=EMERGENT_LLM_KEY, session_id=f"hermes-{datetime.now(timezone.utc).timestamp()}", system_message=HERMES_VALIDATION_PROMPT).with_model("openai", "gpt-4.1-mini")
        result = await chat.send_message(UserMessage(text=user_text))
        return _extract_json_object(result)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(502, f"Hermes validation failed: {exc}") from exc


class BlueprintRequest(BaseModel):
    title: str
    description: str
    requirements: List[str] = []


@router.post("/blueprint")
async def blueprint(req: BlueprintRequest):
    if not EMERGENT_LLM_KEY:
        raise HTTPException(503, "AI services offline")
    prompt = f"Title: {req.title}\nDescription: {req.description}\nRequirements: {req.requirements}"
    system = "You are the ATLAS Blueprint Engine. Return a concise JSON engineering blueprint with components, interfaces, risks, verification, and next_steps."
    try:
        chat = LlmChat(api_key=EMERGENT_LLM_KEY, session_id=f"blueprint-{datetime.now(timezone.utc).timestamp()}", system_message=system).with_model("openai", "gpt-4.1-mini")
        result = await chat.send_message(UserMessage(text=prompt))
        return _extract_json_object(result)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(502, f"Blueprint generation failed: {exc}") from exc


@router.get("/voices")
async def voices():
    return {
        "voices": PERSONA_VOICES,
        "elevenlabs_voices": ELEVEN_PERSONA_VOICES,
        "persona_language": PERSONA_LANGUAGE,
        "active_provider": "elevenlabs" if ELEVENLABS_API_KEY and not _ELEVEN_TTS_DISABLED else "openai",
        "elevenlabs_model": ELEVEN_MODEL_DEFAULT,
    }


@router.get("/voices/elevenlabs")
async def elevenlabs_voices():
    client = _get_eleven_client()
    if client is None:
        raise HTTPException(503, "ElevenLabs not configured")
    try:
        result = await asyncio.to_thread(client.voices.get_all)
        values = getattr(result, "voices", result)
        return {"voices": [getattr(v, "__dict__", str(v)) for v in values]}
    except Exception as exc:
        raise HTTPException(502, f"ElevenLabs voices failed: {exc}") from exc
