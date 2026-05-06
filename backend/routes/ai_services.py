"""AI service endpoints — TTS, Minerva approval, Hermes validation, Blueprint Engine.

All four endpoints use the Emergent Universal LLM Key (no separate keys needed).
"""
import json
import os
import re
from datetime import datetime, timezone
from typing import List, Optional

from dotenv import load_dotenv
from emergentintegrations.llm.chat import LlmChat, UserMessage
from emergentintegrations.llm.openai import OpenAITextToSpeech
from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel

load_dotenv()

router = APIRouter(prefix="/api/ai", tags=["AI Services"])

EMERGENT_LLM_KEY = os.environ.get("EMERGENT_LLM_KEY", "")


# ---------------------------------------------------------------------------
# 1) Text-to-Speech
# ---------------------------------------------------------------------------

# Per-AI default voice mapping. Users can override via the `voice` field.
PERSONA_VOICES = {
    "ajani":   "onyx",     # deep / grounded
    "minerva": "nova",     # warm / flowing
    "hermes":  "echo",     # precise / clear
    "trinity": "shimmer",  # bright / layered
}


class TTSRequest(BaseModel):
    text: str
    persona: Optional[str] = None        # ajani | minerva | hermes | trinity
    voice: Optional[str] = None          # explicit voice overrides persona mapping
    model: str = "tts-1"
    speed: float = 1.0


@router.post("/tts")
async def synthesize_speech(req: TTSRequest):
    """Synthesize speech for an AI persona. Returns MP3 audio bytes."""
    if not EMERGENT_LLM_KEY:
        raise HTTPException(503, "AI services offline (missing EMERGENT_LLM_KEY)")
    if not req.text or not req.text.strip():
        raise HTTPException(400, "text is required")
    if len(req.text) > 4096:
        raise HTTPException(400, "text exceeds 4096 character limit")

    voice = req.voice or PERSONA_VOICES.get((req.persona or "").lower(), "alloy")
    try:
        tts = OpenAITextToSpeech(api_key=EMERGENT_LLM_KEY)
        audio_bytes = await tts.generate_speech(
            text=req.text,
            model=req.model,
            voice=voice,
            speed=req.speed,
        )
    except Exception as exc:
        raise HTTPException(500, f"TTS failed: {exc}")

    return Response(
        content=audio_bytes,
        media_type="audio/mpeg",
        headers={"X-AI-Voice": voice},
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
    """Return the per-persona voice mapping the frontend should use."""
    return {"voices": PERSONA_VOICES}
