"""ATLAS innovation validator.

Scores creative ideas against the No Generic Output Directive.
This is not a final judge; it is a pressure system that forces better ideas.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


@dataclass
class InnovationReport:
    score: int
    passed: bool
    strengths: List[str]
    weaknesses: List[str]
    required_revisions: List[str]

    def to_markdown(self) -> str:
        status = "PASS" if self.passed else "REVISE"
        lines = [f"# Innovation Report: {status}", "", f"Score: {self.score}/100", ""]
        lines.append("## Strengths")
        lines.extend(f"- {item}" for item in self.strengths)
        lines.append("")
        lines.append("## Weaknesses")
        lines.extend(f"- {item}" for item in self.weaknesses)
        lines.append("")
        lines.append("## Required Revisions")
        lines.extend(f"- {item}" for item in self.required_revisions)
        return "\n".join(lines)


class InnovationValidator:
    """Evaluates whether an ATLAS output is distinctive enough to present."""

    DEFAULT_THRESHOLD = 75

    CRITERIA: Dict[str, int] = {
        "distinctive_identity": 20,
        "emotional_grounding": 15,
        "visual_memory": 15,
        "functional_logic": 15,
        "world_history": 15,
        "transformed_influences": 20,
    }

    GENERIC_TERMS = {
        "cool robot",
        "futuristic city",
        "dark villain",
        "chosen one",
        "ancient evil",
        "magic school",
        "evil empire",
        "generic monster",
        "high tech suit",
        "neon skyline",
    }

    def validate(self, description: str, threshold: int | None = None) -> InnovationReport:
        threshold = threshold or self.DEFAULT_THRESHOLD
        text = description.lower()
        score = 0
        strengths: List[str] = []
        weaknesses: List[str] = []
        revisions: List[str] = []

        checks = {
            "distinctive_identity": ["unique", "signature", "specific", "unmistakable", "atlas", "frazier"],
            "emotional_grounding": ["grief", "fear", "wonder", "family", "legacy", "hope", "guilt", "loss", "love"],
            "visual_memory": ["silhouette", "color", "texture", "movement", "shape", "lighting", "symbol"],
            "functional_logic": ["purpose", "material", "mechanism", "engineered", "function", "constraint"],
            "world_history": ["history", "ritual", "ruin", "culture", "belief", "origin", "scar"],
            "transformed_influences": ["transformed", "principle", "not copied", "original", "reimagined", "synthesized"],
        }

        for criterion, keywords in checks.items():
            if any(keyword in text for keyword in keywords):
                score += self.CRITERIA[criterion]
                strengths.append(f"{criterion.replace('_', ' ').title()} is present.")
            else:
                weaknesses.append(f"{criterion.replace('_', ' ').title()} is weak or missing.")
                revisions.append(f"Add stronger {criterion.replace('_', ' ')} before approval.")

        for term in self.GENERIC_TERMS:
            if term in text:
                score -= 10
                weaknesses.append(f"Generic phrase detected: '{term}'.")
                revisions.append(f"Replace '{term}' with a specific ATLAS-native concept.")

        score = max(0, min(100, score))
        passed = score >= threshold and not any(term in text for term in self.GENERIC_TERMS)

        if not passed:
            revisions.append("Do another Council pass before presenting this as final.")

        return InnovationReport(
            score=score,
            passed=passed,
            strengths=strengths,
            weaknesses=weaknesses,
            required_revisions=revisions,
        )
