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
        self.client = OpenAI(
            api_key=os.environ.get("AI_INTEGRATIONS_OPENAI_API_KEY") or os.environ.get("OPENAI_API_KEY"),
            base_url=os.environ.get("AI_INTEGRATIONS_OPENAI_BASE_URL") or os.environ.get("OPENAI_BASE_URL"),
        )

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

        resp = self.client.chat.completions.create(
            model=model,
            messages=input_payload,
            max_tokens=2048,
        )
        text_out = resp.choices[0].message.content or ""

        for item in self.extractor.extract(user_text):
            self.memory.upsert_item(item)

        self.memory.add_entry(MemoryEntry(role=persona, content=text_out))

        return {"persona": persona, "text": text_out, "model": model}
