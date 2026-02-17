"""
atlas_core_new/db/__init__.py

Database package for Atlas Core persistence.
"""

from .models import (
    Base, UserProgress, LessonProgress, KnowledgePack, 
    PersonalProject, ProjectStep, Conversation, ChatMessage,
    Idea, LearningStreak, PatternInsight, BuildSession,
    FieldProgress, ChapterProgress, StudySession, TestResult,
    StudySchedule, FinalProject, ResearchTracker, ResearchActivityLog,
    ResearchResource
)
from .session import engine, SessionLocal, get_db, init_db

__all__ = [
    'Base', 'UserProgress', 'LessonProgress', 'KnowledgePack', 
    'PersonalProject', 'ProjectStep', 'Conversation', 'ChatMessage',
    'Idea', 'LearningStreak', 'PatternInsight', 'BuildSession',
    'FieldProgress', 'ChapterProgress', 'StudySession', 'TestResult',
    'StudySchedule', 'FinalProject', 'ResearchTracker', 'ResearchActivityLog',
    'ResearchResource',
    'engine', 'SessionLocal', 'get_db', 'init_db'
]
