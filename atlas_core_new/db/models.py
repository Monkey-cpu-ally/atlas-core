"""
atlas_core_new/db/models.py

SQLAlchemy ORM models for Atlas Core persistence.
Reference: python_database integration
"""

from datetime import datetime
from sqlalchemy import String, Text, Integer, Float, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from typing import Optional, List


class Base(DeclarativeBase):
    pass


class UserProgress(Base):
    """Tracks overall user learning progress."""
    __tablename__ = "user_progress"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(64), unique=True, index=True, default="default_user")
    current_field: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    current_lesson: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    total_lessons_completed: Mapped[int] = mapped_column(Integer, default=0)
    total_checkpoints_passed: Mapped[int] = mapped_column(Integer, default=0)
    learning_style: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    lessons: Mapped[List["LessonProgress"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class LessonProgress(Base):
    """Tracks progress on individual lessons."""
    __tablename__ = "lesson_progress"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(64), ForeignKey("user_progress.user_id"), index=True)
    field: Mapped[str] = mapped_column(String(64), index=True)
    lesson_id: Mapped[str] = mapped_column(String(128), index=True)
    lesson_title: Mapped[str] = mapped_column(String(256))
    status: Mapped[str] = mapped_column(String(32), default="not_started")
    current_step: Mapped[int] = mapped_column(Integer, default=0)
    total_steps: Mapped[int] = mapped_column(Integer, default=0)
    checkpoints_completed: Mapped[str] = mapped_column(Text, default="[]")
    mastery_level: Mapped[float] = mapped_column(Float, default=0.0)
    time_spent_minutes: Mapped[int] = mapped_column(Integer, default=0)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    user: Mapped["UserProgress"] = relationship(back_populates="lessons")


class KnowledgePack(Base):
    """Custom knowledge packs uploaded by users."""
    __tablename__ = "knowledge_packs"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(64), index=True, default="default_user")
    name: Mapped[str] = mapped_column(String(128), index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    category: Mapped[str] = mapped_column(String(64), default="general")
    persona_scope: Mapped[str] = mapped_column(String(64), default="all")
    content: Mapped[str] = mapped_column(Text)
    source_type: Mapped[str] = mapped_column(String(32), default="text")
    source_filename: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class PersonalProject(Base):
    """Personal projects tracked with LEGO build system."""
    __tablename__ = "personal_projects"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(64), index=True, default="default_user")
    name: Mapped[str] = mapped_column(String(256))
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    category: Mapped[str] = mapped_column(String(64), default="general")
    status: Mapped[str] = mapped_column(String(32), default="planning")
    priority: Mapped[int] = mapped_column(Integer, default=5)
    goal: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    parts_list: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    current_phase: Mapped[str] = mapped_column(String(64), default="ideation")
    assigned_personas: Mapped[str] = mapped_column(String(128), default="all")
    tags: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    steps: Mapped[List["ProjectStep"]] = relationship(back_populates="project", cascade="all, delete-orphan")


class ProjectStep(Base):
    """Individual steps in a personal project (LEGO-style)."""
    __tablename__ = "project_steps"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(Integer, ForeignKey("personal_projects.id"), index=True)
    step_number: Mapped[int] = mapped_column(Integer)
    title: Mapped[str] = mapped_column(String(256))
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    instructions: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    parts_needed: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    checkpoint: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="pending")
    is_milestone: Mapped[bool] = mapped_column(Boolean, default=False)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    project: Mapped["PersonalProject"] = relationship(back_populates="steps")


class Conversation(Base):
    """Chat conversation sessions with personas."""
    __tablename__ = "conversations"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(64), index=True, default="default_user")
    persona: Mapped[str] = mapped_column(String(32), index=True)
    title: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    message_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    messages: Mapped[List["ChatMessage"]] = relationship(back_populates="conversation", cascade="all, delete-orphan")


class ChatMessage(Base):
    """Individual chat messages within conversations."""
    __tablename__ = "chat_messages"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    conversation_id: Mapped[int] = mapped_column(Integer, ForeignKey("conversations.id"), index=True)
    role: Mapped[str] = mapped_column(String(16))
    persona: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    content: Mapped[str] = mapped_column(Text)
    tokens_used: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    extra_data: Mapped[Optional[str]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    conversation: Mapped["Conversation"] = relationship(back_populates="messages")


class Idea(Base):
    """Quick ideas captured for later development."""
    __tablename__ = "ideas"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(64), index=True, default="default_user")
    content: Mapped[str] = mapped_column(Text)
    category: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    tags: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    priority: Mapped[int] = mapped_column(Integer, default=5)
    status: Mapped[str] = mapped_column(String(32), default="captured")
    linked_project_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("personal_projects.id"), nullable=True)
    ai_analysis: Mapped[Optional[str]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class SavedProject(Base):
    """Saved projects and images for later reference."""
    __tablename__ = "saved_projects"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(64), index=True, default="default_user")
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    field_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    image_data: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    project_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class LearningStreak(Base):
    """Track daily learning streaks."""
    __tablename__ = "learning_streaks"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(64), unique=True, index=True, default="default_user")
    current_streak: Mapped[int] = mapped_column(Integer, default=0)
    longest_streak: Mapped[int] = mapped_column(Integer, default=0)
    total_active_days: Mapped[int] = mapped_column(Integer, default=0)
    last_active_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    streak_history: Mapped[Optional[str]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class PatternInsight(Base):
    """Track patterns and insights over time."""
    __tablename__ = "pattern_insights"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(64), index=True, default="default_user")
    insight_type: Mapped[str] = mapped_column(String(64), index=True)
    title: Mapped[str] = mapped_column(String(256))
    content: Mapped[str] = mapped_column(Text)
    source_persona: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    related_topics: Mapped[Optional[str]] = mapped_column(JSON, nullable=True)
    connections: Mapped[Optional[str]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class BuildSession(Base):
    """Track time spent on projects (Build Timer)."""
    __tablename__ = "build_sessions"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(64), index=True, default="default_user")
    project_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("personal_projects.id"), nullable=True)
    session_type: Mapped[str] = mapped_column(String(64), default="build")
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    ended_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    duration_minutes: Mapped[int] = mapped_column(Integer, default=0)
    milestones_hit: Mapped[Optional[str]] = mapped_column(JSON, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


class FieldProgress(Base):
    """Track user progress through entire fields of study."""
    __tablename__ = "field_progress"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(64), index=True, default="default_user")
    field_id: Mapped[str] = mapped_column(String(64), index=True)
    status: Mapped[str] = mapped_column(String(32), default="not_started")
    current_subfield: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    current_chapter: Mapped[int] = mapped_column(Integer, default=0)
    chapters_completed: Mapped[int] = mapped_column(Integer, default=0)
    total_chapters: Mapped[int] = mapped_column(Integer, default=0)
    total_study_minutes: Mapped[int] = mapped_column(Integer, default=0)
    daily_goal_minutes: Mapped[int] = mapped_column(Integer, default=30)
    average_test_score: Mapped[float] = mapped_column(Float, default=0.0)
    project_status: Mapped[str] = mapped_column(String(32), default="not_started")
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ChapterProgress(Base):
    """Track progress through individual chapters."""
    __tablename__ = "chapter_progress"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(64), index=True, default="default_user")
    field_id: Mapped[str] = mapped_column(String(64), index=True)
    subfield_id: Mapped[str] = mapped_column(String(128), index=True)
    chapter_id: Mapped[str] = mapped_column(String(64), index=True)
    chapter_number: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(32), default="not_started")
    study_minutes: Mapped[int] = mapped_column(Integer, default=0)
    test_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    test_passed: Mapped[bool] = mapped_column(Boolean, default=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class StudySession(Base):
    """Daily study timer sessions."""
    __tablename__ = "study_sessions"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(64), index=True, default="default_user")
    field_id: Mapped[str] = mapped_column(String(64), index=True)
    subfield_id: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    chapter_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    goal_minutes: Mapped[int] = mapped_column(Integer, default=30)
    actual_minutes: Mapped[int] = mapped_column(Integer, default=0)
    completed: Mapped[bool] = mapped_column(Boolean, default=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class TestResult(Base):
    """End of chapter test results."""
    __tablename__ = "test_results"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(64), index=True, default="default_user")
    field_id: Mapped[str] = mapped_column(String(64), index=True)
    subfield_id: Mapped[str] = mapped_column(String(128), index=True)
    chapter_id: Mapped[str] = mapped_column(String(64), index=True)
    questions: Mapped[str] = mapped_column(JSON)
    answers: Mapped[str] = mapped_column(JSON)
    score: Mapped[float] = mapped_column(Float, default=0.0)
    passed: Mapped[bool] = mapped_column(Boolean, default=False)
    passing_score: Mapped[float] = mapped_column(Float, default=70.0)
    ai_feedback: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    time_taken_minutes: Mapped[int] = mapped_column(Integer, default=0)
    attempt_number: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class StudySchedule(Base):
    """AI-generated study schedules."""
    __tablename__ = "study_schedules"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(64), index=True, default="default_user")
    field_id: Mapped[str] = mapped_column(String(64), index=True)
    schedule_type: Mapped[str] = mapped_column(String(32), default="daily")
    daily_minutes: Mapped[int] = mapped_column(Integer, default=30)
    preferred_times: Mapped[Optional[str]] = mapped_column(JSON, nullable=True)
    weekly_schedule: Mapped[Optional[str]] = mapped_column(JSON, nullable=True)
    estimated_completion: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    reminders_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    ai_recommendations: Mapped[Optional[str]] = mapped_column(JSON, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class FinalProject(Base):
    """Final projects for completed fields."""
    __tablename__ = "final_projects"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(64), index=True, default="default_user")
    field_id: Mapped[str] = mapped_column(String(64), index=True)
    title: Mapped[str] = mapped_column(String(256))
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    requirements: Mapped[Optional[str]] = mapped_column(JSON, nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="not_started")
    submission: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ai_evaluation: Mapped[Optional[str]] = mapped_column(JSON, nullable=True)
    score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    feedback: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    submitted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ResearchTracker(Base):
    """Tracks live progress of persona research projects."""
    __tablename__ = "research_tracker"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    persona: Mapped[str] = mapped_column(String(32), index=True)
    project_id: Mapped[str] = mapped_column(String(128), index=True)
    project_name: Mapped[str] = mapped_column(String(256))
    codename: Mapped[str] = mapped_column(String(128))
    current_phase: Mapped[str] = mapped_column(String(64))
    progress_percent: Mapped[int] = mapped_column(Integer, default=0)
    current_focus: Mapped[str] = mapped_column(Text, default="")
    last_breakthrough: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    knowledge_tier: Mapped[str] = mapped_column(String(32), default="conceptual_sandbox")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    design_intent: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    assumptions: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    known_unknowns: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    safety_constraints: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    review_stage: Mapped[str] = mapped_column(String(64), default="concept")
    supervisor_status: Mapped[str] = mapped_column(String(32), default="pending_review")
    feasibility_tier: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    engineering_validation: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    validation_status: Mapped[str] = mapped_column(String(32), default="not_validated")
    last_validated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ResearchActivityLog(Base):
    """Daily activity log entries for persona research."""
    __tablename__ = "research_activity_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    persona: Mapped[str] = mapped_column(String(32), index=True)
    project_id: Mapped[str] = mapped_column(String(128), index=True)
    activity_type: Mapped[str] = mapped_column(String(64))
    title: Mapped[str] = mapped_column(String(256))
    description: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ResearchResource(Base):
    """Curated real-world resources for persona research projects."""
    __tablename__ = "research_resource"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    persona: Mapped[str] = mapped_column(String(32), index=True)
    project_id: Mapped[str] = mapped_column(String(128), index=True)
    resource_type: Mapped[str] = mapped_column(String(64))
    title: Mapped[str] = mapped_column(String(512))
    description: Mapped[str] = mapped_column(Text)
    url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    source: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    year: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    is_evidence_based: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class SupervisorReview(Base):
    """Supervisor review records for research project gate decisions."""
    __tablename__ = "supervisor_reviews"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[str] = mapped_column(String(128), index=True)
    persona: Mapped[str] = mapped_column(String(32))
    review_stage: Mapped[str] = mapped_column(String(64))
    decision: Mapped[str] = mapped_column(String(32))
    decision_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    supervisor_questions: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ai_responses: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    safety_flags: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class BuildPlan(Base):
    """Build plans for research project fabrication and machine design."""
    __tablename__ = "build_plans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[str] = mapped_column(String(128), index=True)
    persona: Mapped[str] = mapped_column(String(32), index=True)
    plan_name: Mapped[str] = mapped_column(String(256))
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    build_type: Mapped[str] = mapped_column(String(64), default="component")
    status: Mapped[str] = mapped_column(String(32), default="designing")
    total_steps: Mapped[int] = mapped_column(Integer, default=0)
    completed_steps: Mapped[int] = mapped_column(Integer, default=0)
    safety_flags: Mapped[Optional[str]] = mapped_column(JSON, nullable=True)
    estimated_total_cost: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    cost_currency: Mapped[str] = mapped_column(String(8), default="USD")
    difficulty_level: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    tools_required_summary: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    fabrication_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    parts: Mapped[List["BuildPart"]] = relationship(back_populates="build_plan", cascade="all, delete-orphan")
    steps: Mapped[List["BuildStep"]] = relationship(back_populates="build_plan", cascade="all, delete-orphan")


class BuildPart(Base):
    """Parts and materials needed for a build plan."""
    __tablename__ = "build_parts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    build_plan_id: Mapped[int] = mapped_column(Integer, ForeignKey("build_plans.id"), index=True)
    part_name: Mapped[str] = mapped_column(String(256))
    part_type: Mapped[str] = mapped_column(String(64), default="material")
    specification: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    unit: Mapped[str] = mapped_column(String(32), default="pcs")
    sourcing_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_custom: Mapped[bool] = mapped_column(Boolean, default=False)
    status: Mapped[str] = mapped_column(String(32), default="needed")
    estimated_cost: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    fabrication_method: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    material_spec: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    dimensions: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    weight_grams: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    tolerance: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    file_format: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    supplier_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    build_plan: Mapped["BuildPlan"] = relationship(back_populates="parts")


class BuildStep(Base):
    """Step-by-step fabrication instructions for a build plan."""
    __tablename__ = "build_steps"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    build_plan_id: Mapped[int] = mapped_column(Integer, ForeignKey("build_plans.id"), index=True)
    step_number: Mapped[int] = mapped_column(Integer)
    title: Mapped[str] = mapped_column(String(256))
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    tools_needed: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    safety_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    expected_outcome: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="pending")
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    build_plan: Mapped["BuildPlan"] = relationship(back_populates="steps")


class DailyResearchLog(Base):
    """Daily research progress entries — what each AI worked on today."""
    __tablename__ = "daily_research_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[str] = mapped_column(String(128), index=True)
    persona: Mapped[str] = mapped_column(String(32), index=True)
    research_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    focus_area: Mapped[str] = mapped_column(String(256))
    findings: Mapped[str] = mapped_column(Text)
    next_steps: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    design_iterations: Mapped[Optional[str]] = mapped_column(JSON, nullable=True)
    blockers: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    guardrail_flags: Mapped[Optional[str]] = mapped_column(JSON, nullable=True)
    phase_before: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    phase_after: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    progress_delta: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ValidationPrepEntry(Base):
    """Validation Prep Layer — real-world references, required data, and path-to-proof checklists."""
    __tablename__ = "validation_prep_entries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[str] = mapped_column(String(128), index=True)
    persona: Mapped[str] = mapped_column(String(32), index=True)
    entry_type: Mapped[str] = mapped_column(String(64), default="reference")
    title: Mapped[str] = mapped_column(String(256))
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    source: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    data_required: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    tools_required: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    labs_required: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    proof_status: Mapped[str] = mapped_column(String(32), default="not_started")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class EmpiricalEntry(Base):
    """Empirical Bridge — manual-input-only entries for real measurements and test results."""
    __tablename__ = "empirical_entries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[str] = mapped_column(String(128), index=True)
    entered_by: Mapped[str] = mapped_column(String(64), default="supervisor")
    entry_type: Mapped[str] = mapped_column(String(64), default="measurement")
    title: Mapped[str] = mapped_column(String(256))
    value: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    unit: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    methodology: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    verified: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ExperimentRun(Base):
    """Discovery Pipeline — tracks a full Idea→Model→Simulate→Fail→Adjust cycle."""
    __tablename__ = "experiment_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    run_id: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    project_id: Mapped[str] = mapped_column(String(128), index=True)
    domain_primary: Mapped[str] = mapped_column(String(128), index=True)
    domain_secondary: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    intersection_hypothesis: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    phase: Mapped[str] = mapped_column(String(64), default="idea")
    innovation_level: Mapped[int] = mapped_column(Integer, default=1)
    innovation_label: Mapped[str] = mapped_column(String(64), default="creative_remix")
    hypothesis: Mapped[str] = mapped_column(Text)
    model_spec: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    sim_parameters: Mapped[Optional[str]] = mapped_column(JSON, nullable=True)
    sim_results: Mapped[Optional[str]] = mapped_column(JSON, nullable=True)
    iteration_count: Mapped[int] = mapped_column(Integer, default=0)
    max_iterations: Mapped[int] = mapped_column(Integer, default=100)
    status: Mapped[str] = mapped_column(String(32), default="active")
    assigned_personas: Mapped[Optional[str]] = mapped_column(JSON, nullable=True)
    constraint_set_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    failure_modes: Mapped[List["FailureMode"]] = relationship(back_populates="experiment", cascade="all, delete-orphan")
    iterations: Mapped[List["IterationLog"]] = relationship(back_populates="experiment", cascade="all, delete-orphan")


class FailureMode(Base):
    """Failure modes identified during simulation cycles."""
    __tablename__ = "failure_modes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    run_id: Mapped[str] = mapped_column(String(128), ForeignKey("experiment_runs.run_id"), index=True)
    failure_type: Mapped[str] = mapped_column(String(128))
    severity: Mapped[str] = mapped_column(String(32), default="medium")
    description: Mapped[str] = mapped_column(Text)
    evidence: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    mitigation: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    resolved: Mapped[bool] = mapped_column(Boolean, default=False)
    iteration_found: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    experiment: Mapped["ExperimentRun"] = relationship(back_populates="failure_modes")


class ConstraintSet(Base):
    """Physics/materials/manufacturing constraints for a domain or project."""
    __tablename__ = "constraint_sets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[str] = mapped_column(String(128), index=True)
    domain: Mapped[str] = mapped_column(String(128))
    physics_laws: Mapped[Optional[str]] = mapped_column(JSON, nullable=True)
    materials_available: Mapped[Optional[str]] = mapped_column(JSON, nullable=True)
    manufacturing_tools: Mapped[Optional[str]] = mapped_column(JSON, nullable=True)
    energy_requirements: Mapped[Optional[str]] = mapped_column(JSON, nullable=True)
    safety_profile: Mapped[Optional[str]] = mapped_column(JSON, nullable=True)
    failure_envelope: Mapped[Optional[str]] = mapped_column(JSON, nullable=True)
    cost_constraints: Mapped[Optional[str]] = mapped_column(JSON, nullable=True)
    custom_constraints: Mapped[Optional[str]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ResearchSource(Base):
    """Real web sources found during persona research — papers, articles, patents."""
    __tablename__ = "research_sources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[str] = mapped_column(String(128), index=True)
    persona: Mapped[str] = mapped_column(String(32), index=True)
    source_type: Mapped[str] = mapped_column(String(64))
    title: Mapped[str] = mapped_column(String(500))
    url: Mapped[str] = mapped_column(String(1000), default="")
    url_hash: Mapped[str] = mapped_column(String(32), index=True)
    authors: Mapped[Optional[str]] = mapped_column(JSON, nullable=True)
    published_date: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    abstract: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    citation_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    was_deep_read: Mapped[bool] = mapped_column(Boolean, default=False)
    search_query: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    content_excerpt: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class IterationLog(Base):
    """Logs each iteration of the Idea→Model→Simulate→Fail→Adjust loop."""
    __tablename__ = "iteration_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    run_id: Mapped[str] = mapped_column(String(128), ForeignKey("experiment_runs.run_id"), index=True)
    iteration_number: Mapped[int] = mapped_column(Integer)
    persona: Mapped[str] = mapped_column(String(32))
    action: Mapped[str] = mapped_column(String(64))
    input_data: Mapped[Optional[str]] = mapped_column(JSON, nullable=True)
    output_data: Mapped[Optional[str]] = mapped_column(JSON, nullable=True)
    adjustments: Mapped[Optional[str]] = mapped_column(JSON, nullable=True)
    failure_modes_found: Mapped[int] = mapped_column(Integer, default=0)
    score_before: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    score_after: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    experiment: Mapped["ExperimentRun"] = relationship(back_populates="iterations")
