from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass
class ScreenplayCharacter:
    name: str
    role: str
    voice: str
    want: str
    pressure: str


@dataclass
class StoryScene:
    setting: str
    visual_goal: str
    emotional_turn: str
    conflict: str
    action_notes: List[str] = field(default_factory=list)
    speech_notes: List[str] = field(default_factory=list)


@dataclass
class MiniScreenplayPlan:
    title: str
    logline: str
    characters: List[ScreenplayCharacter]
    scenes: List[StoryScene]
    notes: List[str]

    def to_markdown(self) -> str:
        lines: List[str] = [f"# {self.title}", "", "## Logline", self.logline, "", "## Characters"]
        for character in self.characters:
            lines.append(f"### {character.name}")
            lines.append(f"- Role: {character.role}")
            lines.append(f"- Voice: {character.voice}")
            lines.append(f"- Want: {character.want}")
            lines.append(f"- Pressure: {character.pressure}")
        lines.append("")
        lines.append("## Scenes")
        for index, scene in enumerate(self.scenes, start=1):
            lines.append(f"### Scene {index}: {scene.setting}")
            lines.append(f"- Visual Goal: {scene.visual_goal}")
            lines.append(f"- Emotional Turn: {scene.emotional_turn}")
            lines.append(f"- Conflict: {scene.conflict}")
            lines.append("- Action Notes:")
            lines.extend(f"  - {item}" for item in scene.action_notes)
            lines.append("- Speech Notes:")
            lines.extend(f"  - {item}" for item in scene.speech_notes)
        lines.append("")
        lines.append("## ATLAS Notes")
        lines.extend(f"- {item}" for item in self.notes)
        return "\n".join(lines)


class MiniScreenplayEngine:
    def build_plan(self, title: str, idea: str, emotion: str) -> MiniScreenplayPlan:
        return MiniScreenplayPlan(
            title=title,
            logline=f"A short cinematic story about {idea}, designed to create {emotion}.",
            characters=[
                ScreenplayCharacter(
                    name="PROTAGONIST",
                    role="emotional center",
                    voice="specific, restrained, and shaped by pressure",
                    want="to solve the visible problem",
                    pressure="must reveal the hidden emotional truth",
                )
            ],
            scenes=[
                StoryScene(
                    setting="Opening image",
                    visual_goal="Establish the world through image, sound, and object detail before explanation.",
                    emotional_turn="Curiosity becomes unease.",
                    conflict="The character notices something that should not be there.",
                    action_notes=[
                        "Open on a specific object that carries history.",
                        "Show the character reacting before they speak.",
                        "Let the environment create the first question.",
                    ],
                    speech_notes=["Use one short line only if silence is not enough."],
                ),
                StoryScene(
                    setting="Pressure rises",
                    visual_goal="Use blocking, light, and movement to increase pressure.",
                    emotional_turn="Unease becomes choice.",
                    conflict="The character must act before they fully understand the danger.",
                    action_notes=[
                        "Make the character choose between safety and truth.",
                        "Show consequence immediately after the choice.",
                    ],
                    speech_notes=["Speech should reveal fear, denial, or resolve."],
                ),
                StoryScene(
                    setting="Final image",
                    visual_goal="End with a memorable image that changes the meaning of the opening.",
                    emotional_turn="Choice becomes consequence.",
                    conflict="The truth is revealed visually.",
                    action_notes=[
                        "Return to the opening object with new meaning.",
                        "End on a strong visual consequence, not a speech.",
                    ],
                    speech_notes=["Avoid explaining the ending if the image can carry it."],
                ),
            ],
            notes=[
                "Mini screenplays must be short, visual, emotional, and shootable.",
                "No scene should exist without pressure or change.",
                "Show first. Speak second.",
                "Reject generic speech.",
            ],
        )
