from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class CouncilPerspective:
    reviewer: str
    strengths: List[str] = field(default_factory=list)
    risks: List[str] = field(default_factory=list)
    required_changes: List[str] = field(default_factory=list)


@dataclass
class CouncilReview:
    project_name: str
    perspectives: Dict[str, CouncilPerspective]
    approval_score: int
    approved: bool
    final_directive: str

    def to_markdown(self) -> str:
        lines = [f"# Council Review: {self.project_name}", "", f"Approval Score: {self.approval_score}/100", f"Approved: {self.approved}", ""]
        for key, note in self.perspectives.items():
            lines.append(f"## {note.reviewer}")
            lines.append("Strengths:")
            lines.extend(f"- {item}" for item in note.strengths)
            lines.append("Risks:")
            lines.extend(f"- {item}" for item in note.risks)
            lines.append("Required Changes:")
            lines.extend(f"- {item}" for item in note.required_changes)
            lines.append("")
        lines.append("## Final Directive")
        lines.append(self.final_directive)
        return "\n".join(lines)


class CouncilReviewEngine:
    DEFAULT_THRESHOLD = 75

    def review(self, project_name: str, story_ready: bool, world_ready: bool, visual_ready: bool, original_ready: bool) -> CouncilReview:
        checks = [story_ready, world_ready, visual_ready, original_ready]
        score = sum(25 for item in checks if item)
        perspectives = {
            "ajani": CouncilPerspective(
                reviewer="Ajani",
                strengths=["Story, stakes, character pressure, and consequence are reviewed here."],
                risks=[] if story_ready else ["Story logic or character pressure is not ready."],
                required_changes=[] if story_ready else ["Strengthen scene purpose, stakes, and irreversible choices."],
            ),
            "minerva": CouncilPerspective(
                reviewer="Minerva",
                strengths=["World logic, culture, history, symbolism, and meaning are reviewed here."],
                risks=[] if world_ready else ["Worldbuilding lacks enough connected cause and effect."],
                required_changes=[] if world_ready else ["Connect history, culture, ecology, and institutions more tightly."],
            ),
            "hermes": CouncilPerspective(
                reviewer="Hermes",
                strengths=["Visual identity, material logic, movement, and readability are reviewed here."],
                risks=[] if visual_ready else ["Visual identity is underdeveloped or too familiar."],
                required_changes=[] if visual_ready else ["Strengthen silhouette, materials, lighting, and movement language."],
            ),
            "council": CouncilPerspective(
                reviewer="Council",
                strengths=["Originality, consistency, and integration are reviewed here."],
                risks=[] if original_ready else ["The project still feels too derivative or generic."],
                required_changes=[] if original_ready else ["Transform familiar elements into a clearer ATLAS-native direction."],
            ),
        }
        approved = score >= self.DEFAULT_THRESHOLD and original_ready
        final_directive = "Approved for the next production stage." if approved else "Revise the failed review areas, then run Council Review again."
        return CouncilReview(project_name=project_name, perspectives=perspectives, approval_score=score, approved=approved, final_directive=final_directive)
