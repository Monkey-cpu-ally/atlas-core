from __future__ import annotations

from typing import List, Optional

from .database import LuxuryDatabase
from .models import DesignConcept, ForgeRecord, ForgeStage, MaterialProfile


class MaterialRepository:
    def __init__(self, database: LuxuryDatabase) -> None:
        self.database = database

    def save(self, material: MaterialProfile) -> None:
        with self.database.connect() as connection:
            connection.execute(
                """
                INSERT INTO materials (
                    name, category, properties_json, emotions_json,
                    compatible_materials_json, repairability,
                    sustainability, aging_quality, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(name) DO UPDATE SET
                    category=excluded.category,
                    properties_json=excluded.properties_json,
                    emotions_json=excluded.emotions_json,
                    compatible_materials_json=excluded.compatible_materials_json,
                    repairability=excluded.repairability,
                    sustainability=excluded.sustainability,
                    aging_quality=excluded.aging_quality,
                    notes=excluded.notes
                """,
                (
                    material.name,
                    material.category,
                    self.database.dumps(material.properties),
                    self.database.dumps(material.emotions),
                    self.database.dumps(material.compatible_materials),
                    material.repairability,
                    material.sustainability,
                    material.aging_quality,
                    material.notes,
                ),
            )

    def get(self, name: str) -> Optional[MaterialProfile]:
        with self.database.connect() as connection:
            row = connection.execute("SELECT * FROM materials WHERE name=?", (name,)).fetchone()
        if row is None:
            return None
        return MaterialProfile(
            name=row["name"],
            category=row["category"],
            properties=self.database.loads(row["properties_json"], {}),
            emotions=self.database.loads(row["emotions_json"], []),
            compatible_materials=self.database.loads(row["compatible_materials_json"], []),
            repairability=row["repairability"],
            sustainability=row["sustainability"],
            aging_quality=row["aging_quality"],
            notes=row["notes"],
        )

    def list_all(self) -> List[MaterialProfile]:
        with self.database.connect() as connection:
            names = [row["name"] for row in connection.execute("SELECT name FROM materials ORDER BY name")]
        return [material for name in names if (material := self.get(name)) is not None]


class DesignProjectRepository:
    def __init__(self, database: LuxuryDatabase) -> None:
        self.database = database

    def save(self, record: ForgeRecord, revision: int = 1) -> None:
        concept = record.concept
        with self.database.connect() as connection:
            connection.execute(
                """
                INSERT INTO design_projects (
                    design_id, name, product_type, description, story,
                    silhouette_notes, materials_json, hardware_json,
                    patterns_json, inspirations_json, repair_plan,
                    manufacturing_notes, metadata_json, stage, revision
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(design_id) DO UPDATE SET
                    name=excluded.name,
                    product_type=excluded.product_type,
                    description=excluded.description,
                    story=excluded.story,
                    silhouette_notes=excluded.silhouette_notes,
                    materials_json=excluded.materials_json,
                    hardware_json=excluded.hardware_json,
                    patterns_json=excluded.patterns_json,
                    inspirations_json=excluded.inspirations_json,
                    repair_plan=excluded.repair_plan,
                    manufacturing_notes=excluded.manufacturing_notes,
                    metadata_json=excluded.metadata_json,
                    stage=excluded.stage,
                    revision=excluded.revision,
                    updated_at=CURRENT_TIMESTAMP
                """,
                (
                    concept.design_id,
                    concept.name,
                    concept.product_type,
                    concept.description,
                    concept.story,
                    concept.silhouette_notes,
                    self.database.dumps(concept.materials),
                    self.database.dumps(concept.hardware),
                    self.database.dumps(concept.patterns),
                    self.database.dumps(concept.inspirations),
                    concept.repair_plan,
                    concept.manufacturing_notes,
                    self.database.dumps(concept.metadata),
                    record.stage.value,
                    revision,
                ),
            )
            for history_item in record.history:
                stage, _, note = history_item.partition(":")
                connection.execute(
                    "INSERT INTO forge_history (design_id, stage, note) VALUES (?, ?, ?)",
                    (concept.design_id, stage.strip(), note.strip()),
                )

    def get(self, design_id: str) -> Optional[ForgeRecord]:
        with self.database.connect() as connection:
            row = connection.execute(
                "SELECT * FROM design_projects WHERE design_id=?", (design_id,)
            ).fetchone()
            history_rows = connection.execute(
                "SELECT stage, note FROM forge_history WHERE design_id=? ORDER BY id",
                (design_id,),
            ).fetchall()
        if row is None:
            return None
        concept = DesignConcept(
            design_id=row["design_id"],
            name=row["name"],
            product_type=row["product_type"],
            description=row["description"],
            story=row["story"],
            silhouette_notes=row["silhouette_notes"],
            materials=self.database.loads(row["materials_json"], []),
            hardware=self.database.loads(row["hardware_json"], []),
            patterns=self.database.loads(row["patterns_json"], []),
            inspirations=self.database.loads(row["inspirations_json"], []),
            repair_plan=row["repair_plan"],
            manufacturing_notes=row["manufacturing_notes"],
            metadata=self.database.loads(row["metadata_json"], {}),
        )
        history = [f'{item["stage"]}: {item["note"]}'.strip() for item in history_rows]
        return ForgeRecord(concept=concept, stage=ForgeStage(row["stage"]), history=history)

    def list_ids(self) -> List[str]:
        with self.database.connect() as connection:
            return [row["design_id"] for row in connection.execute(
                "SELECT design_id FROM design_projects ORDER BY updated_at DESC"
            )]
