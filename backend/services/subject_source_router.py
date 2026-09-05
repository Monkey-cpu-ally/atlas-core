"""ATLAS 22-subject -> trusted-source routing.

This module is intentionally deterministic. It gives the research orchestrator
and the three ATLAS personas a shared source-priority policy before any LLM
reasoning happens.
"""
from __future__ import annotations

from typing import Dict, List, Optional

SUBJECTS: List[str] = [
    "Aerospace Engineering",
    "Architecture",
    "Artificial Intelligence",
    "Biology",
    "Business",
    "Chemistry",
    "Creative Writing",
    "Economics",
    "Electronics",
    "Environmental Science",
    "Film Studies",
    "Game Design",
    "History",
    "Mathematics",
    "Music Theory",
    "Nanotechnology",
    "Philosophy",
    "Physics",
    "Psychology",
    "Robotics",
    "Software Engineering",
    "Visual Arts",
]

ALIASES = {
    "aerospace": "Aerospace Engineering",
    "ai": "Artificial Intelligence",
    "artificial intelligence": "Artificial Intelligence",
    "environment": "Environmental Science",
    "film": "Film Studies",
    "games": "Game Design",
    "game development": "Game Design",
    "math": "Mathematics",
    "music": "Music Theory",
    "nano": "Nanotechnology",
    "software": "Software Engineering",
    "software development": "Software Engineering",
    "art": "Visual Arts",
    "visual art": "Visual Arts",
}

# Highest priority first. Every subject gets multiple sources so one provider
# outage never makes the domain unusable.
SOURCE_PRIORITY: Dict[str, List[str]] = {
    "Aerospace Engineering": ["nasa_ntrs", "nist", "arxiv", "openalex", "uspto_patents", "wikipedia", "wikidata"],
    "Architecture": ["library_of_congress", "openalex", "nist", "uspto_patents", "wikipedia", "wikidata"],
    "Artificial Intelligence": ["arxiv", "openalex", "github", "nist", "uspto_patents", "wikipedia", "wikidata"],
    "Biology": ["pubmed", "openalex", "nist", "uspto_patents", "wikipedia", "wikidata"],
    "Business": ["openalex", "library_of_congress", "uspto_patents", "wikipedia", "wikidata"],
    "Chemistry": ["nist", "openalex", "pubmed", "uspto_patents", "wikipedia", "wikidata"],
    "Creative Writing": ["project_gutenberg", "library_of_congress", "openalex", "wikipedia", "wikidata"],
    "Economics": ["openalex", "library_of_congress", "project_gutenberg", "wikipedia", "wikidata"],
    "Electronics": ["nist", "arxiv", "openalex", "github", "uspto_patents", "wikipedia", "wikidata"],
    "Environmental Science": ["nasa_ntrs", "openalex", "pubmed", "nist", "wikipedia", "wikidata"],
    "Film Studies": ["library_of_congress", "project_gutenberg", "openalex", "wikipedia", "wikidata"],
    "Game Design": ["github", "openalex", "arxiv", "uspto_patents", "wikipedia", "wikidata"],
    "History": ["library_of_congress", "project_gutenberg", "wikipedia", "wikidata", "openalex"],
    "Mathematics": ["arxiv", "openalex", "github", "project_gutenberg", "wikipedia", "wikidata"],
    "Music Theory": ["library_of_congress", "project_gutenberg", "openalex", "wikipedia", "wikidata"],
    "Nanotechnology": ["nist", "arxiv", "openalex", "pubmed", "uspto_patents", "wikipedia", "wikidata"],
    "Philosophy": ["project_gutenberg", "openalex", "library_of_congress", "wikipedia", "wikidata"],
    "Physics": ["arxiv", "nist", "openalex", "nasa_ntrs", "project_gutenberg", "wikipedia", "wikidata"],
    "Psychology": ["pubmed", "openalex", "library_of_congress", "project_gutenberg", "wikipedia", "wikidata"],
    "Robotics": ["nasa_ntrs", "arxiv", "github", "nist", "openalex", "uspto_patents", "wikipedia", "wikidata"],
    "Software Engineering": ["github", "arxiv", "openalex", "nist", "uspto_patents", "wikipedia", "wikidata"],
    "Visual Arts": ["library_of_congress", "project_gutenberg", "openalex", "wikipedia", "wikidata"],
}

# Persona affinities are advisory, not access controls. All three agents can
# query every subject and every source.
PERSONA_AFFINITY: Dict[str, List[str]] = {
    "ajani": ["Business", "Economics", "Architecture", "Robotics", "Aerospace Engineering", "Game Design"],
    "minerva": ["Biology", "Environmental Science", "History", "Creative Writing", "Psychology", "Visual Arts", "Music Theory", "Philosophy"],
    "hermes": ["Artificial Intelligence", "Software Engineering", "Electronics", "Mathematics", "Physics", "Chemistry", "Nanotechnology"],
}


def normalize_subject(subject: str) -> Optional[str]:
    raw = (subject or "").strip()
    if not raw:
        return None
    for canonical in SUBJECTS:
        if raw.casefold() == canonical.casefold():
            return canonical
    return ALIASES.get(raw.casefold())


def sources_for_subject(subject: str, limit: Optional[int] = None) -> List[str]:
    canonical = normalize_subject(subject)
    if canonical is None:
        return []
    sources = SOURCE_PRIORITY[canonical]
    return sources[:limit] if limit else list(sources)


def subjects_for_agent(agent: str) -> List[str]:
    return list(PERSONA_AFFINITY.get((agent or "").strip().lower(), []))


def route_subject(subject: str) -> Dict[str, object]:
    canonical = normalize_subject(subject)
    if canonical is None:
        return {"found": False, "subject": subject, "sources": []}
    agents = [name for name, subjects in PERSONA_AFFINITY.items() if canonical in subjects]
    return {
        "found": True,
        "subject": canonical,
        "sources": sources_for_subject(canonical),
        "persona_affinity": agents or ["council"],
        "all_personas_have_access": True,
    }
