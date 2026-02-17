"""
Atlas Core Tools
-----------------
Creative and processing tools for the Atlas Core system.
"""

def _get_dragon_scale_app():
    from .dragon_scale_forge import app
    return app

__all__ = ["_get_dragon_scale_app"]
