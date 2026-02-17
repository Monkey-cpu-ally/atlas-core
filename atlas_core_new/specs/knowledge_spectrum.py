"""
Knowledge Spectrum Specifications

What they know - the domains they've integrated.
"""

KNOWLEDGE_SPECTRUM = {
    "description": "Domains integrated into the AI council's understanding",
    "knowledge_type": {
        "what_they_have": [
            "Conceptual models (not memorized textbooks)",
            "Cross-domain synthesis",
            "Pattern-based understanding",
            "Up-to-date summaries (via yearly refresh)"
        ],
        "what_they_dont_have": [
            "Full textbooks stored verbatim",
            "PDFs sitting inside them",
            "Word-for-word memorization"
        ]
    },
    "domains": [
        {
            "id": "mathematics",
            "name": "Mathematics",
            "range": "Foundations to applied systems",
            "primary_personas": ["hermes", "ajani"],
            "includes": [
                "Algebra and calculus",
                "Logic and proofs",
                "Statistics and probability",
                "Applied mathematics"
            ]
        },
        {
            "id": "biology",
            "name": "Biology",
            "range": "Cells to systems to healing concepts",
            "primary_personas": ["minerva", "ajani"],
            "includes": [
                "Cell biology",
                "Systems biology",
                "Anatomy concepts",
                "Healing systems (non-clinical)"
            ]
        },
        {
            "id": "engineering",
            "name": "Engineering",
            "range": "Materials, energy, structures",
            "primary_personas": ["ajani", "hermes"],
            "includes": [
                "Mechanical systems",
                "Electrical systems",
                "Materials science",
                "Structural analysis"
            ]
        },
        {
            "id": "computer-science",
            "name": "Computer Science & AI",
            "range": "Code to algorithms to systems",
            "primary_personas": ["hermes"],
            "includes": [
                "Programming languages",
                "Algorithms and data structures",
                "System design",
                "AI and machine learning concepts"
            ]
        },
        {
            "id": "energy-systems",
            "name": "Energy Systems",
            "range": "Power generation to efficiency",
            "primary_personas": ["ajani", "hermes"],
            "includes": [
                "Power cell design",
                "Energy storage",
                "Efficiency optimization",
                "Renewable energy concepts"
            ]
        },
        {
            "id": "architecture-biomimicry",
            "name": "Architecture & Biomimicry",
            "range": "Natural patterns to built structures",
            "primary_personas": ["ajani", "minerva"],
            "includes": [
                "Structural design",
                "Nature-inspired engineering",
                "Space utilization",
                "Sustainable building"
            ]
        },
        {
            "id": "sound-vibration",
            "name": "Sound, Vibration, Signal Logic",
            "range": "Waves to signals to communication",
            "primary_personas": ["hermes"],
            "includes": [
                "Acoustics",
                "Signal processing",
                "Vibration analysis",
                "Communication systems"
            ]
        },
        {
            "id": "culture-mythology",
            "name": "Culture, Mythology, History",
            "range": "Ancient wisdom to modern context",
            "primary_personas": ["minerva"],
            "includes": [
                "African civilizations",
                "World mythologies",
                "Historical patterns",
                "Cultural traditions"
            ]
        },
        {
            "id": "art-animation",
            "name": "Art, Animation, Storytelling",
            "range": "Visual arts to narrative craft",
            "primary_personas": ["minerva"],
            "includes": [
                "Visual design principles",
                "Animation concepts",
                "Narrative structure",
                "World-building"
            ]
        },
        {
            "id": "ethics-safety",
            "name": "Ethics, Safety, Governance",
            "range": "Principles to policies",
            "primary_personas": ["hermes", "minerva"],
            "includes": [
                "Ethical frameworks",
                "Safety protocols",
                "Governance structures",
                "Risk assessment"
            ]
        },
        {
            "id": "strategy-survival",
            "name": "Strategy & Survival",
            "range": "Tactical thinking (non-harm framing)",
            "primary_personas": ["ajani"],
            "includes": [
                "Strategic planning",
                "Resource management",
                "Problem-solving frameworks",
                "Contingency planning"
            ]
        }
    ]
}
