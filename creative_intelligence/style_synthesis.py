"""Style synthesis for ATLAS.

Turns creator-study lessons into ATLAS-native direction.
"""

from __future__ import annotations

from typing import Iterable, List

from .schemas import CraftLesson, CreativeBrief


ATLAS_STYLE_PILLARS = [
    "Layered functional design instead of generic shapes.",
    "Visual storytelling before exposition.",
    "Myth, technology, nature, and emotion working together.",
    "Honest consequences: injuries, choices, grief, repair, and growth matter.",
    "Worlds should feel lived-in, engineered, spiritual, and historically scarred.",
    "Beauty and danger should share the frame.",
]


def synthesize_atlas_direction(brief: CreativeBrief, lessons: Iterable[CraftLesson]) -> str:
    lesson_names = ", ".join(lesson.creator_name for lesson in lessons)
    style_notes = "; ".join(brief.user_style_notes) if brief.user_style_notes else "No extra user style notes supplied."
    constraints = "; ".join(brief.constraints) if brief.constraints else "No extra constraints supplied."

    return (
        f"Create '{brief.title}' as an original ATLAS work in the {brief.genre} space. "
        f"The target emotion is {brief.target_emotion}. "
        f"Use craft lessons from: {lesson_names}. "
        "Transform those lessons through the ATLAS pillars: "
        + " ".join(ATLAS_STYLE_PILLARS)
        + f" User style notes: {style_notes}. Constraints: {constraints}. "
        "The result must feel like Frazier/ATLAS, not like a direct imitation of any source."
    )


def build_scene_rules() -> List[str]:
    return [
        "Open scenes with a visual question whenever possible.",
        "Give every scene one emotional purpose and one story consequence.",
        "Use silence, framing, object detail, and body language before dialogue.",
        "Show history through damage, repairs, rituals, tools, and architecture.",
        "Escalate pressure through choices, not random events.",
        "End scenes with a changed relationship, changed threat, or changed understanding.",
    ]


def build_world_rules() -> List[str]:
    return [
        "Every location needs function, history, social meaning, and visual identity.",
        "Architecture should reveal power, fear, faith, class, environment, and technology.",
        "Creatures and machines need survival logic, material logic, and silhouette clarity.",
        "Lore should be discoverable through the environment instead of dumped in speeches.",
        "Nature should not be wallpaper; it should push back, heal, hide, warn, or remember.",
    ]
