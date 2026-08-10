from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass
class WorldBible:
    name: str
    core_identity: str
    history: List[str] = field(default_factory=list)
    geography: List[str] = field(default_factory=list)
    cultures: List[str] = field(default_factory=list)
    politics: List[str] = field(default_factory=list)
    economy: List[str] = field(default_factory=list)
    technology: List[str] = field(default_factory=list)
    belief_systems: List[str] = field(default_factory=list)
    architecture: List[str] = field(default_factory=list)
    ecology: List[str] = field(default_factory=list)
    timeline: List[str] = field(default_factory=list)
    consistency_checks: List[str] = field(default_factory=list)

    def to_markdown(self) -> str:
        lines = [f"# {self.name}", "", f"Core Identity: {self.core_identity}", ""]
        sections = [
            ("History", self.history),
            ("Geography", self.geography),
            ("Cultures", self.cultures),
            ("Politics", self.politics),
            ("Economy", self.economy),
            ("Technology", self.technology),
            ("Belief Systems", self.belief_systems),
            ("Architecture", self.architecture),
            ("Ecology", self.ecology),
            ("Timeline", self.timeline),
            ("Consistency Checks", self.consistency_checks),
        ]
        for title, items in sections:
            lines.append(f"## {title}")
            lines.extend(f"- {item}" for item in items)
            lines.append("")
        return "\n".join(lines)


class WorldBibleEngine:
    def build_bible(self, name: str, core_identity: str) -> WorldBible:
        return WorldBible(
            name=name,
            core_identity=core_identity,
            history=[
                "Define founding event, major rupture, recovery period, and current unresolved tension.",
                "History must leave visible scars in institutions, architecture, language, and behavior.",
            ],
            geography=[
                "Define climate, terrain, travel barriers, resources, and strategic locations.",
                "Geography should shape culture and conflict.",
            ],
            cultures=[
                "Define food, clothing, family structure, rituals, status symbols, music, and taboos.",
                "Avoid monocultures; include internal disagreement and regional variation.",
            ],
            politics=[
                "Define who has power, how they gained it, who resists it, and what keeps the system stable.",
            ],
            economy=[
                "Define labor, trade, scarcity, wealth, transport, and what people cannot easily obtain.",
            ],
            technology=[
                "Define what technology can do, what it cannot do, who controls it, and what it costs.",
            ],
            belief_systems=[
                "Define myths, rituals, sacred places, doubts, reform movements, and contradictions.",
            ],
            architecture=[
                "Let buildings reveal climate, class, technology, religion, and historical change.",
            ],
            ecology=[
                "Define plants, animals, pests, diseases, water systems, seasons, and human impact.",
            ],
            timeline=[
                "Founding",
                "First transformation",
                "Major crisis",
                "Recovery or conquest",
                "Present-day tension",
            ],
            consistency_checks=[
                "Does geography affect politics and trade?",
                "Does history affect architecture and behavior?",
                "Do technology and economy obey the same world constraints?",
                "Does the world feel lived-in instead of assembled from tropes?",
            ],
        )
