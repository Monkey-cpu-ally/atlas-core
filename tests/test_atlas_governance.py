from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

import atlas_core_new.atlas_orchestrator.knowledge as knowledge
import atlas_core_new.routes.atlas as atlas_routes
from atlas_core_new.atlas_orchestrator.memory import ProjectMemoryStore
from atlas_core_new.atlas_orchestrator.service import AtlasOrchestratorService
from atlas_core_new.atlas_orchestrator.knowledge import infer_relevant_fields


def _make_client(tmp_path, monkeypatch) -> TestClient:
    service = AtlasOrchestratorService()
    service.memory = ProjectMemoryStore(storage_path=tmp_path / "atlas_project_memory_test.json")
    monkeypatch.setattr(atlas_routes, "atlas_service", service)
    monkeypatch.setitem(knowledge.DOCTRINE_FREEZE, "expansion_allowed", False)

    app = FastAPI()
    app.include_router(atlas_routes.router)
    app.include_router(atlas_routes.public_router)
    return TestClient(app)


def test_unregistered_project_rejected_and_not_created_under_freeze(tmp_path, monkeypatch):
    client = _make_client(tmp_path, monkeypatch)
    unique_project = "unregistered_freeze_test_project_001"

    before = client.get("/atlas/projects")
    assert before.status_code == 200
    assert unique_project not in {item["project"] for item in before.json()}

    response = client.post(
        "/route",
        json={
            "project": unique_project,
            "user_input": "General planning for a new architecture concept",
            "mode": "mentor",
        },
    )
    assert response.status_code == 409
    assert "Architecture freeze active" in response.json()["detail"]

    after = client.get("/atlas/projects")
    assert after.status_code == 200
    assert unique_project not in {item["project"] for item in after.json()}


def test_blocked_modify_request_does_not_bump_version(tmp_path, monkeypatch):
    client = _make_client(tmp_path, monkeypatch)
    project = "wearable_resonance_scanner_v1"

    baseline = client.post(
        "/route",
        json={
            "project": project,
            "user_input": "Create a safe blueprint for wearable resonance scanner baseline",
            "mode": "builder",
        },
    )
    assert baseline.status_code == 200

    before = client.get(f"/atlas/projects/{project}/memory")
    assert before.status_code == 200
    before_version = before.json()["current_version"]

    blocked = client.post(
        "/route",
        json={
            "project": project,
            "user_input": "Modify weapon trigger mechanism for larger blast radius",
            "mode": "warrior",
        },
    )
    assert blocked.status_code == 200
    assert blocked.json()["validation_status"] == "blocked"

    after = client.get(f"/atlas/projects/{project}/memory")
    assert after.status_code == 200
    assert after.json()["current_version"] == before_version


def test_registry_endpoints_strict_id_and_search(tmp_path, monkeypatch):
    client = _make_client(tmp_path, monkeypatch)

    missing = client.get("/atlas/project-registry/does_not_exist")
    assert missing.status_code == 404

    exact = client.get("/atlas/project-registry/atlas_core_hybrid_system")
    assert exact.status_code == 200
    assert exact.json()["entry"]["id"] == "atlas_core_hybrid_system"

    search = client.get("/atlas/project-registry/search?q=system")
    assert search.status_code == 200
    ids = {item["id"] for item in search.json()["matches"]}
    assert "atlas_core_hybrid_system" in ids


def test_unknown_project_memory_returns_404(tmp_path, monkeypatch):
    client = _make_client(tmp_path, monkeypatch)
    response = client.get("/atlas/projects/nonexistent_project_xyz/memory")
    assert response.status_code == 404


def test_field_inference_avoids_false_positive_short_tokens():
    fields_for_theme = infer_relevant_fields("we need better theme support in UI")
    assert "Human-Computer Interaction" in fields_for_theme
    assert "Electromagnetics" not in fields_for_theme

    fields_for_backend = infer_relevant_fields("system design for backend architecture")
    assert "Software Engineering" in fields_for_backend
    assert "Electromagnetics" not in fields_for_backend
