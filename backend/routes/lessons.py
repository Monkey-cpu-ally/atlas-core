"""
Lesson routes (prefix /api/lessons).

GET   /api/lessons/generated        → recent lessons
GET   /api/lessons/by-source        → lessons for a given knowledge_id
GET   /api/lessons/{lesson_id}      → single lesson
"""
from fastapi import APIRouter, HTTPException, Query

from services import lesson_generator as lg

router = APIRouter(prefix="/api/lessons", tags=["Lessons"])


@router.get("/generated")
async def generated(limit: int = Query(50, ge=1, le=200)):
    items = await lg.list_lessons(limit=limit)
    return {"count": len(items), "items": items}


@router.get("/by-source")
async def by_source(knowledge_id: str = Query(...)):
    items = await lg.lessons_by_source(knowledge_id)
    return {"count": len(items), "items": items}


@router.get("/{lesson_id}")
async def fetch(lesson_id: str):
    items = await lg.list_lessons(limit=500)
    for it in items:
        if it.get("id") == lesson_id or it.get("lesson_id") == lesson_id:
            return it
    raise HTTPException(404, "lesson not found")
