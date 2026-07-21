from pathlib import Path

import pytest

from atlas_core.luxury.models import MaterialProfile
from atlas_core.luxury.service import LuxuryDesignService


def test_project_and_material_survive_reload(tmp_path: Path) -> None:
    database_path = tmp_path / "luxury.db"
    first = LuxuryDesignService(database_path)
    first.initialize()
    first.create_project("bag-001", "Knight Carry", "bag", "A repairable daily carry bag")
    first.add_material(
        MaterialProfile(
            name="Vegetable-tanned leather",
            category="leather",
            properties={"strength": 0.8},
            repairability=0.9,
            sustainability=0.7,
            aging_quality=0.95,
        )
    )

    second = LuxuryDesignService(database_path)
    second.initialize()

    project = second.projects.get("bag-001")
    material = second.materials.get("Vegetable-tanned leather")
    assert project is not None
    assert project.concept.name == "Knight Carry"
    assert material is not None
    assert material.aging_quality == 0.95


def test_weighted_progress_and_milestone(tmp_path: Path) -> None:
    service = LuxuryDesignService(tmp_path / "progress.db")
    service.initialize()
    for module in service.progress_repository.modules():
        service.progress_repository.update(module.module_id, 60, "test evidence")

    report = service.progress_report()
    assert report["overall"] == 60.0
    assert report["reached_60_percent"] is True


def test_unknown_progress_module_is_rejected(tmp_path: Path) -> None:
    service = LuxuryDesignService(tmp_path / "progress.db")
    service.initialize()
    with pytest.raises(KeyError):
        service.progress_repository.update("does-not-exist", 50)


def test_duplicate_project_is_rejected(tmp_path: Path) -> None:
    service = LuxuryDesignService(tmp_path / "projects.db")
    service.initialize()
    service.create_project("shoe-001", "Archive Boot", "footwear", "A rebuildable boot")
    with pytest.raises(ValueError):
        service.create_project("shoe-001", "Duplicate", "footwear", "Duplicate ID")
