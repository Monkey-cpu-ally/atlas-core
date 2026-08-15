"""Production manifest for tracking ATLAS creative projects from plan to delivery."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List


class ProductionStatus(str, Enum):
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    APPROVED = "approved"
    BLOCKED = "blocked"
    COMPLETE = "complete"


@dataclass
class ProductionAsset:
    asset_id: str
    name: str
    asset_type: str
    status: ProductionStatus = ProductionStatus.PLANNED
    owner: str = "unassigned"
    dependencies: List[str] = field(default_factory=list)
    continuity_notes: List[str] = field(default_factory=list)


@dataclass
class ProductionScene:
    scene_number: int
    status: ProductionStatus = ProductionStatus.PLANNED
    character_assets: List[str] = field(default_factory=list)
    environment_assets: List[str] = field(default_factory=list)
    prop_assets: List[str] = field(default_factory=list)
    shot_count: int = 0
    total_frames: int = 0
    total_seconds: float = 0.0
    continuity_notes: List[str] = field(default_factory=list)


@dataclass
class ProductionManifest:
    project: str
    assets: Dict[str, ProductionAsset] = field(default_factory=dict)
    scenes: Dict[int, ProductionScene] = field(default_factory=dict)
    screenplay_status: ProductionStatus = ProductionStatus.PLANNED
    visual_development_status: ProductionStatus = ProductionStatus.PLANNED
    storyboard_status: ProductionStatus = ProductionStatus.PLANNED

    def add_asset(self, asset: ProductionAsset) -> None:
        if asset.asset_id in self.assets:
            raise ValueError(f"duplicate asset_id: {asset.asset_id}")
        self.assets[asset.asset_id] = asset

    def add_scene(self, scene: ProductionScene) -> None:
        if scene.scene_number in self.scenes:
            raise ValueError(f"duplicate scene_number: {scene.scene_number}")
        self.scenes[scene.scene_number] = scene

    def validate_dependencies(self) -> List[str]:
        missing: List[str] = []
        for asset in self.assets.values():
            for dependency in asset.dependencies:
                if dependency not in self.assets:
                    missing.append(f"{asset.asset_id}->{dependency}")
        for scene in self.scenes.values():
            for asset_id in scene.character_assets + scene.environment_assets + scene.prop_assets:
                if asset_id not in self.assets:
                    missing.append(f"scene:{scene.scene_number}->{asset_id}")
        return sorted(set(missing))

    @property
    def is_ready_for_production(self) -> bool:
        return (
            not self.validate_dependencies()
            and self.screenplay_status in {ProductionStatus.APPROVED, ProductionStatus.COMPLETE}
            and self.visual_development_status in {ProductionStatus.APPROVED, ProductionStatus.COMPLETE}
            and self.storyboard_status in {ProductionStatus.APPROVED, ProductionStatus.COMPLETE}
            and bool(self.scenes)
        )

    def summary(self) -> dict:
        return {
            "project": self.project,
            "asset_count": len(self.assets),
            "scene_count": len(self.scenes),
            "missing_dependencies": self.validate_dependencies(),
            "ready_for_production": self.is_ready_for_production,
            "total_frames": sum(scene.total_frames for scene in self.scenes.values()),
            "total_seconds": round(sum(scene.total_seconds for scene in self.scenes.values()), 3),
        }
