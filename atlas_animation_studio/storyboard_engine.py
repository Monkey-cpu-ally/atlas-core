"""Storyboard engine for ATLAS Animation Studio."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass
class StoryboardFrame:
    scene_number: int
    shot_number: int
    shot_type: str
    camera_movement: str
    character_blocking: str
    pose_expression: str
    lighting: str
    color_mood: str
    sound: str
    dialogue_or_silence: str
    emotional_purpose: str
    story_consequence: str
    animation_notes: str

    def to_markdown(self) -> str:
        return "\n".join(
            [
                f"## Scene {self.scene_number} / Shot {self.shot_number}",
                f"- Shot Type: {self.shot_type}",
                f"- Camera Movement: {self.camera_movement}",
                f"- Character Blocking: {self.character_blocking}",
                f"- Pose / Expression: {self.pose_expression}",
                f"- Lighting: {self.lighting}",
                f"- Color Mood: {self.color_mood}",
                f"- Sound: {self.sound}",
                f"- Dialogue or Silence: {self.dialogue_or_silence}",
                f"- Emotional Purpose: {self.emotional_purpose}",
                f"- Story Consequence: {self.story_consequence}",
                f"- Animation Notes: {self.animation_notes}",
            ]
        )


class StoryboardEngine:
    """Creates storyboard planning frames with ATLAS visual-storytelling rules."""

    def build_frame(
        self,
        scene_number: int,
        shot_number: int,
        emotional_purpose: str,
        story_consequence: str,
        dialogue_needed: bool = False,
    ) -> StoryboardFrame:
        return StoryboardFrame(
            scene_number=scene_number,
            shot_number=shot_number,
            shot_type="Wide establishing shot moving into character-focused composition",
            camera_movement="Slow push forward unless tension demands stillness",
            character_blocking="Characters placed to show relationship distance, power, and emotional pressure",
            pose_expression="Pose must communicate emotion before dialogue is added",
            lighting="Lighting reveals mood, history, and threat direction",
            color_mood="Color should track emotional temperature and story state",
            sound="Use environment, breath, texture, music, or silence as story information",
            dialogue_or_silence="Dialogue allowed" if dialogue_needed else "Prefer silence or minimal dialogue",
            emotional_purpose=emotional_purpose,
            story_consequence=story_consequence,
            animation_notes="Prioritize silhouette clarity, weight, anticipation, follow-through, and readable timing",
        )

    def visual_storytelling_questions(self) -> List[str]:
        return [
            "Can this be shown instead of spoken?",
            "Can body language reveal the emotion?",
            "Can lighting reveal the mood?",
            "Can architecture reveal history?",
            "Can damage on an object reveal the past?",
            "Can silence make the scene stronger?",
        ]
