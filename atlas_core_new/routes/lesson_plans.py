import json
from datetime import datetime, date, timedelta
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from atlas_core_new.db import SessionLocal
from atlas_core_new.core.curriculum.lesson_plans import (
    CURRICULUM, get_all_fields as get_curriculum_fields, get_field,
    get_subfield, get_chapter, calculate_field_total_time, estimate_completion_days
)
from atlas_core_new.routes._shared import openai_client, PERSONA_PROMPTS

router = APIRouter(tags=["lesson_plans"])


class StartFieldRequest(BaseModel):
    field_id: str
    daily_minutes: int = 30


class UpdateChapterProgressRequest(BaseModel):
    field_id: str
    subfield_id: str
    chapter_id: str
    study_minutes: int = 0
    status: str = "in_progress"


class SubmitTestRequest(BaseModel):
    field_id: str
    subfield_id: str
    chapter_id: str
    answers: list


class StudyTimerRequest(BaseModel):
    field_id: str
    subfield_id: str | None = None
    chapter_id: str | None = None
    minutes: int


class AIScheduleRequest(BaseModel):
    field_id: str
    daily_minutes: int = 30
    preferred_days: list | None = None


@router.get("/lesson-plans")
def get_all_lesson_plans():
    fields = get_curriculum_fields()
    return {"fields": fields, "total_fields": len(fields)}


@router.get("/lesson-plans/{field_id}")
def get_lesson_plan(field_id: str):
    field = get_field(field_id)
    if not field:
        return {"error": f"Field not found: {field_id}"}

    total_minutes = calculate_field_total_time(field_id)
    est_days_30 = estimate_completion_days(field_id, 30)
    est_days_60 = estimate_completion_days(field_id, 60)

    return {
        "field": field,
        "total_study_minutes": total_minutes,
        "estimated_days_30min": est_days_30,
        "estimated_days_60min": est_days_60
    }


@router.get("/lesson-plans/{field_id}/progress")
def get_field_progress_endpoint(field_id: str, user_id: str = "default_user"):
    db = SessionLocal()
    if db is None:
        return {"error": "Service temporarily unavailable. Please try again."}
    try:
        from atlas_core_new.db import FieldProgress, ChapterProgress

        field_prog = db.query(FieldProgress).filter(
            FieldProgress.user_id == user_id,
            FieldProgress.field_id == field_id
        ).first()

        if not field_prog:
            return {"started": False, "field_id": field_id}

        chapter_progs = db.query(ChapterProgress).filter(
            ChapterProgress.user_id == user_id,
            ChapterProgress.field_id == field_id
        ).all()

        return {
            "started": True,
            "field_id": field_id,
            "status": field_prog.status,
            "current_subfield": field_prog.current_subfield,
            "current_chapter": field_prog.current_chapter,
            "chapters_completed": field_prog.chapters_completed,
            "total_chapters": field_prog.total_chapters,
            "total_study_minutes": field_prog.total_study_minutes,
            "daily_goal_minutes": field_prog.daily_goal_minutes,
            "average_test_score": field_prog.average_test_score,
            "project_status": field_prog.project_status,
            "started_at": field_prog.started_at.isoformat() if field_prog.started_at else None,
            "chapters": [
                {
                    "subfield_id": cp.subfield_id,
                    "chapter_id": cp.chapter_id,
                    "chapter_number": cp.chapter_number,
                    "status": cp.status,
                    "study_minutes": cp.study_minutes,
                    "test_score": cp.test_score,
                    "test_passed": cp.test_passed
                }
                for cp in chapter_progs
            ]
        }
    finally:
        db.close()


@router.post("/lesson-plans/{field_id}/start")
def start_field_study(field_id: str, req: StartFieldRequest, user_id: str = "default_user"):
    db = SessionLocal()
    if db is None:
        return {"error": "Service temporarily unavailable. Please try again."}
    try:
        from atlas_core_new.db import FieldProgress, ChapterProgress

        field = get_field(field_id)
        if not field:
            return {"error": f"Field not found: {field_id}"}

        existing = db.query(FieldProgress).filter(
            FieldProgress.user_id == user_id,
            FieldProgress.field_id == field_id
        ).first()

        if existing:
            return {"error": "Already started this field", "field_id": field_id}

        total_chapters = sum(len(sf["chapters"]) for sf in field["subfields"])
        first_subfield = field["subfields"][0] if field["subfields"] else None

        field_prog = FieldProgress(
            user_id=user_id,
            field_id=field_id,
            status="in_progress",
            current_subfield=first_subfield["id"] if first_subfield else None,
            current_chapter=0,
            total_chapters=total_chapters,
            daily_goal_minutes=req.daily_minutes,
            started_at=datetime.utcnow()
        )
        db.add(field_prog)

        chapter_num = 0
        for sf in field["subfields"]:
            for ch in sf["chapters"]:
                chapter_num += 1
                ch_prog = ChapterProgress(
                    user_id=user_id,
                    field_id=field_id,
                    subfield_id=sf["id"],
                    chapter_id=ch["id"],
                    chapter_number=chapter_num,
                    status="not_started"
                )
                db.add(ch_prog)

        db.commit()

        return {
            "success": True,
            "field_id": field_id,
            "field_name": field["name"],
            "total_chapters": total_chapters,
            "daily_goal_minutes": req.daily_minutes,
            "first_subfield": first_subfield["name"] if first_subfield else None,
            "first_chapter": first_subfield["chapters"][0]["title"] if first_subfield else None
        }
    finally:
        db.close()


@router.post("/lesson-plans/chapter/update")
def update_chapter_progress(req: UpdateChapterProgressRequest, user_id: str = "default_user"):
    db = SessionLocal()
    if db is None:
        return {"error": "Service temporarily unavailable. Please try again."}
    try:
        from atlas_core_new.db import FieldProgress, ChapterProgress

        ch_prog = db.query(ChapterProgress).filter(
            ChapterProgress.user_id == user_id,
            ChapterProgress.field_id == req.field_id,
            ChapterProgress.subfield_id == req.subfield_id,
            ChapterProgress.chapter_id == req.chapter_id
        ).first()

        if not ch_prog:
            return {"error": "Chapter progress not found"}

        if req.status == "in_progress" and ch_prog.status == "not_started":
            ch_prog.started_at = datetime.utcnow()
        elif req.status == "completed" and ch_prog.status != "completed":
            ch_prog.completed_at = datetime.utcnow()

        ch_prog.status = req.status
        ch_prog.study_minutes += req.study_minutes

        field_prog = db.query(FieldProgress).filter(
            FieldProgress.user_id == user_id,
            FieldProgress.field_id == req.field_id
        ).first()

        if field_prog:
            field_prog.total_study_minutes += req.study_minutes
            field_prog.current_subfield = req.subfield_id

            if req.status == "completed":
                completed_count = db.query(ChapterProgress).filter(
                    ChapterProgress.user_id == user_id,
                    ChapterProgress.field_id == req.field_id,
                    ChapterProgress.status == "completed"
                ).count()
                field_prog.chapters_completed = completed_count

                if completed_count >= field_prog.total_chapters:
                    field_prog.status = "chapters_complete"

        db.commit()

        return {
            "success": True,
            "chapter_id": req.chapter_id,
            "status": req.status,
            "total_study_minutes": ch_prog.study_minutes
        }
    finally:
        db.close()


@router.post("/lesson-plans/chapter/test")
def submit_chapter_test(req: SubmitTestRequest, user_id: str = "default_user"):
    db = SessionLocal()
    if db is None:
        return {"error": "Service temporarily unavailable. Please try again."}
    try:
        from atlas_core_new.db import ChapterProgress, TestResult, FieldProgress

        chapter = get_chapter(req.field_id, req.subfield_id, req.chapter_id)
        if not chapter:
            return {"error": "Chapter not found"}

        attempt_count = db.query(TestResult).filter(
            TestResult.user_id == user_id,
            TestResult.field_id == req.field_id,
            TestResult.subfield_id == req.subfield_id,
            TestResult.chapter_id == req.chapter_id
        ).count()

        if openai_client:
            eval_response = openai_client.chat.completions.create(
                model="gpt-5",
                messages=[
                    {"role": "system", "content": f"""You are evaluating a student's test answers for the chapter: {chapter['title']}.
                    Score each answer 0-100 and provide brief feedback. Return JSON with:
                    {{"scores": [<score1>, <score2>, ...], "feedback": ["<feedback1>", ...], "overall_score": <0-100>, "passed": <true/false>, "summary": "<brief overall feedback>"}}
                    Passing score is 70%."""},
                    {"role": "user", "content": f"Student answers: {json.dumps(req.answers)}"}
                ],
                response_format={"type": "json_object"}
            )
            eval_data = json.loads(eval_response.choices[0].message.content)
        else:
            eval_data = {
                "scores": [70] * len(req.answers),
                "feedback": ["Unable to evaluate - AI not configured"] * len(req.answers),
                "overall_score": 70,
                "passed": True,
                "summary": "Test submitted but AI evaluation unavailable"
            }

        test_result = TestResult(
            user_id=user_id,
            field_id=req.field_id,
            subfield_id=req.subfield_id,
            chapter_id=req.chapter_id,
            questions=json.dumps([]),
            answers=json.dumps(req.answers),
            score=eval_data.get("overall_score", 0),
            passed=eval_data.get("passed", False),
            ai_feedback=eval_data.get("summary", ""),
            attempt_number=attempt_count + 1
        )
        db.add(test_result)

        if eval_data.get("passed"):
            ch_prog = db.query(ChapterProgress).filter(
                ChapterProgress.user_id == user_id,
                ChapterProgress.field_id == req.field_id,
                ChapterProgress.chapter_id == req.chapter_id
            ).first()
            if ch_prog:
                ch_prog.test_score = eval_data.get("overall_score", 0)
                ch_prog.test_passed = True
                ch_prog.status = "completed"
                ch_prog.completed_at = datetime.utcnow()

                field_prog = db.query(FieldProgress).filter(
                    FieldProgress.user_id == user_id,
                    FieldProgress.field_id == req.field_id
                ).first()
                if field_prog:
                    all_scores = db.query(ChapterProgress.test_score).filter(
                        ChapterProgress.user_id == user_id,
                        ChapterProgress.field_id == req.field_id,
                        ChapterProgress.test_passed == True
                    ).all()
                    if all_scores:
                        avg = sum(s[0] for s in all_scores if s[0]) / len(all_scores)
                        field_prog.average_test_score = avg

        db.commit()

        return {
            "success": True,
            "chapter_id": req.chapter_id,
            "score": eval_data.get("overall_score", 0),
            "passed": eval_data.get("passed", False),
            "feedback": eval_data.get("summary", ""),
            "detailed_feedback": eval_data.get("feedback", []),
            "attempt": attempt_count + 1
        }
    finally:
        db.close()


@router.post("/study-timer/log")
def log_study_time(req: StudyTimerRequest, user_id: str = "default_user"):
    db = SessionLocal()
    if db is None:
        return {"error": "Service temporarily unavailable. Please try again."}
    try:
        from atlas_core_new.db import StudySession, FieldProgress

        today = date.today()
        existing = db.query(StudySession).filter(
            StudySession.user_id == user_id,
            StudySession.field_id == req.field_id,
            StudySession.date >= datetime.combine(today, datetime.min.time()),
            StudySession.date < datetime.combine(today, datetime.max.time())
        ).first()

        if existing:
            existing.actual_minutes += req.minutes
            existing.completed = existing.actual_minutes >= existing.goal_minutes
            session = existing
        else:
            field_prog = db.query(FieldProgress).filter(
                FieldProgress.user_id == user_id,
                FieldProgress.field_id == req.field_id
            ).first()
            goal = field_prog.daily_goal_minutes if field_prog else 30

            session = StudySession(
                user_id=user_id,
                field_id=req.field_id,
                subfield_id=req.subfield_id,
                chapter_id=req.chapter_id,
                goal_minutes=goal,
                actual_minutes=req.minutes,
                completed=req.minutes >= goal
            )
            db.add(session)

        if field_prog := db.query(FieldProgress).filter(
            FieldProgress.user_id == user_id,
            FieldProgress.field_id == req.field_id
        ).first():
            field_prog.total_study_minutes += req.minutes

        db.commit()

        return {
            "success": True,
            "today_minutes": session.actual_minutes,
            "goal_minutes": session.goal_minutes,
            "completed": session.completed,
            "message": "Great work! Daily goal reached!" if session.completed else f"{session.goal_minutes - session.actual_minutes} minutes left today"
        }
    finally:
        db.close()


@router.get("/study-timer/today")
def get_today_study_status(field_id: str, user_id: str = "default_user"):
    db = SessionLocal()
    if db is None:
        return {"error": "Service temporarily unavailable. Please try again."}
    try:
        from atlas_core_new.db import StudySession, FieldProgress

        today = date.today()
        session = db.query(StudySession).filter(
            StudySession.user_id == user_id,
            StudySession.field_id == field_id,
            StudySession.date >= datetime.combine(today, datetime.min.time())
        ).first()

        field_prog = db.query(FieldProgress).filter(
            FieldProgress.user_id == user_id,
            FieldProgress.field_id == field_id
        ).first()

        goal = field_prog.daily_goal_minutes if field_prog else 30

        return {
            "field_id": field_id,
            "today_minutes": session.actual_minutes if session else 0,
            "goal_minutes": goal,
            "completed": session.completed if session else False,
            "remaining_minutes": max(0, goal - (session.actual_minutes if session else 0))
        }
    finally:
        db.close()


@router.post("/ai-scheduler/create")
def create_ai_study_schedule(req: AIScheduleRequest, user_id: str = "default_user"):
    db = SessionLocal()
    if db is None:
        return {"error": "Service temporarily unavailable. Please try again."}
    try:
        from atlas_core_new.db import StudySchedule, FieldProgress

        field = get_field(req.field_id)
        if not field:
            return {"error": f"Field not found: {req.field_id}"}

        field_prog = db.query(FieldProgress).filter(
            FieldProgress.user_id == user_id,
            FieldProgress.field_id == req.field_id
        ).first()

        total_minutes = calculate_field_total_time(req.field_id)
        remaining_chapters = field_prog.total_chapters - field_prog.chapters_completed if field_prog else sum(len(sf["chapters"]) for sf in field["subfields"])
        est_days = estimate_completion_days(req.field_id, req.daily_minutes)
        est_completion = datetime.utcnow() + timedelta(days=est_days)

        if openai_client:
            schedule_response = openai_client.chat.completions.create(
                model="gpt-5",
                messages=[
                    {"role": "system", "content": f"""Create a study schedule for the field: {field['name']}.
                    The student has {remaining_chapters} chapters remaining.
                    They want to study {req.daily_minutes} minutes per day.
                    Return JSON with: {{"weekly_plan": {{"monday": {{"topic": "...", "focus": "..."}}, ...}}, "tips": ["tip1", ...], "milestones": [{{"week": 1, "goal": "..."}}, ...]}}"""},
                    {"role": "user", "content": f"Preferred study days: {req.preferred_days or 'any'}"}
                ],
                response_format={"type": "json_object"}
            )
            ai_schedule = json.loads(schedule_response.choices[0].message.content)
        else:
            ai_schedule = {
                "weekly_plan": {"everyday": {"topic": "Study next chapter", "focus": "Consistent progress"}},
                "tips": ["Stay consistent", "Take breaks every 25 minutes", "Review before new material"],
                "milestones": [{"week": 1, "goal": "Complete first subfield"}]
            }

        schedule = StudySchedule(
            user_id=user_id,
            field_id=req.field_id,
            daily_minutes=req.daily_minutes,
            preferred_times=json.dumps(req.preferred_days) if req.preferred_days else None,
            weekly_schedule=json.dumps(ai_schedule.get("weekly_plan", {})),
            estimated_completion=est_completion,
            ai_recommendations=json.dumps(ai_schedule)
        )
        db.add(schedule)
        db.commit()

        return {
            "success": True,
            "field_id": req.field_id,
            "daily_minutes": req.daily_minutes,
            "estimated_completion": est_completion.isoformat(),
            "estimated_days": est_days,
            "schedule": ai_schedule
        }
    finally:
        db.close()


@router.get("/ai-scheduler/{field_id}")
def get_study_schedule(field_id: str, user_id: str = "default_user"):
    db = SessionLocal()
    if db is None:
        return {"error": "Service temporarily unavailable. Please try again."}
    try:
        from atlas_core_new.db import StudySchedule

        schedule = db.query(StudySchedule).filter(
            StudySchedule.user_id == user_id,
            StudySchedule.field_id == field_id,
            StudySchedule.is_active == True
        ).first()

        if not schedule:
            return {"exists": False, "field_id": field_id}

        return {
            "exists": True,
            "field_id": field_id,
            "daily_minutes": schedule.daily_minutes,
            "estimated_completion": schedule.estimated_completion.isoformat() if schedule.estimated_completion else None,
            "weekly_schedule": json.loads(schedule.weekly_schedule) if schedule.weekly_schedule else {},
            "recommendations": json.loads(schedule.ai_recommendations) if schedule.ai_recommendations else {}
        }
    finally:
        db.close()


@router.get("/ai-scheduler/{field_id}/nudge")
def get_ai_nudge(field_id: str, user_id: str = "default_user"):
    db = SessionLocal()
    if db is None:
        return {"error": "Service temporarily unavailable. Please try again."}
    try:
        from atlas_core_new.db import StudySession, FieldProgress, StudySchedule

        field = get_field(field_id)
        if not field:
            return {"error": "Field not found"}

        field_prog = db.query(FieldProgress).filter(
            FieldProgress.user_id == user_id,
            FieldProgress.field_id == field_id
        ).first()

        today = date.today()
        week_ago = today - timedelta(days=7)
        recent_sessions = db.query(StudySession).filter(
            StudySession.user_id == user_id,
            StudySession.field_id == field_id,
            StudySession.date >= datetime.combine(week_ago, datetime.min.time())
        ).all()

        days_studied = len(set(s.date.date() for s in recent_sessions))
        total_minutes_week = sum(s.actual_minutes for s in recent_sessions)

        context = {
            "field": field["name"],
            "chapters_completed": field_prog.chapters_completed if field_prog else 0,
            "total_chapters": field_prog.total_chapters if field_prog else "unknown",
            "days_studied_this_week": days_studied,
            "minutes_this_week": total_minutes_week,
            "lead_persona": field.get("lead_persona", "ajani")
        }

        if openai_client:
            persona = field.get("lead_persona", "ajani")
            nudge_response = openai_client.chat.completions.create(
                model="gpt-5",
                messages=[
                    {"role": "system", "content": PERSONA_PROMPTS.get(persona, PERSONA_PROMPTS["ajani"]) + """
                    Give a SHORT (2-3 sentences) encouraging nudge to help the student stay on track with their studies.
                    Be warm but direct. Reference their actual progress. Don't lecture - motivate."""},
                    {"role": "user", "content": f"My study stats: {json.dumps(context)}"}
                ],
                max_completion_tokens=200
            )
            nudge = nudge_response.choices[0].message.content
        else:
            nudge = f"You've studied {days_studied} days this week. Keep the momentum going!"

        return {
            "field_id": field_id,
            "persona": field.get("lead_persona", "ajani"),
            "nudge": nudge,
            "stats": {
                "days_studied_this_week": days_studied,
                "minutes_this_week": total_minutes_week,
                "chapters_completed": field_prog.chapters_completed if field_prog else 0
            }
        }
    finally:
        db.close()
