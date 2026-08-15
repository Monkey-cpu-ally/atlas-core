"""Structured design sheets for the ATLAS creative production pipeline."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Protocol


class CreativeBriefProvider(Protocol):
    def build_brief(self, *, project: str, task: str): ...


@dataclass
class CharacterSheet:
    project: str
    name: str
    role: str
    silhouette: List[str]
    shape_language: List[str]
    costume_materials: List[str]
    expression_range: List[str]
    movement_language: List[str]
    continuity_rules: List[str]
    creative_context: str = ""


@dataclass
class EnvironmentSheet:
    project: str
    name: str
    story_function: str
    architecture: List[str]
    scale_depth: List[str]
    lighting: List[str]
    color_script: List[str]
    materials_weathering: List[str]
    continuity_rules: List[str]
    creative_context: str = ""


@dataclass
class PropSheet:
    project: str
    name: str
    story_function: str
    silhouette: List[str]
    construction: List[str]
    material_logic: List[str]
    interaction_rules: List[str]
    continuity_rules: List[str]
    creative_context: str = ""


class DesignSheetEngine:
    def __init__(self, creative_bridge: CreativeBriefProvider | None = None) -> None:
        self.creative_bridge = creative_bridge

    def _context(self, project: str, task: str) -> str:
        if self.creative_bridge is None:
            return ""
        return self.creative_bridge.build_brief(project=project, task=task).to_prompt_context()

    def character(self, *, project: str, name: str, role: str) -> CharacterSheet:
        return CharacterSheet(
            project=project, name=name, role=role,
            silhouette=["Readable at thumbnail scale", "Signature tools and costume must not merge into torso"],
            shape_language=["Primary shapes express role and temperament", "Secondary shapes support contrast and hierarchy"],
            costume_materials=["Construction must be plausible for the world", "Wear patterns reflect history and behavior"],
            expression_range=["Define neutral, joy, fear, anger, focus, surprise, and recovery", "Keep facial landmarks consistent across expressions"],
            movement_language=["Define idle posture, walk rhythm, action stance, and stress behavior", "Motion must preserve personality and weight"],
            continuity_rules=["Lock proportions and signature identifiers", "Track damage, costume state, carried objects, and scene changes"],
            creative_context=self._context(project, f"character design sheet for {name}; role: {role}"),
        )

    def environment(self, *, project: str, name: str, story_function: str) -> EnvironmentSheet:
        return EnvironmentSheet(
            project=project, name=name, story_function=story_function,
            architecture=["Architecture communicates culture, age, technology, and use", "Navigation paths support blocking and camera choices"],
            scale_depth=["Establish foreground, midground, and background anchors", "Include human-scale references"],
            lighting=["Define key direction, practical sources, and time-of-day behavior", "Lighting supports focal hierarchy"],
            color_script=["Define dominant, support, and accent relationships", "Track emotional changes across scenes"],
            materials_weathering=["Surface wear follows climate, contact, maintenance, and age", "Materials respond consistently to light"],
            continuity_rules=["Lock entrances, exits, landmarks, and major dimensions", "Track destruction, weather, props, and lighting changes"],
            creative_context=self._context(project, f"environment design sheet for {name}; story function: {story_function}"),
        )

    def prop(self, *, project: str, name: str, story_function: str) -> PropSheet:
        return PropSheet(
            project=project, name=name, story_function=story_function,
            silhouette=["Readable in hand and at story distance", "Functional parts remain visually distinct"],
            construction=["Define major components and assembly logic", "Identify moving, removable, fragile, and load-bearing parts"],
            material_logic=["Choose materials by function, manufacture, age, and world rules", "Wear appears where contact and stress occur"],
            interaction_rules=["Define grip, activation, storage, sound, weight, and failure behavior", "Character interaction remains consistent between shots"],
            continuity_rules=["Track orientation, damage, possession, charge/state, and modifications", "Preserve dimensions relative to characters"],
            creative_context=self._context(project, f"prop design sheet for {name}; story function: {story_function}"),
        )
