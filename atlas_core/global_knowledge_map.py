from dataclasses import dataclass, field
from typing import Dict, List


@dataclass(frozen=True)
class GlobalKnowledgeRegion:
    name: str
    study_areas: List[str]
    source_types: List[str]
    primary_ai_roles: List[str]
    notes: str = ""


class GlobalKnowledgeMap:
    def __init__(self) -> None:
        self.regions: Dict[str, GlobalKnowledgeRegion] = {
            "japan": GlobalKnowledgeRegion(
                name="Japan",
                study_areas=[
                    "minimalism",
                    "wood joinery",
                    "ceramics",
                    "textiles",
                    "stationery",
                    "automotive design",
                    "precision manufacturing",
                    "architecture",
                ],
                source_types=["museums", "craft archives", "universities", "manufacturer documentation"],
                primary_ai_roles=["Hermes", "Minerva"],
                notes="Study precision, restraint, craftsmanship, and material respect without copying identity.",
            ),
            "italy": GlobalKnowledgeRegion(
                name="Italy",
                study_areas=[
                    "tailoring",
                    "leatherwork",
                    "furniture",
                    "automotive design",
                    "marble",
                    "architecture",
                    "industrial design",
                ],
                source_types=["design schools", "museums", "craft references", "manufacturer documentation"],
                primary_ai_roles=["Hermes", "Ajani", "Minerva"],
            ),
            "france": GlobalKnowledgeRegion(
                name="France",
                study_areas=[
                    "haute couture",
                    "jewelry",
                    "interiors",
                    "perfume presentation",
                    "luxury retail",
                    "fashion history",
                ],
                source_types=["museums", "fashion archives", "design schools", "historical references"],
                primary_ai_roles=["Minerva", "Ajani", "Hermes"],
            ),
            "germany": GlobalKnowledgeRegion(
                name="Germany",
                study_areas=[
                    "engineering",
                    "machine tools",
                    "industrial design",
                    "automation",
                    "functional product design",
                    "manufacturing systems",
                ],
                source_types=["research institutes", "standards", "universities", "technical documentation"],
                primary_ai_roles=["Hermes", "Ajani"],
            ),
            "switzerland": GlobalKnowledgeRegion(
                name="Switzerland",
                study_areas=["watchmaking", "micro-engineering", "precision mechanics", "medical devices"],
                source_types=["technical schools", "industry documentation", "museums", "standards"],
                primary_ai_roles=["Hermes", "Ajani"],
            ),
            "india": GlobalKnowledgeRegion(
                name="India",
                study_areas=["textiles", "embroidery", "jewelry", "stone carving", "architecture", "color systems"],
                source_types=["museums", "textile archives", "craft references", "universities"],
                primary_ai_roles=["Minerva", "Hermes"],
            ),
            "china": GlobalKnowledgeRegion(
                name="China",
                study_areas=["ceramics", "silk", "advanced manufacturing", "electronics", "high-speed rail", "supply chains"],
                source_types=["universities", "museums", "manufacturer documentation", "industry reports"],
                primary_ai_roles=["Hermes", "Ajani", "Minerva"],
            ),
            "west_africa": GlobalKnowledgeRegion(
                name="West Africa",
                study_areas=["textiles", "metal casting", "wood carving", "goldsmithing", "fashion", "symbol systems"],
                source_types=["museums", "cultural archives", "universities", "craft references"],
                primary_ai_roles=["Minerva", "Hermes"],
                notes="Study with cultural respect and avoid flattening many nations into one style.",
            ),
            "united_states": GlobalKnowledgeRegion(
                name="United States",
                study_areas=["aerospace", "industrial design", "consumer electronics", "software interfaces", "manufacturing systems", "entertainment design"],
                source_types=["universities", "government research", "patents", "manufacturer documentation", "museums"],
                primary_ai_roles=["Ajani", "Hermes", "Minerva"],
            ),
            "scandinavia": GlobalKnowledgeRegion(
                name="Scandinavia",
                study_areas=["furniture", "lighting", "sustainable design", "wood", "human-centered products", "outdoor equipment"],
                source_types=["design museums", "universities", "manufacturer documentation", "architecture references"],
                primary_ai_roles=["Hermes", "Minerva"],
            ),
            "latin_america": GlobalKnowledgeRegion(
                name="Latin America",
                study_areas=["modern architecture", "textiles", "pottery", "furniture", "color", "urban design", "tropical materials"],
                source_types=["museums", "universities", "craft archives", "architecture references"],
                primary_ai_roles=["Minerva", "Hermes"],
            ),
        }

    def list_regions(self) -> List[GlobalKnowledgeRegion]:
        return list(self.regions.values())

    def get_region(self, key: str) -> GlobalKnowledgeRegion:
        return self.regions[key]

    def regions_for_ai(self, ai_name: str) -> List[GlobalKnowledgeRegion]:
        return [region for region in self.regions.values() if ai_name in region.primary_ai_roles]

    def study_areas(self) -> Dict[str, List[str]]:
        return {key: region.study_areas for key, region in self.regions.items()}


def create_global_knowledge_map() -> GlobalKnowledgeMap:
    return GlobalKnowledgeMap()
