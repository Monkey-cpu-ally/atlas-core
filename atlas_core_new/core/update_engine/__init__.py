"""atlas_core/core/update_engine - Self-update system with safety validation."""
from .validator import UpdateValidator, ValidationResult
from .sandbox import Sandbox, SandboxRun
from .updater import Updater, UpdateStatus

__all__ = ["UpdateValidator", "ValidationResult", "Sandbox", "SandboxRun", "Updater", "UpdateStatus"]
