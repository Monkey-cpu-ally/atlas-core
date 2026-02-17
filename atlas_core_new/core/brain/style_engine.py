"""
atlas_core/core/brain/style_engine.py

Converts style labels into instruction text.
"""


class StyleEngine:
    """
    Converts a style label into instruction text.
    """
    STYLE_MAP = {
        "genndy": "Visual language: bold silhouettes, minimal dialogue, strong staging, rhythmic motion.",
        "arcane": "Painterly, high-contrast, cinematic lighting, textured detail, emotional realism.",
        "blueprint": "Technical, measured, labeled, schematic clarity, structured steps.",
        "photoreal": "Photorealistic, natural lighting, realistic materials, subtle imperfections.",
        "anime": "Clean linework, stylized proportions, expressive eyes, cel-shaded rendering.",
    }

    def compile(self, style: str | None) -> str:
        if not style:
            return "Default style: clear, structured, consistent with persona."
        return self.STYLE_MAP.get(style.lower().strip(), f"Style: {style} (apply consistently).")
