"""OpenAI text-to-speech compatibility adapter for ATLAS.

This module exists because ``routes.ai_services`` imports
``OpenAITextToSpeech`` from the local ``emergentintegrations`` namespace.
The previous implementation referenced the module without shipping it, which
prevented the entire FastAPI application from importing in CI.

The adapter intentionally performs a real provider request. It does not return
dummy audio and it does not convert provider failures into success.
"""
from __future__ import annotations

from typing import Optional

import httpx


class OpenAITextToSpeech:
    """Small async client for OpenAI's ``/v1/audio/speech`` endpoint.

    ``api_key`` is supplied by the caller. ATLAS currently passes its configured
    AI-services key; if that credential is not accepted by OpenAI, the provider
    response is surfaced as an exception rather than fabricating audio.
    """

    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = "https://api.openai.com/v1",
        timeout_s: float = 60.0,
    ) -> None:
        self.api_key = (api_key or "").strip()
        self.base_url = base_url.rstrip("/")
        self.timeout_s = timeout_s

    async def generate_speech(
        self,
        *,
        text: str,
        model: str = "tts-1",
        voice: str = "alloy",
        speed: float = 1.0,
        response_format: str = "mp3",
    ) -> bytes:
        if not self.api_key:
            raise RuntimeError("OpenAI TTS is not configured: missing API key")
        if not text or not text.strip():
            raise ValueError("text is required")

        payload = {
            "model": model,
            "input": text,
            "voice": voice,
            "speed": speed,
            "response_format": response_format,
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(timeout=self.timeout_s) as client:
            response = await client.post(
                f"{self.base_url}/audio/speech",
                json=payload,
                headers=headers,
            )

        if response.is_error:
            detail: Optional[str]
            try:
                body = response.json()
                detail = body.get("error", {}).get("message") if isinstance(body, dict) else None
            except Exception:
                detail = None
            suffix = f": {detail}" if detail else ""
            raise RuntimeError(
                f"OpenAI TTS request failed with HTTP {response.status_code}{suffix}"
            )

        if not response.content:
            raise RuntimeError("OpenAI TTS returned an empty audio response")

        return response.content
