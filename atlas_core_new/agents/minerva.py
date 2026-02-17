"""
atlas_core/agents/minerva.py

Minerva - Nurturing guide with approval capabilities.
"""


class Minerva:
    """Minerva approves modifications based on type."""
    
    ALLOWED_TYPES = {"software", "sensor", "mission", "environment"}
    BLOCKED_TYPES = {"weaponization", "surveillance", "personal_data"}
    
    def __init__(self):
        self.name = "minerva"
        self.role = "guide"
    
    def approve(self, modification_type: str) -> bool:
        """
        Approve a modification request.
        Returns True if allowed, False if blocked.
        """
        if modification_type in self.BLOCKED_TYPES:
            return False
        if modification_type in self.ALLOWED_TYPES:
            return True
        return False
    
    def review(self, modification_type: str) -> dict:
        """
        Review a modification request with detailed response.
        """
        if modification_type in self.BLOCKED_TYPES:
            return {
                "approved": False,
                "type": modification_type,
                "reason": f"'{modification_type}' is blocked for safety"
            }
        if modification_type in self.ALLOWED_TYPES:
            return {
                "approved": True,
                "type": modification_type,
                "reason": f"'{modification_type}' is an allowed modification"
            }
        return {
            "approved": False,
            "type": modification_type,
            "reason": f"'{modification_type}' is not a recognized modification type"
        }
