"""
atlas_core/pipeline/validator.py

Bot governance pipeline validation (Blueprint -> Build -> Modify -> Rollback).
"""

from ..bots.profiles import PROFILES


def validate_pipeline(stage: str, data: dict) -> None:
    allowed_stages = {"blueprint", "build", "modify", "rollback"}
    if stage not in allowed_stages:
        raise ValueError("Invalid pipeline stage")

    if stage == "rollback":
        return

    if stage in {"build", "modify"} and not data.get("blueprint_exists"):
        raise PermissionError("Cannot proceed without blueprint")

    bot_type = data.get("bot_type")
    action = data.get("action")

    if bot_type and action:
        if bot_type not in PROFILES:
            raise PermissionError(f"Unknown bot type: {bot_type}")

        profile = PROFILES[bot_type]
        if action not in profile.allowed_actions:
            raise PermissionError(f"Action '{action}' not allowed for {bot_type}")

        if action in profile.requires_human_approval_for and not data.get("human_approved"):
            raise PermissionError(f"Action '{action}' requires human approval for {bot_type}")

    if stage == "modify" and not data.get("approved"):
        raise PermissionError("Modification not approved")

    return
