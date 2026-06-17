"""
Weaver parts library — Phase 6.

A MongoDB-backed library of reusable parts (components, materials,
fasteners, electronics, sensors, actuators, tools, consumables). The
library powers two things in the Weaver pipeline:

  1. Matching a blueprint's free-text part references to known library
     entries → confident BOM lines with cost and lead-time.
  2. Surfacing "missing parts" — names in the blueprint that don't match
     anything in the library go straight into FailurePrediction.

The library is seeded at first call with a small starter set so the
architect always has something to plan against. Add more via
POST /api/weaver/parts.
"""
import logging
import os
import re
from typing import Any, Dict, List, Optional

from motor.motor_asyncio import AsyncIOMotorClient

from models.weaver_models import Part, PartCategory

logger = logging.getLogger("atlas.parts_db")

MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.environ.get("DB_NAME", "test_database")
_client: Optional[AsyncIOMotorClient] = None


def _db():
    global _client
    if _client is None:
        _client = AsyncIOMotorClient(MONGO_URL)
    return _client[DB_NAME]


def _col():
    return _db()["weaver_parts"]


# --- Starter library --------------------------------------------------------
_STARTER_PARTS: List[Dict[str, Any]] = [
    # Materials
    {"name": "PLA filament 1.75mm", "category": "material",  "material": "PLA",  "unit": "kg", "default_cost": 22.0, "default_lead_time_days": 3, "tags": ["3d-print"]},
    {"name": "PETG filament 1.75mm","category": "material",  "material": "PETG", "unit": "kg", "default_cost": 28.0, "default_lead_time_days": 3, "tags": ["3d-print"]},
    {"name": "Aluminium 6061 sheet 2mm","category": "material","material": "Al-6061","unit": "m2", "default_cost": 65.0, "default_lead_time_days": 7, "tags": ["machining","laser-cut"]},
    {"name": "CFRP plate 1mm",       "category": "material",  "material": "CFRP", "unit": "m2", "default_cost": 180.0,"default_lead_time_days": 14,"tags": ["lightweight"]},
    {"name": "Solder 60/40",         "category": "consumable","material": "SnPb", "unit": "roll", "default_cost": 14.0,"default_lead_time_days": 2, "tags": ["electronics"]},
    # Fasteners
    {"name": "M3 cap screw 10mm",    "category": "fastener",  "unit": "unit", "default_cost": 0.08, "default_lead_time_days": 2, "tags": ["m3","steel"]},
    {"name": "M3 hex nut",           "category": "fastener",  "unit": "unit", "default_cost": 0.04, "default_lead_time_days": 2, "tags": ["m3","steel"]},
    {"name": "M5 cap screw 16mm",    "category": "fastener",  "unit": "unit", "default_cost": 0.14, "default_lead_time_days": 2, "tags": ["m5","steel"]},
    # Electronics
    {"name": "ATmega328P MCU",       "category": "electronic","unit": "unit", "default_cost": 3.20, "default_lead_time_days": 5, "tags": ["mcu","8bit"]},
    {"name": "ESP32-S3 module",      "category": "electronic","unit": "unit", "default_cost": 6.50, "default_lead_time_days": 5, "tags": ["mcu","wifi","ble"]},
    {"name": "STM32F4 dev board",    "category": "electronic","unit": "unit", "default_cost": 18.0, "default_lead_time_days": 7, "tags": ["mcu","32bit"]},
    {"name": "Buck converter 5V 3A", "category": "electronic","unit": "unit", "default_cost": 4.50, "default_lead_time_days": 5, "tags": ["power"]},
    {"name": "LiPo 1S 850 mAh",      "category": "electronic","unit": "unit", "default_cost": 9.00, "default_lead_time_days": 4, "tags": ["battery"]},
    # Sensors
    {"name": "MPU6050 IMU",          "category": "sensor",    "unit": "unit", "default_cost": 2.10, "default_lead_time_days": 4, "tags": ["imu","i2c"]},
    {"name": "BME280 env sensor",    "category": "sensor",    "unit": "unit", "default_cost": 3.20, "default_lead_time_days": 4, "tags": ["pressure","humidity","i2c"]},
    {"name": "VL53L1X ToF",          "category": "sensor",    "unit": "unit", "default_cost": 5.10, "default_lead_time_days": 5, "tags": ["distance","i2c"]},
    {"name": "OV2640 camera",        "category": "sensor",    "unit": "unit", "default_cost": 7.40, "default_lead_time_days": 6, "tags": ["camera"]},
    # Actuators
    {"name": "SG90 micro servo",     "category": "actuator",  "unit": "unit", "default_cost": 2.80, "default_lead_time_days": 4, "tags": ["servo"]},
    {"name": "MG996R servo",         "category": "actuator",  "unit": "unit", "default_cost": 5.90, "default_lead_time_days": 4, "tags": ["servo","metal-gear"]},
    {"name": "2204 brushless motor", "category": "actuator",  "unit": "unit", "default_cost": 12.0, "default_lead_time_days": 10,"tags": ["bldc","drone"]},
    {"name": "N20 micro gearmotor",  "category": "actuator",  "unit": "unit", "default_cost": 6.10, "default_lead_time_days": 5, "tags": ["dc","gearmotor"]},
    # Tools (required, not consumed)
    {"name": "Soldering iron",       "category": "tool",      "unit": "unit", "default_cost": 0.0,  "default_lead_time_days": 0, "tags": ["solder"]},
    {"name": "Hex key set M2-M6",    "category": "tool",      "unit": "unit", "default_cost": 0.0,  "default_lead_time_days": 0, "tags": ["assembly"]},
    {"name": "3D printer 200x200",   "category": "tool",      "unit": "unit", "default_cost": 0.0,  "default_lead_time_days": 0, "tags": ["fdm","manufacturing"]},
    {"name": "Multimeter",           "category": "tool",      "unit": "unit", "default_cost": 0.0,  "default_lead_time_days": 0, "tags": ["debug"]},
]


_SEEDED = False


async def ensure_seeded() -> int:
    """Insert the starter library on first call. Idempotent."""
    global _SEEDED
    if _SEEDED:
        return 0
    count = await _col().count_documents({})
    if count == 0:
        docs = []
        for spec in _STARTER_PARTS:
            p = Part(**spec)
            docs.append(p.model_dump())
        if docs:
            await _col().insert_many(docs)
            logger.info("parts_db seeded with %d starter parts", len(docs))
    _SEEDED = True
    return len(_STARTER_PARTS) if count == 0 else 0


# --- CRUD ------------------------------------------------------------------
async def add_part(p: Part) -> Dict[str, Any]:
    await ensure_seeded()
    doc = p.model_dump()
    await _col().insert_one(doc.copy())
    return _strip(doc)


async def list_parts(
    *, category: Optional[str] = None, q: Optional[str] = None, limit: int = 50,
) -> List[Dict[str, Any]]:
    await ensure_seeded()
    filt: Dict[str, Any] = {}
    if category:
        filt["category"] = category
    if q:
        filt["$or"] = [
            {"name": {"$regex": q, "$options": "i"}},
            {"tags": {"$in": [q.lower()]}},
            {"material": {"$regex": q, "$options": "i"}},
        ]
    cur = _col().find(filt, {"_id": 0}).limit(limit)
    return [d async for d in cur]


async def get_part(part_id: str) -> Optional[Dict[str, Any]]:
    return await _col().find_one({"id": part_id}, {"_id": 0})


async def delete_part(part_id: str) -> bool:
    res = await _col().delete_one({"id": part_id})
    return res.deleted_count > 0


# --- Matching --------------------------------------------------------------
async def match_part(name: str) -> Optional[Dict[str, Any]]:
    """Best-effort case-insensitive substring match. Returns the highest-
    confidence library row, or None if nothing crosses the threshold."""
    await ensure_seeded()
    needle = (name or "").strip().lower()
    if len(needle) < 2:
        return None
    # Token-overlap scoring across name + tags + material.
    candidates: List[Dict[str, Any]] = await list_parts(limit=500)
    best, best_score = None, 0.0
    needle_tokens = set(_tokenise(needle))
    for c in candidates:
        haystack_tokens = set(_tokenise(c["name"]))
        haystack_tokens |= set(t.lower() for t in c.get("tags", []))
        if c.get("material"):
            haystack_tokens |= set(_tokenise(c["material"]))
        if not haystack_tokens:
            continue
        overlap = len(needle_tokens & haystack_tokens)
        score = overlap / max(len(needle_tokens), 1)
        # Bonus when the full needle name is contained in the haystack
        if needle in c["name"].lower():
            score += 0.5
        if score > best_score:
            best_score = score
            best = dict(c, _match_confidence=min(1.0, score))
    if best and best_score >= 0.5:
        return best
    return None


_TOKEN_RE = re.compile(r"[a-z0-9]+")


def _tokenise(text: str) -> List[str]:
    return [t for t in _TOKEN_RE.findall((text or "").lower()) if len(t) >= 2]


def _strip(doc: Dict[str, Any]) -> Dict[str, Any]:
    return {k: v for k, v in doc.items() if k != "_id"}
