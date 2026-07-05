from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class AcademyPhase:
    number: int
    name: str
    status: str
    goals: List[str]
    outputs: List[str]


class LuxuryDesignPhaseRegistry:
    def __init__(self) -> None:
        self.phases: Dict[int, AcademyPhase] = {
            1: AcademyPhase(
                number=1,
                name="Foundation",
                status="started",
                goals=[
                    "Define luxury through craftsmanship, trust, material honesty, emotion, and timelessness.",
                    "Connect luxury study to the Frazier Design Language.",
                ],
                outputs=["Luxury Intelligence Library", "Frazier Design Language", "Design Critique System"],
            ),
            2: AcademyPhase(
                number=2,
                name="Critique Engine",
                status="started",
                goals=[
                    "Accept design concepts.",
                    "Score luxury, originality, and Frazier alignment.",
                    "Return practical revision guidance.",
                ],
                outputs=["luxury_design_academy.py"],
            ),
            3: AcademyPhase(
                number=3,
                name="Visual Style Memory",
                status="planned",
                goals=[
                    "Learn from user-approved references.",
                    "Detect repeated style preferences.",
                    "Store recurring patterns as Frazier Design DNA.",
                ],
                outputs=["Visual Style Memory document", "Style pattern records"],
            ),
            4: AcademyPhase(
                number=4,
                name="Luxury Curriculum",
                status="planned",
                goals=[
                    "Build structured study areas for fashion, materials, form, craftsmanship, and psychology.",
                    "Assign lessons to Ajani, Hermes, and Minerva.",
                ],
                outputs=["Luxury Foundations", "Fashion Academy", "Materials Library", "Craftsmanship Library"],
            ),
            5: AcademyPhase(
                number=5,
                name="Originality and Similarity Detection",
                status="planned",
                goals=[
                    "Warn when a design resembles existing visual languages too closely.",
                    "Recommend changes that increase originality.",
                ],
                outputs=["Similarity risk reports", "Originality improvement plans"],
            ),
            6: AcademyPhase(
                number=6,
                name="Frazier Design Studio",
                status="planned",
                goals=[
                    "Generate original design directions from Frazier principles.",
                    "Create concept briefs, material palettes, and revision plans.",
                ],
                outputs=["Design briefs", "Council critique reports"],
            ),
            7: AcademyPhase(
                number=7,
                name="Memory Integration",
                status="planned",
                goals=[
                    "Store critiques and lessons learned in ATLAS memory.",
                    "Use past reviews to improve future decisions.",
                ],
                outputs=["Critique memory records", "Lesson summaries"],
            ),
            8: AcademyPhase(
                number=8,
                name="Production Readiness",
                status="planned",
                goals=[
                    "Convert approved concepts into build briefs.",
                    "Add materials, costs, risks, testing plans, and manufacturing notes.",
                ],
                outputs=["Prototype briefs", "Manufacturing checklists"],
            ),
        }

    def get_phase(self, number: int) -> AcademyPhase:
        return self.phases[number]

    def list_phases(self) -> List[AcademyPhase]:
        return [self.phases[key] for key in sorted(self.phases)]

    def active_phases(self) -> List[AcademyPhase]:
        return [phase for phase in self.list_phases() if phase.status == "started"]

    def planned_phases(self) -> List[AcademyPhase]:
        return [phase for phase in self.list_phases() if phase.status == "planned"]


def create_phase_registry() -> LuxuryDesignPhaseRegistry:
    return LuxuryDesignPhaseRegistry()
