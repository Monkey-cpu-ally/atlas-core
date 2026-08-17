"""Creative Masters Library for ATLAS.

The entries below are not imitation targets. They are craft-study profiles.
ATLAS should learn principles, then transform them into original work.
"""

from __future__ import annotations

from typing import Dict, Iterable, List

from .schemas import CreatorProfile, Domain


def _profile(name: str, domains: List[Domain], priority: int, focus: List[str], use: str) -> CreatorProfile:
    return CreatorProfile(name=name, domains=domains, priority=priority, craft_focus=focus, atlas_use=use)


# Original 32 masters plus 32 expansion profiles spanning comics, manga,
# literature, speculative fiction, horror, creature design and science fiction.
CREATIVE_MASTERS: Dict[str, CreatorProfile] = {
    "Eric England": _profile("Eric England", [Domain.HORROR, Domain.CINEMA], 3, ["grounded horror", "human flaws", "slow escalation", "believable realism"], "Use grounded consequences and believable behavior before supernatural or extreme events escalate."),
    "Simon Barrett": _profile("Simon Barrett", [Domain.HORROR, Domain.STORY], 4, ["mystery construction", "hidden clues", "plot turns", "dialogue with subtext"], "Build stories where clues are visible early, but their meaning changes after the reveal."),
    "Adam Wingard": _profile("Adam Wingard", [Domain.HORROR, Domain.CINEMA], 4, ["kinetic pacing", "camera energy", "modern horror rhythm", "visual momentum"], "Use movement and editing rhythm to make scenes feel dangerous before violence even starts."),
    "Eduardo Sanchez": _profile("Eduardo Sanchez", [Domain.HORROR, Domain.CINEMA], 3, ["found-footage realism", "uncertainty", "natural performances", "fear of the unseen"], "Make fear feel discovered instead of announced; let the audience search the frame for danger."),
    "Gregg Hale": _profile("Gregg Hale", [Domain.HORROR, Domain.CINEMA], 3, ["production realism", "believability", "immersive horror"], "Ground extreme concepts in believable materials, locations, and character reactions."),
    "Gareth Evans": _profile("Gareth Evans", [Domain.CINEMA], 5, ["action choreography", "impact", "environmental combat", "clarity under chaos"], "Design action where space, injury, and objects matter; every hit should change the tactical situation."),
    "Timo Tjahjanto": _profile("Timo Tjahjanto", [Domain.HORROR, Domain.CINEMA], 4, ["chaotic intensity", "violent momentum", "action-horror escalation"], "Use controlled chaos: scenes can feel wild, but the audience must always understand the danger."),
    "Jason Eisener": _profile("Jason Eisener", [Domain.HORROR, Domain.CINEMA], 3, ["stylized horror", "monster concepts", "pulp energy", "visual aggression"], "Push creature and scenario concepts beyond ordinary choices while keeping a clear emotional core."),
    "David Bruckner": _profile("David Bruckner", [Domain.HORROR, Domain.CINEMA], 4, ["psychological horror", "cosmic dread", "atmosphere", "visual tension"], "Use architecture, silence, and impossible spaces to make fear feel ancient and intelligent."),
    "Ti West": _profile("Ti West", [Domain.HORROR, Domain.CINEMA], 4, ["slow burn", "suspense", "patience", "retro horror structure"], "Let scenes breathe before danger hits; suspense grows when the audience has time to worry."),
    "Glenn McQuaid": _profile("Glenn McQuaid", [Domain.HORROR, Domain.CINEMA], 3, ["dark humor", "character interaction", "horror-comedy balance"], "Use humor as pressure release, not as a way to destroy tension."),
    "Joe Swanberg": _profile("Joe Swanberg", [Domain.CINEMA, Domain.STORY], 3, ["natural dialogue", "relationship realism", "emotional authenticity"], "Make characters sound like people with private histories, not exposition machines."),
    "Bob Persichetti": _profile("Bob Persichetti", [Domain.ANIMATION, Domain.CINEMA], 4, ["comic composition", "stylized animation", "dynamic framing"], "Treat the frame like a designed page: shape, pose, color, and motion should tell story together."),
    "Peter Ramsey": _profile("Peter Ramsey", [Domain.ANIMATION, Domain.CINEMA], 4, ["mythic emotion", "heroism", "visual storytelling", "character belief"], "Give heroic moments emotional weight before spectacle; make wonder feel earned."),
    "Rodney Rothman": _profile("Rodney Rothman", [Domain.ANIMATION, Domain.STORY], 3, ["ensemble writing", "comedy timing", "screenplay structure"], "Use humor to reveal character and keep ensemble stories moving."),
    "Jake Castorena": _profile("Jake Castorena", [Domain.ANIMATION], 4, ["action animation", "pose clarity", "fight readability", "motion rhythm"], "Every animated fight should read clearly in silhouette before details are added."),
    "George Lucas": _profile("George Lucas", [Domain.CINEMA, Domain.WORLD_BUILDING], 5, ["mythic structure", "universe design", "politics", "civilizations", "technology aesthetics"], "Build worlds with history, institutions, spiritual conflict, technology, and everyday life beyond the hero."),
    "Andy Muschietti": _profile("Andy Muschietti", [Domain.HORROR, Domain.CINEMA], 4, ["childhood fear", "trauma", "creature design", "emotional horror"], "Connect monsters to emotional wounds so fear means more than a jump scare."),
    "Ari Aster": _profile("Ari Aster", [Domain.HORROR, Domain.CINEMA], 5, ["psychological dread", "family trauma", "ritual", "symbolism", "emotional discomfort"], "Make horror grow from relationships, grief, and meaning; dread should feel inevitable."),
    "Matt Braly": _profile("Matt Braly", [Domain.ANIMATION, Domain.STORY], 4, ["adventure", "friendship", "coming-of-age", "world growth"], "Let external adventure mirror internal maturity."),
    "Dana Terrace": _profile("Dana Terrace", [Domain.ANIMATION, Domain.FANTASY], 4, ["magic systems", "identity", "fantasy comedy", "character growth"], "Build magic with personal meaning; powers should reveal values and choices."),
    "Alex Hirsch": _profile("Alex Hirsch", [Domain.ANIMATION, Domain.STORY], 5, ["hidden lore", "mystery", "comedy", "cosmic weirdness", "clue networks"], "Layer mysteries so jokes, props, and background details can become story keys later."),
    "Matt Reeves": _profile("Matt Reeves", [Domain.CINEMA, Domain.STORY], 4, ["grounded realism", "detective structure", "atmosphere", "emotional action"], "Make investigation and emotion drive spectacle; style should support moral pressure."),
    "Mathijs de Jonge": _profile("Mathijs de Jonge", [Domain.GAME_DESIGN, Domain.WORLD_BUILDING], 4, ["open exploration", "ruins", "environmental mystery", "discovery loops"], "Reward curiosity with story, not just loot; environments should answer old questions and create new ones."),
    "Hayao Miyazaki": _profile("Hayao Miyazaki", [Domain.ANIMATION, Domain.FANTASY], 5, ["nature", "wonder", "quiet emotion", "living worlds", "humanity"], "Balance conflict with quiet beauty; make the world feel alive even when no plot is happening."),
    "Hidetaka Miyazaki": _profile("Hidetaka Miyazaki", [Domain.GAME_DESIGN, Domain.WORLD_BUILDING, Domain.FANTASY], 5, ["environmental storytelling", "hidden lore", "ancient civilizations", "melancholy", "minimal exposition"], "Let architecture, item history, enemy placement, and ruins tell the story without overexplaining."),
    "Eric Williams": _profile("Eric Williams", [Domain.GAME_DESIGN, Domain.STORY], 4, ["character dynamics", "gameplay pacing", "cinematic action", "relationship payoffs"], "Use gameplay situations to test relationships, not just mechanics."),
    "Cory Barlog": _profile("Cory Barlog", [Domain.GAME_DESIGN, Domain.STORY], 5, ["emotional storytelling", "father-child dynamics", "cinematic continuity", "myth adaptation"], "Make myth personal; large worlds hit harder when anchored to family and regret."),
    "David Jaffe": _profile("David Jaffe", [Domain.GAME_DESIGN], 4, ["bold mechanics", "boss design", "spectacle", "player empowerment"], "Create mechanics that are instantly readable and emotionally satisfying to use."),
    "Genndy Tartakovsky": _profile("Genndy Tartakovsky", [Domain.ANIMATION, Domain.CINEMA], 5, ["silence", "body language", "composition", "action rhythm", "minimal dialogue", "visual emotion"], "Tell story through pose, timing, framing, and silence before adding dialogue."),
    "Ryan Coogler": _profile("Ryan Coogler", [Domain.CINEMA, Domain.STORY], 5, ["culture", "legacy", "family", "character arcs", "emotional payoff"], "Center culture and family so the plot feels rooted in identity and responsibility."),
    "Jordan Peele": _profile("Jordan Peele", [Domain.HORROR, Domain.CINEMA], 5, ["social symbolism", "foreshadowing", "psychological suspense", "layered reveals"], "Use symbols and genre mechanics to say something deeper without turning the story into a lecture."),

    # Expansion 33-64
    "Scott Snyder": _profile("Scott Snyder", [Domain.STORY, Domain.HORROR, Domain.WORLD_BUILDING], 5, ["horror mythology", "mystery escalation", "long-form comic plotting", "threat design"], "Build layered mysteries and escalating mythology while keeping the emotional stakes anchored to character choices."),
    "Kelly Thompson": _profile("Kelly Thompson", [Domain.STORY, Domain.FANTASY], 5, ["character voice", "relationship dynamics", "hero reinvention", "ensemble writing"], "Reimagine familiar heroic ideas through distinct character voices, relationships, and consequences rather than surface changes."),
    "Jonathan Hickman": _profile("Jonathan Hickman", [Domain.STORY, Domain.WORLD_BUILDING], 5, ["systems storytelling", "timelines", "civilizations", "long-range plotting", "information design"], "Design stories as interacting systems whose institutions, timelines, technologies, and characters create consequences across long arcs."),
    "Grant Morrison": _profile("Grant Morrison", [Domain.STORY, Domain.FANTASY, Domain.WORLD_BUILDING], 5, ["metafiction", "mythic abstraction", "high concepts", "symbolic storytelling"], "Use ambitious concepts and layered symbolism while preserving a clear emotional route for the audience."),
    "Alan Moore": _profile("Alan Moore", [Domain.STORY, Domain.WORLD_BUILDING], 5, ["formal structure", "symbolism", "parallel narratives", "thematic density"], "Make structure reinforce theme; recurring images, contrasts, and parallel events should carry meaning without copying protected expression."),
    "Neil Gaiman": _profile("Neil Gaiman", [Domain.STORY, Domain.FANTASY, Domain.WORLD_BUILDING], 5, ["myth", "folklore", "dream logic", "modern fantasy", "voice"], "Combine old myths with contemporary human concerns so fantastic elements feel emotionally intimate and culturally layered."),
    "Mike Mignola": _profile("Mike Mignola", [Domain.HORROR, Domain.FANTASY, Domain.STORY], 5, ["folklore", "occult atmosphere", "visual economy", "monster mythology"], "Use strong silhouettes, negative space, folklore, and restrained exposition to make supernatural worlds feel old and lived-in."),
    "James Tynion IV": _profile("James Tynion IV", [Domain.HORROR, Domain.STORY], 5, ["modern horror", "conspiracy", "monster systems", "character vulnerability"], "Build horror around rules, institutions, secrets, and vulnerable characters whose choices expose larger systems."),
    "Daniel Warren Johnson": _profile("Daniel Warren Johnson", [Domain.STORY, Domain.CINEMA], 4, ["kinetic visual storytelling", "emotional action", "expressive anatomy", "impact"], "Make action communicate emotion and consequence; motion should reveal character rather than exist only as spectacle."),
    "Hayden Sherman": _profile("Hayden Sherman", [Domain.STORY, Domain.CINEMA], 4, ["experimental layouts", "composition", "visual rhythm", "spatial storytelling"], "Explore unconventional framing and page rhythm while keeping geography, focus, and narrative progression readable."),
    "Alex Ross": _profile("Alex Ross", [Domain.CINEMA, Domain.STORY], 4, ["heroic realism", "monumental composition", "lighting", "iconography"], "Use scale, lighting, posture, and composition to communicate mythic importance without depending on borrowed character designs."),
    "Fiona Staples": _profile("Fiona Staples", [Domain.STORY, Domain.WORLD_BUILDING], 4, ["character acting", "visual identity", "environment design", "expressive storytelling"], "Give characters and environments distinct visual identities and let expression and staging carry narrative information."),
    "Frank Miller": _profile("Frank Miller", [Domain.STORY, Domain.CINEMA], 4, ["noir composition", "visual economy", "urban atmosphere", "high contrast storytelling"], "Strip scenes to their strongest visual and dramatic information; use atmosphere and composition to sharpen conflict."),
    "Todd McFarlane": _profile("Todd McFarlane", [Domain.STORY, Domain.HORROR], 4, ["dynamic anatomy", "silhouettes", "creature aesthetics", "visual exaggeration"], "Use exaggerated shape language and readable silhouettes to make creatures and action immediately identifiable."),
    "Kentaro Miura": _profile("Kentaro Miura", [Domain.FANTASY, Domain.HORROR, Domain.WORLD_BUILDING], 5, ["dark fantasy", "intricate environments", "monumental scale", "character endurance"], "Build dense worlds where architecture, creatures, history, and personal struggle reinforce one another."),
    "Katsuhiro Otomo": _profile("Katsuhiro Otomo", [Domain.STORY, Domain.WORLD_BUILDING, Domain.CINEMA], 5, ["urban science fiction", "machinery", "destruction", "motion", "city systems"], "Treat cities and machines as functional systems; large-scale destruction should preserve spatial clarity and physical consequence."),
    "Naoki Urasawa": _profile("Naoki Urasawa", [Domain.STORY], 5, ["suspense", "character networks", "mystery", "human antagonists", "long-form payoff"], "Build suspense through interconnected people, incomplete information, and consequences that accumulate across long narratives."),
    "Takehiko Inoue": _profile("Takehiko Inoue", [Domain.STORY, Domain.CINEMA], 4, ["movement", "anatomy", "quiet emotion", "character observation"], "Balance precise physical movement with quiet observational moments that reveal internal character change."),
    "Hiromu Arakawa": _profile("Hiromu Arakawa", [Domain.FANTASY, Domain.STORY, Domain.WORLD_BUILDING], 5, ["rule-based systems", "consequences", "ensemble casts", "political worldbuilding"], "Give fantastic systems understandable rules and costs, then let characters and institutions exploit or suffer those rules."),
    "Tsutomu Nihei": _profile("Tsutomu Nihei", [Domain.WORLD_BUILDING, Domain.HORROR], 5, ["megastructures", "biomechanical design", "scale", "environmental storytelling", "minimal exposition"], "Use architecture and scale as narrative forces; environments should imply technology, history, and danger without excessive explanation."),
    "Ursula K. Le Guin": _profile("Ursula K. Le Guin", [Domain.STORY, Domain.WORLD_BUILDING, Domain.FANTASY], 5, ["culture design", "anthropology", "social systems", "language", "speculative societies"], "Build speculative societies from coherent cultural assumptions and examine how those assumptions shape ordinary lives."),
    "Octavia E. Butler": _profile("Octavia E. Butler", [Domain.STORY, Domain.WORLD_BUILDING], 5, ["adaptation", "biology", "power", "social systems", "survival"], "Use speculative biology and changing power relationships to pressure-test characters, communities, and ethical assumptions."),
    "N. K. Jemisin": _profile("N. K. Jemisin", [Domain.FANTASY, Domain.WORLD_BUILDING, Domain.STORY], 5, ["civilization design", "geology", "social hierarchy", "structural worldbuilding"], "Make physical world systems and social systems interact so environment, history, and power all shape the narrative."),
    "Isaac Asimov": _profile("Isaac Asimov", [Domain.STORY, Domain.WORLD_BUILDING], 5, ["robotics concepts", "logical constraints", "future societies", "idea-driven conflict"], "Explore technology by defining clear constraints and then examining the unexpected social and ethical consequences of those rules."),
    "Arthur C. Clarke": _profile("Arthur C. Clarke", [Domain.STORY, Domain.WORLD_BUILDING], 5, ["space exploration", "future technology", "scientific wonder", "cosmic scale"], "Ground speculative technology in scientific reasoning while preserving awe, mystery, and humanity's limited perspective."),
    "Philip K. Dick": _profile("Philip K. Dick", [Domain.STORY, Domain.WORLD_BUILDING], 5, ["identity", "artificial intelligence", "perception", "simulated reality", "uncertainty"], "Use unstable perception and technological systems to ask who controls reality and how characters determine what is trustworthy."),
    "William Gibson": _profile("William Gibson", [Domain.STORY, Domain.WORLD_BUILDING], 5, ["networks", "cybernetics", "technology culture", "near-future atmosphere"], "Treat technology as culture and infrastructure, showing how networks reshape language, work, status, and everyday behavior."),
    "Mary Shelley": _profile("Mary Shelley", [Domain.HORROR, Domain.STORY], 5, ["artificial life", "creator responsibility", "isolation", "scientific ambition"], "Use invention as an ethical relationship between creator, creation, society, and unintended consequence."),
    "H. P. Lovecraft": _profile("H. P. Lovecraft", [Domain.HORROR, Domain.WORLD_BUILDING], 3, ["cosmic scale", "unknowability", "ancient history", "atmospheric dread"], "Study cosmic scale and atmosphere critically; reject racist ideology and dehumanizing assumptions while retaining only broadly reusable craft principles."),
    "Stephen King": _profile("Stephen King", [Domain.HORROR, Domain.STORY], 5, ["character-driven horror", "community dynamics", "escalation", "ordinary-life detail"], "Establish believable people and communities first so supernatural or extreme events threaten something emotionally concrete."),
    "Guillermo del Toro": _profile("Guillermo del Toro", [Domain.CINEMA, Domain.HORROR, Domain.FANTASY], 5, ["creature design", "folklore", "sympathetic monsters", "production design", "visual mythology"], "Design creatures as characters with anatomy, history, emotion, and symbolic purpose rather than as disposable threats."),
    "Denis Villeneuve": _profile("Denis Villeneuve", [Domain.CINEMA, Domain.WORLD_BUILDING], 5, ["scale", "atmosphere", "visual restraint", "science-fiction worldbuilding", "tension"], "Use composition, sound, architecture, and restraint to communicate scale and make speculative worlds feel physically credible."),
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
