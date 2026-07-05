from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class LuxuryLesson:
    id: str
    title: str
    owner_ai: str
    principles: List[str]
    review_questions: List[str]


class LuxuryCurriculumRegistry:
    def __init__(self) -> None:
        self.lessons: Dict[str, LuxuryLesson] = {
            "luxury_trust": LuxuryLesson(
                id="luxury_trust",
                title="Luxury Is Trust",
                owner_ai="Council",
                principles=[
                    "Every detail should feel intentional.",
                    "Reliable construction creates confidence.",
                    "Weak details reduce perceived quality.",
                ],
                review_questions=[
                    "Would a user trust this for years?",
                    "Does the design communicate care and precision?",
                    "Are weak details solved or hidden?",
                ],
            ),
            "craftsmanship": LuxuryLesson(
                id="craftsmanship",
                title="Craftsmanship",
                owner_ai="Hermes",
                principles=[
                    "Craftsmanship appears in seams, finishes, joints, tolerances, and transitions.",
                    "A premium rendering is not enough if physical construction is weak.",
                ],
                review_questions=[
                    "Are the seams, fasteners, and transitions resolved?",
                    "Does the finish support the intended quality level?",
                ],
            ),
            "restraint": LuxuryLesson(
                id="restraint",
                title="Restraint",
                owner_ai="Hermes",
                principles=[
                    "More detail is not always better.",
                    "Strong luxury often comes from removing noise.",
                ],
                review_questions=[
                    "What can be removed?",
                    "Which details serve function, and which are visual noise?",
                ],
            ),
            "timelessness": LuxuryLesson(
                id="timelessness",
                title="Timelessness",
                owner_ai="Minerva",
                principles=[
                    "A strong design should age well.",
                    "Trends should be studied but not blindly followed.",
                ],
                review_questions=[
                    "Will this still feel strong in ten years?",
                    "Is the concept trend-dependent or enduring?",
                ],
            ),
            "emotional_design": LuxuryLesson(
                id="emotional_design",
                title="Emotional Design",
                owner_ai="Minerva",
                principles=[
                    "Luxury should create a clear emotional response.",
                    "A design with no emotional signal is easy to forget.",
                ],
                review_questions=[
                    "What emotion does this create?",
                    "Is the emotional direction clear enough?",
                ],
            ),
            "originality": LuxuryLesson(
                id="originality",
                title="Originality",
                owner_ai="Ajani",
                principles=[
                    "Study principles, not identities.",
                    "The goal is stronger Frazier Design Language, not imitation.",
                ],
                review_questions=[
                    "What principle can be learned without copying?",
                    "What makes this design distinctly Frazier?",
                ],
            ),
        }

    def list_lessons(self) -> List[LuxuryLesson]:
        return list(self.lessons.values())

    def get_lesson(self, lesson_id: str) -> LuxuryLesson:
        return self.lessons[lesson_id]

    def lessons_for_ai(self, owner_ai: str) -> List[LuxuryLesson]:
        return [lesson for lesson in self.lessons.values() if lesson.owner_ai == owner_ai]


def create_luxury_curriculum() -> LuxuryCurriculumRegistry:
    return LuxuryCurriculumRegistry()
