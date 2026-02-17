"""
atlas_core/core/update_engine/sandbox.py

Sandbox for testing code updates before applying.
"""

from dataclasses import dataclass
from typing import List

from .validator import UpdateValidator


@dataclass
class SandboxRun:
    ok: bool
    log: List[str]


class Sandbox:
    """
    Pretend-sandbox:
    - In real life you'd run tests, lint, import checks here.
    """
    def __init__(self):
        self.validator = UpdateValidator()

    def dry_run_update(self, changed_files: List[str]) -> SandboxRun:
        log = ["Sandbox: starting dry run", f"Files: {changed_files}"]
        res = self.validator.validate_manifest(changed_files)
        if not res.ok:
            log += ["Sandbox: FAILED"] + [f"- {e}" for e in res.errors]
            return SandboxRun(ok=False, log=log)

        log += ["Sandbox: PASSED (stub)"]
        return SandboxRun(ok=True, log=log)
