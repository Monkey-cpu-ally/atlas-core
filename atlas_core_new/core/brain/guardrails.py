"""
atlas_core/core/brain/guardrails.py

Safety guardrails wrapping governance.
"""

from ..agent.governance import Governance


class Guardrails:
    def __init__(self):
        self.gov = Governance()

    def check(self, user_text: str):
        return self.gov.evaluate(user_text)
