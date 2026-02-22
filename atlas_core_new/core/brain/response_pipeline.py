"""
atlas_core/core/brain/response_pipeline.py

Multi-stage response pipeline with OpenAI integration.
"""

import os
from typing import Optional, Dict, Any
from openai import OpenAI

from .guardrails import Guardrails
from ..memory.memory_models import MemoryEntry
from ..memory.memory_policy import MemoryExtractor
from ..memory.memory_store import SimpleMemoryStore


class ResponsePipeline:
    """
    Multi-stage: guardrails -> memory -> LLM -> memory writeback
    Uses OpenAI-compatible API for AI responses.
    """
    def __init__(self, kernel, memory: SimpleMemoryStore):
        self.kernel = kernel
        self.memory = memory
        self.guardrails = Guardrails()
        self.extractor = MemoryExtractor()
        self._api_key = os.environ.get("AI_INTEGRATIONS_OPENAI_API_KEY") or os.environ.get("OPENAI_API_KEY")
        self._base_url = os.environ.get("AI_INTEGRATIONS_OPENAI_BASE_URL") or os.environ.get("OPENAI_BASE_URL")
        self.client: OpenAI | None = None

    def _ensure_client(self) -> OpenAI:
        if self.client is not None:
            return self.client

        api_key = self._api_key or os.environ.get("AI_INTEGRATIONS_OPENAI_API_KEY") or os.environ.get("OPENAI_API_KEY")
        base_url = self._base_url or os.environ.get("AI_INTEGRATIONS_OPENAI_BASE_URL") or os.environ.get("OPENAI_BASE_URL")

        if not api_key:
            from atlas_core_new.utils.error_handling import AtlasError
            raise AtlasError(
                "AI services are currently offline. Please configure an API key to use this endpoint.",
                status_code=503,
                detail="Missing OPENAI_API_KEY / AI_INTEGRATIONS_OPENAI_API_KEY",
            )

        kwargs: dict[str, object] = {"api_key": api_key}
        if base_url:
            kwargs["base_url"] = base_url
        self.client = OpenAI(**kwargs)
        return self.client

    def run(
        self,
        user_text: str,
        persona: str,
        style: Optional[str],
        mode: str,
        use_tools: bool,
        image_bytes: bytes | None = None,
    ) -> Dict[str, Any]:

        decision = self.guardrails.check(user_text)
        if not decision.allowed:
            return {"persona": persona, "text": f"Blocked: {decision.reason}", "severity": decision.severity}

        sys = self.kernel.system_prompt(persona=persona, style=style, mode=mode)

        self.memory.add_entry(MemoryEntry(role="user", content=user_text))

        input_payload = [
            {"role": "system", "content": sys},
            {"role": "user", "content": user_text},
        ]

        # the newest OpenAI model is "gpt-5" which was released August 7, 2025.
        # do not change this unless explicitly requested by the user
        model = "gpt-4o-mini"

        client = self._ensure_client()
        resp = client.chat.completions.create(
            model=model,
            messages=input_payload,
            max_tokens=2048,
        )
        text_out = resp.choices[0].message.content or ""

        for item in self.extractor.extract(user_text):
            self.memory.upsert_item(item)

        self.memory.add_entry(MemoryEntry(role=persona, content=text_out))

        return {"persona": persona, "text": text_out, "model": model}
