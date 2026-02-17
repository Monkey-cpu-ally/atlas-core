import random
from datetime import datetime, timedelta
from fastapi import APIRouter
from pydantic import BaseModel
from atlas_core_new.utils.error_handling import sanitize_error
from atlas_core_new.db import (
    SessionLocal, Idea, LearningStreak, PatternInsight, BuildSession,
    PersonalProject, Conversation
)
from atlas_core_new.routes._shared import openai_client

router = APIRouter(tags=["user_data"])


class IdeaCreate(BaseModel):
    content: str
    category: str | None = None
    tags: str | None = None
    priority: int = 5


class SavedProjectCreate(BaseModel):
    title: str
    description: str = None
    field_id: str = None
    image_data: str = None
    project_data: dict = None


class InsightCreate(BaseModel):
    title: str
    content: str
    insight_type: str = "observation"
    source_persona: str | None = None
    related_topics: list | None = None


class BuildSessionCreate(BaseModel):
    project_id: int | None = None
    session_type: str = "build"


class PushSubscription(BaseModel):
    endpoint: str
    keys: dict
    user_id: str = "default_user"


push_subscriptions = {}


@router.get("/ideas")
def list_ideas(user_id: str = "default_user", status: str | None = None, limit: int = 50):
    db = SessionLocal()
    if db is None:
        return {"ideas": [], "error": "Service temporarily unavailable. Please try again."}
    try:
        query = db.query(Idea).filter(Idea.user_id == user_id)
        if status:
            query = query.filter(Idea.status == status)
        ideas = query.order_by(Idea.created_at.desc()).limit(limit).all()
        return {
            "ideas": [
                {
                    "id": i.id,
                    "content": i.content,
                    "category": i.category,
                    "tags": i.tags,
                    "priority": i.priority,
                    "status": i.status,
                    "linked_project_id": i.linked_project_id,
                    "ai_analysis": i.ai_analysis,
                    "created_at": i.created_at.isoformat()
                }
                for i in ideas
            ]
        }
    finally:
        db.close()


@router.post("/ideas")
def capture_idea(req: IdeaCreate, user_id: str = "default_user", analyze: bool = True):
    db = SessionLocal()
    if db is None:
        return {"error": "Service temporarily unavailable. Please try again."}
    try:
        ai_analysis = None
        if analyze and openai_client:
            try:
                response = openai_client.chat.completions.create(
                    model="gpt-5",
                    messages=[
                        {"role": "system", "content": "You are an idea analyzer. Given an idea, return JSON with: category (one of: project, invention, story, learning, improvement, random), suggested_tags (comma-separated), potential (1-10), next_steps (brief suggestion). Keep it concise."},
                        {"role": "user", "content": req.content}
                    ],
                    max_completion_tokens=256
                )
                ai_analysis = response.choices[0].message.content
            except:
                pass

        idea = Idea(
            user_id=user_id,
            content=req.content,
            category=req.category,
            tags=req.tags,
            priority=req.priority,
            ai_analysis=ai_analysis
        )
        db.add(idea)
        db.commit()
        db.refresh(idea)

        return {
            "id": idea.id,
            "content": idea.content,
            "category": idea.category,
            "ai_analysis": ai_analysis,
            "created_at": idea.created_at.isoformat()
        }
    finally:
        db.close()


@router.put("/ideas/{idea_id}/link/{project_id}")
def link_idea_to_project(idea_id: int, project_id: int):
    db = SessionLocal()
    if db is None:
        return {"error": "Service temporarily unavailable. Please try again."}
    try:
        idea = db.query(Idea).filter(Idea.id == idea_id).first()
        if not idea:
            return {"error": "Idea not found"}
        idea.linked_project_id = project_id
        idea.status = "developing"
        db.commit()
        return {"success": True, "idea_id": idea_id, "project_id": project_id}
    finally:
        db.close()


@router.get("/saved-projects")
def get_saved_projects(user_id: str = "default_user", limit: int = 50):
    db = SessionLocal()
    if db is None:
        return []
    try:
        from atlas_core_new.db.models import SavedProject
        projects = db.query(SavedProject).filter(
            SavedProject.user_id == user_id
        ).order_by(SavedProject.created_at.desc()).limit(limit).all()

        return [{
            "id": str(p.id),
            "title": p.title,
            "description": p.description,
            "field_id": p.field_id,
            "image_data": p.image_data,
            "project_data": p.project_data,
            "created_at": p.created_at.isoformat() if p.created_at else None
        } for p in projects]
    except Exception as e:
        print(f"Error loading saved projects: {e}")
        return []
    finally:
        db.close()


@router.post("/saved-projects")
def save_project(req: SavedProjectCreate, user_id: str = "default_user"):
    db = SessionLocal()
    if db is None:
        return {"error": "Service temporarily unavailable. Please try again."}
    try:
        from atlas_core_new.db.models import SavedProject
        project = SavedProject(
            user_id=user_id,
            title=req.title,
            description=req.description,
            field_id=req.field_id,
            image_data=req.image_data,
            project_data=req.project_data
        )
        db.add(project)
        db.commit()
        db.refresh(project)

        return {
            "id": str(project.id),
            "title": project.title,
            "created_at": project.created_at.isoformat() if project.created_at else None
        }
    except Exception as e:
        print(f"Error saving project: {e}")
        return {"error": sanitize_error(e)}
    finally:
        db.close()


@router.delete("/saved-projects/{project_id}")
def delete_saved_project(project_id: int, user_id: str = "default_user"):
    db = SessionLocal()
    if db is None:
        return {"error": "Service temporarily unavailable. Please try again."}
    try:
        from atlas_core_new.db.models import SavedProject
        project = db.query(SavedProject).filter(
            SavedProject.id == project_id,
            SavedProject.user_id == user_id
        ).first()
        if project:
            db.delete(project)
            db.commit()
            return {"success": True}
        return {"error": "Project not found"}
    finally:
        db.close()


@router.get("/streaks")
def get_streak(user_id: str = "default_user"):
    db = SessionLocal()
    if db is None:
        return {"error": "Service temporarily unavailable. Please try again."}
    try:
        streak = db.query(LearningStreak).filter(LearningStreak.user_id == user_id).first()
        if not streak:
            streak = LearningStreak(user_id=user_id)
            db.add(streak)
            db.commit()
            db.refresh(streak)

        return {
            "current_streak": streak.current_streak,
            "longest_streak": streak.longest_streak,
            "total_active_days": streak.total_active_days,
            "last_active": streak.last_active_date.isoformat() if streak.last_active_date else None,
            "streak_history": streak.streak_history
        }
    finally:
        db.close()


@router.post("/streaks/check-in")
def streak_check_in(user_id: str = "default_user"):
    db = SessionLocal()
    if db is None:
        return {"error": "Service temporarily unavailable. Please try again."}
    try:
        streak = db.query(LearningStreak).filter(LearningStreak.user_id == user_id).first()
        if not streak:
            streak = LearningStreak(user_id=user_id)
            db.add(streak)

        today = datetime.utcnow().date()
        last_active = streak.last_active_date.date() if streak.last_active_date else None

        if last_active == today:
            return {"message": "Already checked in today", "current_streak": streak.current_streak}

        if last_active == today - timedelta(days=1):
            streak.current_streak += 1
        elif last_active is None or (today - last_active).days > 1:
            streak.current_streak = 1

        if streak.current_streak > streak.longest_streak:
            streak.longest_streak = streak.current_streak

        streak.total_active_days += 1
        streak.last_active_date = datetime.utcnow()

        celebration = None
        if streak.current_streak in [7, 14, 30, 60, 100, 365]:
            celebration = f"Milestone! {streak.current_streak} day streak!"

        db.commit()

        return {
            "current_streak": streak.current_streak,
            "longest_streak": streak.longest_streak,
            "total_active_days": streak.total_active_days,
            "celebration": celebration
        }
    finally:
        db.close()


@router.get("/insights")
def list_insights(user_id: str = "default_user", insight_type: str | None = None, limit: int = 50):
    db = SessionLocal()
    if db is None:
        return {"insights": [], "error": "Service temporarily unavailable. Please try again."}
    try:
        query = db.query(PatternInsight).filter(PatternInsight.user_id == user_id)
        if insight_type:
            query = query.filter(PatternInsight.insight_type == insight_type)
        insights = query.order_by(PatternInsight.created_at.desc()).limit(limit).all()
        return {
            "insights": [
                {
                    "id": i.id,
                    "title": i.title,
                    "content": i.content,
                    "insight_type": i.insight_type,
                    "source_persona": i.source_persona,
                    "related_topics": i.related_topics,
                    "connections": i.connections,
                    "created_at": i.created_at.isoformat()
                }
                for i in insights
            ]
        }
    finally:
        db.close()


@router.post("/insights")
def save_insight(req: InsightCreate, user_id: str = "default_user"):
    db = SessionLocal()
    if db is None:
        return {"error": "Service temporarily unavailable. Please try again."}
    try:
        insight = PatternInsight(
            user_id=user_id,
            title=req.title,
            content=req.content,
            insight_type=req.insight_type,
            source_persona=req.source_persona,
            related_topics=req.related_topics
        )
        db.add(insight)
        db.commit()
        db.refresh(insight)
        return {
            "id": insight.id,
            "title": insight.title,
            "created_at": insight.created_at.isoformat()
        }
    finally:
        db.close()


@router.get("/build-sessions")
def list_build_sessions(user_id: str = "default_user", project_id: int | None = None, limit: int = 20):
    db = SessionLocal()
    if db is None:
        return {"sessions": [], "error": "Service temporarily unavailable. Please try again."}
    try:
        query = db.query(BuildSession).filter(BuildSession.user_id == user_id)
        if project_id:
            query = query.filter(BuildSession.project_id == project_id)
        sessions = query.order_by(BuildSession.started_at.desc()).limit(limit).all()
        return {
            "sessions": [
                {
                    "id": s.id,
                    "project_id": s.project_id,
                    "session_type": s.session_type,
                    "started_at": s.started_at.isoformat(),
                    "ended_at": s.ended_at.isoformat() if s.ended_at else None,
                    "duration_minutes": s.duration_minutes,
                    "milestones_hit": s.milestones_hit
                }
                for s in sessions
            ],
            "total_time": sum(s.duration_minutes for s in sessions)
        }
    finally:
        db.close()


@router.post("/build-sessions/start")
def start_build_session(req: BuildSessionCreate, user_id: str = "default_user"):
    db = SessionLocal()
    if db is None:
        return {"error": "Service temporarily unavailable. Please try again."}
    try:
        session = BuildSession(
            user_id=user_id,
            project_id=req.project_id,
            session_type=req.session_type
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        return {
            "session_id": session.id,
            "started_at": session.started_at.isoformat()
        }
    finally:
        db.close()


@router.post("/build-sessions/{session_id}/stop")
def stop_build_session(session_id: int, notes: str | None = None):
    db = SessionLocal()
    if db is None:
        return {"error": "Service temporarily unavailable. Please try again."}
    try:
        session = db.query(BuildSession).filter(BuildSession.id == session_id).first()
        if not session:
            return {"error": "Session not found"}

        session.ended_at = datetime.utcnow()
        delta = session.ended_at - session.started_at
        session.duration_minutes = int(delta.total_seconds() / 60)
        if notes:
            session.notes = notes

        celebration = None
        if session.duration_minutes >= 60:
            celebration = "Deep work session complete! Over an hour of focused building."
        elif session.duration_minutes >= 30:
            celebration = "Solid session! 30+ minutes of progress."

        db.commit()

        return {
            "session_id": session_id,
            "duration_minutes": session.duration_minutes,
            "celebration": celebration
        }
    finally:
        db.close()


@router.get("/morning-briefing")
def morning_briefing(user_id: str = "default_user"):
    db = SessionLocal()
    if db is None:
        return {"error": "Service temporarily unavailable. Please try again."}
    try:
        streak = db.query(LearningStreak).filter(LearningStreak.user_id == user_id).first()
        current_streak = streak.current_streak if streak else 0

        active_projects = db.query(PersonalProject).filter(
            PersonalProject.user_id == user_id,
            PersonalProject.status.in_(["planning", "in_progress"])
        ).limit(3).all()

        recent_ideas = db.query(Idea).filter(
            Idea.user_id == user_id,
            Idea.status == "captured"
        ).order_by(Idea.created_at.desc()).limit(3).all()

        briefing = {
            "greeting": _get_time_greeting(),
            "streak_status": {
                "days": current_streak,
                "message": _get_streak_message(current_streak)
            },
            "active_projects": [
                {"id": p.id, "name": p.name, "phase": p.current_phase}
                for p in active_projects
            ],
            "pending_ideas": len(recent_ideas),
            "persona_messages": {
                "ajani": "Ready to build. What's the first step today?",
                "minerva": "New day, new stories to discover. What narrative draws you?",
                "hermes": "Systems are waiting. Where shall we find patterns today?"
            }
        }

        return briefing
    finally:
        db.close()


@router.get("/project-nudges")
def get_project_nudges(user_id: str = "default_user", inactive_days: int = 3):
    db = SessionLocal()
    if db is None:
        return {"error": "Service temporarily unavailable. Please try again."}
    try:
        cutoff = datetime.utcnow() - timedelta(days=inactive_days)

        inactive_projects = db.query(PersonalProject).filter(
            PersonalProject.user_id == user_id,
            PersonalProject.status.in_(["planning", "in_progress"]),
            PersonalProject.updated_at < cutoff
        ).all()

        nudges = []
        persona_nudge_styles = {
            "ajani": [
                "This project awaits your hand. Shall we pick up where we left off?",
                "The blueprint is ready. One step forward?",
                "Warriors don't abandon their craft. Ready to continue?"
            ],
            "minerva": [
                "Your story here is unfinished. What chapter comes next?",
                "The threads of this project await weaving. Shall we continue?",
                "Memory fades without practice. Let's revisit this together."
            ],
            "hermes": [
                "System idle. Ready to resume operations?",
                "Patterns detected in this project. Analysis awaits continuation.",
                "Logic suggests completion brings satisfaction. Continue?"
            ]
        }

        for project in inactive_projects:
            days_inactive = (datetime.utcnow() - project.updated_at).days
            personas = project.assigned_personas or "all"
            persona = personas.split(",")[0].strip() if "," in personas else personas if personas != "all" else "ajani"
            messages = persona_nudge_styles.get(persona, persona_nudge_styles["ajani"])

            nudges.append({
                "project_id": project.id,
                "project_name": project.name,
                "days_inactive": days_inactive,
                "current_phase": project.current_phase,
                "persona": persona,
                "nudge_message": random.choice(messages),
                "urgency": "high" if days_inactive > 7 else "medium" if days_inactive > 3 else "low"
            })

        return {
            "nudges": nudges,
            "total_inactive": len(nudges),
            "checked_at": datetime.utcnow().isoformat()
        }
    finally:
        db.close()


@router.get("/focus-mode/{persona}")
def get_focus_mode(persona: str, user_id: str = "default_user"):
    persona = persona.lower()
    if persona not in ["ajani", "minerva", "hermes"]:
        return {"error": "Invalid persona. Choose ajani, minerva, or hermes."}

    focus_configs = {
        "ajani": {
            "persona": "ajani",
            "title": "Builder's Focus",
            "color_theme": "#8B4513",
            "background": "linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%)",
            "ambient": "workshop",
            "greeting": "Clear your mind. We build with intention.",
            "specialties": ["engineering", "strategy", "construction", "materials"],
            "focus_prompts": [
                "What are we building today?",
                "What's the next concrete step?",
                "What tool do you need?",
                "What's blocking progress?"
            ]
        },
        "minerva": {
            "persona": "minerva",
            "title": "Storyteller's Focus",
            "color_theme": "#4A235A",
            "background": "linear-gradient(135deg, #1a1a2e 0%, #2d1b3d 50%, #4a235a 100%)",
            "ambient": "library",
            "greeting": "Let the noise fade. Stories await.",
            "specialties": ["culture", "narrative", "mythology", "creativity"],
            "focus_prompts": [
                "What story calls to you?",
                "Who is your character today?",
                "What world shall we explore?",
                "What truth are you seeking?"
            ]
        },
        "hermes": {
            "persona": "hermes",
            "title": "Guardian's Focus",
            "color_theme": "#1B4F72",
            "background": "linear-gradient(135deg, #0a0a0f 0%, #1a2a3a 50%, #1b4f72 100%)",
            "ambient": "observatory",
            "greeting": "Silence. Observe. Understand.",
            "specialties": ["logic", "systems", "patterns", "safety"],
            "focus_prompts": [
                "What system needs analysis?",
                "What pattern do you see?",
                "What needs to be understood?",
                "What's the logical next step?"
            ]
        }
    }

    db = SessionLocal()
    if db is None:
        config = focus_configs[persona]
        config["active_projects"] = []
        config["recent_conversations"] = 0
        return config

    try:
        active_projects = db.query(PersonalProject).filter(
            PersonalProject.user_id == user_id,
            PersonalProject.assigned_personas.contains(persona),
            PersonalProject.status.in_(["planning", "in_progress"])
        ).limit(5).all()

        recent_convos = db.query(Conversation).filter(
            Conversation.user_id == user_id,
            Conversation.persona == persona
        ).count()

        config = focus_configs[persona]
        config["active_projects"] = [
            {"id": p.id, "name": p.name, "phase": p.current_phase}
            for p in active_projects
        ]
        config["recent_conversations"] = recent_convos

        return config
    finally:
        db.close()


@router.post("/push/subscribe")
def subscribe_push(subscription: PushSubscription):
    push_subscriptions[subscription.user_id] = {
        "endpoint": subscription.endpoint,
        "keys": subscription.keys,
        "subscribed_at": datetime.utcnow().isoformat()
    }
    return {
        "success": True,
        "message": "Successfully subscribed to notifications",
        "user_id": subscription.user_id
    }


@router.delete("/push/unsubscribe")
def unsubscribe_push(user_id: str = "default_user"):
    if user_id in push_subscriptions:
        del push_subscriptions[user_id]
        return {"success": True, "message": "Unsubscribed from notifications"}
    return {"success": False, "message": "No subscription found"}


@router.get("/push/status")
def push_status(user_id: str = "default_user"):
    is_subscribed = user_id in push_subscriptions
    return {
        "subscribed": is_subscribed,
        "subscription_info": push_subscriptions.get(user_id) if is_subscribed else None
    }


@router.get("/push/vapid-key")
def get_vapid_key():
    import os
    vapid_key = os.environ.get("VAPID_PUBLIC_KEY", "")
    return {
        "vapid_key": vapid_key,
        "configured": bool(vapid_key)
    }


@router.get("/widget/config")
def get_widget_config(user_id: str = "default_user"):
    db = SessionLocal()
    if db is None:
        return {
            "widgets": _get_default_widget_configs(),
            "shortcuts": _get_widget_shortcuts()
        }

    try:
        streak = db.query(LearningStreak).filter(LearningStreak.user_id == user_id).first()
        current_streak = streak.current_streak if streak else 0

        active_session = db.query(BuildSession).filter(
            BuildSession.user_id == user_id,
            BuildSession.ended_at == None
        ).first()

        recent_idea = db.query(Idea).filter(
            Idea.user_id == user_id
        ).order_by(Idea.created_at.desc()).first()

        return {
            "widgets": [
                {
                    "type": "streak_counter",
                    "title": "Learning Streak",
                    "data": {
                        "current": current_streak,
                        "icon": "flame",
                        "color": "#ff6b35" if current_streak > 0 else "#555"
                    },
                    "action": "/streaks/check-in",
                    "refresh_interval": 3600
                },
                {
                    "type": "quick_chat",
                    "title": "Ask the Council",
                    "data": {
                        "personas": ["ajani", "minerva", "hermes"],
                        "placeholder": "What's on your mind?"
                    },
                    "action": "/chat",
                    "refresh_interval": 0
                },
                {
                    "type": "build_timer",
                    "title": "Build Timer",
                    "data": {
                        "active": active_session is not None,
                        "session_id": active_session.id if active_session else None,
                        "project_id": active_session.project_id if active_session else None,
                        "started": active_session.started_at.isoformat() if active_session else None
                    },
                    "action": "/build-sessions",
                    "refresh_interval": 60
                },
                {
                    "type": "idea_capture",
                    "title": "Quick Idea",
                    "data": {
                        "last_idea": recent_idea.content[:50] + "..." if recent_idea and len(recent_idea.content) > 50 else (recent_idea.content if recent_idea else None),
                        "placeholder": "Capture a thought..."
                    },
                    "action": "/ideas",
                    "refresh_interval": 0
                }
            ],
            "shortcuts": _get_widget_shortcuts(),
            "theme": {
                "background": "#0a0a0f",
                "text": "#e0e0e0",
                "accent": "#ff6b35"
            }
        }
    finally:
        db.close()


def _get_time_greeting():
    hour = datetime.now().hour
    if hour < 12:
        return "Good morning"
    elif hour < 17:
        return "Good afternoon"
    else:
        return "Good evening"


def _get_streak_message(streak):
    if streak == 0:
        return "Start your streak today!"
    elif streak < 7:
        return f"{streak} day streak - building momentum!"
    elif streak < 30:
        return f"{streak} days strong - you're on fire!"
    else:
        return f"{streak} days - legendary consistency!"


def _get_default_widget_configs():
    return [
        {
            "type": "streak_counter",
            "title": "Learning Streak",
            "data": {"current": 0, "icon": "flame", "color": "#555"},
            "action": "/streaks/check-in",
            "refresh_interval": 3600
        },
        {
            "type": "quick_chat",
            "title": "Ask the Council",
            "data": {"personas": ["ajani", "minerva", "hermes"], "placeholder": "What's on your mind?"},
            "action": "/chat",
            "refresh_interval": 0
        }
    ]


def _get_widget_shortcuts():
    return [
        {"name": "Talk to Ajani", "icon": "hammer", "url": "/?persona=ajani", "color": "#8B4513"},
        {"name": "Talk to Minerva", "icon": "book", "url": "/?persona=minerva", "color": "#4A235A"},
        {"name": "Talk to Hermes", "icon": "shield", "url": "/?persona=hermes", "color": "#1B4F72"},
        {"name": "Trinity Counsel", "icon": "users", "url": "/?persona=trinity", "color": "#ff6b35"},
        {"name": "Capture Idea", "icon": "lightbulb", "url": "/?action=idea", "color": "#f1c40f"},
        {"name": "Start Timer", "icon": "clock", "url": "/?action=timer", "color": "#2ecc71"}
    ]
