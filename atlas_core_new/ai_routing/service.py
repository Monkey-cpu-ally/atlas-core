"""Service layer for persona routing and decision orchestration."""

from __future__ import annotations

from dataclasses import dataclass

from .personas import (
    AjaniPersona,
    HermesPersona,
    MinervaPersona,
    PersonaAdvisor,
    PersonaName,
    ValidationReport,
)


@dataclass
class RoutingDecision:
    persona: PersonaName
    reason: str
    scores: dict[PersonaName, int]


class PersonaRoutingService:
    def __init__(self) -> None:
        self._personas: dict[PersonaName, PersonaAdvisor] = {
            "ajani": AjaniPersona(),
            "minerva": MinervaPersona(),
            "hermes": HermesPersona(),
        }
        self._priority: tuple[PersonaName, ...] = ("ajani", "hermes", "minerva")
        self._default_persona: PersonaName = "ajani"

    def resolve_persona(
        self,
        text: str,
        requested_persona: PersonaName | None = None,
    ) -> tuple[PersonaAdvisor, RoutingDecision]:
        if requested_persona:
            scores = {name: 0 for name in self._personas}
            return self._personas[requested_persona], RoutingDecision(
                persona=requested_persona,
                reason=f"Explicit persona requested: {requested_persona}.",
                scores=scores,
            )

        lowered = text.lower()
        scores: dict[PersonaName, int] = {}
        for name, persona in self._personas.items():
            scores[name] = sum(1 for keyword in persona.routing_keywords if keyword in lowered)

        best_persona: PersonaName = self._default_persona
        best_score = -1
        for candidate in self._priority:
            score = scores[candidate]
            if score > best_score:
                best_persona = candidate
                best_score = score

        if best_score <= 0:
            best_persona = self._default_persona
            reason = "No strong keyword match; defaulted to Ajani for tactical planning."
        else:
            reason = f"Routed to {best_persona} using persona keyword scores."

        return self._personas[best_persona], RoutingDecision(
            persona=best_persona,
            reason=reason,
            scores=scores,
        )

    def suggest(
        self,
        goal: str,
        constraints: list[str],
        persona: PersonaName | None = None,
    ) -> tuple[PersonaName, RoutingDecision, str, list[str]]:
        routing_text = " ".join([goal, *constraints]).strip()
        selected_persona, decision = self.resolve_persona(
            text=routing_text,
            requested_persona=persona,
        )
        suggestion, checklist = selected_persona.suggest(goal=goal, constraints=constraints)
        return selected_persona.name, decision, suggestion, checklist

    def validate(
        self,
        goal: str,
        proposal: str,
        persona: PersonaName | None = None,
    ) -> tuple[PersonaName, RoutingDecision, ValidationReport, bool]:
        routing_text = f"{goal}\n{proposal}"
        selected_persona, decision = self.resolve_persona(
            text=routing_text,
            requested_persona=persona,
        )
        report = selected_persona.validate(goal=goal, proposal=proposal)
        has_blocking_issue = any(
            "harmful" in issue.lower() or "unsafe" in issue.lower() for issue in report.issues
        )
        is_valid = report.score >= 0.65 and not has_blocking_issue
        return selected_persona.name, decision, report, is_valid
