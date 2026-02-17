"""
atlas_core/generator/image_pipeline.py

Image generation wrapper using OpenAI DALL-E API.
Generates concept art for projects with dark moody industrial aesthetic.
"""

import base64
import os
import logging

from openai import OpenAI

logger = logging.getLogger(__name__)

STYLE_PROMPTS = {
    "blueprint": "Dark moody industrial blueprint concept art, technical schematic overlay, dark metallic surfaces, cyberpunk industrial aesthetic, dark background",
    "prototype": "Dark moody prototype concept art, work-in-progress on test bench, industrial workshop or laboratory setting, dark background",
    "biomimetic": "Dark moody biomimetic sci-fi concept art, organic-mechanical fusion, bioluminescent elements, dark atmospheric aesthetic",
    "cybernetic": "Dark moody cybernetic naturalism concept art, nature integrated with technology, dark atmospheric aesthetic",
    "cosmic": "Dark moody cosmic horror concept art, Lovecraftian scale and mystery, void-black and deep crimson palette",
    "default": "Dark moody industrial concept art, atmospheric lighting, dark background",
}

PERSONA_ACCENTS = {
    "ajani": "teal accent lighting",
    "minerva": "crimson accent lighting",
    "hermes": "amber accent lighting",
}


class ImagePipeline:
    """
    Image generation using OpenAI DALL-E API.
    Produces dark, moody, industrial concept art for Atlas Core projects.
    """

    def __init__(self):
        self.client = OpenAI(
            api_key=os.environ.get("AI_INTEGRATIONS_OPENAI_API_KEY") or os.environ.get("OPENAI_API_KEY"),
            base_url=os.environ.get("AI_INTEGRATIONS_OPENAI_BASE_URL") or os.environ.get("OPENAI_BASE_URL"),
        )

    def generate(self, prompt: str, style: str | None = None, persona: str | None = None) -> str:
        """
        Generate an image and return it as base64-encoded PNG data.

        Args:
            prompt: Description of what to generate
            style: Style key from STYLE_PROMPTS (blueprint, prototype, etc.)
            persona: Persona name for accent color (ajani, minerva, hermes)

        Returns:
            Base64-encoded PNG image data
        """
        style_suffix = STYLE_PROMPTS.get(style, STYLE_PROMPTS["default"])
        accent = PERSONA_ACCENTS.get(persona, "") if persona else ""

        full_prompt = f"{prompt}, {style_suffix}"
        if accent:
            full_prompt += f", {accent}"

        try:
            response = self.client.images.generate(
                model="dall-e-3",
                prompt=full_prompt,
                size="1024x1024",
                quality="standard",
                n=1,
                response_format="b64_json",
            )
            image_data = response.data[0].b64_json
            logger.info(f"Generated image for prompt: {prompt[:60]}...")
            return image_data
        except Exception as e:
            logger.error(f"Image generation failed: {e}")
            raise

    def generate_and_save(self, prompt: str, output_path: str, style: str | None = None, persona: str | None = None) -> str:
        """
        Generate an image and save it to disk.

        Args:
            prompt: Description of what to generate
            output_path: Full file path to save the PNG
            style: Style key from STYLE_PROMPTS
            persona: Persona name for accent color

        Returns:
            The output_path where the image was saved
        """
        image_b64 = self.generate(prompt, style=style, persona=persona)
        image_bytes = base64.b64decode(image_b64)

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "wb") as f:
            f.write(image_bytes)

        logger.info(f"Saved image to {output_path}")
        return output_path
