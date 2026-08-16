import pytest

from creative_production.manifest import ProductionManifest, ProductionScene, ProductionStatus


def ready_manifest() -> ProductionManifest:
    manifest = ProductionManifest(
        project="Night Band",
        screenplay_status=ProductionStatus.APPROVED,
        visual_development_status=ProductionStatus.APPROVED,
        storyboard_status=ProductionStatus.APPROVED,
    )
    manifest.add_scene(ProductionScene(scene_number=2))
    return manifest


def test_unresolved_continuity_blocks_production_readiness():
    manifest = ready_manifest()
    scene = manifest.scenes[2]
    scene.continuity_issue_ids.extend(["condition:girl:1-2", "prop:star-horn:1-2"])

    assert not manifest.is_ready_for_production
    assert manifest.unresolved_continuity() == {
        2: ["condition:girl:1-2", "prop:star-horn:1-2"]
    }
    assert manifest.summary()["ready_for_production"] is False


def test_intentional_changes_can_be_approved_without_deleting_audit_history():
    manifest = ready_manifest()
    scene = manifest.scenes[2]
    scene.continuity_issue_ids.extend(["condition:girl:1-2", "prop:star-horn:1-2"])

    scene.approve_continuity_change("condition:girl:1-2")
    assert not manifest.is_ready_for_production
    assert scene.continuity_issue_ids == ["condition:girl:1-2", "prop:star-horn:1-2"]

    scene.approve_continuity_change("prop:star-horn:1-2")
    assert manifest.is_ready_for_production
    assert scene.continuity_issue_ids == ["condition:girl:1-2", "prop:star-horn:1-2"]
    assert scene.approved_continuity_issue_ids == ["condition:girl:1-2", "prop:star-horn:1-2"]


def test_unknown_continuity_issue_cannot_be_approved():
    scene = ProductionScene(scene_number=2, continuity_issue_ids=["prop:star-horn:1-2"])
    with pytest.raises(KeyError):
        scene.approve_continuity_change("costume:girl:1-2")
