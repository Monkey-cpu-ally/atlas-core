"""
Knowledge Distiller — LLM-driven structured distillation.

Reads a FetchedSource, asks the architect-routed persona to extract:
  * title (≤ 90 chars)
  * summary (3-6 sentences, ATLAS's own wording)
  * key_points[] (3-7 bullets)
  * tags[] (lower-case, ≤ 8)
  * concepts[] (graph nodes, ≤ 5)
  * confidence_score (0..1)

The system prompt explicitly forbids verbatim copying of long passages
(copyright + the spec's "do not store raw text" rule). Graceful JSON
extraction handles fenced / preambled responses.

Persona routing:
  ajani   — engineering, robotics, manufacturing, strategy, blueprints
  minerva — science, agriculture, medicine, education, research
  hermes  — math, logic, validation, optimization, software, code review
  council — cross-cutting / fallback
"""
import json
import logging
import re
from typing import Optional

from models.knowledge_models import Distillation, FetchedSource
from services.llm_provider import send as llm_send

logger = logging.getLogger("atlas.knowledge_distiller")

# --- Agent routing rules ----------------------------------------------------
_AGENT_KEYWORDS = {
    "ajani":   [
        "engineering", "engineer", "manufactur", "robot", "robotics",
        "blueprint", "fabrication", "assembly", "factory", "strategy",
        "drone", "motor", "actuator", "vehicle", "rocket", "cad",
    ],
    "minerva": [
        "science", "physics", "biolog", "chemistry", "agricultur", "farm",
        "plant", "medic", "doctor", "education", "teach", "learn",
        "research", "ecology", "environment", "ecosystem", "climate",
    ],
    "hermes":  [
        "math", "logic", "algorithm", "proof", "theorem", "validation",
        "optimization", "optimisation", "software", "code", "code review",
        "compile", "lint", "test", "type system", "complexity",
    ],
}


def route_agent(text: str, suggested_tags: Optional[list] = None) -> str:
    """Return the lead persona based on keyword density."""
    blob = (text or "").lower()
    if suggested_tags:
        blob += " " + " ".join(t.lower() for t in suggested_tags)
    scores = {p: 0 for p in _AGENT_KEYWORDS}
    for persona, kws in _AGENT_KEYWORDS.items():
        for kw in kws:
            scores[persona] += blob.count(kw)
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "council"


# --- Per-persona system prompts --------------------------------------------
_BASE_RULES = (
    "You are an ATLAS persona distilling an external source into long-term memory. "
    "STRICT RULES:\n"
    "  • Rewrite in YOUR OWN wording — do NOT copy more than 15 consecutive words verbatim.\n"
    "  • Be concise. Summary = 3-6 sentences. Key points = 3-7 short bullets.\n"
    "  • Tags = lower-case single words / short phrases, max 8.\n"
    "  • Concepts = graph-friendly nouns the architect would want to link, max 5.\n"
    "  • confidence_score in [0, 1] — how clearly the source supports the summary.\n"
    "Return STRICT JSON only. No markdown, no preamble.\n"
)

_PERSONA_VOICE = {
    "ajani":   "You are Ajani, Zulu warrior-engineer. Focus on what can be BUILT and what FAILS.",
    "minerva": "You are Minerva, Greek goddess of wisdom and science. Focus on principles and consequences.",
    "hermes":  "You are Hermes, Maasai pattern hunter. Focus on patterns, contradictions, and optimisations.",
    "council": "You are the ATLAS Council. Synthesise across engineering, science, and validation.",
}


async def distill(source: FetchedSource, *, force_agent: Optional[str] = None) -> Distillation:
    persona = (force_agent or "").lower().strip() or route_agent(
        f"{source.title or ''}\n{source.text[:1500]}",
    )
    if persona not in _PERSONA_VOICE:
        persona = "council"

    system = _PERSONA_VOICE[persona] + "\n\n" + _BASE_RULES + (
        '\nSchema:\n{"title":"≤90 chars","summary":"...","key_points":["..."],'
        '"tags":["..."],"concepts":["..."],"confidence_score":0.0}'
    )
    user = (
        f"SOURCE TYPE: {source.source_type.value}\n"
        f"URL: {source.source_url}\n"
        f"TITLE HINT: {source.title or '—'}\n"
        f"AUTHOR HINT: {source.author or '—'}\n\n"
        f"MATERIAL:\n---\n{source.text[:6000]}\n---\n\n"
        "Distil this into the JSON schema. Remember: own wording, concise, no verbatim copying."
    )
    try:
        res = await llm_send(persona, system, user,
                             session_id=f"knowledge-distill-{persona}")
        raw = (res.get("text") or "").strip()
    except Exception as exc:    # noqa: BLE001
        logger.warning("distill LLM call failed: %s", exc)
        return _fallback(source, persona)

    payload = _extract_json(raw)
    if not isinstance(payload, dict):
        return _fallback(source, persona)

    return Distillation(
        title=str(payload.get("title") or source.title or "Untitled source")[:200],
        summary=str(payload.get("summary") or "").strip(),
        key_points=_list_strs(payload.get("key_points"), limit=7),
        tags=_list_strs(payload.get("tags"), limit=8, lower=True),
        concepts=_list_strs(payload.get("concepts"), limit=5),
        confidence_score=_clip(float(payload.get("confidence_score") or 0.6)),
        suggested_agent=persona,
    )


# --- Helpers ----------------------------------------------------------------
def _extract_json(raw: str):
    if not raw:
        return None
    raw = re.sub(r"```(?:json)?", "", raw).replace("```", "")
    m = re.search(r"\{[\s\S]*\}", raw)
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except json.JSONDecodeError:
        return None


def _list_strs(value, *, limit: int, lower: bool = False) -> list:
    if not isinstance(value, list):
        return []
    out = []
    for v in value:
        s = str(v).strip()
        if not s:
            continue
        if lower:
            s = s.lower()
        if s not in out:
            out.append(s)
        if len(out) >= limit:
            break
    return out


def _clip(x: float) -> float:
    return max(0.0, min(1.0, round(x, 3)))


def _fallback(source: FetchedSource, persona: str) -> Distillation:
    """LLM unavailable / returned garbage — write a minimal honest record."""
    text = source.text or ""
    first = text[:400].replace("\n", " ").strip()
    return Distillation(
        title=(source.title or "Untitled source")[:200],
        summary=(first or "(no usable text extracted)"),
        key_points=[],
        tags=[source.source_type.value],
        concepts=[],
        confidence_score=0.20,
        suggested_agent=persona,
    )
