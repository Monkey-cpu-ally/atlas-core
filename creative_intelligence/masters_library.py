"""Creative Masters Library for ATLAS.

The entries below are not imitation targets. They are craft-study profiles.
ATLAS should learn principles, then transform them into original work.
"""

from __future__ import annotations

from typing import Dict, Iterable, List

from .schemas import CreatorProfile, Domain


CREATIVE_MASTERS: Dict[str, CreatorProfile] = {
    "Eric England": CreatorProfile(
        name="Eric England",
        domains=[Domain.HORROR, Domain.CINEMA],
        priority=3,
        craft_focus=["grounded horror", "human flaws", "slow escalation", "believable realism"],
        atlas_use="Use grounded consequences and believable behavior before supernatural or extreme events escalate.",
    ),
    "Simon Barrett": CreatorProfile(
        name="Simon Barrett",
        domains=[Domain.HORROR, Domain.STORY],
        priority=4,
        craft_focus=["mystery construction", "hidden clues", "plot turns", "dialogue with subtext"],
        atlas_use="Build stories where clues are visible early, but their meaning changes after the reveal.",
    ),
    "Adam Wingard": CreatorProfile(
        name="Adam Wingard",
        domains=[Domain.HORROR, Domain.CINEMA],
        priority=4,
        craft_focus=["kinetic pacing", "camera energy", "modern horror rhythm", "visual momentum"],
        atlas_use="Use movement and editing rhythm to make scenes feel dangerous before violence even starts.",
    ),
    "Eduardo Sanchez": CreatorProfile(
        name="Eduardo Sanchez",
        domains=[Domain.HORROR, Domain.CINEMA],
        priority=3,
        craft_focus=["found-footage realism", "uncertainty", "natural performances", "fear of the unseen"],
        atlas_use="Make fear feel discovered instead of announced; let the audience search the frame for danger.",
    ),
    "Gregg Hale": CreatorProfile(
        name="Gregg Hale",
        domains=[Domain.HORROR, Domain.CINEMA],
        priority=3,
        craft_focus=["production realism", "believability", "immersive horror"],
        atlas_use="Ground extreme concepts in believable materials, locations, and character reactions.",
    ),
    "Gareth Evans": CreatorProfile(
        name="Gareth Evans",
        domains=[Domain.CINEMA],
        priority=5,
        craft_focus=["action choreography", "impact", "environmental combat", "clarity under chaos"],
        atlas_use="Design action where space, injury, and objects matter; every hit should change the tactical situation.",
    ),
    "Timo Tjahjanto": CreatorProfile(
        name="Timo Tjahjanto",
        domains=[Domain.HORROR, Domain.CINEMA],
        priority=4,
        craft_focus=["chaotic intensity", "violent momentum", "action-horror escalation"],
        atlas_use="Use controlled chaos: scenes can feel wild, but the audience must always understand the danger.",
    ),
    "Jason Eisener": CreatorProfile(
        name="Jason Eisener",
        domains=[Domain.HORROR, Domain.CINEMA],
        priority=3,
        craft_focus=["stylized horror", "monster concepts", "pulp energy", "visual aggression"],
        atlas_use="Push creature and scenario concepts beyond ordinary choices while keeping a clear emotional core.",
    ),
    "David Bruckner": CreatorProfile(
        name="David Bruckner",
        domains=[Domain.HORROR, Domain.CINEMA],
        priority=4,
        craft_focus=["psychological horror", "cosmic dread", "atmosphere", "visual tension"],
        atlas_use="Use architecture, silence, and impossible spaces to make fear feel ancient and intelligent.",
    ),
    "Ti West": CreatorProfile(
        name="Ti West",
        domains=[Domain.HORROR, Domain.CINEMA],
        priority=4,
        craft_focus=["slow burn", "suspense", "patience", "retro horror structure"],
        atlas_use="Let scenes breathe before danger hits; suspense grows when the audience has time to worry.",
    ),
    "Glenn McQuaid": CreatorProfile(
        name="Glenn McQuaid",
        domains=[Domain.HORROR, Domain.CINEMA],
        priority=3,
        craft_focus=["dark humor", "character interaction", "horror-comedy balance"],
        atlas_use="Use humor as pressure release, not as a way to destroy tension.",
    ),
    "Joe Swanberg": CreatorProfile(
        name="Joe Swanberg",
        domains=[Domain.CINEMA, Domain.STORY],
        priority=3,
        craft_focus=["natural dialogue", "relationship realism", "emotional authenticity"],
        atlas_use="Make characters sound like people with private histories, not exposition machines.",
    ),
    "Bob Persichetti": CreatorProfile(
        name="Bob Persichetti",
        domains=[Domain.ANIMATION, Domain.CINEMA],
        priority=4,
        craft_focus=["comic composition", "stylized animation", "dynamic framing"],
        atlas_use="Treat the frame like a designed page: shape, pose, color, and motion should tell story together.",
    ),
    "Peter Ramsey": CreatorProfile(
        name="Peter Ramsey",
        domains=[Domain.ANIMATION, Domain.CINEMA],
        priority=4,
        craft_focus=["mythic emotion", "heroism", "visual storytelling", "character belief"],
        atlas_use="Give heroic moments emotional weight before spectacle; make wonder feel earned.",
    ),
    "Rodney Rothman": CreatorProfile(
        name="Rodney Rothman",
        domains=[Domain.ANIMATION, Domain.STORY],
        priority=3,
        craft_focus=["ensemble writing", "comedy timing", "screenplay structure"],
        atlas_use="Use humor to reveal character and keep ensemble stories moving.",
    ),
    "Jake Castorena": CreatorProfile(
        name="Jake Castorena",
        domains=[Domain.ANIMATION],
        priority=4,
        craft_focus=["action animation", "pose clarity", "fight readability", "motion rhythm"],
        atlas_use="Every animated fight should read clearly in silhouette before details are added.",
    ),
    "George Lucas": CreatorProfile(
        name="George Lucas",
        domains=[Domain.CINEMA, Domain.WORLD_BUILDING],
        priority=5,
        craft_focus=["mythic structure", "universe design", "politics", "civilizations", "technology aesthetics"],
        atlas_use="Build worlds with history, institutions, spiritual conflict, technology, and everyday life beyond the hero.",
    ),
    "Andy Muschietti": CreatorProfile(
        name="Andy Muschietti",
        domains=[Domain.HORROR, Domain.CINEMA],
        priority=4,
        craft_focus=["childhood fear", "trauma", "creature design", "emotional horror"],
        atlas_use="Connect monsters to emotional wounds so fear means more than a jump scare.",
    ),
    "Ari Aster": CreatorProfile(
        name="Ari Aster",
        domains=[Domain.HORROR, Domain.CINEMA],
        priority=5,
        craft_focus=["psychological dread", "family trauma", "ritual", "symbolism", "emotional discomfort"],
        atlas_use="Make horror grow from relationships, grief, and meaning; dread should feel inevitable.",
    ),
    "Matt Braly": CreatorProfile(
        name="Matt Braly",
        domains=[Domain.ANIMATION, Domain.STORY],
        priority=4,
        craft_focus=["adventure", "friendship", "coming-of-age", "world growth"],
        atlas_use="Let external adventure mirror internal maturity.",
    ),
    "Dana Terrace": CreatorProfile(
        name="Dana Terrace",
        domains=[Domain.ANIMATION, Domain.FANTASY],
        priority=4,
        craft_focus=["magic systems", "identity", "fantasy comedy", "character growth"],
        atlas_use="Build magic with personal meaning; powers should reveal values and choices.",
    ),
    "Alex Hirsch": CreatorProfile(
        name="Alex Hirsch",
        domains=[Domain.ANIMATION, Domain.STORY],
        priority=5,
        craft_focus=["hidden lore", "mystery", "comedy", "cosmic weirdness", "clue networks"],
        atlas_use="Layer mysteries so jokes, props, and background details can become story keys later.",
    ),
    "Matt Reeves": CreatorProfile(
        name="Matt Reeves",
        domains=[Domain.CINEMA, Domain.STORY],
        priority=4,
        craft_focus=["grounded realism", "detective structure", "atmosphere", "emotional action"],
        atlas_use="Make investigation and emotion drive spectacle; style should support moral pressure.",
    ),
    "Mathijs de Jonge": CreatorProfile(
        name="Mathijs de Jonge",
        domains=[Domain.GAME_DESIGN, Domain.WORLD_BUILDING],
        priority=4,
        craft_focus=["open exploration", "ruins", "environmental mystery", "discovery loops"],
        atlas_use="Reward curiosity with story, not just loot; environments should answer old questions and create new ones.",
    ),
    "Hayao Miyazaki": CreatorProfile(
        name="Hayao Miyazaki",
        domains=[Domain.ANIMATION, Domain.FANTASY],
        priority=5,
        craft_focus=["nature", "wonder", "quiet emotion", "living worlds", "humanity"],
        atlas_use="Balance conflict with quiet beauty; make the world feel alive even when no plot is happening.",
    ),
    "Hidetaka Miyazaki": CreatorProfile(
        name="Hidetaka Miyazaki",
        domains=[Domain.GAME_DESIGN, Domain.WORLD_BUILDING, Domain.FANTASY],
        priority=5,
        craft_focus=["environmental storytelling", "hidden lore", "ancient civilizations", "melancholy", "minimal exposition"],
        atlas_use="Let architecture, item history, enemy placement, and ruins tell the story without overexplaining.",
    ),
    "Eric Williams": CreatorProfile(
        name="Eric Williams",
        domains=[Domain.GAME_DESIGN, Domain.STORY],
        priority=4,
        craft_focus=["character dynamics", "gameplay pacing", "cinematic action", "relationship payoffs"],
        atlas_use="Use gameplay situations to test relationships, not just mechanics.",
    ),
    "Cory Barlog": CreatorProfile(
        name="Cory Barlog",
        domains=[Domain.GAME_DESIGN, Domain.STORY],
        priority=5,
        craft_focus=["emotional storytelling", "father-child dynamics", "cinematic continuity", "myth adaptation"],
        atlas_use="Make myth personal; large worlds hit harder when anchored to family and regret.",
    ),
    "David Jaffe": CreatorProfile(
        name="David Jaffe",
        domains=[Domain.GAME_DESIGN],
        priority=4,
        craft_focus=["bold mechanics", "boss design", "spectacle", "player empowerment"],
        atlas_use="Create mechanics that are instantly readable and emotionally satisfying to use.",
    ),
    "Genndy Tartakovsky": CreatorProfile(
        name="Genndy Tartakovsky",
        domains=[Domain.ANIMATION, Domain.CINEMA],
        priority=5,
        craft_focus=["silence", "body language", "composition", "action rhythm", "minimal dialogue", "visual emotion"],
        atlas_use="Tell story through pose, timing, framing, and silence before adding dialogue.",
    ),
    "Ryan Coogler": CreatorProfile(
        name="Ryan Coogler",
        domains=[Domain.CINEMA, Domain.STORY],
        priority=5,
        craft_focus=["culture", "legacy", "family", "character arcs", "emotional payoff"],
        atlas_use="Center culture and family so the plot feels rooted in identity and responsibility.",
    ),
    "Jordan Peele": CreatorProfile(
        name="Jordan Peele",
        domains=[Domain.HORROR, Domain.CINEMA],
        priority=5,
        craft_focus=["social symbolism", "foreshadowing", "psychological suspense", "layered reveals"],
        atlas_use="Use symbols and genre mechanics to say something deeper without turning the story into a lecture.",
    ),
}


def get_creator(name: str) -> CreatorProfile:
    try:
        return CREATIVE_MASTERS[name]
    except KeyError as exc:
        available = ", ".join(sorted(CREATIVE_MASTERS))
        raise KeyError(f"Unknown creator '{name}'. Available creators: {available}") from exc


def list_creators(domain: Domain | None = None, min_priority: int = 1) -> List[CreatorProfile]:
    profiles: Iterable[CreatorProfile] = CREATIVE_MASTERS.values()
    if domain is not None:
        profiles = [profile for profile in profiles if domain in profile.domains]
    return sorted(
        [profile for profile in profiles if profile.priority >= min_priority],
        key=lambda item: (-item.priority, item.name),
    )
