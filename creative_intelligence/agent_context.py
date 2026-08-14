"""Agent-facing retrieval of learned Creative Intelligence principles."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from .creative_memory import CreativeLesson


class CreativeMemoryReader(Protocol):
    def recall(self, project: str | None = None, term: str | None = None) -> list[CreativeLesson]: ...


ROLE_LENSES = {
    "ajani": "Strategy lens: prioritize function, audience impact, hierarchy, and decisive creative choices.",
    "minerva": "Scholar lens: compare references, explain craft logic, themes, culture, and teachable principles.",
    "hermes": "Architect lens: translate principles into systems, constraints, production methods, and implementation details.",
}


@dataclass(frozen=True)
class CreativeContextPacket:
    agent: str
    project: str
    query: str
    lessons: list[CreativeLesson]

    def to_prompt_context(self, max_lessons: int = 8) -> str:
        lens = ROLE_LENSES.get(self.agent.casefold(), "Creative lens: apply retrieved principles to the current problem.")
        selected = self.lessons[:max_lessons]
        lines = [
            f"ATLAS CREATIVE MEMORY — {self.agent.upper()}",
            f"Project: {self.project}",
            f"Task/query: {self.query}",
            lens,
            "Use these as reusable principles, not as instructions to copy a source's distinctive expression.",
        ]
        for index, lesson in enumerate(selected, 1):
            lines.append(
                f"{index}. Principle: {lesson.principle_attempted} | Learned: {lesson.lesson} "
                f"| Revision: {lesson.revision} | Confidence: {lesson.confidence:.2f}"
            )
        if not selected:
            lines.append("No matching learned principles were found.")
        return "\n".join(lines)


class AgentCreativeContextService:
    def __init__(self, memory: CreativeMemoryReader) -> None:
        self.memory = memory

    def retrieve(self, *, agent: str, project: str, query: str) -> CreativeContextPacket:
        if agent.casefold() not in ROLE_LENSES:
            raise ValueError("agent must be Ajani, Minerva, or Hermes")
        project_lessons = self.memory.recall(project=project)
        if query.strip():
            needle = query.casefold()
            matching = [
                lesson for lesson in project_lessons
                if needle in " ".join(
                    [
                        lesson.task,
                        lesson.principle_attempted,
                        lesson.outcome,
                        lesson.critique,
                        lesson.revision,
                        lesson.lesson,
                    ]
                ).casefold()
            ]
            lessons = matching or project_lessons
        else:
            lessons = project_lessons
        lessons = sorted(lessons, key=lambda item: item.confidence, reverse=True)
        return CreativeContextPacket(agent=agent, project=project, query=query, lessons=lessons)
