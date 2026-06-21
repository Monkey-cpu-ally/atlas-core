"""NIR spectral models — Phase D4.

A `NIRSpectrum` captures a single near-infrared scan (700-2500 nm
typically). Wavelengths and intensities are stored as parallel arrays so
the database stays document-shaped (we do not assume column-store).

Analysis produces zero-or-more `MaterialMatch` records by comparing the
spectrum's normalised fingerprint against a `LibraryEntry` library
using cosine similarity.

The library is small + curated (≤ 200 entries) so the matcher is O(n)
linear scan — well below 50 ms on the backend pod.
"""
from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4

from pydantic import BaseModel, Field


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class NIRSource(str, Enum):
    HANDHELD          = "handheld"            # USB / Bluetooth device
    ESP32_NODE        = "esp32_node"          # via ATLAS robot stack
    LAB_INSTRUMENT    = "lab_instrument"      # benchtop FTIR / Si-photo
    SYNTHETIC         = "synthetic"           # generated for testing


class NIRSpectrum(BaseModel):
    """A single NIR scan, persisted as-is."""
    id: str = Field(default_factory=lambda: uuid4().hex)
    label: Optional[str] = None
    source: NIRSource = NIRSource.LAB_INSTRUMENT
    device_id: Optional[str] = None           # robot device id if from ESP32

    # Parallel arrays (must be same length)
    wavelengths_nm: List[float]
    intensities:    List[float]

    # Acquisition metadata
    integration_ms: Optional[float] = None
    temperature_c:  Optional[float] = None

    tags:    List[str] = Field(default_factory=list)
    captured_at: str = Field(default_factory=_now)


class MaterialMatch(BaseModel):
    """A single library hit for a scan."""
    library_id:   str
    library_name: str
    category:     str
    cosine_score: float                       # 0..1 — higher is better
    peaks_matched_count: int
    notes:        Optional[str] = None


class ScanResult(BaseModel):
    """Full analysis output for one spectrum."""
    id: str = Field(default_factory=lambda: uuid4().hex)
    spectrum_id: str
    captured_at: str

    detected_peaks_nm: List[float]
    peak_widths_nm:    List[float]
    baseline_intensity: float
    snr: Optional[float] = None

    top_matches: List[MaterialMatch]          # sorted by cosine_score desc
    best_match:  Optional[MaterialMatch] = None
    confidence:  float = 0.0                  # 0..1

    interpretation: str = ""                  # human-readable
    warnings: List[str] = Field(default_factory=list)


class LibraryEntry(BaseModel):
    """A canonical NIR fingerprint we match scans against."""
    id: str = Field(default_factory=lambda: uuid4().hex)
    name: str
    category: str                             # 'plastic' | 'agrichem' | 'metal' | 'biological' | 'organic_compound'
    # Characteristic peaks in nm. ScanResult.detected_peaks_nm is matched
    # against this with a ±tolerance.
    characteristic_peaks_nm: List[float]
    # Optional canonical full-spectrum fingerprint (same length as a scan,
    # already normalised). Used for cosine similarity. If None, we fall
    # back to peak-list overlap.
    fingerprint_intensities: Optional[List[float]] = None
    notes: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    created_at: str = Field(default_factory=_now)
