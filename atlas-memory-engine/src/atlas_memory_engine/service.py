"""Memory service for ATLAS."""

from __future__ import annotations

from dataclasses import dataclass, field

try:
    from atlas_core_runtime.service import HealthReport, ServiceStatus
except ImportError:
    HealthReport = object  # type: ignore
    ServiceStatus = None  # type: ignore

from .models import MemoryRecord, MemoryStatus, MemoryType
from .repository import MemoryRepository


@dataclass
class MemoryService:
    """Stores ATLAS memory records in memory and optionally persists them."""

    repository: MemoryRepository | None = None
    name: str = "atlas-memory-engine"
    version: str = "0.1.0"
    _records: dict[str, MemoryRecord] = field(default_factory=dict)
    _running: bool = False

    def start(self) -> None:
        self._running = True

    def stop(self) -> None:
        self._running = False

    def create_record(self, record: MemoryRecord) -> MemoryRecord:
        if record.memory_id in self._records:
            raise ValueError(f"Memory already exists: {record.memory_id}")
        self._records[record.memory_id] = record
        if self.repository is not None:
            self.repository.save(record)
        return record

    def get_record(self, memory_id: str) -> MemoryRecord:
        return self._records[memory_id]

    def list_records(
        self,
        memory_type: MemoryType | None = None,
        status: MemoryStatus | None = None,
    ) -> list[MemoryRecord]:
        records = list(self._records.values())
        if memory_type is not None:
            records = [record for record in records if record.memory_type == memory_type]
        if status is not None:
            records = [record for record in records if record.status == status]
        return records

    def archive_record(self, memory_id: str) -> MemoryRecord:
        record = self.get_record(memory_id)
        record.status = MemoryStatus.ARCHIVED
        self._records[memory_id] = record
        if self.repository is not None:
            self.repository.save(record)
        return record

    def persisted_records(self) -> list[dict[str, object]]:
        if self.repository is None:
            return []
        return self.repository.list_all()

    def health_check(self):
        if ServiceStatus is None:
            return {"service_name": self.name, "status": "healthy" if self._running else "offline"}
        persistence = "persistent" if self.repository is not None else "in-memory only"
        return HealthReport(
            service_name=self.name,
            status=ServiceStatus.HEALTHY if self._running else ServiceStatus.OFFLINE,
            message=f"{len(self._records)} memory records stored; mode={persistence}",
        )
