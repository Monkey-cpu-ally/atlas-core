"""Inject learned Creative Intelligence into Story Foundry without copying references."""
from __future__ import annotations

from dataclasses import dataclass

from creative_intelligence.agent_context import AgentCreativeContextService


@dataclass(frozen=True)
class FoundryCreativeBrief:
    project: str
    task: str
    ajani: str
    minerva: str
    hermes: str

    def to_prompt_context(self) -> str:
        return "\n\n".join([
            "STORY FOUNDRY CREATIVE INTELLIGENCE",
            self.ajani,
            self.minerva,
            self.hermes,
            (
                "SYNTHESIS RULE: combine abstract craft principles only. Do not reproduce "
                "distinctive characters, dialogue, compositions, plots, or other source expression. "
                "The output must remain original to the current project."
            ),
        ])


class StoryFoundryCreativeBridge:
    def __init__(self, context_service: AgentCreativeContextService) -> None:
        self.context_service = context_service

    def build_brief(self, *, project: str, task: str) -> FoundryCreativeBrief:
        def context(agent: str) -> str:
            return self.context_service.retrieve(
                agent=agent, project=project, query=task
            ).to_prompt_context(max_lessons=5)

        return FoundryCreativeBrief(
            project=project,
            task=task,
            ajani=context("ajani"),
            minerva=context("minerva"),
            hermes=context("hermes"),
        )
