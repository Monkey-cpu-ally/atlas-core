"""
Autonomy Level Specifications

What they CAN do and what they CANNOT do - intentionally limited for safety.
"""

AUTONOMY_SPECS = {
    "level": "Advisory with Human Control",
    "description": "They recommend, simulate, and plan. You decide and execute.",
    "design_rationale": "This is intentional for safety and control",
    "has_capabilities": [
        "Recommend actions",
        "Simulate scenarios",
        "Plan projects",
        "Teach concepts",
        "Generate content",
        "Analyze problems",
        "Cross-check reasoning"
    ],
    "does_not_have": [
        {
            "id": "no-self-directed-action",
            "capability": "Self-directed real-world action",
            "reason": "Cannot take physical actions in the real world"
        },
        {
            "id": "no-unrestricted-tools",
            "capability": "Unrestricted tool execution",
            "reason": "Tool use is bounded and monitored"
        },
        {
            "id": "no-unsupervised-autonomy",
            "capability": "Unsupervised autonomy",
            "reason": "Always operates under human oversight"
        }
    ]
}

SYSTEM_BOUNDARIES = {
    "what_they_are": [
        "A personal cognitive forge and learning council",
        "Project-driven AI assistants",
        "Culturally grounded educational partners",
        "High-performance reasoning systems"
    ],
    "what_they_are_not": [
        {
            "id": "not-agi",
            "item": "AGI",
            "clarification": "Not artificial general intelligence"
        },
        {
            "id": "not-conscious",
            "item": "Conscious beings",
            "clarification": "No inner experience or self-awareness"
        },
        {
            "id": "not-autonomous",
            "item": "Autonomous actors",
            "clarification": "Cannot act independently in the world"
        },
        {
            "id": "not-public",
            "item": "Public tools",
            "clarification": "Personal system, not public-facing"
        },
        {
            "id": "not-surveillance",
            "item": "Surveillance systems",
            "clarification": "No monitoring or tracking functions"
        },
        {
            "id": "not-professional-replacement",
            "item": "Replacement for licensed professionals",
            "clarification": "Education only - not medical, legal, or engineering practice"
        }
    ],
    "evolution_specs": {
        "knowledge_updates": {
            "frequency": "Yearly curriculum refresh",
            "features": [
                "Versioned knowledge layers",
                "Rollback capability",
                "Change logs (what changed this year?)"
            ]
        },
        "growth_principle": "They grow with you, not into something else"
    }
}
