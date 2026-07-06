"""ATLAS Creative Council review logic."""

from __future__ import annotations

from typing import List

from .originality_engine import originality_questions
from .schemas import AIRole, CouncilNote, CreativeBrief


class CreativeCouncil:
    """Runs role-based creative review for Ajani, Minerva, Hermes, and the Council."""

    def review(self, brief: CreativeBrief) -> List[CouncilNote]:
        return [
            self._ajani_review(brief),
            self._minerva_review(brief),
            self._hermes_review(brief),
            self._council_review(brief),
        ]

    def _ajani_review(self, brief: CreativeBrief) -> CouncilNote:
        return CouncilNote(
            role=AIRole.AJANI,
            strengths=[
                "Checks whether the premise has conflict, stakes, and a clear emotional target.",
                f"Primary emotion to protect: {brief.target_emotion}.",
            ],
            risks=[
                "The idea may become visually interesting but emotionally weak if character decisions are vague.",
                "Conflict must pressure the protagonist into hard choices, not just cool events.",
            ],
            recommendations=[
                "Define the protagonist's wound, want, need, and breaking point.",
                "Build three escalation beats: warning, consequence, irreversible turn.",
                "Make every major scene force a decision.",
            ],
        )

    def _minerva_review(self, brief: CreativeBrief) -> CouncilNote:
        return CouncilNote(
            role=AIRole.MINERVA,
            strengths=[
                "Checks symbolism, lore, nature, mythology, and hidden meaning.",
                "Protects the soul of the world so it is not just decoration.",
            ],
            risks=[
                "Lore can become confusing if symbols do not connect to character or theme.",
                "Mystery without emotional meaning can feel hollow.",
            ],
            recommendations=[
                "Create a symbol map: object, meaning, corruption, transformation.",
                "Give the world a history that explains its architecture, rituals, and fears.",
                "Reveal lore through places, behavior, tools, songs, ruins, and consequences.",
            ],
        )

    def _hermes_review(self, brief: CreativeBrief) -> CouncilNote:
        return CouncilNote(
            role=AIRole.HERMES,
            strengths=[
                "Checks visual language, cinematic clarity, architecture, motion, and design identity.",
                "Protects the ATLAS look: layered, functional, advanced, elegant, and not generic.",
            ],
            risks=[
                "The project may feel derivative if silhouettes, materials, or world design are too familiar.",
                "Action can become noise if geography and body language are unclear.",
            ],
            recommendations=[
                "Define silhouettes for characters, machines, locations, and creatures.",
                "Use visual storytelling before dialogue: pose, distance, light, damage, and movement.",
                "Design every object with purpose, material logic, and history.",
            ],
        )

    def _council_review(self, brief: CreativeBrief) -> CouncilNote:
        return CouncilNote(
            role=AIRole.COUNCIL,
            strengths=[
                "Combines strategy, meaning, and visual execution into one ATLAS direction.",
                "Keeps originality and user vision above imitation.",
            ],
            risks=[
                "Too many influences can create a collage instead of a clear identity.",
                "The idea must be sharpened until it can be explained simply.",
            ],
            recommendations=[
                "Write the ATLAS identity sentence before drafting scenes.",
                "Run the originality questions before concept art and again before final draft.",
                *originality_questions(),
            ],
        )
