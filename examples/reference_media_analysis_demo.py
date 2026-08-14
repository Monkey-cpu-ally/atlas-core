from creative_intelligence.media_analysis import (
    ReferenceMediaAnalyzer,
    StoryStructureAnalyzer,
    VisualCraftAnalyzer,
)


def main() -> None:
    visual = VisualCraftAnalyzer().analyze(
        subject="armored creature encounter",
        silhouette=["broad upper mass", "clear weapon profile", "readable head shape"],
        shape_language=["angular armor", "organic interruptions"],
        proportion=["exaggerated shoulders", "compact lower body"],
        color=["dark base", "high-contrast accent zones"],
        value=["bright focal areas against large dark masses"],
        lighting=["hard rim light", "directional environment light"],
        materials=["worn metal", "fabric", "organic tissue"],
        composition=["strong diagonals", "clear foreground threat"],
        movement=["heavy anticipation", "fast impact", "short recovery"],
    )

    story = StoryStructureAnalyzer().analyze(
        title="Reference Sequence",
        premise="A character enters a space where the environment reveals the threat before the threat fully appears.",
        character_goals=["reach the exit", "understand the danger"],
        conflicts=["limited visibility", "hostile environment", "time pressure"],
        reveals=["the environment was damaged by the creature before the character arrived"],
        pacing_notes=["slow scan", "brief silence", "rapid escalation"],
        visual_storytelling=["damage patterns reveal scale", "lighting hides the full creature"],
        themes=["curiosity versus survival"],
        scene_changes=["curiosity becomes fear", "escape becomes confrontation"],
    )

    report = ReferenceMediaAnalyzer().build_report(
        source_name="Example Reference Study",
        source_type="film/game sequence",
        visual=visual,
        story=story,
    )

    print(report.to_markdown())


if __name__ == "__main__":
    main()
