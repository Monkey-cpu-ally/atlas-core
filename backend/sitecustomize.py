"""Backend-local compatibility hooks loaded automatically by Python."""

from __future__ import annotations

import importlib.util
import sys
import types
from typing import Any


def _install_openai_tts_compatibility() -> None:
    module_name = "emergentintegrations.llm.openai"
    try:
        if importlib.util.find_spec(module_name) is not None:
            return
    except (ImportError, ModuleNotFoundError, ValueError):
        pass

    module = types.ModuleType(module_name)

    class OpenAITextToSpeech:
        """Lazy adapter matching the older Emergent TTS interface."""

        def __init__(self, api_key: str, **_: Any) -> None:
            self.api_key = api_key

        async def generate_speech(
            self,
            *,
            text: str,
            model: str = "tts-1",
            voice: str = "alloy",
            speed: float = 1.0,
            **_: Any,
        ) -> bytes:
            if not self.api_key:
                raise RuntimeError("OpenAI TTS is not configured")
            try:
                from openai import AsyncOpenAI
            except ImportError as exc:
                raise RuntimeError("OpenAI TTS requires the optional openai package") from exc

            client = AsyncOpenAI(api_key=self.api_key)
            response = await client.audio.speech.create(
                model=model,
                voice=voice,
                input=text,
                speed=speed,
                response_format="mp3",
            )
            content = getattr(response, "content", None)
            if isinstance(content, bytes):
                return content
            read = getattr(response, "read", None)
            if callable(read):
                result = read()
                if hasattr(result, "__await__"):
                    result = await result
                if isinstance(result, bytes):
                    return result
            raise RuntimeError("OpenAI TTS returned an unsupported response type")

    module.OpenAITextToSpeech = OpenAITextToSpeech
    sys.modules[module_name] = module


_install_openai_tts_compatibility()
