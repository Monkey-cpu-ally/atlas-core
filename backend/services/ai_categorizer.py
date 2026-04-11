"""
AI Categorization Service
Uses LLM to analyze uploaded files and categorize them intelligently
"""
import os
import json
from typing import Dict, List
import mimetypes

# AI Persona profiles for categorization
AI_PERSONAS = {
    "ajani": {
        "name": "Ajani",
        "domain": "Elemental Kinetics",
        "keywords": ["energy", "robotics", "engineering", "physics", "mechanics", "power", "solar", "kinetic", "elemental", "automation", "materials", "construction"],
        "sections": ["projects", "lab", "blueprints"]
    },
    "minerva": {
        "name": "Minerva",
        "domain": "Bio-Genesis",
        "keywords": ["biology", "genetics", "culture", "art", "mythology", "history", "writing", "plants", "medicine", "regeneration", "architecture", "permaculture"],
        "sections": ["projects", "subjects", "archives"]
    },
    "hermes": {
        "name": "Hermes",
        "domain": "Nano-Synthesis",
        "keywords": ["nanotechnology", "quantum", "logic", "security", "encryption", "atomic", "precision", "molecular", "chemistry", "computing"],
        "sections": ["lab", "projects", "blueprints"]
    },
    "trinity": {
        "name": "Trinity Counsel",
        "domain": "Multi-Domain Synthesis",
        "keywords": ["collaboration", "synthesis", "complex", "multi-domain", "integration", "strategy"],
        "sections": ["projects", "subjects"]
    }
}

SECTIONS = {
    "projects": ["project", "implementation", "build", "development", "production"],
    "lab": ["experiment", "test", "research", "study", "analysis", "data"],
    "subjects": ["learn", "education", "teach", "theory", "concept", "fundamentals"],
    "blueprints": ["design", "plan", "specification", "blueprint", "architecture", "schema"],
    "archives": ["archive", "history", "documentation", "reference", "record", "storage"]
}


def analyze_filename_and_type(filename: str, file_type: str) -> Dict:
    """
    Basic analysis based on filename and file type
    Returns preliminary categorization
    """
    filename_lower = filename.lower()
    
    # Score each AI persona based on keywords in filename
    scores = {persona: 0 for persona in AI_PERSONAS.keys()}
    tags = []
    
    for persona, info in AI_PERSONAS.items():
        for keyword in info["keywords"]:
            if keyword in filename_lower:
                scores[persona] += 1
                if keyword not in tags:
                    tags.append(keyword)
    
    # Determine best AI persona
    best_persona = max(scores.items(), key=lambda x: x[1])
    ai_persona = best_persona[0] if best_persona[1] > 0 else "trinity"
    
    # Determine section based on filename keywords
    section_scores = {section: 0 for section in SECTIONS.keys()}
    for section, keywords in SECTIONS.items():
        for keyword in keywords:
            if keyword in filename_lower:
                section_scores[section] += 1
    
    best_section = max(section_scores.items(), key=lambda x: x[1])
    section = best_section[0] if best_section[1] > 0 else "archives"
    
    # Ensure section is valid for the persona
    if section not in AI_PERSONAS[ai_persona]["sections"]:
        section = AI_PERSONAS[ai_persona]["sections"][0]
    
    # Generate basic description
    description = f"{file_type.split('/')[1].upper()} file: {filename}"
    
    # Extract more tags from filename
    words = filename_lower.replace('_', ' ').replace('-', ' ').replace('.', ' ').split()
    for word in words:
        if len(word) > 3 and word not in tags and word.isalpha():
            tags.append(word)
    
    return {
        "ai_persona": ai_persona,
        "section": section,
        "tags": tags[:5],  # Limit to 5 tags
        "description": description,
        "confidence": "basic"  # Can be enhanced with LLM
    }


async def categorize_file_with_ai(filename: str, file_type: str, file_content: str = None) -> Dict:
    """
    Use AI (LLM) to categorize file more accurately
    Falls back to basic categorization if LLM not available
    """
    
    # For now, use basic categorization
    # Can be enhanced with Emergent LLM integration later
    basic_result = analyze_filename_and_type(filename, file_type)
    
    # TODO: Integrate with Emergent LLM for deeper analysis
    # if file_content:
    #     # Use LLM to analyze content and provide better categorization
    #     pass
    
    return basic_result


def get_ai_persona_info(persona: str) -> Dict:
    """Get information about an AI persona"""
    return AI_PERSONAS.get(persona, AI_PERSONAS["trinity"])


def get_available_sections(persona: str) -> List[str]:
    """Get available sections for an AI persona"""
    return AI_PERSONAS.get(persona, {}).get("sections", ["projects", "archives"])
