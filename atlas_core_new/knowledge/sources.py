"""
Knowledge Sources Registry
Organized by domain, mapped to persona specialties.

These are patterns learned from sources, not stored copies.
"""
from dataclasses import dataclass
from typing import List


@dataclass
class KnowledgeSource:
    """A category of knowledge sources"""
    id: str
    name: str
    description: str
    example_influences: List[str]
    used_for: List[str]
    primary_personas: List[str]
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "example_influences": self.example_influences,
            "used_for": self.used_for,
            "primary_personas": self.primary_personas
        }


KNOWLEDGE_SOURCES: List[KnowledgeSource] = [
    KnowledgeSource(
        id="math-logic",
        name="Math & Logic",
        description="Foundational mathematical reasoning and logical structures",
        example_influences=[
            "Calculus principles (Stewart-style explanations)",
            "Linear Algebra concepts (Strang-style clarity)",
            "Discrete Mathematics & Its Applications",
            "Mathematical logic and proof structures",
            "Engineering mathematics frameworks"
        ],
        used_for=[
            "Step-by-step reasoning",
            "Problem decomposition",
            "Proofs explained simply",
            "Pattern recognition in numbers"
        ],
        primary_personas=["hermes", "ajani"]
    ),
    KnowledgeSource(
        id="biology-life",
        name="Biology & Life Sciences",
        description="Understanding of living systems and biological processes",
        example_influences=[
            "Cell biology principles (Alberts-style depth)",
            "General biology concepts (Campbell-style breadth)",
            "Anatomy conceptual structures",
            "Cell signaling and physiology patterns",
            "Systems biology frameworks"
        ],
        used_for=[
            "Understanding cell function",
            "Signaling logic",
            "Anatomy concepts",
            "Healing systems (high-level, non-clinical)"
        ],
        primary_personas=["minerva", "ajani"]
    ),
    KnowledgeSource(
        id="engineering-physics",
        name="Engineering & Physics",
        description="How forces move, energy flows, and materials behave",
        example_influences=[
            "Engineering fundamentals",
            "Materials science principles",
            "Physics for scientists & engineers",
            "Control systems concepts",
            "Energy systems frameworks"
        ],
        used_for=[
            "How forces move",
            "How energy flows",
            "Why materials behave the way they do",
            "Safety limits and margins"
        ],
        primary_personas=["ajani", "hermes"]
    ),
    KnowledgeSource(
        id="computer-science",
        name="Computer Science & AI",
        description="Code structure, algorithms, and system design",
        example_influences=[
            "Program structure and interpretation principles",
            "Clean code practices",
            "Algorithm design patterns",
            "AI/ML fundamentals",
            "Distributed systems concepts"
        ],
        used_for=[
            "Code structure",
            "System architecture",
            "Debugging logic",
            "Modular thinking"
        ],
        primary_personas=["hermes"]
    ),
    KnowledgeSource(
        id="cultural-historical",
        name="Cultural, Historical & Mythic",
        description="Memory, meaning, and storytelling traditions",
        example_influences=[
            "African civilizations (Mali, Nubia, Ethiopia, Benin)",
            "Indigenous knowledge systems",
            "Asian, Norse, Greek, Japanese traditions",
            "Oral history patterns",
            "African-American history and literature"
        ],
        used_for=[
            "Storytelling",
            "Framing lessons with meaning",
            "Ethical grounding",
            "Symbolic understanding"
        ],
        primary_personas=["minerva"]
    ),
    KnowledgeSource(
        id="literature-storytelling",
        name="Literature & Storytelling",
        description="Narrative structures and creative patterns",
        example_influences=[
            "Classic myth cycles",
            "Dramatic structure patterns",
            "African-American literature themes",
            "Sci-fi & speculative fiction patterns",
            "Graphic novel storytelling structures"
        ],
        used_for=[
            "Narrative logic",
            "World-building",
            "Creativity",
            "Metaphor-driven teaching"
        ],
        primary_personas=["minerva"]
    ),
    KnowledgeSource(
        id="technical-standards",
        name="Technical Manuals & Standards",
        description="Professional practices and safety frameworks (conceptual level)",
        example_influences=[
            "Engineering handbook concepts",
            "Safety standard frameworks",
            "System design practices",
            "Architecture and design guides"
        ],
        used_for=[
            "Design thinking",
            "Risk awareness",
            "Professional structure",
            "Safety margins"
        ],
        primary_personas=["hermes", "ajani"]
    ),
    KnowledgeSource(
        id="educational-media",
        name="Public Knowledge & Educational Media",
        description="Open educational resources and multiple explanation styles",
        example_influences=[
            "University open course materials",
            "Educational lecture patterns",
            "Documentary explanation styles",
            "Visual teaching methods"
        ],
        used_for=[
            "Clarity",
            "Multiple explanation styles",
            "Visual metaphors",
            "Accessible teaching"
        ],
        primary_personas=["minerva", "ajani", "hermes"]
    ),
    KnowledgeSource(
        id="research-literature",
        name="Research Literature",
        description="Modern understanding from peer-reviewed patterns (high-level summaries)",
        example_influences=[
            "Peer-reviewed research patterns",
            "Abstracts and summaries",
            "Survey papers",
            "State-of-the-art reviews"
        ],
        used_for=[
            "Modern understanding",
            "Trends",
            "What is possible vs speculative",
            "Cutting-edge concepts"
        ],
        primary_personas=["hermes", "ajani", "minerva"]
    )
]


def get_all_sources() -> List[dict]:
    """Get all knowledge sources"""
    return [s.to_dict() for s in KNOWLEDGE_SOURCES]


def get_sources_for_persona(persona: str) -> List[dict]:
    """Get knowledge sources relevant to a specific persona"""
    persona = persona.lower()
    return [
        s.to_dict() for s in KNOWLEDGE_SOURCES 
        if persona in s.primary_personas
    ]


def get_source_by_id(source_id: str) -> dict | None:
    """Get a specific knowledge source by ID"""
    for source in KNOWLEDGE_SOURCES:
        if source.id == source_id:
            return source.to_dict()
    return None
