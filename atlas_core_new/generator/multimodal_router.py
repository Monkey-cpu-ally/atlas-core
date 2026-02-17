"""
atlas_core/generator/multimodal_router.py

Decides what kind of generation the user is asking for.
"""


class MultimodalRouter:
    """
    Decides what kind of generation the user is asking for.
    """
    def route(self, text: str, has_image: bool) -> str:
        t = (text or "").lower()
        if has_image:
            if "generate an image" in t or "make an image" in t:
                return "image_gen"
            return "image_to_text"
        return "text"
