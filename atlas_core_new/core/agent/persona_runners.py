"""
atlas_core/core/agent/persona_runners.py

Persona-specific runners.
"""

from typing import Optional, Dict, Any


class BaseRunner:
    persona_name: str = "ajani"

    def __init__(self, pipeline):
        self.pipeline = pipeline

    def run(self, user_text: str, style: Optional[str], mode: str, use_tools: bool, image_bytes=None) -> Dict[str, Any]:
        return self.pipeline.run(
            user_text=user_text,
            persona=self.persona_name,
            style=style,
            mode=mode,
            use_tools=use_tools,
            image_bytes=image_bytes,
        )


class AjaniRunner(BaseRunner):
    persona_name = "ajani"


class MinervaRunner(BaseRunner):
    persona_name = "minerva"


class HermesRunner(BaseRunner):
    persona_name = "hermes"
