from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Iterable, List


class SupplierStatus(str, Enum):
    CANDIDATE = "candidate"
    REVIEW = "review"
    APPROVED = "approved"
    SUSPENDED = "suspended"
    REJECTED = "rejected"


@dataclass
class Supplier:
    supplier_id: str
    name: str
    category: str
    country: str
    certifications: List[str] = field(default_factory=list)
    minimum_order_quantity: int = 0
    lead_time_days: int = 0
    quality_score: float = 0.0
    reliability_score: float = 0.0
    sustainability_score: float = 0.0
    status: SupplierStatus = SupplierStatus.CANDIDATE
    notes: str = ""

    def __post_init__(self) -> None:
        if self.minimum_order_quantity < 0 or self.lead_time_days < 0:
            raise ValueError("MOQ and lead time cannot be negative")
        for name, value in {
            "quality_score": self.quality_score,
            "reliability_score": self.reliability_score,
            "sustainability_score": self.sustainability_score,
        }.items():
            if not 0.0 <= value <= 100.0:
                raise ValueError(f"{name} must be between 0 and 100")

    @property
    def weighted_score(self) -> float:
        return round(
            self.quality_score * 0.45
            + self.reliability_score * 0.35
            + self.sustainability_score * 0.20,
            2,
        )


class SupplierRegistry:
    def __init__(self) -> None:
        self._suppliers: Dict[str, Supplier] = {}

    def add(self, supplier: Supplier) -> None:
        if supplier.supplier_id in self._suppliers:
            raise ValueError(f"Supplier already exists: {supplier.supplier_id}")
        self._suppliers[supplier.supplier_id] = supplier

    def get(self, supplier_id: str) -> Supplier:
        try:
            return self._suppliers[supplier_id]
        except KeyError as exc:
            raise KeyError(f"Unknown supplier: {supplier_id}") from exc

    def approve(self, supplier_id: str, minimum_score: float = 75.0) -> Supplier:
        supplier = self.get(supplier_id)
        if supplier.weighted_score < minimum_score:
            raise ValueError("Supplier score is below the approval threshold")
        supplier.status = SupplierStatus.APPROVED
        return supplier

    def list(self, status: SupplierStatus | None = None) -> List[Supplier]:
        suppliers: Iterable[Supplier] = self._suppliers.values()
        if status is not None:
            suppliers = (item for item in suppliers if item.status == status)
        return sorted(suppliers, key=lambda item: item.name.lower())
