"""Originality checks for ATLAS creative work.

This is a lightweight guardrail engine. It does not replace legal review,
but it helps ATLAS avoid lazy imitation and pushes ideas toward original execution.
"""

from __future__ import annotations

from typing import Iterable, List

from .schemas import CreativeBrief


PROTECTED_EXPRESSION_WARNINGS = [
    "Do not reuse copyrighted character names or direct equivalents.",
    "Do not recreate specific scenes, shots, dialogue, worlds, or plot sequences.",
    "Do not make a thinly disguised version of a known franchise.",
    "Do not rely on one influence so heavily that the project loses ATLAS identity.",
]


COMMON_SIMILARITY_TRIGGERS = {
    "lightsaber": "Replace direct franchise-coded weapons with an original technology, ritual, or material logic.",
    "jedi": "Avoid direct spiritual-order equivalents; define a distinct philosophy, training system, and social role.",
    "sith": "Avoid direct dark-order equivalents; build a new conflict structure and moral language.",
    "hogwarts": "Avoid direct school-of-magic structures unless the institution, rules, culture, and conflict are distinct.",
    "wakanda": "Avoid copying hidden advanced-nation structures; create original history, resources, politics, and visual language.",
    "batman": "Avoid billionaire vigilante equivalence; change motive, resources, ethics, methods, and social context.",
    "god of war": "Avoid copying mythic revenge/father-child structures; transform myth into original emotional and mechanical design.",
    "dark souls": "Avoid direct bonfire/souls/undead kingdom structures; use different progression, metaphysics, and lore delivery.",
}


def scan_similarity_risks(brief: CreativeBrief, extra_terms: Iterable[str] | None = None) -> List[str]:
    text = " ".join([brief.title, brief.premise, brief.genre, brief.target_emotion, *brief.user_style_notes]).lower()
    warnings: List[str] = []

    for trigger, recommendation in COMMON_SIMILARITY_TRIGGERS.items():
        if trigger in text:
            warnings.append(f"Similarity risk: '{trigger}' detected. {recommendation}")

    if extra_terms:
        for term in extra_terms:
            if term.lower() in text:
                warnings.append(f"User-provided similarity concern detected: '{term}'. Transform the idea before development.")

    if not warnings:
        warnings.append("No obvious similarity trigger detected, but perform a deeper review during concept art, outline, and draft stages.")

    warnings.extend(PROTECTED_EXPRESSION_WARNINGS)
    return warnings


def originality_questions() -> List[str]:
    return [
        "What is the one-sentence ATLAS identity of this idea?",
        "Which parts feel too close to known works?",
        "Can the same emotion be achieved through a different world, object, ritual, or conflict?",
        "What would make this unmistakably Frazier/ATLAS instead of a remix?",
        "What should be removed because it is only there as borrowed cool factor?",
    ]
