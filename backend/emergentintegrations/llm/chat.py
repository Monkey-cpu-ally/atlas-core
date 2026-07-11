"""Compatibility implementation for the former private LlmChat package.

The public ATLAS repository can now install and test without the unavailable
`emergentintegrations` wheel. The interface intentionally matches the subset
used by ATLAS: `LlmChat(...).with_model(...).send_message(UserMessage(...))`.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional

import httpx


@dataclass(frozen=True)
class UserMessage:
    text: str


class LlmChat:
    def __init__(
        self,
        *,
        api_key: str,
        session_id: str,
        system_message: str,
    ) -> None:
        self.api_key = api_key
        self.session_id = session_id
        self.system_message = system_message
        self.provider = "openai"
        self.model = "gpt-4.1-mini"

    def with_model(self, provider: str, model: str) -> "LlmChat":
        self.provider = (provider or "openai").lower()
        self.model = model
        return self

    async def send_message(self, message: UserMessage) -> str:
        if not isinstance(message, UserMessage):
            raise TypeError("message must be a UserMessage")
        if not self.api_key:
            raise RuntimeError("LLM API key is not configured")

        base_url = self._base_url()
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": self.system_message},
                {"role": "user", "content": message.text},
            ],
            "stream": False,
        }

        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{base_url.rstrip('/')}/chat/completions",
                headers=headers,
                json=payload,
            )
        response.raise_for_status()
        data = response.json()
        try:
            content = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise RuntimeError("Malformed LLM response") from exc
        if not isinstance(content, str):
            raise RuntimeError("LLM response content was not text")
        return content

    def _base_url(self) -> str:
        explicit = os.environ.get("ATLAS_LLM_BASE_URL")
        if explicit:
            return explicit
        if self.provider == "openai":
            return os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
        provider_url = os.environ.get(f"{self.provider.upper()}_BASE_URL")
        if provider_url:
            return provider_url
        raise RuntimeError(
            f"Provider '{self.provider}' requires ATLAS_LLM_BASE_URL or "
            f"{self.provider.upper()}_BASE_URL"
        )
