"""Storyboard engine for ATLAS Animation Studio."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass
class StoryboardFrame:
    scene_number: int
    beat_number: int
    shot_number: int
    beat_goal: str
    shot_type: str
    camera_movement: str
    character_blocking: str
    pose_expression: str
    lighting: str
    color_mood: str
    movement: str
    sound: str
    dialogue_or_silence: str
    emotional_purpose: str
    story_consequence: str
    animation_notes: str

    def to_markdown(self) -> str:
        return "\n".join([
            f"## Scene {self.scene_number} / Beat {self.beat_number} / Shot {self.shot_number}",
            f"- Beat Goal: {self.beat_goal}",
            f"- Shot Type: {self.shot_type}",
            f"- Camera Movement: {self.camera_movement}",
            f"- Character Blocking: {self.character_blocking}",
            f"- Pose / Expression: {self.pose_expression}",
            f"- Lighting: {self.lighting}",
            f"- Color Mood: {self.color_mood}",
            f"- Movement: {self.movement}",
            f"- Sound: {self.sound}",
            f"- Dialogue or Silence: {self.dialogue_or_silence}",
            f"- Emotional Purpose: {self.emotional_purpose}",
            f"- Story Consequence: {self.story_consequence}",
            f"- Animation Notes: {self.animation_notes}",
        ])


@dataclass
class StoryboardSequence:
    title: str
    frames: List[StoryboardFrame] = field(default_factory=list)

    def to_markdown(self) -> str:
        lines = [f"# {self.title}", ""]
        for frame in self.frames:
            lines.append(frame.to_markdown())
            lines.append("")
        return "\n".join(lines)


class StoryboardEngine:
    """Creates scene-to-beat-to-shot plans using ATLAS visual storytelling rules."""

    def build_frame(
        self,
        scene_number: int,
        shot_number: int,
        emotional_purpose: str,
        story_consequence: str,
        dialogue_needed: bool = False,
        beat_number: int = 1,
        beat_goal: str = "Change the audience's understanding or emotional state",
    ) -> StoryboardFrame:
        return StoryboardFrame(
            scene_number=scene_number,
            beat_number=beat_number,
            shot_number=shot_number,
            beat_goal=beat_goal,
            shot_type="Wide establishing shot moving into character-focused composition",
            camera_movement="Move only when the emotional or story point benefits from movement",
            character_blocking="Place characters to show relationship distance, power, and pressure",
            pose_expression="Pose must communicate emotion before dialogue is added",
            lighting="Lighting reveals mood, history, focal point, and threat direction",
            color_mood="Color tracks emotional temperature and story state",
            movement="Movement must show weight, intention, and personality",
            sound="Use environment, breath, texture, music, or silence as story information",
            dialogue_or_silence="Dialogue allowed" if dialogue_needed else "Prefer silence or minimal dialogue",
            emotional_purpose=emotional_purpose,
            story_consequence=story_consequence,
            animation_notes="Prioritize silhouette clarity, anticipation, weight, follow-through, and readable timing",
        )

    def build_sequence(self, title: str, scene_number: int, beat_goals: List[str]) -> StoryboardSequence:
        frames: List[StoryboardFrame] = []
        for beat_index, beat_goal in enumerate(beat_goals, start=1):
            frames.append(self.build_frame(
                scene_number=scene_number,
                beat_number=beat_index,
                shot_number=beat_index,
                beat_goal=beat_goal,
                emotional_purpose=f"Deliver beat {beat_index}: {beat_goal}",
                story_consequence="The scene must end this beat with a changed relationship, threat, choice, or understanding.",
            ))
        return StoryboardSequence(title=title, frames=frames)

    def visual_storytelling_questions(self) -> List[str]:
        return [
            "Can this be shown instead of spoken?",
            "Can body language reveal the emotion?",
            "Can lighting reveal the mood?",
            "Can architecture reveal history?",
            "Can damage on an object reveal the past?",
            "Can silence make the scene stronger?",
            "Does every shot have a reason to exist?",
        ]
