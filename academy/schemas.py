from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List


class MasteryLevel(str, Enum):
    INTRODUCTION = "Introduction"
    FOUNDATIONS = "Foundations"
    INTERMEDIATE = "Intermediate"
    ADVANCED = "Advanced"
    PROFESSIONAL = "Professional"
    MASTER = "Master"
    CREATIVE_DIRECTOR = "Creative Director"
    RESEARCH = "Research"
    INNOVATION = "Innovation"
    ATLAS_ORIGINAL = "ATLAS Original"


@dataclass(frozen=True)
class AcademySchool:
    name: str
    lead_ai: str
    mission: str
    disciplines: List[str]
    mastery_projects: List[str]


@dataclass(frozen=True)
class AcademyLesson:
    title: str
    school: str
    level: MasteryLevel
    principle: str
    exercise: str
    creative_challenge: str
    review_questions: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class AcademyProject:
    title: str
    school: str
    level: MasteryLevel
    goal: str
    deliverables: List[str]
    approval_standard: List[str]
