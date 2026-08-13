"""Compatibility implementation for the former private LlmChat package.

The public ATLAS repository can now install and test without the unavailable
`emergentintegrations` wheel. The interface intentionally matches the subset
used by ATLAS: `LlmChat(...).with_model(...).send_message(UserMessage(...))`.

When ATLAS_TEST_MODE=1, this shim returns deterministic local responses rather
than calling an external provider. Production behavior is unchanged.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass

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

        if os.environ.get("ATLAS_TEST_MODE") == "1":
            return self._test_response(message.text)

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

    def _test_response(self, user_text: str) -> str:
        """Return stable offline content for integration tests.

        The compatibility shim is the network boundary, so keeping the fake
        here lets route/service tests exercise their real persistence,
        retrieval, parsing and orchestration code without provider secrets.
        """
        system = self.system_message.lower()
        user = (user_text or "").lower()

        if "slider tweak" in system or '"control"' in system:
            return json.dumps({
                "control": "temperature",
                "value": 80,
                "reason": "Reduce thermal stress first; stable operating constraints protect output and hardware.",
            })

        if "ethical_score" in system and "ancestral_wisdom" in system:
            return json.dumps({
                "verdict": "approve_with_conditions",
                "summary": "Proceed with bounded safeguards and human review.",
                "ethical_score": 84,
                "concerns": ["Validate downstream impacts."],
                "conditions": ["Keep a reversible human approval gate."],
                "alternatives": [],
                "ancestral_wisdom": "Wisdom measures the path before the foot commits.",
            })

        if "feasibility_score" in system and "failure_modes" in system:
            return json.dumps({
                "verdict": "valid_with_constraints",
                "summary": "The concept is technically viable with explicit safety constraints.",
                "feasibility_score": 82,
                "safety_score": 86,
                "failure_modes": ["Thermal overload", "Unbounded control output"],
                "constraints": ["Enforce tested operating limits", "Require fail-safe shutdown"],
                "patterns": ["bounded control system"],
                "next_steps": ["Run verification tests"],
            })

        if "five-phase blueprint" in system or "philosophy" in system and "research" in system:
            return json.dumps({
                "philosophy": "Build for measurable human value.",
                "research": "Verify assumptions against trusted sources.",
                "architecture": "Use modular interfaces and explicit constraints.",
                "prototype": "Test the smallest safe implementation.",
                "verification": "Measure behavior before promotion.",
            })

        if "ajani" in system:
            return (
                "Ajani: Treat this as an engineering system. Check the architecture, load, "
                "constraints, safety margins, interfaces, and verification evidence before "
                "advancing the design."
            )
        if "minerva" in system:
            return (
                "Minerva: Connect the evidence to the learner. Explain the pattern clearly, "
                "preserve the source context, and turn the knowledge into a practical lesson."
            )
        if "hermes" in system:
            return (
                "Hermes: Verify the pattern against the data, test edge cases, record failure "
                "modes, and only promote claims that survive the evidence."
            )
        if "council" in system:
            return (
                "Council synthesis: Ajani checks structure, Minerva checks meaning, and Hermes "
                "checks evidence. Advance only when all three views agree on the verified path."
            )

        return (
            "ATLAS test response: verify the evidence, preserve traceability, apply explicit "
            "engineering constraints, and record the result before the next phase."
        )

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
