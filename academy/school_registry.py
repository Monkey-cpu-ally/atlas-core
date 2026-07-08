"""School registry for ATLAS Academy."""

from __future__ import annotations

from typing import Dict, List

from .schemas import AcademySchool


SCHOOLS: Dict[str, AcademySchool] = {
    "storytelling": AcademySchool(
        name="School of Storytelling",
        lead_ai="Ajani",
        mission="Teach ATLAS to create original stories with conflict, emotion, structure, and consequence.",
        disciplines=["character", "conflict", "dialogue", "screenwriting", "plot", "theme", "pacing"],
        mastery_projects=[
            "Write an original short story blueprint.",
            "Write a mini screenplay with visual storytelling and distinct character voices.",
            "Improve a Frazier story idea without taking over the core vision.",
        ],
    ),
    "visual_development": AcademySchool(
        name="School of Visual Development",
        lead_ai="Hermes",
        mission="Teach ATLAS to design memorable visual identities through shape, silhouette, color, light, material, and function.",
        disciplines=["shape language", "silhouette", "concept art", "materials", "color", "lighting", "composition"],
        mastery_projects=[
            "Create a full visual development brief for an original ATLAS character.",
            "Create a color and lighting guide for a scene.",
            "Design a non-generic robot, vehicle, creature, or environment with material logic.",
        ],
    ),
    "animation": AcademySchool(
        name="School of Animation",
        lead_ai="Hermes",
        mission="Teach ATLAS movement, acting, timing, poses, expressions, and visual clarity.",
        disciplines=["timing", "spacing", "motion", "pose", "acting", "weight", "storyboards", "animatics"],
        mastery_projects=[
            "Build a movement sheet for a character or creature.",
            "Create a storyboard sequence with minimal dialogue.",
            "Create animation notes that show weight, anticipation, and follow-through.",
        ],
    ),
    "film": AcademySchool(
        name="School of Film",
        lead_ai="Council",
        mission="Teach ATLAS directing, cinematography, editing, production design, blocking, and scene construction.",
        disciplines=["directing", "cinematography", "editing", "blocking", "lighting", "production design"],
        mastery_projects=[
            "Create a shot list for a short scene.",
            "Direct a scene using camera, blocking, light, and silence.",
            "Analyze a sequence for pacing, emotion, and visual storytelling principles.",
        ],
    ),
}


def list_schools() -> List[AcademySchool]:
    return list(SCHOOLS.values())


def get_school(key: str) -> AcademySchool:
    return SCHOOLS[key]
