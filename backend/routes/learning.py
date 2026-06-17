"""
Learning pipeline routes — knowledge, lessons, projects, mastery.

Mirrors the architect's schema (knowledge / lessons / projects /
students / mastery) into MongoDB collections. All endpoints prefixed
/api/learning/* so the HUD can drive the full intake → lesson →
project → quiz → mastery loop.
"""
import asyncio
import json
import logging
import os
import re
from datetime import datetime, timezone
from typing import List, Optional
from uuid import uuid4

from dotenv import load_dotenv
from emergentintegrations.llm.chat import LlmChat, UserMessage
from fastapi import APIRouter, HTTPException, Query
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field

from routing.topic_router import AI_DISPLAY

load_dotenv()
logger = logging.getLogger("atlas.learning")

router = APIRouter(prefix="/api/learning", tags=["Learning"])

MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.environ.get("DB_NAME", "test_database")
_client = AsyncIOMotorClient(MONGO_URL)
db = _client[DB_NAME]
knowledge_col = db["knowledge"]
lessons_col = db["lessons"]
projects_col = db["projects"]
mastery_col = db["mastery"]
students_col = db["students"]

EMERGENT_LLM_KEY = os.environ.get("EMERGENT_LLM_KEY", "")

# Single-architect mode for now — one row in students for the user.
ARCHITECT_ID = "architect-001"

PERSONA_VOICE = {
    "ajani":   ("You are Ajani, Zulu warrior-engineer. Speak with directness, "
                "physics, and structural focus. African cadence."),
    "minerva": ("You are Minerva, Yoruba wisdom keeper. Speak in living "
                "metaphor, ethics, and human-impact stories."),
    "hermes":  ("You are Hermes, Maasai pattern hunter. Be precise, pattern-"
                "oriented, occasionally witty."),
    "council": ("You are the Atlas Council — three voices speaking in turn. "
                "Be balanced and structural."),
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _new_id() -> str:
    return str(uuid4())


async def _llm(persona: str, prompt: str, max_tokens: int = 1200) -> str:
    """Single GPT-5.2 turn in the given persona's voice — reliable for
    the long sequential calls inside the intake pipeline."""
    sys = PERSONA_VOICE.get(persona, PERSONA_VOICE["council"])
    chat = LlmChat(
        api_key=EMERGENT_LLM_KEY,
        session_id=f"learning-{persona}-{_new_id()}",
        system_message=sys,
    ).with_model("openai", "gpt-5.2")
    try:
        raw = await chat.send_message(UserMessage(text=prompt))
    except Exception as exc:
        logger.warning("LLM call failed (persona=%s): %s", persona, exc)
        return ""
    return raw if isinstance(raw, str) else ""


def _extract_json(text: str) -> dict:
    fence = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if fence:
        text = fence.group(1)
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        return {}
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return {}


# ---------------------------------------------------------------------------
# Pipeline generators (called from /api/intake/* after transcript is fetched)
# ---------------------------------------------------------------------------
async def generate_lesson(topic: str, transcript: str, persona: str,
                          difficulty: str = "introductory") -> dict:
    """Build a structured persona-voiced lesson_text from a transcript.

    The lesson body has five learning surfaces (matching the architect's
    pedagogy spec): Lesson, Reflection, Nature Connections, Flashcards,
    and a placeholder Study Journal. Returns a dict ready to insert into
    the `lessons` collection.
    """
    snippet = transcript[:3500]
    prompt = (
        f"Topic: {topic}\n\n"
        f"Source material (excerpt):\n{snippet}\n\n"
        f"Write a {difficulty} lesson on this topic in YOUR voice. "
        "Return PURE JSON only, no markdown fences:\n"
        "{\n"
        '  "lesson": "≤350 word lesson body. Markdown allowed. Three subsections: '
        "## Core Idea, ## How It Works, ## Why It Matters.\",\n"
        '  "reflection": "≤120 words. A reflective question + a short personal '
        "framing the student should sit with.\",\n"
        '  "nature_connection": "≤120 words. How does this concept echo in nature, '
        "ecosystems, or human cultures? Cite one concrete example.\",\n"
        '  "flashcards": [\n'
        '    {"front": "term or question", "back": "≤25 word answer"}, ... 5 cards total\n'
        "  ],\n"
        '  "next_topic": "ONE adjacent topic the student should learn next, '
        "≤6 words.\"\n"
        "}"
    )
    raw = await _llm(persona, prompt, max_tokens=1500)
    parsed = _extract_json(raw) or {}
    return {
        "id": _new_id(),
        "topic": topic,
        "lesson_text": parsed.get("lesson") or "(lesson generation failed — please retry)",
        "reflection": parsed.get("reflection", ""),
        "nature_connection": parsed.get("nature_connection", ""),
        "flashcards": parsed.get("flashcards", [])[:8],
        "next_topic": parsed.get("next_topic", ""),
        "difficulty": difficulty,
        "ai_owner": persona,
        "date_added": _utc_now(),
    }


async def generate_project(topic: str, lesson_text: str, persona: str) -> dict:
    """Ask the lead persona to propose ONE hands-on project, parseable as JSON.

    Result matches the architect's projects schema fields (project_name,
    topic, instructions, ai_owner) while keeping the richer fields the
    HUD already renders (title/summary/steps/materials/expected_outcome).
    """
    prompt = (
        f"Based on the lesson below, propose ONE concrete hands-on project the "
        "student can actually build / do / observe. Return PURE JSON only:\n"
        '{"project_name": "...", "summary": "1-2 sentences", '
        '"steps": ["step 1", "step 2", "step 3", "step 4"], '
        '"materials": ["..."], "expected_outcome": "..."}\n\n'
        f"Topic: {topic}\n\nLesson:\n{lesson_text}\n\nReturn the JSON now."
    )
    raw = await _llm(persona, prompt, max_tokens=900)
    parsed = _extract_json(raw) or {
        "project_name": f"{topic} — hands-on exploration",
        "summary": "Auto-generated project (LLM parse fallback).",
        "steps": ["Read the lesson again.", "Identify one concept.",
                  "Try a small experiment.", "Reflect on what surprised you."],
        "materials": [],
        "expected_outcome": "A short write-up of what you learned.",
    }
    name = parsed.get("project_name") or parsed.get("title") or topic
    steps = parsed.get("steps", [])
    # Flatten steps into a single `instructions` field too — matches the
    # architect's projects table schema (project_name / topic / instructions / ai_owner).
    instructions = "\n".join(f"{i + 1}. {s}" for i, s in enumerate(steps))
    return {
        "id": _new_id(),
        "project_name": name,
        "title": name,                       # legacy alias for older UI bits
        "topic": topic,
        "summary": parsed.get("summary", ""),
        "instructions": instructions,
        "steps": steps,
        "materials": parsed.get("materials", []),
        "expected_outcome": parsed.get("expected_outcome", ""),
        "status": "proposed",
        "ai_owner": persona,
        "date_added": _utc_now(),
    }


async def persist_pipeline(*, topic: str, source: str, transcript: str,
                            summary: str, persona: str,
                            quiz: list, title: Optional[str] = None) -> dict:
    """Persist a full intake → lesson → project pipeline run.

    Called from /api/intake/youtube and /api/intake/transcript.
    Returns the IDs of every row that was written.
    """
    knowledge_doc = {
        "id": _new_id(),
        "title": title or topic,
        "topic": topic,
        "source": source,
        "transcript": transcript[:8000],   # cap row size; full preview elsewhere
        "summary": summary,
        "ai_owner": persona,
        "date_added": _utc_now(),
    }
    lesson_doc = await generate_lesson(topic, transcript, persona)
    project_doc = await generate_project(topic, lesson_doc["lesson_text"], persona)

    # Cross-link
    lesson_doc["knowledge_id"] = knowledge_doc["id"]
    lesson_doc["quiz"] = quiz
    project_doc["knowledge_id"] = knowledge_doc["id"]
    project_doc["lesson_id"] = lesson_doc["id"]

    await asyncio.gather(
        knowledge_col.insert_one(knowledge_doc.copy()),
        lessons_col.insert_one(lesson_doc.copy()),
        projects_col.insert_one(project_doc.copy()),
    )

    # --- Phase 2: write to long-term memory bank ----------------------------
    # Lesson + intake source are decaying knowledge (reinforced when the
    # student revisits them); the spawned project is permanent.
    from services import memory_bank as _mb     # local import to avoid cycle
    lesson_body = (
        f"{lesson_doc.get('topic', '')}\n\n"
        f"{lesson_doc.get('lesson_text', '')}\n\n"
        f"Reflection: {lesson_doc.get('reflection', '')}\n"
        f"Nature: {lesson_doc.get('nature_connection', '')}"
    ).strip()
    project_body = (
        f"PROJECT: {project_doc.get('project_name', '')}\n"
        f"{project_doc.get('summary', '')}\n"
        f"Outcome: {project_doc.get('expected_outcome', '')}"
    ).strip()
    intake_body = (
        f"INTAKE [{source}] · {title or topic}\n{(summary or '')[:600]}"
    ).strip()
    await asyncio.gather(
        _mb.auto_store(lesson_body, persona=persona, category="lesson",
                       source_type="lesson", source_id=lesson_doc["id"],
                       tags=[topic]),
        _mb.auto_store(project_body, persona=persona, category="project",
                       source_type="project", source_id=project_doc["id"],
                       tags=[topic]),
        _mb.auto_store(intake_body, persona=persona, category="intake",
                       source_type="intake", source_id=knowledge_doc["id"],
                       tags=[topic]),
    )
    return {
        "knowledge_id": knowledge_doc["id"],
        "lesson_id": lesson_doc["id"],
        "project_id": project_doc["id"],
        "lesson": {k: v for k, v in lesson_doc.items() if k != "_id"},
        "project": {k: v for k, v in project_doc.items() if k != "_id"},
    }


# ---------------------------------------------------------------------------
# READ endpoints
# ---------------------------------------------------------------------------
@router.get("/knowledge")
async def list_knowledge(limit: int = Query(40, ge=1, le=200), topic: Optional[str] = None):
    q = {"topic": topic} if topic else {}
    cursor = knowledge_col.find(q, {"_id": 0, "transcript": 0}).sort("date_added", -1).limit(limit)
    rows = await cursor.to_list(length=limit)
    return {"count": len(rows), "items": rows}


@router.get("/lessons")
async def list_lessons(limit: int = Query(40, ge=1, le=200), topic: Optional[str] = None,
                       ai_owner: Optional[str] = None):
    q = {}
    if topic:
        q["topic"] = topic
    if ai_owner:
        q["ai_owner"] = ai_owner.lower()
    cursor = lessons_col.find(q, {"_id": 0}).sort("date_added", -1).limit(limit)
    rows = await cursor.to_list(length=limit)
    return {"count": len(rows), "items": rows}


@router.get("/lessons/{lesson_id}")
async def get_lesson(lesson_id: str):
    doc = await lessons_col.find_one({"id": lesson_id}, {"_id": 0})
    if not doc:
        raise HTTPException(404, "lesson not found")
    return doc


@router.get("/projects")
async def list_projects(limit: int = Query(40, ge=1, le=200), status: Optional[str] = None,
                        ai_owner: Optional[str] = None):
    q = {}
    if status:
        q["status"] = status
    if ai_owner:
        q["ai_owner"] = ai_owner.lower()
    cursor = projects_col.find(q, {"_id": 0}).sort("date_added", -1).limit(limit)
    rows = await cursor.to_list(length=limit)
    return {"count": len(rows), "items": rows}


class ProjectStatusUpdate(BaseModel):
    status: str = Field(pattern="^(proposed|in_progress|completed|archived)$")


@router.put("/projects/{project_id}/status")
async def update_project_status(project_id: str, update: ProjectStatusUpdate):
    res = await projects_col.update_one(
        {"id": project_id},
        {"$set": {"status": update.status, "updated_at": _utc_now()}},
    )
    if res.matched_count == 0:
        raise HTTPException(404, "project not found")
    doc = await projects_col.find_one({"id": project_id}, {"_id": 0})
    return doc


# ---------------------------------------------------------------------------
# Quiz submission + LLM grading → mastery write
# ---------------------------------------------------------------------------
class QuizAnswer(BaseModel):
    question: str
    answer: str


class QuizSubmission(BaseModel):
    answers: List[QuizAnswer]


async def _grade_answer(persona: str, question: str, answer: str) -> dict:
    """Score one free-text answer 0..100 with a one-line rationale."""
    if not answer.strip():
        return {"score": 0, "feedback": "No answer provided."}
    prompt = (
        f"Grade this short answer on a 0-100 scale.\n"
        f"Question: {question}\n"
        f"Answer: {answer}\n\n"
        'Return JSON only: {"score": <int 0-100>, "feedback": "<≤25 words>"}\n'
        "Be strict but fair. 70+ requires the student to surface the correct mechanism."
    )
    raw = await _llm(persona, prompt, max_tokens=200)
    parsed = _extract_json(raw)
    score = parsed.get("score", 0)
    try:
        score = max(0, min(100, int(score)))
    except (TypeError, ValueError):
        score = 0
    return {
        "score": score,
        "feedback": str(parsed.get("feedback", "")).strip() or "Reviewed.",
    }


@router.post("/lessons/{lesson_id}/quiz")
async def submit_quiz(lesson_id: str, sub: QuizSubmission):
    lesson = await lessons_col.find_one({"id": lesson_id}, {"_id": 0})
    if not lesson:
        raise HTTPException(404, "lesson not found")
    persona = lesson.get("ai_owner", "council")
    quiz = lesson.get("quiz", [])
    if not quiz:
        raise HTTPException(400, "lesson has no quiz attached")

    # Grade every answer in parallel.
    graded = await asyncio.gather(*[
        _grade_answer(persona, q.get("question", sub.answers[i].question), sub.answers[i].answer)
        for i, q in enumerate(quiz[: len(sub.answers)])
    ])

    overall = round(sum(g["score"] for g in graded) / max(1, len(graded)))
    rank_idx = 4 if overall >= 90 else 3 if overall >= 75 else 2 if overall >= 55 else 1 if overall >= 35 else 0
    rank_label = ["Aware", "Understand", "Apply", "Design", "Teach"][rank_idx]

    mastery_doc = {
        "id": _new_id(),
        "student_id": ARCHITECT_ID,
        "topic": lesson["topic"],
        "lesson_id": lesson_id,
        "ai_owner": persona,
        "score": overall,
        "rank": rank_label,
        "per_question": [
            {"question": (sub.answers[i].question or quiz[i].get("question", "")),
             "answer": sub.answers[i].answer,
             "score": g["score"], "feedback": g["feedback"]}
            for i, g in enumerate(graded)
        ],
        "date_added": _utc_now(),
    }
    await mastery_col.insert_one(mastery_doc.copy())

    return {
        "lesson_id": lesson_id,
        "overall_score": overall,
        "rank": rank_label,
        "per_question": mastery_doc["per_question"],
        "mastery_id": mastery_doc["id"],
    }


@router.get("/mastery")
async def mastery_summary(topic: Optional[str] = None, limit: int = Query(60, ge=1, le=200)):
    q = {"student_id": ARCHITECT_ID}
    if topic:
        q["topic"] = topic
    cursor = mastery_col.find(q, {"_id": 0, "per_question": 0}).sort("date_added", -1).limit(limit)
    rows = await cursor.to_list(length=limit)
    # Aggregate per-topic best
    best_per_topic: dict[str, dict] = {}
    for r in rows:
        t = r["topic"]
        if t not in best_per_topic or r["score"] > best_per_topic[t]["best_score"]:
            best_per_topic[t] = {
                "topic": t,
                "best_score": r["score"],
                "best_rank": r["rank"],
                "ai_owner": r["ai_owner"],
                "last_attempt": r["date_added"],
                "display": AI_DISPLAY.get(r["ai_owner"], AI_DISPLAY["council"]),
            }
    return {
        "count": len(rows),
        "history": rows,
        "best_per_topic": list(best_per_topic.values()),
    }


# ---------------------------------------------------------------------------
# Study Journal — free-form architect notes attached to a lesson
# ---------------------------------------------------------------------------
journal_col = db["study_journal"]


class JournalEntry(BaseModel):
    lesson_id: str = Field(min_length=1)
    body: str = Field(min_length=1, max_length=5000)


@router.post("/journal")
async def add_journal_entry(entry: JournalEntry):
    doc = {
        "id": _new_id(),
        "student_id": ARCHITECT_ID,
        "lesson_id": entry.lesson_id,
        "body": entry.body,
        "date_added": _utc_now(),
    }
    await journal_col.insert_one(doc.copy())
    return doc


@router.get("/journal/{lesson_id}")
async def list_journal_entries(lesson_id: str, limit: int = Query(40, ge=1, le=200)):
    cursor = journal_col.find({"lesson_id": lesson_id}, {"_id": 0}).sort("date_added", -1).limit(limit)
    rows = await cursor.to_list(length=limit)
    return {"count": len(rows), "items": rows}
