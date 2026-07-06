"""Example usage for ATLAS Creative Intelligence.

Run from repository root with:

    python -m creative_intelligence.example_usage
"""

from __future__ import annotations

from .creative_engine import CreativeIntelligenceEngine
from .schemas import CreativeBrief


def main() -> None:
    engine = CreativeIntelligenceEngine()

    brief = CreativeBrief(
        title="The Night Band Expansion Test",
        premise=(
            "A child discovers a hidden musical fairy world tied to grief, spring, and the danger of eternal night."
        ),
        target_emotion="wonder mixed with gentle fear",
        genre="animated dark fairy tale",
        user_style_notes=[
            "classic Disney feeling",
            "less talking when visuals can carry the scene",
            "beautiful but mysterious forest atmosphere",
            "ATLAS original style, not a copy",
        ],
        constraints=[
            "No copied characters, dialogue, scenes, or protected worlds.",
            "Keep the story child-friendly but emotionally strong.",
        ],
    )

    plan = engine.build_plan(
        brief=brief,
        creator_names=[
            "Hayao Miyazaki",
            "Genndy Tartakovsky",
            "Alex Hirsch",
            "Peter Ramsey",
            "Jordan Peele",
        ],
    )

    print(plan.to_markdown())


if __name__ == "__main__":
    main()
