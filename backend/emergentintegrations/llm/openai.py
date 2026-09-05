"""Compatibility adapter for ATLAS OpenAI text-to-speech.

The original application imports ``OpenAITextToSpeech`` from the local
``emergentintegrations`` namespace.  Some environments only carry the chat
adapter, which made importing ``routes.ai_services`` crash the whole API.

This module keeps that local contract stable.  In production it calls the
OpenAI Audio Speech REST endpoint.  In ``ATLAS_TEST_MODE`` it returns a
small deterministic MP3-shaped byte payload so CI never makes paid/external
network calls merely to validate routing.
"""
from __future__ import annotations

import os
from typing import Optional

import httpx


class OpenAITextToSpeech:
    """Minimal async TTS client matching the interface used by ATLAS."""

    def __init__(self, api_key: str, base_url: Optional[str] = None) -> None:
        self.api_key = api_key
        self.base_url = (base_url or os.environ.get("OPENAI_BASE_URL") or "https://api.openai.com/v1").rstrip("/")

    async def generate_speech(
        self,
        *,
        text: str,
        model: str = "tts-1",
        voice: str = "alloy",
        speed: float = 1.0,
    ) -> bytes:
        if os.environ.get("ATLAS_TEST_MODE") == "1":
            # Enough bytes for the integration tests to verify that the route
            # returns non-empty audio without contacting an external service.
            return b"ID3" + (b"\x00" * 8192)

        if not self.api_key:
            raise RuntimeError("OpenAI TTS is not configured")

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
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.base_url}/audio/speech",
                headers=headers,
                json=payload,
            )
            response.raise_for_status()
            return response.content
