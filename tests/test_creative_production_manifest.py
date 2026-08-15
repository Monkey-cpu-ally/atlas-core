import pytest

from creative_production.manifest import (
    ProductionAsset,
    ProductionManifest,
    ProductionScene,
    ProductionStatus,
)


def test_manifest_tracks_assets_scenes_timing_and_readiness():
    manifest = ProductionManifest(
        project="Night Band",
        screenplay_status=ProductionStatus.APPROVED,
        visual_development_status=ProductionStatus.APPROVED,
        storyboard_status=ProductionStatus.APPROVED,
    )
    manifest.add_asset(ProductionAsset("char-protagonist", "Protagonist", "character", ProductionStatus.APPROVED))
    manifest.add_asset(ProductionAsset("env-forest", "Mystic Forest", "environment", ProductionStatus.APPROVED))
    manifest.add_asset(ProductionAsset("prop-horn", "Star Horn", "prop", ProductionStatus.APPROVED, dependencies=["char-protagonist"]))
    manifest.add_scene(ProductionScene(
        scene_number=1,
        status=ProductionStatus.IN_PROGRESS,
        character_assets=["char-protagonist"],
        environment_assets=["env-forest"],
        prop_assets=["prop-horn"],
        shot_count=2,
        total_frames=120,
        total_seconds=5.0,
    ))

    assert manifest.validate_dependencies() == []
    assert manifest.is_ready_for_production
    assert manifest.summary()["total_frames"] == 120
    assert manifest.summary()["total_seconds"] == 5.0


def test_manifest_detects_missing_dependencies_and_duplicate_ids():
    manifest = ProductionManifest(project="X")
    manifest.add_asset(ProductionAsset("prop-key", "Key", "prop", dependencies=["missing-character"]))
    manifest.add_scene(ProductionScene(scene_number=1, prop_assets=["missing-prop"]))
    assert "prop-key->missing-character" in manifest.validate_dependencies()
    assert "scene:1->missing-prop" in manifest.validate_dependencies()
    assert not manifest.is_ready_for_production

    with pytest.raises(ValueError):
        manifest.add_asset(ProductionAsset("prop-key", "Duplicate", "prop"))
    with pytest.raises(ValueError):
        manifest.add_scene(ProductionScene(scene_number=1))
