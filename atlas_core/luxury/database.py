from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator, Optional


SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS materials (
    name TEXT PRIMARY KEY,
    category TEXT NOT NULL,
    properties_json TEXT NOT NULL DEFAULT '{}',
    emotions_json TEXT NOT NULL DEFAULT '[]',
    compatible_materials_json TEXT NOT NULL DEFAULT '[]',
    repairability REAL NOT NULL CHECK (repairability BETWEEN 0 AND 1),
    sustainability REAL NOT NULL CHECK (sustainability BETWEEN 0 AND 1),
    aging_quality REAL NOT NULL CHECK (aging_quality BETWEEN 0 AND 1),
    notes TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS design_projects (
    design_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    product_type TEXT NOT NULL,
    description TEXT NOT NULL,
    story TEXT NOT NULL DEFAULT '',
    silhouette_notes TEXT NOT NULL DEFAULT '',
    materials_json TEXT NOT NULL DEFAULT '[]',
    hardware_json TEXT NOT NULL DEFAULT '[]',
    patterns_json TEXT NOT NULL DEFAULT '[]',
    inspirations_json TEXT NOT NULL DEFAULT '[]',
    repair_plan TEXT NOT NULL DEFAULT '',
    manufacturing_notes TEXT NOT NULL DEFAULT '',
    metadata_json TEXT NOT NULL DEFAULT '{}',
    stage TEXT NOT NULL DEFAULT 'idea',
    revision INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS forge_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    design_id TEXT NOT NULL,
    stage TEXT NOT NULL,
    note TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (design_id) REFERENCES design_projects(design_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS genome_scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    design_id TEXT NOT NULL,
    category TEXT NOT NULL,
    score REAL NOT NULL CHECK (score BETWEEN 0 AND 100),
    reason TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (design_id) REFERENCES design_projects(design_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS ai_reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    design_id TEXT NOT NULL,
    reviewer TEXT NOT NULL,
    verdict TEXT NOT NULL,
    score REAL NOT NULL CHECK (score BETWEEN 0 AND 100),
    strengths_json TEXT NOT NULL DEFAULT '[]',
    concerns_json TEXT NOT NULL DEFAULT '[]',
    required_changes_json TEXT NOT NULL DEFAULT '[]',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (design_id) REFERENCES design_projects(design_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS academy_modules (
    module_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    weight REAL NOT NULL CHECK (weight > 0),
    completion REAL NOT NULL DEFAULT 0 CHECK (completion BETWEEN 0 AND 100),
    evidence TEXT NOT NULL DEFAULT '',
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""


class LuxuryDatabase:
    def __init__(self, path: str | Path = "atlas_luxury.db") -> None:
        self.path = str(path)

    @contextmanager
    def connect(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        try:
            connection.execute("PRAGMA foreign_keys = ON")
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def initialize(self) -> None:
        with self.connect() as connection:
            connection.executescript(SCHEMA)

    def table_exists(self, table_name: str) -> bool:
        with self.connect() as connection:
            row = connection.execute(
                "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?",
                (table_name,),
            ).fetchone()
        return row is not None

    @staticmethod
    def dumps(value: object) -> str:
        return json.dumps(value, sort_keys=True)

    @staticmethod
    def loads(value: Optional[str], default: object) -> object:
        if not value:
            return default
        return json.loads(value)
