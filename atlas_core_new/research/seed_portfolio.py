"""
Seed new portfolio projects into the research_tracker database.

Usage: python -m atlas_core_new.research.seed_portfolio
"""

import os
import sys

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from atlas_core_new.db.models import ResearchTracker, ResearchActivityLog
from atlas_core_new.research.persona_research import PERSONA_RESEARCH_PROFILES

PHASE_PROGRESS = {
    "philosophy": 5,
    "concept": 15,
    "research": 30,
    "blueprint": 45,
    "simulation": 60,
    "digital_proto": 75,
    "physical_proto": 85,
    "refinement": 100,
}

NEW_PROJECT_IDS = [
    "green-robotics", "robotic-arms", "liquid-armor", "morphing-structures",
    "bio-architecture", "ancient-architecture", "survival-botany", "plant-alchemy",
    "permaculture", "mythologies", "comic-development", "dna-storage",
    "quantum-encryption",
]


def seed_new_projects():
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        print("ERROR: DATABASE_URL not set")
        sys.exit(1)

    engine = create_engine(database_url, pool_pre_ping=True)
    Session = sessionmaker(bind=engine)
    db = Session()

    added = 0
    skipped = 0

    try:
        for persona_key, profile in PERSONA_RESEARCH_PROFILES.items():
            for project in profile.projects:
                if project.id not in NEW_PROJECT_IDS:
                    continue

                existing = db.query(ResearchTracker).filter(
                    ResearchTracker.project_id == project.id,
                    ResearchTracker.persona == persona_key,
                ).first()

                if existing:
                    print(f"  SKIP  {persona_key}/{project.id} — already exists")
                    skipped += 1
                    continue

                progress = PHASE_PROGRESS.get(project.phase, 0)
                last_bt = project.breakthroughs[-1] if project.breakthroughs else None

                tracker = ResearchTracker(
                    persona=persona_key,
                    project_id=project.id,
                    project_name=project.name,
                    codename=project.codename,
                    current_phase=project.phase,
                    progress_percent=progress,
                    current_focus=project.current_focus,
                    last_breakthrough=last_bt,
                    is_active=True,
                    review_stage="concept",
                    supervisor_status="pending_review",
                )
                db.add(tracker)

                db.add(ResearchActivityLog(
                    persona=persona_key,
                    project_id=project.id,
                    activity_type="daily_update",
                    title=f"{project.name} initialized",
                    description=f"Project {project.codename} seeded at phase: {project.phase} ({progress}% complete). Focus: {project.current_focus}",
                ))

                for bt in project.breakthroughs:
                    db.add(ResearchActivityLog(
                        persona=persona_key,
                        project_id=project.id,
                        activity_type="breakthrough",
                        title=f"Breakthrough — {project.codename}",
                        description=bt,
                    ))

                print(f"  ADD   {persona_key}/{project.id} — {project.name} ({project.codename})")
                added += 1

        db.commit()
        print(f"\nDone. Added: {added}, Skipped: {skipped}")

    except Exception as e:
        db.rollback()
        print(f"ERROR: {e}")
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    seed_new_projects()
