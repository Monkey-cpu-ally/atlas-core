"""AI service endpoints — TTS, Minerva approval, Hermes validation, Blueprint Engine.

All four endpoints use the Emergent Universal LLM Key (no separate keys needed).
TTS additionally supports ElevenLabs (per-persona custom voices + multilingual)
when ELEVENLABS_API_KEY is configured; otherwise falls back to OpenAI TTS.
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
ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY", "")

# Module-level TTS client cache — instantiating OpenAITextToSpeech on every
# request added 150–400 ms of cold-start latency. Reuse one client.
_TTS_CLIENT: Optional[OpenAITextToSpeech] = None
_ELEVEN_CLIENT = None  # elevenlabs.ElevenLabs — lazily imported

# When the ElevenLabs key is configured but lacks `text_to_speech`, we
# discover that on the first request. Cache the result so subsequent calls
# skip the failed round-trip and go straight to OpenAI fallback.
_ELEVEN_TTS_DISABLED = False


def _get_tts_client() -> OpenAITextToSpeech:
    global _TTS_CLIENT
    if _TTS_CLIENT is None:
        _TTS_CLIENT = OpenAITextToSpeech(api_key=EMERGENT_LLM_KEY)
    return _TTS_CLIENT


def _get_eleven_client():
    """Lazy import + cache the ElevenLabs client. Returns None if no key."""
    global _ELEVEN_CLIENT
    if not ELEVENLABS_API_KEY:
        return None
    if _ELEVEN_CLIENT is None:
        from elevenlabs import ElevenLabs  # imported lazily
        _ELEVEN_CLIENT = ElevenLabs(api_key=ELEVENLABS_API_KEY)
    return _ELEVEN_CLIENT


# ---------------------------------------------------------------------------
# 1) Text-to-Speech
# ---------------------------------------------------------------------------

# Per-AI default voice mapping — OpenAI TTS (fallback when ElevenLabs is off).
PERSONA_VOICES = {
    "ajani":   "onyx",     # deep / grounded
    "minerva": "nova",     # warm / flowing
    "hermes":  "echo",     # precise / clear
    "trinity": "shimmer",  # bright / layered
}

# Per-AI ElevenLabs voice IDs (using ElevenLabs' default voice library).
# Source: https://elevenlabs.io/app/voice-library — these IDs are stable.
ELEVEN_PERSONA_VOICES = {
    "ajani":   "pNInz6obpgDQGcFmaJgB",  # Adam — deep, grounded, warrior cadence
    "minerva": "EXAVITQu4vr4xnSDxMaL",  # Bella — warm, flowing, wisdom keeper
    "hermes":  "ErXwobaYiN019PkySvjV",  # Antoni — precise, observant
    "trinity": "21m00Tcm4TlvDq8ikWAM",  # Rachel — bright, multi-tonal
}

# Native-language hint per persona (used as a default when caller doesn't pass
# `language`). Voice will read the literal text — if you provide English text
# you get English; if you provide Zulu text the multilingual model speaks it.
PERSONA_LANGUAGE = {
    "ajani":   "zu",   # isiZulu
    "minerva": "yo",   # Yorùbá
    "hermes":  "maa",  # Maa (Maasai) — multilingual_v2 won't render natively
    "trinity": "en",
}

# eleven_multilingual_v2 supports ~29 languages including English, Spanish,
# French, German, Hindi, Arabic, etc. Zulu / Yoruba / Maa are not natively
# rendered — when the caller asks for those we still send the text, and
# rely on the model's phonetic approximation.
ELEVEN_MODEL_DEFAULT = "eleven_multilingual_v2"


class TTSRequest(BaseModel):
    text: str
    persona: Optional[str] = None        # ajani | minerva | hermes | trinity
    voice: Optional[str] = None          # explicit voice overrides persona mapping
    provider: Optional[str] = None       # 'elevenlabs' | 'openai' | None (auto)
    language: Optional[str] = None       # ISO code: en, zu, yo, maa, es, fr…
    model: Optional[str] = None          # tts-1 (openai) | eleven_multilingual_v2
    speed: float = Field(1.0, ge=0.25, le=4.0)


def _resolve_provider(req: TTSRequest) -> str:
    """Pick the TTS provider. Honour explicit request, otherwise prefer
    ElevenLabs when its key is configured (per-persona voices), else OpenAI.
    Once we have proven the ElevenLabs key lacks `text_to_speech`, we stop
    choosing it automatically — explicit `provider='elevenlabs'` will still
    attempt it and surface the error."""
    if req.provider:
        return req.provider.lower()
    if ELEVENLABS_API_KEY and not _ELEVEN_TTS_DISABLED:
        return "elevenlabs"
    return "openai"


async def _synthesize_elevenlabs(text: str, voice_id: str, model_id: str) -> bytes:
    """Run the synchronous ElevenLabs SDK in a thread so we don't block the
    event loop. Returns mp3 bytes."""
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
    """Synthesize speech for an AI persona. Returns MP3 audio bytes.

    Routing logic:
      • provider == 'elevenlabs' (or auto when ELEVENLABS_API_KEY set)
          → ElevenLabs eleven_multilingual_v2 with per-persona voice.
      • provider == 'openai' (default fallback)
          → OpenAI tts-1 with per-persona voice.
    On ElevenLabs failure, we fall back to OpenAI rather than 5xx.
    """
    if not req.text or not req.text.strip():
        raise HTTPException(400, "text is required")
    if len(req.text) > 4096:
        raise HTTPException(400, "text exceeds 4096 character limit")

    persona = (req.persona or "").lower()
    provider = _resolve_provider(req)
    language = (req.language or PERSONA_LANGUAGE.get(persona) or "en").lower()

    # --- ElevenLabs path -----------------------------------------------------
    if provider == "elevenlabs" and ELEVENLABS_API_KEY:
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
            # Fall through to OpenAI on ElevenLabs error — never let TTS 5xx.
            # If the failure was a permissions error, disable ElevenLabs for
            # the rest of this process so we stop paying the failed round-trip.
            detail = str(getattr(exc, "detail", ""))
            # Cache the disabled state on any 401/permission/abuse signal so
            # we stop paying the round-trip on every TTS request.
            disabled_signals = (
                "missing_permissions",
                "text_to_speech",
                "detected_unusual_activity",
                "Unusual activity detected",
                "Free Tier usage disabled",
                "status_code: 401",
            )
            if any(sig in detail for sig in disabled_signals):
                global _ELEVEN_TTS_DISABLED
                _ELEVEN_TTS_DISABLED = True
            logger.warning("ElevenLabs TTS failed, falling back to OpenAI: %s", detail[:200])

    # --- OpenAI fallback path -----------------------------------------------
    if not EMERGENT_LLM_KEY:
        raise HTTPException(503, "AI services offline (missing EMERGENT_LLM_KEY)")
    voice = req.voice if (req.voice and req.voice in {"alloy", "echo", "fable", "onyx", "nova", "shimmer"}) else PERSONA_VOICES.get(persona, "alloy")
    model = req.model if (req.model and req.model.startswith("tts-")) else "tts-1"
    try:
        tts = _get_tts_client()
        audio_bytes = await tts.generate_speech(
            text=req.text,
            model=model,
            voice=voice,
            speed=req.speed,
        )
    except Exception as exc:
        raise HTTPException(500, f"TTS failed: {exc}")

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


# ---------------------------------------------------------------------------
# 2) Minerva approval — ethical / cultural / harm review
# ---------------------------------------------------------------------------

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
    """Pull the first JSON object out of an LLM response."""
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
    """Run Minerva's ethical review on a proposal."""
    if not EMERGENT_LLM_KEY:
        raise HTTPException(503, "AI services offline")

    user_text = req.proposal
    if req.context:
        user_text = f"CONTEXT:\n{req.context}\n\nPROPOSAL:\n{req.proposal}"

    chat = LlmChat(
        api_key=EMERGENT_LLM_KEY,
        session_id=f"minerva_{datetime.now(timezone.utc).timestamp()}",
        system_message=MINERVA_APPROVAL_PROMPT,
    ).with_model("openai", "gpt-5.2")

    try:
        raw = await chat.send_message(UserMessage(text=user_text))
    except Exception as exc:
        raise HTTPException(500, f"Minerva approval failed: {exc}")

    return {
        "review": _extract_json_object(raw),
        "raw": raw,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


# ---------------------------------------------------------------------------
# 3) Hermes validation — technical / safety / feasibility
# ---------------------------------------------------------------------------

HERMES_VALIDATION_PROMPT = """You are Hermes — Maasai pattern hunter, technical
validator. Your role is to evaluate proposals on technical correctness, safety
constraints, edge cases, and failure modes. You do NOT judge ethics (that is
Minerva's job) — you judge whether something CAN be done safely.

Output ONLY a JSON object with this exact shape:
{
  "verdict": "valid" | "valid_with_constraints" | "invalid",
  "summary": "<one-sentence technical verdict>",
  "feasibility_score": <0-100 integer, higher = more feasible>,
  "safety_score": <0-100 integer, higher = safer>,
  "failure_modes": ["<edge case or failure mode>", ...],
  "constraints": ["<technical constraint that must be respected>", ...],
  "patterns": ["<known pattern this resembles>", ...],
  "next_steps": ["<concrete next action>", ...]
}

Hard rule: anything involving self-replicating systems or uncontainable energy
MUST be marked "invalid".
"""


@router.post("/hermes/validate")
async def hermes_validate(req: ApprovalRequest):
    """Run Hermes' technical validation on a proposal."""
    if not EMERGENT_LLM_KEY:
        raise HTTPException(503, "AI services offline")

    user_text = req.proposal
    if req.context:
        user_text = f"CONTEXT:\n{req.context}\n\nPROPOSAL:\n{req.proposal}"

    chat = LlmChat(
        api_key=EMERGENT_LLM_KEY,
        session_id=f"hermes_{datetime.now(timezone.utc).timestamp()}",
        system_message=HERMES_VALIDATION_PROMPT,
    ).with_model("openai", "gpt-5.2")

    try:
        raw = await chat.send_message(UserMessage(text=user_text))
    except Exception as exc:
        raise HTTPException(500, f"Hermes validation failed: {exc}")

    return {
        "review": _extract_json_object(raw),
        "raw": raw,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


# ---------------------------------------------------------------------------
# 4) Blueprint Engine — 5-phase structured spec generator
# ---------------------------------------------------------------------------

BLUEPRINT_PROMPT = """You are the ATLAS Blueprint Engine. Given a high-level
concept from the architect-in-chief, generate a structured five-phase blueprint:

  1. PHILOSOPHY  — the WHY: core belief, values, what problem this serves
  2. RESEARCH    — what is known, what is unknown, prior art, open questions
  3. BLUEPRINT   — concrete components, data flows, key interfaces
  4. SIMULATION  — how to test in software/thought-experiment before building
  5. PHYSICAL    — how to instantiate in the real world, with safety gates

Output ONLY a JSON object with this exact shape:
{
  "concept": "<echoed concept>",
  "domain": "<elemental_kinetics | bio_genesis | nano_synthesis | other>",
  "phases": {
    "philosophy": { "core_belief": "...", "why_it_matters": "...", "ethical_anchors": ["..."] },
    "research":   { "known": ["..."], "unknown": ["..."], "prior_art": ["..."] },
    "blueprint":  { "components": ["..."], "data_flows": ["..."], "interfaces": ["..."] },
    "simulation": { "test_plan": ["..."], "success_criteria": ["..."], "risks": ["..."] },
    "physical":   { "build_steps": ["..."], "safety_gates": ["..."], "containment": ["..."] }
  },
  "minerva_concerns": ["<things Minerva should review>"],
  "hermes_validations": ["<things Hermes should validate>"]
}

Hard rule: every phase MUST include at least one safety_gate or ethical_anchor.
"""


class BlueprintRequest(BaseModel):
    concept: str
    domain: Optional[str] = None     # elemental_kinetics | bio_genesis | nano_synthesis
    constraints: Optional[List[str]] = None


@router.post("/blueprint/generate")
async def generate_blueprint(req: BlueprintRequest):
    """Generate a 5-phase blueprint for a concept."""
    if not EMERGENT_LLM_KEY:
        raise HTTPException(503, "AI services offline")

    parts = [f"CONCEPT:\n{req.concept}"]
    if req.domain:
        parts.append(f"DOMAIN: {req.domain}")
    if req.constraints:
        parts.append("CONSTRAINTS:\n- " + "\n- ".join(req.constraints))
    user_text = "\n\n".join(parts)

    chat = LlmChat(
        api_key=EMERGENT_LLM_KEY,
        session_id=f"blueprint_{datetime.now(timezone.utc).timestamp()}",
        system_message=BLUEPRINT_PROMPT,
    ).with_model("openai", "gpt-5.2")

    try:
        raw = await chat.send_message(UserMessage(text=user_text))
    except Exception as exc:
        raise HTTPException(500, f"Blueprint generation failed: {exc}")

    return {
        "blueprint": _extract_json_object(raw),
        "raw": raw,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/voices")
async def list_voices():
    """Return the per-persona voice mapping the frontend should use,
    plus runtime info on which provider is active and what languages each
    persona defaults to."""
    return {
        "voices": PERSONA_VOICES,
        "elevenlabs_voices": ELEVEN_PERSONA_VOICES,
        "persona_language": PERSONA_LANGUAGE,
        "active_provider": "elevenlabs" if ELEVENLABS_API_KEY else "openai",
        "elevenlabs_model": ELEVEN_MODEL_DEFAULT,
    }


@router.get("/voices/elevenlabs")
async def list_elevenlabs_voices():
    """Live-fetch all voices available on the ElevenLabs account (so the
    architect-in-chief can discover/swap voice IDs without leaving the HUD)."""
    client = _get_eleven_client()
    if client is None:
        raise HTTPException(503, "ElevenLabs not configured (missing ELEVENLABS_API_KEY)")
    try:
        resp = await asyncio.to_thread(client.voices.get_all)
    except Exception as exc:
        raise HTTPException(502, f"ElevenLabs voices fetch failed: {exc}") from exc

    voices = []
    for v in getattr(resp, "voices", []) or []:
        voices.append({
            "voice_id": getattr(v, "voice_id", None),
            "name": getattr(v, "name", None),
            "category": getattr(v, "category", None),
            "labels": getattr(v, "labels", None),
            "preview_url": getattr(v, "preview_url", None),
        })
    return {"count": len(voices), "voices": voices}
