from __future__ import annotations

import json
import sqlite3
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, List, Optional

from .models import AIReview, CouncilDecision, CritiqueFinding, DesignGenome, GenomeScore, ReviewVerdict


class EvaluationStore:
    """SQLite-backed storage for design evaluations and Council decisions."""

    def __init__(self, database_path: str | Path) -> None:
        self.database_path = str(database_path)
        self.initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        return connection

    def initialize(self) -> None:
        with self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS design_evaluations (
                    design_id TEXT PRIMARY KEY,
                    genome_json TEXT NOT NULL,
                    critiques_json TEXT NOT NULL,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS council_decisions (
                    design_id TEXT PRIMARY KEY,
                    verdict TEXT NOT NULL,
                    overall_score REAL NOT NULL,
                    summary TEXT NOT NULL,
                    reviews_json TEXT NOT NULL,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
                """
            )

    def save_evaluation(
        self,
        genome: DesignGenome,
        critiques: List[CritiqueFinding],
    ) -> None:
        genome_payload = [asdict(score) for score in genome.scores]
        critique_payload = [asdict(item) for item in critiques]
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO design_evaluations(design_id, genome_json, critiques_json)
                VALUES (?, ?, ?)
                ON CONFLICT(design_id) DO UPDATE SET
                    genome_json = excluded.genome_json,
                    critiques_json = excluded.critiques_json,
                    updated_at = CURRENT_TIMESTAMP
                """,
                (genome.design_id, json.dumps(genome_payload), json.dumps(critique_payload)),
            )

    def load_evaluation(self, design_id: str) -> tuple[DesignGenome, List[CritiqueFinding]] | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT genome_json, critiques_json FROM design_evaluations WHERE design_id = ?",
                (design_id,),
            ).fetchone()
        if row is None:
            return None
        scores = [GenomeScore(**item) for item in json.loads(row["genome_json"])]
        critiques = [CritiqueFinding(**item) for item in json.loads(row["critiques_json"])]
        return DesignGenome(design_id=design_id, scores=scores), critiques

    def save_council_decision(self, decision: CouncilDecision) -> None:
        reviews = []
        for review in decision.reviews:
            payload = asdict(review)
            payload["verdict"] = review.verdict.value
            reviews.append(payload)
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO council_decisions(
                    design_id, verdict, overall_score, summary, reviews_json
                ) VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(design_id) DO UPDATE SET
                    verdict = excluded.verdict,
                    overall_score = excluded.overall_score,
                    summary = excluded.summary,
                    reviews_json = excluded.reviews_json,
                    updated_at = CURRENT_TIMESTAMP
                """,
                (
                    decision.design_id,
                    decision.verdict.value,
                    decision.overall_score,
                    decision.summary,
                    json.dumps(reviews),
                ),
            )

    def load_council_decision(self, design_id: str) -> CouncilDecision | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM council_decisions WHERE design_id = ?",
                (design_id,),
            ).fetchone()
        if row is None:
            return None
        reviews = []
        for item in json.loads(row["reviews_json"]):
            item["verdict"] = ReviewVerdict(item["verdict"])
            reviews.append(AIReview(**item))
        return CouncilDecision(
            design_id=design_id,
            verdict=ReviewVerdict(row["verdict"]),
            overall_score=float(row["overall_score"]),
            reviews=reviews,
            summary=row["summary"],
        )
