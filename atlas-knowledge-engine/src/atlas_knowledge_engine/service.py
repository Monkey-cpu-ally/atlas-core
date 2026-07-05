"""In-memory knowledge service for ATLAS."""

from __future__ import annotations

from dataclasses import dataclass, field

try:
    from atlas_core_runtime.service import HealthReport, ServiceStatus
except ImportError:
    HealthReport = object  # type: ignore
    ServiceStatus = None  # type: ignore

from .models import EvidenceRating, KnowledgeEntry, KnowledgeStatus, SourcePassport


@dataclass
class KnowledgeService:
    """Stores source passports and knowledge entries in memory."""

    name: str = "atlas-knowledge-engine"
    version: str = "0.1.0"
    _sources: dict[str, SourcePassport] = field(default_factory=dict)
    _entries: dict[str, KnowledgeEntry] = field(default_factory=dict)
    _running: bool = False

    def start(self) -> None:
        self._running = True

    def stop(self) -> None:
        self._running = False

    def add_source(self, source: SourcePassport) -> SourcePassport:
        if source.source_id in self._sources:
            raise ValueError(f"Source already exists: {source.source_id}")
        self._sources[source.source_id] = source
        return source

    def get_source(self, source_id: str) -> SourcePassport:
        return self._sources[source_id]

    def list_sources(self, evidence_rating: EvidenceRating | None = None) -> list[SourcePassport]:
        sources = list(self._sources.values())
        if evidence_rating is not None:
            sources = [source for source in sources if source.evidence_rating == evidence_rating]
        return sources

    def add_entry(self, entry: KnowledgeEntry) -> KnowledgeEntry:
        if entry.entry_id in self._entries:
            raise ValueError(f"Knowledge entry already exists: {entry.entry_id}")
        self._entries[entry.entry_id] = entry
        return entry

    def get_entry(self, entry_id: str) -> KnowledgeEntry:
        return self._entries[entry_id]

    def list_entries(self, status: KnowledgeStatus | None = None) -> list[KnowledgeEntry]:
        entries = list(self._entries.values())
        if status is not None:
            entries = [entry for entry in entries if entry.status == status]
        return entries

    def health_check(self):
        if ServiceStatus is None:
            return {"service_name": self.name, "status": "healthy" if self._running else "offline"}
        return HealthReport(
            service_name=self.name,
            status=ServiceStatus.HEALTHY if self._running else ServiceStatus.OFFLINE,
            message=f"{len(self._sources)} sources and {len(self._entries)} entries stored in memory",
        )
