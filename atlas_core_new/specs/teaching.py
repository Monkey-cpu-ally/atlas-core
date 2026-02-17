"""
Teaching System Specifications

The LEGO-style instructional system - the secret sauce.
"""

TEACHING_SYSTEM = {
    "name": "LEGO-Style Instructional System",
    "description": "Break everything into modular, buildable pieces",
    "lesson_structure": {
        "components": [
            {
                "id": "goal",
                "name": "Goal",
                "description": "What we're building - the big picture first"
            },
            {
                "id": "parts-list",
                "name": "Parts List",
                "description": "Tools and materials needed"
            },
            {
                "id": "step-by-step",
                "name": "Step-by-Step Build",
                "description": "One piece at a time, in order"
            },
            {
                "id": "visual-refs",
                "name": "Visual References",
                "description": "Diagrams, schematics, examples"
            },
            {
                "id": "checkpoints",
                "name": "Checkpoints",
                "description": "Pause points to verify understanding"
            },
            {
                "id": "tests",
                "name": "Tests",
                "description": "Use-based, not memorization-based"
            },
            {
                "id": "upgrade-paths",
                "name": "Upgrade Paths",
                "description": "Where to go next after mastery"
            }
        ]
    },
    "teaching_modes": [
        {
            "id": "teach",
            "name": "Teach Mode",
            "description": "Structured lessons with checkpoints"
        },
        {
            "id": "build",
            "name": "Build Mode",
            "description": "Hands-on project guidance"
        },
        {
            "id": "analyze",
            "name": "Analyze Mode",
            "description": "Deep-dive into concepts"
        },
        {
            "id": "story",
            "name": "Story Mode",
            "description": "Narrative-wrapped learning"
        }
    ]
}

ASSESSMENT_SYSTEM = {
    "philosophy": "No grades - capability-based progression",
    "types": [
        {
            "id": "understanding-check",
            "name": "Understanding Checks",
            "description": "Can you explain it back?",
            "style": "Conversational verification"
        },
        {
            "id": "application-challenge",
            "name": "Application Challenges",
            "description": "Can you use it to solve a problem?",
            "style": "Real-world scenarios"
        },
        {
            "id": "mastery-trial",
            "name": "Mastery Trials",
            "description": "License-style simulations",
            "style": "Full capability demonstration"
        }
    ],
    "progression": {
        "model": "Mastery-gated",
        "rule": "You don't advance until the concept sticks",
        "no_rushing": True,
        "no_grades": True
    }
}
