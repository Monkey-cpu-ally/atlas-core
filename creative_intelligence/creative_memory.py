"""Project-based creative learning records for ATLAS."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import List


@dataclass
class CreativeLesson:
    project: str
    task: str
    references: List[str]
    principle_attempted: str
    outcome: str
    critique: str
    revision: str
    lesson: str
    confidence: float = 0.5
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> dict:
        return asdict(self)


class CreativeMemory:
    """In-process lesson store; adapters can persist these records later."""

    def __init__(self) -> None:
        self._lessons: list[CreativeLesson] = []

    def remember(self, lesson: CreativeLesson) -> CreativeLesson:
        if not 0.0 <= lesson.confidence <= 1.0:
            raise ValueError("confidence must be between 0.0 and 1.0")
        self._lessons.append(lesson)
        return lesson

    def recall(self, project: str | None = None, term: str | None = None) -> list[CreativeLesson]:
        results = list(self._lessons)
        if project:
            results = [x for x in results if x.project.casefold() == project.casefold()]
        if term:
            needle = term.casefold()
            results = [
                x for x in results
                if needle in " ".join(
                    [x.task, x.principle_attempted, x.outcome, x.critique, x.revision, x.lesson]
                ).casefold()
            ]
        return results
