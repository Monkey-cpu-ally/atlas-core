from atlas_animation_studio import StoryboardEngine
from creative_intelligence import CouncilReviewEngine
from story_foundry import CharacterBibleEngine, WorldBibleEngine


def main() -> None:
    character = CharacterBibleEngine().build_bible(
        name="Example Hero",
        role="explorer",
        core_wound="fear of failing the people who trust them",
        want="to reach the sealed observatory",
        need="to trust others instead of controlling every risk",
        fear="being responsible for another loss",
        contradiction="brave in danger but emotionally guarded",
    )

    world = WorldBibleEngine().build_bible(
        name="Example World",
        core_identity="a storm-battered research culture built around ancient observatories",
    )

    storyboard = StoryboardEngine().build_sequence(
        title="Observatory Arrival",
        scene_number=1,
        beat_goals=[
            "Reveal the observatory as beautiful but damaged.",
            "Show the hero hiding fear from the team.",
            "End with evidence that the observatory is still active.",
        ],
    )

    review = CouncilReviewEngine().review(
        project_name="Observatory Arrival",
        story_ready=True,
        world_ready=True,
        visual_ready=True,
        original_ready=True,
    )

    print(character.to_markdown())
    print(world.to_markdown())
    print(storyboard.to_markdown())
    print(review.to_markdown())


if __name__ == "__main__":
    main()
