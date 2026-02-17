"""Persona strategy classes used by modular AI routing."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Literal


PersonaName = Literal["ajani", "minerva", "hermes"]


@dataclass
class ValidationReport:
    score: float
    strengths: list[str]
    issues: list[str]
    next_steps: list[str]


def _contains_any(text: str, terms: tuple[str, ...]) -> bool:
    lowered = text.lower()
    return any(term in lowered for term in terms)


def _score(strengths: list[str], issues: list[str], *, base: float = 0.45) -> float:
    value = base + (0.15 * len(strengths)) - (0.12 * len(issues))
    return max(0.0, min(1.0, round(value, 2)))


class PersonaAdvisor(ABC):
    name: PersonaName
    routing_keywords: tuple[str, ...]

    @abstractmethod
    def suggest(self, goal: str, constraints: list[str]) -> tuple[str, list[str]]:
        raise NotImplementedError

    @abstractmethod
    def validate(self, goal: str, proposal: str) -> ValidationReport:
        raise NotImplementedError


class AjaniPersona(PersonaAdvisor):
    name: PersonaName = "ajani"
    routing_keywords = (
        "plan",
        "strategy",
        "timeline",
        "risk",
        "build",
        "execution",
        "roadmap",
        "milestone",
    )

    def suggest(self, goal: str, constraints: list[str]) -> tuple[str, list[str]]:
        suggestion = (
            f"Break '{goal}' into three tactical phases: scope the mission, ship the "
            "smallest useful version, then verify quality with measurable checks."
        )
        checklist = [
            "Define one clear objective and one non-goal.",
            "Choose a first deliverable that can ship quickly.",
            "Attach one measurable success metric to each phase.",
            "List top risks and fallback actions before execution.",
        ]
        if constraints:
            checklist.append(f"Apply constraints in every phase: {', '.join(constraints)}.")
        return suggestion, checklist

    def validate(self, goal: str, proposal: str) -> ValidationReport:
        text = proposal.lower()
        strengths: list[str] = []
        issues: list[str] = []
        next_steps: list[str] = []

        if _contains_any(text, ("phase", "step", "milestone", "roadmap", "plan")):
            strengths.append("Proposal includes execution structure.")
        else:
            issues.append("Missing execution structure (steps/phases/milestones).")
            next_steps.append("Add a phased plan with clear milestones.")

        if _contains_any(text, ("measure", "metric", "kpi", "success criteria", "test")):
            strengths.append("Proposal defines how success will be measured.")
        else:
            issues.append("Missing measurable success criteria.")
            next_steps.append("Add at least one metric and one pass/fail check.")

        if _contains_any(text, ("risk", "fallback", "mitigate", "safety", "rollback")):
            strengths.append("Proposal considers risk management.")
        else:
            issues.append("No explicit risk or fallback plan.")
            next_steps.append("Document top two risks and a rollback strategy.")

        score = _score(strengths, issues)
        if not next_steps:
            next_steps.append("Run a small pilot and review results before full rollout.")

        return ValidationReport(
            score=score,
            strengths=strengths,
            issues=issues,
            next_steps=next_steps,
        )


class MinervaPersona(PersonaAdvisor):
    name: PersonaName = "minerva"
    routing_keywords = (
        "ethic",
        "culture",
        "community",
        "story",
        "identity",
        "equity",
        "inclusive",
        "wellbeing",
    )
    _harmful_terms = ("harm", "exploit", "manipulate", "deceive", "discriminate")

    def suggest(self, goal: str, constraints: list[str]) -> tuple[str, list[str]]:
        suggestion = (
            f"For '{goal}', start with the human impact: who benefits, who carries risk, "
            "and what values the system must protect from day one."
        )
        checklist = [
            "Define who this helps first and how to include edge communities.",
            "Write a values statement (safety, fairness, transparency).",
            "Identify likely misunderstandings and clarify language early.",
            "Plan feedback loops with real users before scaling.",
        ]
        if constraints:
            checklist.append(f"Embed constraints into user-facing decisions: {', '.join(constraints)}.")
        return suggestion, checklist

    def validate(self, goal: str, proposal: str) -> ValidationReport:
        text = proposal.lower()
        strengths: list[str] = []
        issues: list[str] = []
        next_steps: list[str] = []

        if _contains_any(text, ("user", "people", "community", "learner", "family")):
            strengths.append("Proposal addresses people and stakeholders.")
        else:
            issues.append("Stakeholder impact is not explicitly addressed.")
            next_steps.append("Add a section that names affected users and outcomes.")

        if _contains_any(text, ("ethical", "fair", "bias", "transparent", "consent", "safe")):
            strengths.append("Proposal includes ethics or safety considerations.")
        else:
            issues.append("Ethics/safety guardrails are unclear.")
            next_steps.append("Add explicit safety and fairness guardrails.")

        if _contains_any(text, self._harmful_terms):
            issues.append("Contains potentially harmful or manipulative framing.")
            next_steps.append("Remove harmful framing and replace with protective language.")

        score = _score(strengths, issues)
        if not next_steps:
            next_steps.append("Collect user feedback and refine wording for clarity and trust.")

        return ValidationReport(
            score=score,
            strengths=strengths,
            issues=issues,
            next_steps=next_steps,
        )


class HermesPersona(PersonaAdvisor):
    name: PersonaName = "hermes"
    routing_keywords = (
        "api",
        "backend",
        "code",
        "fastapi",
        "schema",
        "class",
        "module",
        "performance",
        "bug",
        "test",
    )

    def suggest(self, goal: str, constraints: list[str]) -> tuple[str, list[str]]:
        suggestion = (
            f"Treat '{goal}' as a systems job: define interfaces first, keep logic modular, "
            "and make every route testable with predictable inputs/outputs."
        )
        checklist = [
            "Define request/response schemas before coding handlers.",
            "Separate routing, persona logic, and validation concerns.",
            "Add deterministic validation rules for quick feedback.",
            "Cover happy path and one failure path with tests.",
        ]
        if constraints:
            checklist.append(f"Encode constraints in API contracts: {', '.join(constraints)}.")
        return suggestion, checklist

    def validate(self, goal: str, proposal: str) -> ValidationReport:
        text = proposal.lower()
        strengths: list[str] = []
        issues: list[str] = []
        next_steps: list[str] = []

        if _contains_any(text, ("endpoint", "api", "route", "schema", "payload")):
            strengths.append("Proposal defines API-facing structure.")
        else:
            issues.append("Missing explicit API structure (routes/schemas).")
            next_steps.append("Specify endpoints and request/response payloads.")

        if _contains_any(text, ("class", "module", "service", "router", "separate")):
            strengths.append("Proposal shows modular architecture.")
        else:
            issues.append("Modularity is unclear.")
            next_steps.append("Separate persona logic from route handling.")

        if _contains_any(text, ("test", "validate", "assert", "monitor", "log")):
            strengths.append("Proposal includes validation or observability.")
        else:
            issues.append("No clear validation/testing plan.")
            next_steps.append("Add test and validation criteria before implementation.")

        score = _score(strengths, issues)
        if not next_steps:
            next_steps.append("Run endpoint smoke tests and capture expected response shapes.")

        return ValidationReport(
            score=score,
            strengths=strengths,
            issues=issues,
            next_steps=next_steps,
        )
