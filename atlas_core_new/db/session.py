"""
atlas_core_new/db/session.py

Database session configuration for Atlas Core.
Reference: python_database integration
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base


DATABASE_URL = os.environ.get("DATABASE_URL")

engine = create_engine(
    DATABASE_URL,
    pool_recycle=300,
    pool_pre_ping=True,
) if DATABASE_URL else None

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) if engine else None


def get_db():
    if SessionLocal is None:
        return None
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    if engine is not None:
        Base.metadata.create_all(bind=engine)
        return True
    return False
