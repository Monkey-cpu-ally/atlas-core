"""
ATLAS Internal Knowledge Core

Purpose:
- Keep the 22-subject education database INSIDE Ajani, Minerva, and Hermes
- Treat the HUD/rings as an interface only
- Allow the AIs to search, remember, teach, and recommend videos from the internal core

Rule: HUD = visual access layer | AI Core = real knowledge/memory/teaching system
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


# ---------------------------------------------------------
# 1. DATA MODELS
# ---------------------------------------------------------

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


# ---------------------------------------------------------
# 2. INTERNAL KNOWLEDGE CORE
# ---------------------------------------------------------

class AtlasKnowledgeCore:
    """
    This is the actual internal knowledge system.
    Ajani, Minerva, and Hermes use this directly.
    The HUD/rings should never own this data.
    """

    def __init__(self):
        self.subjects: Dict[str, SubjectKnowledge] = {}
        self._load_default_subjects()

    def _load_default_subjects(self):
        """Loads the starter 22-subject ATLAS library."""

        # 1. Physics
        self.add_subject(
            SubjectKnowledge(
                subject="Physics",
                books=BookStack(
                    beginner=["Conceptual Physics"],
                    hands_on=["How Things Work"],
                    university=["Fundamentals of Physics"],
                    advanced=["Classical Electrodynamics", "Plasma Physics and Fusion Energy"],
                ),
                core_topics=["motion", "energy", "electricity", "waves", "plasma", "fusion"],
                video_help_sources=["Veritasium", "Physics Girl", "PBS Space Time", "Dr. Becky"],
                projects=["motion experiment", "energy system model", "plasma simulation"],
                lessons={
                    "energy": "Energy is the ability to cause change or do work. At university level, it connects mechanics, thermodynamics, electricity, and quantum physics. In simple terms: energy is what makes things happen.",
                    "plasma": "Plasma is a state of matter where gas becomes electrically charged. It appears in stars, lightning, and fusion research. Simple version: plasma is super-hot electric gas."
                },
            )
        )

        # 2. Biology
        self.add_subject(
            SubjectKnowledge(
                subject="Biology",
                books=BookStack(
                    beginner=["Campbell Biology"],
                    hands_on=["Botany for Gardeners", "The Vegetable Gardener's Bible"],
                    university=["Essential Cell Biology"],
                    advanced=["Molecular Biology of the Cell"],
                ),
                core_topics=["cells", "DNA", "cell division", "plants", "genetics", "microbiology"],
                video_help_sources=["Amoeba Sisters", "CrashCourse Biology", "Khan Academy Biology", "Ninja Nerd"],
                projects=["cell diagram", "plant growth lab", "DNA inheritance model"],
                lessons={
                    "cell division": "Cell division is how cells make new cells. University version: mitosis and meiosis control reproduction, growth, repair, and genetic inheritance. Simple version: cells copy themselves so life can grow and heal.",
                    "plants": "Plants turn sunlight, water, and carbon dioxide into food through photosynthesis. Simple version: plants are living solar-powered food makers."
                },
            )
        )

        # 3. Artificial Intelligence
        self.add_subject(
            SubjectKnowledge(
                subject="Artificial Intelligence",
                books=BookStack(
                    beginner=["Machine Learning for Absolute Beginners"],
                    hands_on=["Hands-On Machine Learning"],
                    university=["Artificial Intelligence: A Modern Approach"],
                    advanced=["Deep Learning"],
                ),
                core_topics=["machine learning", "agents", "memory", "reasoning", "ethics"],
                video_help_sources=["3Blue1Brown", "freeCodeCamp", "DeepLearningAI", "Two Minute Papers"],
                projects=["AI tutor", "memory engine", "persona system"],
                lessons={
                    "machine learning": "Machine learning is when a computer learns patterns from examples. University version: models optimize parameters to reduce prediction error. Simple version: it learns by practicing on data."
                },
            )
        )

        # 4. Aerospace Engineering
        self.add_subject(
            SubjectKnowledge(
                subject="Aerospace Engineering",
                books=BookStack(
                    beginner=["Introduction to Flight"],
                    hands_on=["Aircraft Construction", "Standard Aircraft Handbook"],
                    university=["Orbital Mechanics for Engineering Students"],
                    advanced=["Fundamentals of Aerodynamics"],
                ),
                core_topics=["aerodynamics", "flight", "propulsion", "orbits", "aircraft structure"],
                video_help_sources=["MIT OpenCourseWare Aerospace", "NASA educational videos", "Real Engineering", "Scott Manley"],
                projects=["paper rocket test", "wing lift test", "orbital path simulation"],
                lessons={
                    "lift": "Lift is the upward force that helps aircraft fly. University version: lift comes from pressure differences and airflow around wings. Simple version: wings shape air so the plane gets pushed upward."
                },
            )
        )

        # 5. Chemistry
        self.add_subject(
            SubjectKnowledge(
                subject="Chemistry",
                books=BookStack(
                    beginner=["Chemistry: The Central Science"],
                    hands_on=["Illustrated Guide to Home Chemistry Experiments"],
                    university=["Organic Chemistry"],
                    advanced=["Physical Chemistry"],
                ),
                core_topics=["atoms", "molecules", "reactions", "organic chemistry", "bonds"],
                video_help_sources=["NileRed", "Professor Dave Explains", "Khan Academy Chemistry"],
                projects=["acid-base test", "crystal growing", "reaction rates"],
                lessons={
                    "atoms": "Atoms are the building blocks of matter. University version: atoms contain protons, neutrons, and electrons in precise arrangements. Simple version: atoms are tiny pieces that make up everything."
                },
            )
        )

        # Continue with remaining 17 subjects (shortened for brevity - you can expand)
        # 6. Mathematics, 7. Computer Science, 8. Robotics, 9. Nanotechnology
        # 10. Architecture, 11. Environmental Science, 12. Psychology
        # 13. History, 14. Literature, 15. Art, 16. Music
        # 17. Philosophy, 18. Economics, 19. Medicine, 20. Agriculture
        # 21. Astronomy, 22. Geology

    def add_subject(self, subject_data: SubjectKnowledge):
        key = subject_data.subject.lower().strip()
        self.subjects[key] = subject_data

    def get_subject(self, subject: str) -> Optional[SubjectKnowledge]:
        return self.subjects.get(subject.lower().strip())

    def search_topic(self, query: str) -> List[SubjectKnowledge]:
        query = query.lower().strip()
        results = []

        for subject in self.subjects.values():
            if query in subject.subject.lower():
                results.append(subject)
                continue

            for topic in subject.core_topics:
                if query in topic.lower():
                    results.append(subject)
                    break

        return results

    def teach(self, subject: str, topic: str) -> TeachingResponse:
        subject_data = self.get_subject(subject)
        if not subject_data:
            raise ValueError(f"Subject not found in ATLAS Knowledge Core: {subject}")

        topic_key = topic.lower().strip()
        base_lesson = subject_data.lessons.get(
            topic_key,
            f"{topic} belongs to {subject_data.subject}. I need a deeper lesson added for this exact topic."
        )

        return TeachingResponse(
            subject=subject_data.subject,
            topic=topic,
            ajani=f"Ajani: {base_lesson} Strategy view: understand the system, its limits, and how it can be applied in the real world.",
            minerva=f"Minerva: {base_lesson} Memory view: connect the idea to a story, image, or lived example so it stays with you.",
            hermes=f"Hermes: {base_lesson} Simple view: break it down into plain steps and examples first.",
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
            "available_lessons": list(subject_data.lessons.keys())
        }


# ---------------------------------------------------------
# 3. GLOBAL KNOWLEDGE CORE INSTANCE
# ---------------------------------------------------------

# Create single shared knowledge core instance
_knowledge_core_instance = None

def get_knowledge_core() -> AtlasKnowledgeCore:
    """Get or create the global knowledge core instance"""
    global _knowledge_core_instance
    if _knowledge_core_instance is None:
        _knowledge_core_instance = AtlasKnowledgeCore()
    return _knowledge_core_instance
