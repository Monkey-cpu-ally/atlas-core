"""
atlas_core/agents/hermes.py

Hermes - Guardian/Validator agent with enforcement capabilities.
"""

from atlas_core_new.pipeline.validator import validate_pipeline


class Hermes:
    """Hermes enforces pipeline rules and validates bot actions."""
    
    def __init__(self):
        self.name = "hermes"
        self.role = "guardian"
    
    def enforce(self, stage: str, data: dict) -> bool:
        """
        Enforce pipeline rules. Raises PermissionError if validation fails.
        Returns True if validation passes.
        """
        validate_pipeline(stage, data)
        return True
    
    def check(self, stage: str, data: dict) -> dict:
        """
        Check pipeline rules without raising. Returns result dict.
        """
        try:
            validate_pipeline(stage, data)
            return {"valid": True, "stage": stage}
        except (ValueError, PermissionError) as e:
            return {"valid": False, "error": str(e)}
