"""Deterministic continuity intelligence for ATLAS creative productions."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional


@dataclass(frozen=True)
class ContinuityState:
    scene_number: int
    character: str
    location: str
    time_of_day: str
    costume: str = ""
    condition: str = ""
    props: Dict[str, str] = field(default_factory=dict)
    facts: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ContinuityIssue:
    category: str
    subject: str
    previous_scene: int
    current_scene: int
    before: Any
    after: Any
    message: str


class ContinuityEngine:
    """Finds unexplained state changes between consecutive appearances."""

    def audit(self, states: Iterable[ContinuityState]) -> List[ContinuityIssue]:
        issues: List[ContinuityIssue] = []
        previous_by_character: Dict[str, ContinuityState] = {}
        for current in sorted(states, key=lambda state: state.scene_number):
            previous = previous_by_character.get(current.character)
            if previous is not None:
                issues.extend(self._compare(previous, current))
            previous_by_character[current.character] = current
        return issues

    def _compare(self, before: ContinuityState, after: ContinuityState) -> List[ContinuityIssue]:
        issues: List[ContinuityIssue] = []
        for category, old, new in (
            ("costume", before.costume, after.costume),
            ("condition", before.condition, after.condition),
        ):
            if old and new and old != new:
                issues.append(self._issue(category, after.character, before, after, old, new))

        for prop in sorted(set(before.props) & set(after.props)):
            if before.props[prop] != after.props[prop]:
                issues.append(self._issue("prop", prop, before, after, before.props[prop], after.props[prop]))

        for fact in sorted(set(before.facts) & set(after.facts)):
            if before.facts[fact] != after.facts[fact]:
                issues.append(self._issue("story_fact", fact, before, after, before.facts[fact], after.facts[fact]))
        return issues

    @staticmethod
    def _issue(category: str, subject: str, before: ContinuityState, after: ContinuityState, old: Any, new: Any) -> ContinuityIssue:
        return ContinuityIssue(
            category=category,
            subject=subject,
            previous_scene=before.scene_number,
            current_scene=after.scene_number,
            before=old,
            after=new,
            message=f"{category} continuity changed for {subject}: {old!r} -> {new!r}",
        )

    def compare_revisions(self, before_payload: Dict[str, Any], after_payload: Dict[str, Any]) -> List[ContinuityIssue]:
        before = self._state_from_snapshot(before_payload)
        after = self._state_from_snapshot(after_payload)
        if before is None or after is None or before.character != after.character:
            return []
        return self._compare(before, after)

    @staticmethod
    def _state_from_snapshot(payload: Dict[str, Any]) -> Optional[ContinuityState]:
        state = payload.get("continuity_state")
        if not isinstance(state, dict):
            return None
        return ContinuityState(**state)
