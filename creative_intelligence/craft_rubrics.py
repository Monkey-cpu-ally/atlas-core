"""Craft-quality rubrics for ATLAS Creative Intelligence.

These rubrics separate technical validity from artistic/narrative quality. They are
medium-aware and intentionally avoid equating detail, realism, darkness, violence,
or resolution with quality.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple


@dataclass(frozen=True)
class CraftDimension:
    name: str
    question: str
    failure_signals: Tuple[str, ...]


@dataclass(frozen=True)
class CraftRubric:
    name: str
    dimensions: Tuple[CraftDimension, ...]
    passing_score: int = 90

    def validate_scores(self, scores: Dict[str, int]) -> Dict[str, int]:
        expected = {d.name for d in self.dimensions}
        missing = expected - set(scores)
        if missing:
            raise ValueError(f"missing craft dimensions: {sorted(missing)}")
        return {key: max(0, min(100, int(scores[key]))) for key in expected}


STORY = CraftRubric("story", (
    CraftDimension("character_motivation", "Do choices follow believable wants, fears, knowledge, and pressure?", ("arbitrary decision", "plot-forced behavior")),
    CraftDimension("internal_logic", "Does the story obey the rules it establishes?", ("contradiction", "unearned exception")),
    CraftDimension("conflict", "Does opposition meaningfully pressure characters and values?", ("passive conflict", "repetitive threat")),
    CraftDimension("setup_payoff", "Do planted details, promises, and questions receive earned consequences?", ("forgotten setup", "unearned payoff")),
    CraftDimension("originality", "Does the work transform influences into a distinct premise and execution?", ("trope collage", "reference clone")),
    CraftDimension("emotional_authenticity", "Are emotional reactions earned and specific to the characters?", ("forced emotion", "melodrama without cause")),
    CraftDimension("pacing", "Do scene length, escalation, recovery, and revelation serve the intended experience?", ("rushed", "repetitive", "no breathing room")),
    CraftDimension("dialogue", "Does dialogue reveal character, conflict, information, or subtext without sounding interchangeable?", ("exposition dump", "same voice", "forced joke")),
    CraftDimension("theme", "Do events and choices meaningfully explore the story's underlying ideas?", ("theme stated but not dramatized",)),
    CraftDimension("ending", "Does the ending resolve or deliberately transform the story's central dramatic promises?", ("abrupt ending", "unearned twist")),
))


VISUAL_ART = CraftRubric("visual_art", (
    CraftDimension("composition", "Are forms arranged intentionally to support meaning and readability?", ("accidental tangent", "dead composition")),
    CraftDimension("focal_hierarchy", "Does the viewer know where to look first, second, and third?", ("equal contrast everywhere", "competing focal points")),
    CraftDimension("value_structure", "Do light/dark masses organize depth, focus, and mood?", ("muddy values", "flat value grouping")),
    CraftDimension("color_relationships", "Do hue, saturation, and temperature relationships support the image's purpose?", ("uncontrolled palette", "temperature conflict")),
    CraftDimension("shape_language", "Do shapes communicate identity, function, mood, and hierarchy?", ("generic shapes", "unclear silhouette")),
    CraftDimension("gesture", "Do pose and directional flow communicate weight, intent, and energy?", ("stiff pose", "unclear action")),
    CraftDimension("depth", "Do overlap, scale, perspective, value, and edges establish convincing spatial organization?", ("flattened space", "confused planes")),
    CraftDimension("edge_control", "Are hard, soft, lost, and found edges used intentionally?", ("uniform edges", "cutout look")),
    CraftDimension("visual_storytelling", "Does the image communicate narrative or emotional information beyond decoration?", ("decorative only", "unclear moment")),
    CraftDimension("originality", "Does the image have a project-specific visual identity rather than generic generated aesthetics?", ("generic ai look", "reference clone")),
))


MEDIUMS = {
    "oil_painting": CraftRubric("oil_painting", (
        CraftDimension("layering", "Do underpainting, opaque passages, glazing/scumbling, and corrections behave intentionally?", ("filter-like layering",)),
        CraftDimension("brush_direction", "Does mark direction describe form, movement, material, or emphasis?", ("random brush texture",)),
        CraftDimension("paint_body", "Are thin and impasto passages varied with purpose?", ("uniform fake impasto",)),
        CraftDimension("edge_behavior", "Do painted edges emerge, soften, disappear, and return intentionally?", ("digital cutout edges",)),
        CraftDimension("surface_integration", "Does canvas/surface texture interact plausibly with marks rather than overlay them?", ("texture overlay",)),
    )),
    "watercolor": CraftRubric("watercolor", (
        CraftDimension("wash_control", "Are washes, gradients, blooms, and backruns controlled or intentionally exploited?", ("random bloom artifacts",)),
        CraftDimension("transparency", "Does layering preserve believable transparent pigment behavior?", ("opaque filter look",)),
        CraftDimension("paper_interaction", "Do edges, granulation, pooling, and dry areas respond plausibly to paper and water?", ("paper texture overlay",)),
        CraftDimension("reserved_light", "Are whites and luminous passages planned rather than digitally painted over?", ("fake white paint recovery",)),
        CraftDimension("mark_variety", "Are wet-on-wet, wet-on-dry, drybrush, and controlled edges used intentionally?", ("single-effect rendering",)),
    )),
    "ink": CraftRubric("ink", (
        CraftDimension("line_weight", "Does line weight communicate depth, form, emphasis, and material?", ("uniform line weight",)),
        CraftDimension("black_shapes", "Are spotted blacks designed as compositional masses rather than filled randomly?", ("random black fill",)),
        CraftDimension("hatching", "Does hatching describe plane, value, texture, and form consistently?", ("decorative hatching",)),
        CraftDimension("line_economy", "Are marks purposeful rather than noisy or overworked?", ("indiscriminate detail",)),
        CraftDimension("negative_space", "Is untouched space actively designed as part of the image?", ("filled-everywhere composition",)),
    )),
}


QUALITY_PRINCIPLES = (
    "Quality is intentional execution of the work's artistic objective.",
    "Complexity is not quality.",
    "Realism is not quality.",
    "Detail is not quality.",
    "Darkness, violence, or seriousness are not quality.",
    "High resolution is not artistic quality by itself.",
    "A simple image or story can outperform a complex one when its decisions are clearer and more effective.",
)
