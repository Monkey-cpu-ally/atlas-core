from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Set


@dataclass
class CollectionProduct:
    design_id: str
    role: str = "supporting"
    colors: Set[str] = field(default_factory=set)
    materials: Set[str] = field(default_factory=set)
    hardware_family: str = ""
    story_tags: Set[str] = field(default_factory=set)


@dataclass
class DesignCollection:
    collection_id: str
    name: str
    theme: str
    story: str
    palette: Set[str] = field(default_factory=set)
    material_family: Set[str] = field(default_factory=set)
    products: List[CollectionProduct] = field(default_factory=list)

    def add_product(self, product: CollectionProduct) -> None:
        if any(item.design_id == product.design_id for item in self.products):
            raise ValueError(f"Design already belongs to collection: {product.design_id}")
        self.products.append(product)

    @property
    def hero_products(self) -> List[CollectionProduct]:
        return [product for product in self.products if product.role == "hero"]

    def cohesion_score(self) -> float:
        if not self.products:
            return 0.0
        color_scores: List[float] = []
        material_scores: List[float] = []
        hardware: Dict[str, int] = {}
        for product in self.products:
            color_scores.append(
                len(product.colors & self.palette) / max(len(product.colors), 1)
            )
            material_scores.append(
                len(product.materials & self.material_family)
                / max(len(product.materials), 1)
            )
            if product.hardware_family:
                hardware[product.hardware_family] = hardware.get(product.hardware_family, 0) + 1
        dominant_hardware = max(hardware.values(), default=0) / len(self.products)
        story_sets = [product.story_tags for product in self.products if product.story_tags]
        shared_story = (
            len(set.intersection(*story_sets)) / max(len(set.union(*story_sets)), 1)
            if story_sets
            else 0.0
        )
        score = (
            sum(color_scores) / len(color_scores) * 0.30
            + sum(material_scores) / len(material_scores) * 0.30
            + dominant_hardware * 0.20
            + shared_story * 0.20
        )
        return round(score * 100.0, 2)

    def readiness_issues(self, minimum_products: int = 3) -> List[str]:
        issues: List[str] = []
        if len(self.products) < minimum_products:
            issues.append(f"Collection needs at least {minimum_products} products")
        if len(self.hero_products) != 1:
            issues.append("Collection must contain exactly one hero product")
        if self.cohesion_score() < 70.0:
            issues.append("Collection cohesion is below 70")
        return issues
