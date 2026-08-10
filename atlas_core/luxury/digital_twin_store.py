from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from .digital_twin import LifecycleEvent, LifecycleEventType, ProductDigitalTwin


class DigitalTwinStore:
    def __init__(self, database_path: str | Path = "atlas_luxury.db") -> None:
        self.database_path = str(database_path)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS product_digital_twins (
                    product_id TEXT PRIMARY KEY,
                    product_name TEXT NOT NULL,
                    collection_id TEXT,
                    design_revision INTEGER NOT NULL DEFAULT 1,
                    serial_number TEXT,
                    materials_json TEXT NOT NULL DEFAULT '[]',
                    hardware_json TEXT NOT NULL DEFAULT '[]',
                    readiness_level INTEGER NOT NULL DEFAULT 1 CHECK (readiness_level BETWEEN 1 AND 9),
                    owner_reference TEXT,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS product_lifecycle_events (
                    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    summary TEXT NOT NULL,
                    metadata_json TEXT NOT NULL DEFAULT '{}',
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (product_id) REFERENCES product_digital_twins(product_id) ON DELETE CASCADE
                );
                """
            )

    def save(self, twin: ProductDigitalTwin) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO product_digital_twins(
                    product_id, product_name, collection_id, design_revision,
                    serial_number, materials_json, hardware_json,
                    readiness_level, owner_reference, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(product_id) DO UPDATE SET
                    product_name=excluded.product_name,
                    collection_id=excluded.collection_id,
                    design_revision=excluded.design_revision,
                    serial_number=excluded.serial_number,
                    materials_json=excluded.materials_json,
                    hardware_json=excluded.hardware_json,
                    readiness_level=excluded.readiness_level,
                    owner_reference=excluded.owner_reference,
                    updated_at=CURRENT_TIMESTAMP
                """,
                (
                    twin.product_id,
                    twin.product_name,
                    twin.collection_id,
                    twin.design_revision,
                    twin.serial_number,
                    json.dumps(twin.materials),
                    json.dumps(twin.hardware),
                    twin.readiness_level,
                    twin.owner_reference,
                ),
            )
            connection.execute(
                "DELETE FROM product_lifecycle_events WHERE product_id = ?",
                (twin.product_id,),
            )
            connection.executemany(
                """
                INSERT INTO product_lifecycle_events(
                    product_id, event_type, summary, metadata_json, created_at
                ) VALUES (?, ?, ?, ?, ?)
                """,
                [
                    (
                        twin.product_id,
                        event.event_type.value,
                        event.summary,
                        json.dumps(event.metadata, sort_keys=True),
                        event.created_at,
                    )
                    for event in twin.events
                ],
            )

    def load(self, product_id: str) -> ProductDigitalTwin | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM product_digital_twins WHERE product_id = ?",
                (product_id,),
            ).fetchone()
            if row is None:
                return None
            events = connection.execute(
                "SELECT * FROM product_lifecycle_events WHERE product_id = ? ORDER BY event_id",
                (product_id,),
            ).fetchall()

        twin = ProductDigitalTwin(
            product_id=row["product_id"],
            product_name=row["product_name"],
            collection_id=row["collection_id"],
            design_revision=row["design_revision"],
            serial_number=row["serial_number"],
            materials=list(json.loads(row["materials_json"])),
            hardware=list(json.loads(row["hardware_json"])),
            readiness_level=row["readiness_level"],
            owner_reference=row["owner_reference"],
        )
        twin.events.extend(
            LifecycleEvent(
                event_type=LifecycleEventType(event["event_type"]),
                summary=event["summary"],
                metadata=json.loads(event["metadata_json"]),
                created_at=event["created_at"],
            )
            for event in events
        )
        return twin

    def list_twins(self) -> list[ProductDigitalTwin]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT product_id FROM product_digital_twins ORDER BY product_id"
            ).fetchall()
        return [twin for row in rows if (twin := self.load(row["product_id"])) is not None]
