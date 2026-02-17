"""atlas_core/core/ui - Input handling (voice, image, dashboard)."""
from .voice_input import transcribe_stub
from .image_input import describe_image_stub

__all__ = ["transcribe_stub", "describe_image_stub"]
