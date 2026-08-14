"""Bridge media-study reports into ATLAS Creative Memory."""

from __future__ import annotations

from creative_intelligence.creative_memory import CreativeLesson, CreativeMemory

from .schemas import MediaStudyReport


class MediaStudyMemoryBridge:
    def __init__(self, memory: CreativeMemory) -> None:
        self.memory = memory

    def remember_report(
        self,
        report: MediaStudyReport,
        *,
        project: str,
        task: str,
        confidence: float = 0.65,
    ) -> list[CreativeLesson]:
        stored: list[CreativeLesson] = []
        principles = report.extracted_principles or [
            "Study the source for reusable craft principles before applying it."
        ]
        for principle in principles:
            lesson = CreativeLesson(
                project=project,
                task=task,
                references=[report.source_name],
                principle_attempted=principle,
                outcome="Reference study captured for future retrieval.",
                critique="Do not treat one source as a style template.",
                revision="Combine this principle with other references and project constraints.",
                lesson=(
                    report.application_notes[0]
                    if report.application_notes
                    else "Apply the principle only when it solves the current project problem."
                ),
                confidence=confidence,
            )
            stored.append(self.memory.remember(lesson))
        return stored
