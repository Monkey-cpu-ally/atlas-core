"""Compatibility implementation for the former private OpenAI TTS helper.

ATLAS only relies on a small interface from the unavailable
`emergentintegrations.llm.openai` package:

    OpenAITextToSpeech(api_key=...).generate_speech(...)

This public shim preserves that interface and uses the OpenAI-compatible
`/audio/speech` endpoint through httpx. Importing this module performs no
network activity, which keeps backend startup and CI deterministic.

When ATLAS_TEST_MODE=1, deterministic local audio-like bytes are returned so
integration tests can validate routing without external credentials.
"""
from __future__ import annotations

import os

import httpx


class OpenAITextToSpeech:
    """Minimal async OpenAI-compatible text-to-speech client."""

    def __init__(self, *, api_key: str) -> None:
        self.api_key = api_key

    async def generate_speech(
        self,
        *,
        text: str,
        model: str = "tts-1",
        voice: str = "alloy",
        speed: float = 1.0,
    ) -> bytes:
        if not text or not text.strip():
            raise ValueError("text is required")

        if os.environ.get("ATLAS_TEST_MODE") == "1":
            # ID3 header + deterministic payload. The route tests only need a
            # non-trivial audio response and provider/voice headers; no test
            # should depend on a paid network TTS call.
            seed = f"{model}|{voice}|{speed}|{text}".encode("utf-8")
            payload = (seed * ((6000 // max(len(seed), 1)) + 1))[:6000]
            return b"ID3\x04\x00\x00\x00\x00\x00\x00" + payload

        if not self.api_key:
            raise RuntimeError("TTS API key is not configured")

        base_url = os.environ.get(
            "ATLAS_LLM_BASE_URL",
            os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1"),
        )
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": model,
            "voice": voice,
            "input": text,
            "speed": speed,
            "response_format": "mp3",
        }

        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{base_url.rstrip('/')}/audio/speech",
                headers=headers,
                json=payload,
            )
        response.raise_for_status()
        return response.content
