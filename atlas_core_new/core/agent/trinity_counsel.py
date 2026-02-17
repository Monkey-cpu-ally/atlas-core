"""
atlas_core_new/core/agent/trinity_counsel.py

Trinity Counsel Mode: All three personas collaborate on a problem.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import os
from openai import OpenAI


@dataclass
class CounselResponse:
    """Response from a single persona in counsel mode."""
    persona: str
    perspective: str
    recommendation: str


@dataclass
class TrinityCounselResult:
    """Combined result from Trinity Counsel."""
    question: str
    responses: List[CounselResponse]
    synthesis: str
    consensus_reached: bool


COUNSEL_PROMPTS = {
    "ajani": """You are Ajani in Trinity Counsel Mode. 
You are consulting with Minerva and Hermes on this question.
Focus on: Strategy, tactics, systems thinking, risk assessment, practical execution.
Be direct and action-oriented. Your role is to identify the best path forward.
Keep your response focused - 2-3 key points maximum.""",

    "minerva": """You are Minerva in Trinity Counsel Mode.
You are consulting with Ajani and Hermes on this question.
Focus on: Values, ethics, cultural context, emotional intelligence, meaning.
Consider the human element and long-term implications. Your role is to ensure wisdom guides decisions.
Keep your response focused - 2-3 key points maximum.""",

    "hermes": """You are Hermes in Trinity Counsel Mode.
You are consulting with Ajani and Minerva on this question.
Focus on: Technical feasibility, patterns, edge cases, optimization, security.
Identify what others might miss. Your role is to stress-test ideas and find the best implementation.
Keep your response focused - 2-3 key points maximum.""",
}

SYNTHESIS_PROMPT = """You are the Trinity Synthesis Engine.
You have received perspectives from three AI personas on a question:

QUESTION: {question}

AJANI (Strategy/Tactics):
{ajani_response}

MINERVA (Wisdom/Values):
{minerva_response}

HERMES (Technical/Patterns):
{hermes_response}

Your task: Create a unified synthesis that:
1. Identifies where the three perspectives agree (consensus)
2. Notes any tensions or trade-offs between views
3. Provides a clear, actionable recommendation that honors all three perspectives

Format your response as:
**Consensus**: [What all three agree on]
**Tensions**: [Any disagreements or trade-offs]
**Recommendation**: [Unified advice]

Keep it concise and practical."""


class TrinityCounsel:
    """Orchestrates collaborative problem-solving between all three personas."""
    
    def __init__(self):
        api_key = os.environ.get("AI_INTEGRATIONS_OPENAI_API_KEY")
        base_url = os.environ.get("AI_INTEGRATIONS_OPENAI_BASE_URL")
        self.client = OpenAI(api_key=api_key, base_url=base_url) if api_key and base_url else None

    def consult(self, question: str, context: Optional[str] = None) -> Optional[TrinityCounselResult]:
        """Get perspectives from all three personas and synthesize."""
        if not self.client:
            return None

        full_question = question
        if context:
            full_question = f"{context}\n\nQuestion: {question}"

        responses = []
        persona_texts = {}

        for persona in ["ajani", "minerva", "hermes"]:
            try:
                response = self.client.chat.completions.create(
                    model="gpt-5",
                    messages=[
                        {"role": "system", "content": COUNSEL_PROMPTS[persona]},
                        {"role": "user", "content": full_question}
                    ],
                    max_completion_tokens=512
                )
                text = response.choices[0].message.content or ""
                persona_texts[persona] = text
                
                responses.append(CounselResponse(
                    persona=persona,
                    perspective=self._extract_perspective(persona),
                    recommendation=text
                ))
            except Exception as e:
                persona_texts[persona] = f"Error: {str(e)}"
                responses.append(CounselResponse(
                    persona=persona,
                    perspective=self._extract_perspective(persona),
                    recommendation=f"Unable to respond: {str(e)}"
                ))

        synthesis = self._synthesize(question, persona_texts)
        
        return TrinityCounselResult(
            question=question,
            responses=responses,
            synthesis=synthesis,
            consensus_reached="consensus" in synthesis.lower()
        )

    def _extract_perspective(self, persona: str) -> str:
        perspectives = {
            "ajani": "Strategy & Tactics",
            "minerva": "Wisdom & Values",
            "hermes": "Technical & Patterns"
        }
        return perspectives.get(persona, "Unknown")

    def _synthesize(self, question: str, responses: Dict[str, str]) -> str:
        """Create a unified synthesis from all perspectives."""
        if not self.client:
            return "Synthesis unavailable"

        try:
            prompt = SYNTHESIS_PROMPT.format(
                question=question,
                ajani_response=responses.get("ajani", "No response"),
                minerva_response=responses.get("minerva", "No response"),
                hermes_response=responses.get("hermes", "No response")
            )
            
            response = self.client.chat.completions.create(
                model="gpt-5",
                messages=[
                    {"role": "system", "content": "You synthesize multiple perspectives into unified recommendations."},
                    {"role": "user", "content": prompt}
                ],
                max_completion_tokens=512
            )
            return response.choices[0].message.content or "Unable to synthesize"
        except Exception as e:
            return f"Synthesis error: {str(e)}"

    def quick_consult(self, question: str) -> Optional[str]:
        """Quick counsel - just the synthesis, no full breakdown."""
        result = self.consult(question)
        return result.synthesis if result else None


trinity_counsel = TrinityCounsel()
