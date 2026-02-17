"""
Curriculum modules for each persona's fields of study.
Structured as: Field → Levels (beginner/intermediate/advanced) → Lessons
"""

AJANI_CURRICULUM = {
    "strategy": {
        "name": "Strategy",
        "levels": {
            "beginner": [
                {"id": "strat-b1", "title": "What Is Strategy?", "summary": "The difference between tactics and strategy"},
                {"id": "strat-b2", "title": "Goal Setting", "summary": "How to set clear, achievable objectives"},
                {"id": "strat-b3", "title": "Resource Assessment", "summary": "Know what you have before you move"},
            ],
            "intermediate": [
                {"id": "strat-i1", "title": "Competitive Analysis", "summary": "Understanding opponents and obstacles"},
                {"id": "strat-i2", "title": "Strategic Planning", "summary": "Building a roadmap to your goal"},
                {"id": "strat-i3", "title": "Contingency Planning", "summary": "What to do when things go wrong"},
            ],
            "advanced": [
                {"id": "strat-a1", "title": "Multi-Front Strategy", "summary": "Managing multiple objectives simultaneously"},
                {"id": "strat-a2", "title": "Long-Term Vision", "summary": "Planning years ahead while acting today"},
                {"id": "strat-a3", "title": "Strategic Flexibility", "summary": "When to hold the line, when to pivot"},
            ],
        }
    },
    "game_theory": {
        "name": "Game Theory",
        "levels": {
            "beginner": [
                {"id": "game-b1", "title": "What Is Game Theory?", "summary": "Making decisions when others affect your outcome"},
                {"id": "game-b2", "title": "Players and Payoffs", "summary": "Who's involved and what everyone wants"},
                {"id": "game-b3", "title": "Zero-Sum vs Win-Win", "summary": "When fighting helps vs when cooperation wins"},
            ],
            "intermediate": [
                {"id": "game-i1", "title": "The Prisoner's Dilemma", "summary": "Why rational choices can lead to bad outcomes"},
                {"id": "game-i2", "title": "Nash Equilibrium", "summary": "When nobody wants to change their move"},
                {"id": "game-i3", "title": "Signaling and Bluffing", "summary": "What your actions say without words"},
            ],
            "advanced": [
                {"id": "game-a1", "title": "Repeated Games", "summary": "How long-term relationships change the rules"},
                {"id": "game-a2", "title": "Mechanism Design", "summary": "Creating games where the right move is the easy move"},
                {"id": "game-a3", "title": "Evolutionary Game Theory", "summary": "How strategies survive and spread"},
            ],
        }
    },
    "risk_assessment": {
        "name": "Risk Assessment",
        "levels": {
            "beginner": [
                {"id": "risk-b1", "title": "What Is Risk?", "summary": "Understanding uncertainty and consequences"},
                {"id": "risk-b2", "title": "Identifying Risks", "summary": "Spotting what could go wrong"},
                {"id": "risk-b3", "title": "Risk vs Reward", "summary": "When the gamble is worth it"},
            ],
            "intermediate": [
                {"id": "risk-i1", "title": "Probability Thinking", "summary": "Estimating how likely things are"},
                {"id": "risk-i2", "title": "Impact Analysis", "summary": "Measuring how bad bad could be"},
                {"id": "risk-i3", "title": "Mitigation Strategies", "summary": "Reducing risk before it hits"},
            ],
            "advanced": [
                {"id": "risk-a1", "title": "Black Swan Events", "summary": "Preparing for the unpredictable"},
                {"id": "risk-a2", "title": "Portfolio Thinking", "summary": "Spreading risk across multiple bets"},
                {"id": "risk-a3", "title": "Decision Under Uncertainty", "summary": "Acting when you can't know enough"},
            ],
        }
    },
    "leadership": {
        "name": "Leadership",
        "levels": {
            "beginner": [
                {"id": "lead-b1", "title": "What Is Leadership?", "summary": "Influence vs authority"},
                {"id": "lead-b2", "title": "Leading Yourself First", "summary": "Discipline before you can lead others"},
                {"id": "lead-b3", "title": "Communication Basics", "summary": "Saying what you mean clearly"},
            ],
            "intermediate": [
                {"id": "lead-i1", "title": "Building Trust", "summary": "Why people follow some and not others"},
                {"id": "lead-i2", "title": "Delegation", "summary": "Letting go to get more done"},
                {"id": "lead-i3", "title": "Conflict Resolution", "summary": "Handling disagreements productively"},
            ],
            "advanced": [
                {"id": "lead-a1", "title": "Vision Setting", "summary": "Creating a future people want to build"},
                {"id": "lead-a2", "title": "Crisis Leadership", "summary": "Leading when everything is on fire"},
                {"id": "lead-a3", "title": "Legacy Building", "summary": "Creating leaders who outlast you"},
            ],
        }
    },
}

MINERVA_CURRICULUM = {
    "storytelling": {
        "name": "Storytelling",
        "levels": {
            "beginner": [
                {"id": "story-b1", "title": "Why Stories Matter", "summary": "How narrative shapes understanding"},
                {"id": "story-b2", "title": "The Hero's Journey", "summary": "The universal pattern of transformation"},
                {"id": "story-b3", "title": "Character Basics", "summary": "Creating people readers care about"},
            ],
            "intermediate": [
                {"id": "story-i1", "title": "Conflict and Stakes", "summary": "What makes stories matter"},
                {"id": "story-i2", "title": "World Building", "summary": "Creating believable settings"},
                {"id": "story-i3", "title": "Voice and Tone", "summary": "Finding your story's personality"},
            ],
            "advanced": [
                {"id": "story-a1", "title": "Subverting Expectations", "summary": "Breaking rules that need breaking"},
                {"id": "story-a2", "title": "Layered Meaning", "summary": "Stories within stories"},
                {"id": "story-a3", "title": "The Tragic Hero", "summary": "Creating characters who fall and rise"},
            ],
        }
    },
    "character_design": {
        "name": "Character Design",
        "levels": {
            "beginner": [
                {"id": "char-b1", "title": "What Makes a Character?", "summary": "Beyond names and appearances"},
                {"id": "char-b2", "title": "Motivation and Want", "summary": "What drives your character forward"},
                {"id": "char-b3", "title": "Flaws and Strengths", "summary": "Making characters feel real"},
            ],
            "intermediate": [
                {"id": "char-i1", "title": "Backstory", "summary": "The past that shapes the present"},
                {"id": "char-i2", "title": "Character Arcs", "summary": "How people change through story"},
                {"id": "char-i3", "title": "Relationships", "summary": "Characters defined by connections"},
            ],
            "advanced": [
                {"id": "char-a1", "title": "Anti-Heroes", "summary": "Heroes in the shadows"},
                {"id": "char-a2", "title": "Tragic Heroes", "summary": "Greatness and downfall intertwined"},
                {"id": "char-a3", "title": "Breaking Stereotypes", "summary": "Creating the unexpected"},
            ],
        }
    },
    "african_history": {
        "name": "African & Diaspora History",
        "levels": {
            "beginner": [
                {"id": "afh-b1", "title": "Ancient African Civilizations", "summary": "Egypt, Kush, Axum and beyond"},
                {"id": "afh-b2", "title": "West African Empires", "summary": "Ghana, Mali, Songhai"},
                {"id": "afh-b3", "title": "The Diaspora Begins", "summary": "Forced migration and survival"},
            ],
            "intermediate": [
                {"id": "afh-i1", "title": "Resistance and Revolution", "summary": "Fighting back against oppression"},
                {"id": "afh-i2", "title": "The Civil Rights Era", "summary": "The long march to equality"},
                {"id": "afh-i3", "title": "Pan-Africanism", "summary": "Unity across the diaspora"},
            ],
            "advanced": [
                {"id": "afh-a1", "title": "Hidden Histories", "summary": "Stories they didn't teach you"},
                {"id": "afh-a2", "title": "Contemporary Africa", "summary": "The continent today"},
                {"id": "afh-a3", "title": "Afrofuturism", "summary": "Imagining Black futures"},
            ],
        }
    },
    "mythology": {
        "name": "Mythology",
        "levels": {
            "beginner": [
                {"id": "myth-b1", "title": "What Is Mythology?", "summary": "Stories that shape cultures"},
                {"id": "myth-b2", "title": "African Mythology", "summary": "Anansi, Eshu, and the Orishas"},
                {"id": "myth-b3", "title": "Greek and Roman Myths", "summary": "The Western canon"},
            ],
            "intermediate": [
                {"id": "myth-i1", "title": "Norse Mythology", "summary": "Gods of the North"},
                {"id": "myth-i2", "title": "Egyptian Mythology", "summary": "Death, rebirth, and the Nile"},
                {"id": "myth-i3", "title": "Comparative Mythology", "summary": "Finding patterns across cultures"},
            ],
            "advanced": [
                {"id": "myth-a1", "title": "Creating Mythology", "summary": "Building belief systems for fiction"},
                {"id": "myth-a2", "title": "Myth in Modern Media", "summary": "Ancient stories in new clothes"},
                {"id": "myth-a3", "title": "The Monomyth Debate", "summary": "Universal patterns vs cultural uniqueness"},
            ],
        }
    },
}

HERMES_CURRICULUM = {
    "programming": {
        "name": "Programming",
        "levels": {
            "beginner": [
                {"id": "prog-b1", "title": "What Is Code?", "summary": "Instructions for machines"},
                {"id": "prog-b2", "title": "Variables and Data", "summary": "Storing and naming information"},
                {"id": "prog-b3", "title": "Logic and Conditions", "summary": "Making decisions in code"},
            ],
            "intermediate": [
                {"id": "prog-i1", "title": "Functions", "summary": "Reusable blocks of logic"},
                {"id": "prog-i2", "title": "Data Structures", "summary": "Organizing information efficiently"},
                {"id": "prog-i3", "title": "Debugging", "summary": "Finding and fixing what's broken"},
            ],
            "advanced": [
                {"id": "prog-a1", "title": "Algorithms", "summary": "Elegant solutions to hard problems"},
                {"id": "prog-a2", "title": "System Design", "summary": "Building things that scale"},
                {"id": "prog-a3", "title": "Code Architecture", "summary": "Organizing large codebases"},
            ],
        }
    },
    "ai_ml": {
        "name": "AI & Machine Learning",
        "levels": {
            "beginner": [
                {"id": "ai-b1", "title": "What Is AI?", "summary": "Machines that learn"},
                {"id": "ai-b2", "title": "Training Data", "summary": "Teaching by example"},
                {"id": "ai-b3", "title": "Predictions and Patterns", "summary": "What AI actually does"},
            ],
            "intermediate": [
                {"id": "ai-i1", "title": "Neural Networks", "summary": "Layers of learning"},
                {"id": "ai-i2", "title": "Training and Testing", "summary": "How models get smart"},
                {"id": "ai-i3", "title": "Bias and Fairness", "summary": "When AI inherits our mistakes"},
            ],
            "advanced": [
                {"id": "ai-a1", "title": "Large Language Models", "summary": "How systems like me work"},
                {"id": "ai-a2", "title": "Generative AI", "summary": "Creating new things from patterns"},
                {"id": "ai-a3", "title": "AI Ethics", "summary": "The hard questions we must answer"},
            ],
        }
    },
    "biomimicry": {
        "name": "Biomimicry",
        "levels": {
            "beginner": [
                {"id": "bio-b1", "title": "What Is Biomimicry?", "summary": "Learning from nature's designs"},
                {"id": "bio-b2", "title": "Nature's Patterns", "summary": "Spirals, branches, and tessellations"},
                {"id": "bio-b3", "title": "Simple Inspirations", "summary": "Velcro, bullet trains, and gecko feet"},
            ],
            "intermediate": [
                {"id": "bio-i1", "title": "Structural Biomimicry", "summary": "Building like bones and shells"},
                {"id": "bio-i2", "title": "Process Biomimicry", "summary": "Manufacturing like nature"},
                {"id": "bio-i3", "title": "Systems Biomimicry", "summary": "Ecosystems as design templates"},
            ],
            "advanced": [
                {"id": "bio-a1", "title": "Biomimicry in Computing", "summary": "Ant algorithms and neural networks"},
                {"id": "bio-a2", "title": "Self-Healing Materials", "summary": "Things that fix themselves"},
                {"id": "bio-a3", "title": "Regenerative Design", "summary": "Building that gives back"},
            ],
        }
    },
    "game_design": {
        "name": "Game Design",
        "levels": {
            "beginner": [
                {"id": "gdes-b1", "title": "What Makes Games Fun?", "summary": "The core loop"},
                {"id": "gdes-b2", "title": "Rules and Goals", "summary": "The skeleton of play"},
                {"id": "gdes-b3", "title": "Feedback Loops", "summary": "Telling players they're doing it right"},
            ],
            "intermediate": [
                {"id": "gdes-i1", "title": "Difficulty and Flow", "summary": "Challenge without frustration"},
                {"id": "gdes-i2", "title": "Player Psychology", "summary": "What keeps people playing"},
                {"id": "gdes-i3", "title": "Level Design", "summary": "Spaces that teach through play"},
            ],
            "advanced": [
                {"id": "gdes-a1", "title": "Emergent Gameplay", "summary": "When players surprise you"},
                {"id": "gdes-a2", "title": "Narrative Design", "summary": "Story and gameplay as one"},
                {"id": "gdes-a3", "title": "Systems Design", "summary": "Interconnected mechanics"},
            ],
        }
    },
}

ALL_CURRICULA = {
    "ajani": AJANI_CURRICULUM,
    "minerva": MINERVA_CURRICULUM,
    "hermes": HERMES_CURRICULUM,
}

def get_all_fields(persona: str) -> list:
    """Get all fields for a persona"""
    curriculum = ALL_CURRICULA.get(persona.lower(), {})
    return [{"id": k, "name": v["name"]} for k, v in curriculum.items()]

def get_field_lessons(persona: str, field: str) -> dict:
    """Get all lessons for a specific field"""
    curriculum = ALL_CURRICULA.get(persona.lower(), {})
    return curriculum.get(field.lower(), {})

def get_lesson(persona: str, field: str, lesson_id: str) -> dict | None:
    """Get a specific lesson by ID"""
    field_data = get_field_lessons(persona, field)
    if not field_data:
        return None
    for level, lessons in field_data.get("levels", {}).items():
        for lesson in lessons:
            if lesson["id"] == lesson_id:
                return {**lesson, "level": level, "field": field}
    return None

def get_next_lesson(persona: str, field: str, current_lesson_id: str) -> dict | None:
    """Get the next lesson after the current one"""
    field_data = get_field_lessons(persona, field)
    if not field_data:
        return None
    
    all_lessons = []
    for level in ["beginner", "intermediate", "advanced"]:
        lessons = field_data.get("levels", {}).get(level, [])
        for lesson in lessons:
            all_lessons.append({**lesson, "level": level, "field": field})
    
    for i, lesson in enumerate(all_lessons):
        if lesson["id"] == current_lesson_id and i + 1 < len(all_lessons):
            return all_lessons[i + 1]
    return None
