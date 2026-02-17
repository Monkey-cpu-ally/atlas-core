"""
atlas_core/core/update_engine/validator.py

Guardrails for safe code updates.
"""

from dataclasses import dataclass
from typing import List


@dataclass
class ValidationResult:
    ok: bool
    errors: List[str]


class UpdateValidator:
    """
    Guardrails against:
    - persona prompt removal
    - pipeline bypass
    - updating core identity accidentally
    """

    REQUIRED_FILES = [
        "core/personas/definitions.py",
        "core/brain/persona_kernel.py",
        "core/brain/response_pipeline.py",
        "generator/multimodal_router.py",
    ]

    def validate_manifest(self, changed_files: List[str]) -> ValidationResult:
        errors = []
        for req in self.REQUIRED_FILES:
            pass

        sensitive = any(
            f.startswith("core/personas/") or f.startswith("core/brain/")
            for f in changed_files
        )
        if sensitive:
            errors.append("Sensitive update touches persona/brain. Require Hermes approval step (not implemented yet).")

        return ValidationResult(ok=(len(errors) == 0), errors=errors)
