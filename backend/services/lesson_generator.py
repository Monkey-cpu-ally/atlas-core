"""
Lesson Plan Generator.

Given a Knowledge Bank record (typically just-ingested), produce a structured
lesson plan in ATLAS voice and persist it to the `lessons` collection.

Lesson schema:
  lesson_id, title, subject, skill_level, learning_objectives,
  simple_explanation, deeper_explanation, hands_on_project, quiz_questions,
  wrong_right_examples, vocabulary, related_sources, next_lesson_suggestion,
  source_url, source_knowledge_id, agent, created_at

Voice rules (from the user's brief):
  * Step-by-step, hands-on, Lego-style breakdown
  * 6th-9th grade explanation for hard topics
  * No robotic classroom tone
  * Include examples and mistakes to avoid
  * Connect to ATLAS projects when relevant

LLM is the existing services.llm_provider.send(persona, ...) — gpt-5.2 via
EMERGENT_LLM_KEY. We ask for JSON; if the model returns prose we fall back to
a structured-but-shallow lesson so the pipeline never fails open.
"""
from __future__ import annotations

import json
import logging
import os
import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4

from motor.motor_asyncio import AsyncIOMotorClient

from services import llm_provider, memory_bank as mb
from services import adaptation as ad

logger = logging.getLogger("atlas.lesson_generator")

MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.environ.get("DB_NAME", "test_database")
_client: Optional[AsyncIOMotorClient] = None


def _db():
    global _client
    if _client is None:
        _client = AsyncIOMotorClient(MONGO_URL)
    return _client[DB_NAME]


def _lessons(): return _db()["lessons"]


def _utc(): return datetime.now(timezone.utc).isoformat()


_SYS = """You are ATLAS — a hands-on, no-fluff teacher.
Speak like a sharp older friend explaining things at a workbench.
Use Lego-style breakdowns. Give 6th-9th grade analogies for hard topics.
Show wrong-vs-right examples. Mention real mistakes to avoid.
Never use robotic classroom tone. Be specific, not generic.

Return STRICT JSON matching this schema. No prose outside the JSON.

{
  "title": str,
  "subject": str,
  "skill_level": "beginner" | "intermediate" | "advanced",
  "learning_objectives": [str, str, str],
  "simple_explanation": str,
  "deeper_explanation": str,
  "hands_on_project": {
    "name": str,
    "steps": [str, str, str],
    "materials": [str]
  },
  "quiz_questions": [
    {"q": str, "a": str, "why": str}
  ],
  "wrong_right_examples": [
    {"wrong": str, "right": str}
  ],
  "vocabulary": [{"term": str, "meaning": str}],
  "related_sources": [str],
  "next_lesson_suggestion": str
}
"""


async def generate_lesson(
    *, knowledge_id: str, source_url: str, title: str,
    concepts: List[str], agent: str,
    mode: str = "default",
) -> Dict[str, Any]:
    """Generate + persist a lesson plan for the given knowledge entry.
    Bias the prompt with the user's learning profile (Step 2 integration).
    `mode` ∈ {default, adhd, lego, beginner, professional, certification}."""
    profile = await ad.get_learning_profile()
    bias_lines = []
    level = profile.get("preferred_explanation_level", "6-9grade")
    if level == "6-9grade":
        bias_lines.append("USER PREFERENCE · Open with a 6th-9th grade analogy BEFORE the technical depth.")
    elif level == "advanced":
        bias_lines.append("USER PREFERENCE · Go straight to advanced — skip beginner framing.")
    else:
        bias_lines.append("USER PREFERENCE · Intermediate level. Brief beginner setup, then technical.")
    fmt = profile.get("preferred_lesson_format", "lego_steps")
    if fmt == "lego_steps":
        bias_lines.append("USER PREFERENCE · Use Lego-style step breakdowns in the hands-on project.")
    if profile.get("hands_on_examples", True):
        bias_lines.append("USER PREFERENCE · Hands-on project must be tangible & executable, not abstract.")
    confusing = profile.get("confusing_topics") or []
    if confusing:
        names = ", ".join(c.get("topic", "")[:60] for c in confusing[-5:])
        bias_lines.append(f"USER STRUGGLES WITH (re-explain especially clearly if relevant): {names}")

    # Mode-specific styling overlay (Autonomous Research Orchestrator phase)
    MODE_OVERLAYS = {
        "adhd":         "MODE · ADHD-FRIENDLY: short paragraphs, 1 idea per chunk, frequent bolded keywords, no walls of text.",
        "lego":         "MODE · LEGO-STEPS: every step builds on the previous; explicit 'snap-this-onto-the-last-one' framing.",
        "beginner":     "MODE · BEGINNER: assume zero prior knowledge; analogies before vocabulary.",
        "professional": "MODE · PROFESSIONAL: terse, jargon-allowed, references-driven.",
        "certification": "MODE · CERTIFICATION-PREP: cover the test domain explicitly, end with a 5-question mock exam.",
        "default":      "",
    }
    overlay = MODE_OVERLAYS.get(mode, "")
    if overlay:
        bias_lines.append(overlay)
    bias_block = "\n".join(bias_lines)

    user_msg = (
        f"Write a hands-on lesson plan grounded in this source:\n\n"
        f"Title: {title}\n"
        f"Source URL: {source_url}\n"
        f"Key concepts: {', '.join(concepts[:8]) or 'general'}\n"
        f"Agent persona: {agent}\n\n"
        f"{bias_block}\n\n"
        f"Pick a skill level (beginner/intermediate/advanced) based on the concepts.\n"
        f"Make the hands-on project something a curious teen could actually try.\n"
        f"Quiz: 3-5 questions, each with why-it-matters.\n"
        f"Cite the source URL in `related_sources`.\n"
        f"Reply with the JSON only."
    )

    result = await llm_provider.send(agent or "minerva", _SYS, user_msg)
    raw = (result.get("text") or "").strip()
    data = _safe_json(raw)
    if not data:
        data = _fallback(title, concepts, source_url)

    lesson_id = uuid4().hex
    doc = {
        "id": lesson_id,
        "lesson_id": lesson_id,
        "title": data.get("title") or title,
        "subject": data.get("subject") or (concepts[0] if concepts else "general"),
        "skill_level": data.get("skill_level") or "intermediate",
        "learning_objectives": data.get("learning_objectives") or [],
        "simple_explanation": data.get("simple_explanation") or "",
        "deeper_explanation": data.get("deeper_explanation") or "",
        "hands_on_project": data.get("hands_on_project") or {},
        "quiz_questions": data.get("quiz_questions") or [],
        "wrong_right_examples": data.get("wrong_right_examples") or [],
        "vocabulary": data.get("vocabulary") or [],
        "related_sources": list({source_url, *(data.get("related_sources") or [])}),
        "next_lesson_suggestion": data.get("next_lesson_suggestion") or "",
        "source_url": source_url,
        "source_knowledge_id": knowledge_id,
        "agent": agent,
        "model_used": result.get("model_used"),
        "provider_used": result.get("provider_used"),
        "created_at": _utc(),
        "updated_at": _utc(),
        "profile_bias": {
            "explanation_level": level,
            "lesson_format": fmt,
            "hands_on": profile.get("hands_on_examples", True),
            "confusing_topics_count": len(confusing),
            "mode": mode,
        },
    }
    await _lessons().insert_one(doc)

    # mirror into memory_bank category=lesson so persona chat can cite it
    try:
        body = f"LESSON · {doc['title']}\n{doc['simple_explanation'][:600]}"
        await mb.auto_store(
            body, persona=agent or "minerva", category="lesson",
            source_type="lesson", source_id=lesson_id,
            tags=["lesson", f"subject:{_slug(doc['subject'])}",
                  f"level:{doc['skill_level']}", f"agent:{agent}"],
        )
    except Exception as exc:    # noqa: BLE001
        logger.warning("lesson MB mirror failed: %s", exc)

    return doc


async def list_lessons(limit: int = 50) -> List[Dict[str, Any]]:
    cur = _lessons().find({}, {"_id": 0}).sort("created_at", -1).limit(limit)
    return [d async for d in cur]


async def lessons_by_source(knowledge_id: str) -> List[Dict[str, Any]]:
    cur = _lessons().find({"source_knowledge_id": knowledge_id}, {"_id": 0})
    return [d async for d in cur]


# --- helpers ---------------------------------------------------------------
_JSON_RE = re.compile(r"\{.*\}", re.DOTALL)


def _safe_json(raw: str) -> Optional[Dict[str, Any]]:
    if not raw:
        return None
    try:
        return json.loads(raw)
    except Exception:    # noqa: BLE001
        pass
    m = _JSON_RE.search(raw)
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except Exception:    # noqa: BLE001
        return None


def _fallback(title: str, concepts: List[str], source_url: str) -> Dict[str, Any]:
    concept_preview = concepts[:6] or ["general"]
    return {
        "title": title,
        "subject": concept_preview[0],
        "skill_level": "intermediate",
        "learning_objectives": [f"Understand {c}" for c in concept_preview[:3]],
        "simple_explanation": (
            f"Quick take: this source covers {', '.join(concept_preview)}. "
            f"Treat each concept like a Lego block — learn one, then snap the next on top."
        ),
        "deeper_explanation": (
            f"Read the source, then sketch your own one-page diagram. "
            f"If you can re-draw it without peeking, you understand it."
        ),
        "hands_on_project": {
            "name": f"Mini-build around {concept_preview[0]}",
            "steps": [
                "Read the source end-to-end (skim first, then careful pass).",
                "List the 3 hardest words in your own terms.",
                "Make a small artefact: drawing, snippet, model — anything tangible.",
            ],
            "materials": ["paper", "pen", "the source URL above"],
        },
        "quiz_questions": [
            {"q": f"What does '{c}' mean?", "a": "...", "why": "core concept"}
            for c in concept_preview[:3]
        ],
        "wrong_right_examples": [{
            "wrong": "Memorise the terms verbatim",
            "right": "Re-explain each term using your own analogy",
        }],
        "vocabulary": [{"term": c, "meaning": "see source"} for c in concept_preview[:5]],
        "related_sources": [source_url],
        "next_lesson_suggestion": (
            f"Pick the most confusing concept ({concept_preview[0]}) and "
            f"go deeper on it."
        ),
    }


def _slug(s: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", (s or "").lower()).strip("-")
    return s[:48] or "x"
