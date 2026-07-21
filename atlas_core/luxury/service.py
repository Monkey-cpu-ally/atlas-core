from __future__ import annotations

from pathlib import Path
from typing import Dict

from .database import LuxuryDatabase
from .models import DesignConcept, ForgeRecord, MaterialProfile
from .progress import AcademyProgressTracker, ProgressRepository
from .repositories import DesignProjectRepository, MaterialRepository


class LuxuryDesignService:
    """High-level application service used by the CLI, API, and future ATLAS HUD."""

    def __init__(self, database_path: str | Path = "atlas_luxury.db") -> None:
        self.database = LuxuryDatabase(database_path)
        self.materials = MaterialRepository(self.database)
        self.projects = DesignProjectRepository(self.database)
        self.progress_repository = ProgressRepository(self.database)
        self.progress = AcademyProgressTracker(self.progress_repository)

    def initialize(self) -> None:
        self.database.initialize()
        self.progress_repository.seed()

    def create_project(
        self,
        design_id: str,
        name: str,
        product_type: str,
        description: str,
    ) -> ForgeRecord:
        if self.projects.get(design_id) is not None:
            raise ValueError(f"Design project already exists: {design_id}")
        record = ForgeRecord(
            concept=DesignConcept(
                design_id=design_id,
                name=name,
                product_type=product_type,
                description=description,
            )
        )
        record.history.append("idea: project created")
        self.projects.save(record)
        return record

    def add_material(self, material: MaterialProfile) -> None:
        self.materials.save(material)

    def progress_report(self) -> Dict[str, object]:
        return self.progress.report()
