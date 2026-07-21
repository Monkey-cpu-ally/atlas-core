from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List

from .database import LuxuryDatabase


@dataclass(frozen=True)
class ProgressModule:
    module_id: str
    name: str
    category: str
    weight: float
    completion: float = 0.0
    evidence: str = ""

    def __post_init__(self) -> None:
        if self.weight <= 0:
            raise ValueError("weight must be greater than zero")
        if not 0 <= self.completion <= 100:
            raise ValueError("completion must be between 0 and 100")


DEFAULT_ROADMAP: List[ProgressModule] = [
    ProgressModule("curriculum-foundation", "Curriculum foundation", "curriculum", 8),
    ProgressModule("leather-academy", "Leather Academy", "curriculum", 4),
    ProgressModule("textile-academy", "Textile Academy", "curriculum", 4),
    ProgressModule("hardware-academy", "Hardware Academy", "curriculum", 4),
    ProgressModule("pattern-language", "Pattern Language", "curriculum", 4),
    ProgressModule("bag-academy", "Bag Academy", "product_academies", 4),
    ProgressModule("footwear-academy", "Footwear Academy", "product_academies", 4),
    ProgressModule("furniture-academy", "Furniture Academy", "product_academies", 4),
    ProgressModule("jewelry-watch-academy", "Watch and Jewelry Academy", "product_academies", 4),
    ProgressModule("design-models", "Design data models", "software", 5),
    ProgressModule("genome-engine", "Design Genome engine", "software", 5),
    ProgressModule("critique-engine", "Critique and originality engines", "software", 5),
    ProgressModule("council-engine", "Council review engine", "software", 4),
    ProgressModule("forge-engine", "Design Forge engine", "software", 5),
    ProgressModule("database", "Persistent database", "software", 6),
    ProgressModule("material-library", "Material Library", "data", 6),
    ProgressModule("project-manager", "Design project manager", "software", 5),
    ProgressModule("manufacturing-engine", "Manufacturing and costing engine", "software", 6),
    ProgressModule("engineering-tools", "Product engineering calculators", "software", 5),
    ProgressModule("prototype-testing", "Prototype testing system", "software", 4),
    ProgressModule("cli", "Command-line interface", "integration", 3),
    ProgressModule("api", "ATLAS API layer", "integration", 4),
    ProgressModule("ai-agents", "Hermes, Minerva, Ajani agent integration", "integration", 6),
    ProgressModule("automated-tests", "Automated test suite and CI", "testing", 5),
]


class ProgressRepository:
    def __init__(self, database: LuxuryDatabase) -> None:
        self.database = database

    def seed(self, modules: Iterable[ProgressModule] = DEFAULT_ROADMAP) -> None:
        with self.database.connect() as connection:
            for module in modules:
                connection.execute(
                    """
                    INSERT INTO academy_modules
                        (module_id, name, category, weight, completion, evidence)
                    VALUES (?, ?, ?, ?, ?, ?)
                    ON CONFLICT(module_id) DO NOTHING
                    """,
                    (
                        module.module_id,
                        module.name,
                        module.category,
                        module.weight,
                        module.completion,
                        module.evidence,
                    ),
                )

    def update(self, module_id: str, completion: float, evidence: str = "") -> None:
        if not 0 <= completion <= 100:
            raise ValueError("completion must be between 0 and 100")
        with self.database.connect() as connection:
            cursor = connection.execute(
                """
                UPDATE academy_modules
                SET completion=?, evidence=?, updated_at=CURRENT_TIMESTAMP
                WHERE module_id=?
                """,
                (completion, evidence, module_id),
            )
            if cursor.rowcount == 0:
                raise KeyError(f"Unknown roadmap module: {module_id}")

    def modules(self) -> List[ProgressModule]:
        with self.database.connect() as connection:
            rows = connection.execute(
                "SELECT * FROM academy_modules ORDER BY category, name"
            ).fetchall()
        return [
            ProgressModule(
                module_id=row["module_id"],
                name=row["name"],
                category=row["category"],
                weight=row["weight"],
                completion=row["completion"],
                evidence=row["evidence"],
            )
            for row in rows
        ]


class AcademyProgressTracker:
    def __init__(self, repository: ProgressRepository) -> None:
        self.repository = repository

    def overall(self) -> float:
        modules = self.repository.modules()
        total_weight = sum(module.weight for module in modules)
        if total_weight == 0:
            return 0.0
        weighted = sum(module.weight * module.completion for module in modules)
        return round(weighted / total_weight, 2)

    def by_category(self) -> Dict[str, float]:
        groups: Dict[str, List[ProgressModule]] = {}
        for module in self.repository.modules():
            groups.setdefault(module.category, []).append(module)
        result: Dict[str, float] = {}
        for category, modules in groups.items():
            weight = sum(module.weight for module in modules)
            result[category] = round(
                sum(module.weight * module.completion for module in modules) / weight,
                2,
            )
        return result

    def reached(self, threshold: float = 60.0) -> bool:
        return self.overall() >= threshold

    def report(self) -> Dict[str, object]:
        return {
            "overall": self.overall(),
            "categories": self.by_category(),
            "reached_60_percent": self.reached(60.0),
            "modules": [module.__dict__ for module in self.repository.modules()],
        }
