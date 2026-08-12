"""
ATLAS Internal Knowledge Core

Canonical 22-subject education system used by Ajani, Minerva, and Hermes.
HUD/rings are presentation only; this module owns starter subject metadata.
External/current knowledge is supplied by the Knowledge Bank ingestion and
subject-source routing layers.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class BookStack:
    beginner: List[str] = field(default_factory=list)
    hands_on: List[str] = field(default_factory=list)
    university: List[str] = field(default_factory=list)
    advanced: List[str] = field(default_factory=list)


@dataclass
class SubjectKnowledge:
    subject: str
    books: BookStack
    core_topics: List[str]
    video_help_sources: List[str]
    projects: List[str]
    lessons: Dict[str, str] = field(default_factory=dict)


@dataclass
class TeachingResponse:
    subject: str
    topic: str
    ajani: str
    minerva: str
    hermes: str
    video_help: List[str]
    projects: List[str]


def _stack(beginner, hands_on, university, advanced):
    return BookStack(beginner=list(beginner), hands_on=list(hands_on), university=list(university), advanced=list(advanced))


def _subject(name, books, topics, videos, projects, lessons):
    return SubjectKnowledge(
        subject=name,
        books=_stack(*books),
        core_topics=list(topics),
        video_help_sources=list(videos),
        projects=list(projects),
        lessons=dict(lessons),
    )


CANONICAL_SUBJECTS: List[SubjectKnowledge] = [
    _subject(
        "Aerospace Engineering",
        (["Introduction to Flight"], ["Standard Aircraft Handbook"], ["Orbital Mechanics for Engineering Students"], ["Fundamentals of Aerodynamics"]),
        ["aerodynamics", "flight mechanics", "propulsion", "orbital mechanics", "aircraft structures", "space systems"],
        ["NASA", "MIT OpenCourseWare Aerospace", "Real Engineering", "Scott Manley"],
        ["wing lift experiment", "model rocket analysis", "orbital transfer simulation"],
        {"lift": "Lift is the aerodynamic force that acts roughly perpendicular to the incoming airflow. Simple version: a wing changes the air's motion and pressure so the aircraft is pushed upward."},
    ),
    _subject(
        "Architecture",
        (["Architecture: Form, Space, and Order"], ["Architectural Graphics"], ["Building Construction Illustrated"], ["A Pattern Language"]),
        ["design principles", "structures", "materials", "building systems", "urban design", "sustainability"],
        ["MIT OpenCourseWare Architecture", "30X40 Design Workshop", "The B1M"],
        ["small house floor plan", "passive solar model", "structural concept study"],
        {"design principles": "Architecture balances function, structure, human experience, environment, and aesthetics. Simple version: make a place useful, safe, comfortable, and meaningful."},
    ),
    _subject(
        "Artificial Intelligence",
        (["Machine Learning for Absolute Beginners"], ["Hands-On Machine Learning"], ["Artificial Intelligence: A Modern Approach"], ["Deep Learning"]),
        ["machine learning", "agents", "reasoning", "memory", "computer vision", "natural language processing", "AI safety"],
        ["3Blue1Brown", "DeepLearning.AI", "MIT OpenCourseWare", "Two Minute Papers"],
        ["classifier", "AI tutor", "retrieval augmented assistant", "multi-agent simulation"],
        {"machine learning": "Machine learning lets a computer improve a task by learning patterns from data instead of relying only on hand-written rules."},
    ),
    _subject(
        "Biology",
        (["Campbell Biology"], ["Botany for Gardeners"], ["Essential Cell Biology"], ["Molecular Biology of the Cell"]),
        ["cells", "DNA", "genetics", "evolution", "microbiology", "plants", "ecology", "physiology"],
        ["Amoeba Sisters", "CrashCourse Biology", "Khan Academy Biology", "Ninja Nerd"],
        ["cell model", "plant growth lab", "inheritance simulation"],
        {"cells": "Cells are life's basic working units. They take in materials, use energy, maintain internal conditions, and reproduce or support larger organisms."},
    ),
    _subject(
        "Business",
        (["The Personal MBA"], ["Business Model Generation"], ["Principles of Management"], ["Competitive Strategy"]),
        ["business models", "operations", "marketing", "finance", "entrepreneurship", "strategy", "leadership"],
        ["Y Combinator", "Stanford eCorner", "MIT OpenCourseWare Management"],
        ["lean business model", "unit economics worksheet", "product launch plan"],
        {"business models": "A business model explains who receives value, what value is delivered, how it is delivered, and how the organization sustains itself financially."},
    ),
    _subject(
        "Chemistry",
        (["Chemistry: The Central Science"], ["Illustrated Guide to Home Chemistry Experiments"], ["Organic Chemistry"], ["Physical Chemistry"]),
        ["atoms", "molecules", "bonding", "reactions", "thermodynamics", "organic chemistry", "electrochemistry"],
        ["Khan Academy Chemistry", "Professor Dave Explains", "Periodic Videos"],
        ["acid-base indicator lab", "crystal growth", "reaction-rate model"],
        {"atoms": "Atoms contain a nucleus and electrons. Their electron arrangements largely determine how elements bond and react."},
    ),
    _subject(
        "Creative Writing",
        (["Bird by Bird"], ["Steering the Craft"], ["The Anatomy of Story"], ["The Art of Fiction"]),
        ["character", "plot", "dialogue", "setting", "theme", "voice", "worldbuilding", "revision"],
        ["Brandon Sanderson lectures", "Reedsy", "Writing Excuses"],
        ["short story", "character bible", "scene rewrite", "worldbuilding dossier"],
        {"character": "A strong character has wants, pressures, choices, contradictions, and consequences. Readers learn who a character is by what they do under pressure."},
    ),
    _subject(
        "Economics",
        (["The Undercover Economist"], ["Economics in One Lesson"], ["Principles of Economics"], ["Microeconomic Theory"]),
        ["supply and demand", "markets", "inflation", "labor", "trade", "public policy", "microeconomics", "macroeconomics"],
        ["Marginal Revolution University", "Khan Academy Economics", "MIT OpenCourseWare Economics"],
        ["market simulation", "inflation dashboard", "cost-benefit analysis"],
        {"supply and demand": "Supply describes how much sellers offer; demand describes how much buyers want. Prices help coordinate the two when markets function normally."},
    ),
    _subject(
        "Electronics",
        (["Make: Electronics"], ["Practical Electronics for Inventors"], ["Microelectronic Circuits"], ["The Art of Electronics"]),
        ["voltage", "current", "resistance", "analog circuits", "digital logic", "sensors", "microcontrollers", "power electronics"],
        ["Afrotechmods", "EEVblog", "GreatScott!", "MIT OpenCourseWare Circuits"],
        ["LED resistor circuit", "sensor node", "audio amplifier", "microcontroller controller"],
        {"voltage": "Voltage is electrical potential difference—the push that can drive charge through a circuit. Current is the resulting flow of charge."},
    ),
    _subject(
        "Environmental Science",
        (["Environmental Science for a Changing World"], ["The Hidden Life of Trees"], ["Environmental Science"], ["Principles of Environmental Engineering and Science"]),
        ["ecosystems", "climate", "water", "air quality", "soil", "pollution", "conservation", "renewable energy"],
        ["NOAA", "NASA Earth", "USGS", "CrashCourse Ecology"],
        ["water-quality study", "local biodiversity survey", "energy-use audit"],
        {"ecosystems": "An ecosystem is a network of organisms and their physical environment exchanging energy and materials."},
    ),
    _subject(
        "Film Studies",
        (["Film Art: An Introduction"], ["The Five C's of Cinematography"], ["Film History: An Introduction"], ["Sculpting in Time"]),
        ["cinematography", "editing", "sound", "screenwriting", "film history", "genre", "mise-en-scene", "directing"],
        ["StudioBinder", "Every Frame a Painting", "BFI", "Library of Congress"],
        ["shot analysis", "one-minute silent film", "editing comparison", "storyboard sequence"],
        {"cinematography": "Cinematography uses camera position, lens choice, movement, lighting, framing, and exposure to shape what the audience sees and feels."},
    ),
    _subject(
        "Game Design",
        (["The Art of Game Design"], ["Game Feel"], ["Rules of Play"], ["Game Programming Patterns"]),
        ["game loops", "mechanics", "level design", "systems design", "player psychology", "narrative design", "balancing", "prototyping"],
        ["GDC", "Game Maker's Toolkit", "Extra Credits", "Godot documentation"],
        ["paper prototype", "single-mechanic digital prototype", "level greybox", "balance spreadsheet"],
        {"game loops": "A game loop is the repeating cycle of player action, system response, feedback, and new decision that keeps play moving."},
    ),
    _subject(
        "History",
        (["A Little History of the World"], ["The Historian's Craft"], ["The Landscape of History"], ["What Is History?"]),
        ["primary sources", "chronology", "causation", "political history", "social history", "economic history", "cultural history"],
        ["Library of Congress", "Smithsonian", "National Archives", "CrashCourse History"],
        ["primary-source analysis", "historical timeline", "oral-history project"],
        {"primary sources": "Primary sources come from the period being studied—letters, records, photographs, objects, newspapers, interviews, and similar evidence."},
    ),
    _subject(
        "Mathematics",
        (["The Joy of x"], ["How to Solve It"], ["Calculus"], ["Concrete Mathematics"]),
        ["arithmetic", "algebra", "geometry", "trigonometry", "calculus", "linear algebra", "probability", "statistics", "discrete mathematics"],
        ["Khan Academy", "3Blue1Brown", "Professor Leonard", "MIT OpenCourseWare Mathematics"],
        ["function visualizer", "probability experiment", "geometry construction", "optimization model"],
        {"algebra": "Algebra uses symbols to represent quantities and relationships. Solving an equation means finding values that make both sides equal."},
    ),
    _subject(
        "Music Theory",
        (["Music Theory for Dummies"], ["The Complete Musician"], ["Tonal Harmony"], ["The Study of Counterpoint"]),
        ["rhythm", "scales", "intervals", "chords", "harmony", "melody", "counterpoint", "form", "ear training"],
        ["12tone", "Signals Music Studio", "Nahre Sol", "David Bennett Piano"],
        ["chord progression analysis", "melody harmonization", "rhythm transcription", "short composition"],
        {"harmony": "Harmony is how simultaneous notes and chords interact. Functional harmony often creates tension and release by moving between tonal roles."},
    ),
    _subject(
        "Nanotechnology",
        (["Nanotechnology for Dummies"], ["Introduction to Nanoscience and Nanotechnology"], ["Nanostructures and Nanomaterials"], ["Principles of Nano-Optics"]),
        ["nanoscale materials", "surface effects", "quantum confinement", "nanofabrication", "nanomedicine", "nanoelectronics", "characterization"],
        ["NIST", "nanoHUB", "MIT OpenCourseWare", "arXiv"],
        ["nanoparticle literature review", "surface-area model", "nano-device simulation"],
        {"nanoscale materials": "At nanometer scales, surface area and quantum effects can dominate behavior, so materials may act differently than they do in bulk form."},
    ),
    _subject(
        "Philosophy",
        (["The Philosophy Book"], ["Think"], ["The Problems of Philosophy"], ["A Theory of Justice"]),
        ["logic", "ethics", "epistemology", "metaphysics", "political philosophy", "philosophy of mind", "philosophy of science"],
        ["Wireless Philosophy", "Closer To Truth", "Stanford Encyclopedia of Philosophy"],
        ["argument map", "ethical case analysis", "thought-experiment journal"],
        {"logic": "Logic studies when conclusions follow from premises. A valid argument preserves truth from its premises to its conclusion."},
    ),
    _subject(
        "Physics",
        (["Conceptual Physics"], ["How Things Work"], ["Fundamentals of Physics"], ["Classical Electrodynamics"]),
        ["motion", "forces", "energy", "electricity", "magnetism", "waves", "thermodynamics", "quantum physics", "relativity"],
        ["Veritasium", "Physics Girl", "PBS Space Time", "MIT OpenCourseWare Physics"],
        ["motion experiment", "circuit-energy model", "wave simulation"],
        {"energy": "Energy is a conserved quantity that can move between systems and change form. Simple version: it tracks a system's capacity to produce change."},
    ),
    _subject(
        "Psychology",
        (["Psychology"], ["The Man Who Mistook His Wife for a Hat"], ["Cognitive Psychology"], ["The Principles of Psychology"]),
        ["cognition", "learning", "memory", "development", "social psychology", "personality", "behavior", "research methods"],
        ["CrashCourse Psychology", "Yale Open Courses", "APA educational resources"],
        ["memory experiment", "bias observation journal", "research-method critique"],
        {"memory": "Human memory involves encoding information, storing it over time, and retrieving it later. Attention and context strongly affect what is remembered."},
    ),
    _subject(
        "Robotics",
        (["Robot Builder's Bonanza"], ["Make: Arduino Bots and Gadgets"], ["Introduction to Robotics: Mechanics and Control"], ["Modern Robotics"]),
        ["kinematics", "dynamics", "sensors", "actuators", "control", "planning", "computer vision", "ROS", "human-robot interaction"],
        ["MIT OpenCourseWare Robotics", "Articulated Robotics", "ROS documentation", "NASA Robotics"],
        ["line-following robot", "robot arm kinematics", "PID motor controller", "ROS simulation"],
        {"kinematics": "Robot kinematics describes how joint positions and motions determine where a robot's links and end effector move, without first focusing on forces."},
    ),
    _subject(
        "Software Engineering",
        (["Code"], ["The Pragmatic Programmer"], ["Clean Architecture"], ["Designing Data-Intensive Applications"]),
        ["programming", "data structures", "algorithms", "databases", "APIs", "testing", "architecture", "version control", "security", "DevOps"],
        ["freeCodeCamp", "MIT OpenCourseWare", "GitHub Skills", "official language and framework documentation"],
        ["REST API", "tested CLI application", "database-backed web service", "CI/CD pipeline"],
        {"testing": "Software tests check that code behaves as expected. Unit tests isolate small pieces; integration tests check components working together; end-to-end tests exercise complete workflows."},
    ),
    _subject(
        "Visual Arts",
        (["The Story of Art"], ["Drawing on the Right Side of the Brain"], ["Color and Light"], ["Interaction of Color"]),
        ["drawing", "composition", "color theory", "perspective", "painting", "sculpture", "digital art", "art history", "visual storytelling"],
        ["Proko", "Marco Bucci", "Smithsonian", "The Met Open Access"],
        ["value study", "perspective drawing", "color script", "character or environment concept sheet"],
        {"composition": "Composition is the arrangement of visual elements so the viewer's eye moves through an image with clear hierarchy, balance, rhythm, and emphasis."},
    ),
]


class AtlasKnowledgeCore:
    """Shared starter knowledge system for the canonical 22 ATLAS subjects."""

    def __init__(self):
        self.subjects: Dict[str, SubjectKnowledge] = {}
        self._load_default_subjects()

    def _load_default_subjects(self):
        for subject in CANONICAL_SUBJECTS:
            self.add_subject(subject)

    def add_subject(self, subject_data: SubjectKnowledge):
        self.subjects[subject_data.subject.lower().strip()] = subject_data

    def get_subject(self, subject: str) -> Optional[SubjectKnowledge]:
        return self.subjects.get(subject.lower().strip())

    def search_topic(self, query: str) -> List[SubjectKnowledge]:
        query = query.lower().strip()
        results = []
        for subject in self.subjects.values():
            if query in subject.subject.lower() or any(query in topic.lower() for topic in subject.core_topics):
                results.append(subject)
        return results

    def teach(self, subject: str, topic: str) -> TeachingResponse:
        subject_data = self.get_subject(subject)
        if not subject_data:
            raise ValueError(f"Subject not found in ATLAS Knowledge Core: {subject}")
        topic_key = topic.lower().strip()
        base_lesson = subject_data.lessons.get(
            topic_key,
            f"{topic} is part of {subject_data.subject}. Use the Knowledge Bank research pipeline for a deeper sourced lesson on this exact topic.",
        )
        return TeachingResponse(
            subject=subject_data.subject,
            topic=topic,
            ajani=f"Ajani: {base_lesson} Strategy view: understand the system, constraints, tradeoffs, and real-world application.",
            minerva=f"Minerva: {base_lesson} Scholar view: connect the concept to context, evidence, history, and memorable examples.",
            hermes=f"Hermes: {base_lesson} Engineering view: break it into components, mechanisms, interfaces, and testable steps.",
            video_help=subject_data.video_help_sources,
            projects=subject_data.projects,
        )

    def list_all_subjects(self) -> List[str]:
        return [subject.subject for subject in self.subjects.values()]

    def get_subject_details(self, subject: str) -> Optional[Dict]:
        subject_data = self.get_subject(subject)
        if not subject_data:
            return None
        return {
            "subject": subject_data.subject,
            "core_topics": subject_data.core_topics,
            "books": {
                "beginner": subject_data.books.beginner,
                "hands_on": subject_data.books.hands_on,
                "university": subject_data.books.university,
                "advanced": subject_data.books.advanced,
            },
            "video_help": subject_data.video_help_sources,
            "projects": subject_data.projects,
            "available_lessons": list(subject_data.lessons.keys()),
        }


_knowledge_core_instance = None


def get_knowledge_core() -> AtlasKnowledgeCore:
    global _knowledge_core_instance
    if _knowledge_core_instance is None:
        _knowledge_core_instance = AtlasKnowledgeCore()
    return _knowledge_core_instance
