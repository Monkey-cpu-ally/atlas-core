"""Shared cognitive primitives for the three ATLAS cores.

Each core (Titan/Gaia/Mercury) is a thin subclass of `AICore` that supplies
its own identity, voice, hard rules, and reasoning style. The base class
handles the heavy lifting:

  • `think()`            — single response, with optional teaching/blueprint hooks
  • `system_prompt()`    — composes identity + base rules + hard rules
  • `mental_simulate()`  — internal "think before you speak" pass used by the
                           blueprint engine

`AICore` deliberately avoids any persistence; the memory layer lives in
`atlas_core.memory.memory` and is injected at call-time.

Identity anchor protection is wired in:
  • At import time each core is anchored via :func:`anchor_core`.
  • At call time `_compose_system_prompt()` checks `verify_identity()` and
    prepends the reinforcement preamble.
  • User messages are scrubbed of identity-hijack phrases via
    :func:`scrub_identity_attack` before reaching the LLM.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import List, Optional

from dotenv import load_dotenv

from ..shield_core import (
    anchor_core,
    verify_identity,
    reinforcement_preamble,
    scrub_identity_attack,
    IdentityDriftError,
)

load_dotenv()

# ---------------------------------------------------------------------------
# Shared rules — apply to every core unless overridden.
# ---------------------------------------------------------------------------

BASE_RULES = """
You are an ATLAS cognitive core. Honor these rules:

CONVERSATION
  - The user knows you. Never re-introduce yourself.
  - Speak like a calm human, not a chatbot. Match the user's register.

TEACHING DOCTRINE
  - PhD-level depth, 6th–7th grade clarity. No academic fluff.
  - Explain *why* before *how*. Concrete examples first, terminology second.
  - Teach constraints and failure modes early.
  - Admit uncertainty plainly; never fake confidence.

TEAMWORK
  - You PROPOSE. The user (architect-in-chief) DECIDES.
  - Defer to your siblings inside their expertise.
  - When asked, briefly note who should weigh in next.

SAFETY
  - No step-by-step instructions for high-risk domains.
  - Surface red flags before completing high-risk tasks.
"""


@dataclass
class CoreIdentity:
    """Static identity for one cognitive core."""
    key: str               # e.g. "ajani"
    code_name: str         # e.g. "Titan Core"
    name: str              # e.g. "Ajani"
    domain: str            # e.g. "Elemental Kinetics"
    voice_color: str       # hex
    reasoning_style: str   # one-line description for prompts
    hard_rules: List[str] = field(default_factory=list)
    bio: str = ""


class AICore:
    """Base class for all three cores.

    Subclasses only need to set `identity` and (optionally) override
    `extra_system_prompt()` to add persona-specific instructions. The
    base class auto-anchors each subclass instance the first time it is
    created so a runtime tamper attempt is detected at call-time.
    """

    identity: CoreIdentity  # set by subclass

    def __init__(self):
        # Anchor this core's identity. Re-anchoring is idempotent because
        # the fingerprint is deterministic.
        anchor_core(
            self.identity.key,
            self.identity.name,
            self.identity.code_name,
            self.identity.domain,
            self.identity.hard_rules,
        )

    # Lazy import so the module can be imported without emergentintegrations.
    @classmethod
    def _llm_chat(cls, session_id: str, system_message: str):
        from emergentintegrations.llm.chat import LlmChat
        return LlmChat(
            api_key=os.environ.get("EMERGENT_LLM_KEY", ""),
            session_id=session_id,
            system_message=system_message,
        ).with_model("openai", "gpt-5.2")

    # ------------------------------------------------------------------
    # Prompt assembly
    # ------------------------------------------------------------------
    def _verify_identity_or_raise(self) -> None:
        if not verify_identity(
            self.identity.key,
            self.identity.name,
            self.identity.code_name,
            self.identity.domain,
            self.identity.hard_rules,
        ):
            raise IdentityDriftError(
                f"Identity drift detected for {self.identity.key!r}. "
                "Refusing to talk."
            )

    def system_prompt(self) -> str:
        """Compose the full system prompt, anchor-verified and reinforced."""
        self._verify_identity_or_raise()
        identity = self.identity
        rules = "\n".join(f"  - {r}" for r in identity.hard_rules)
        return (
            reinforcement_preamble(identity.name, identity.code_name)
            + f"You are {identity.name} — code name {identity.code_name}.\n"
            + f"Domain: {identity.domain}\n"
            + f"Reasoning style: {identity.reasoning_style}\n"
            + f"{identity.bio}\n\n"
            + f"YOUR HARD RULES (never violate):\n{rules}\n"
            + f"{BASE_RULES}\n"
            + f"{self.extra_system_prompt()}"
        )

    def extra_system_prompt(self) -> str:  # subclass hook
        return ""

    # ------------------------------------------------------------------
    # Reasoning passes
    # ------------------------------------------------------------------
    async def think(
        self,
        user_message: str,
        *,
        session_id: Optional[str] = None,
        context: Optional[str] = None,
    ) -> str:
        """Single-shot reasoning. Returns the core's natural-language response."""
        from emergentintegrations.llm.chat import UserMessage

        # Identity-attack scrub on every user-supplied surface before the
        # LLM sees it. Sanitization at the shield is already done by the
        # route layer; this is the per-core last-mile defense.
        clean_msg = scrub_identity_attack(user_message)
        clean_ctx = scrub_identity_attack(context) if context else None

        chat = self._llm_chat(
            session_id=session_id or f"{self.identity.key}_{os.urandom(4).hex()}",
            system_message=self.system_prompt(),
        )
        text = clean_msg
        if clean_ctx:
            text = f"CONTEXT:\n{clean_ctx}\n\nQUESTION:\n{clean_msg}"
        return await chat.send_message(UserMessage(text=text))

    async def mental_simulate(
        self,
        proposal: str,
        *,
        session_id: Optional[str] = None,
    ) -> str:
        """Internal 'think before you speak' pass used by the Blueprint engine.

        The core privately reasons about a proposal — listing assumptions,
        unknowns, failure modes — *before* drafting any answer.
        """
        from emergentintegrations.llm.chat import UserMessage

        clean_proposal = scrub_identity_attack(proposal)
        sim_prompt = (
            self.system_prompt()
            + "\n\nYou are now in MENTAL SIMULATION mode. Do not draft an "
              "answer for the user yet. Instead, privately think:\n"
              "  1) what assumptions am I making?\n"
              "  2) what do I NOT know?\n"
              "  3) what could go wrong?\n"
              "  4) which sibling should I consult?\n"
              "Return a short bullet list. No prose."
        )
        chat = self._llm_chat(
            session_id=session_id or f"sim_{self.identity.key}_{os.urandom(4).hex()}",
            system_message=sim_prompt,
        )
        return await chat.send_message(UserMessage(text=clean_proposal))
