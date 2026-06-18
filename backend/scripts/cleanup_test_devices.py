"""
Test-device cleanup — Phase 8 housekeeping.

Removes ephemeral robot devices created by pytest runs (their name carries
the `TEST-` / `FIX-` / `CLEAR-` / `HEALTHY-` / `MTLS-TEST-` / `ANOMALY-TEST-`
prefixes used by `/app/backend/tests/test_*.py`). Also wipes the orphan
twins they spawned + their telemetry + their command logs + their
autonomic-fire dedupe rows.

Architect-spec seed devices (POSEIDON-BUOY / AETHER-STATION / SOIL-WATCH)
are NEVER touched.

Usage:
    cd /app/backend && python -m scripts.cleanup_test_devices               # dry-run
    cd /app/backend && python -m scripts.cleanup_test_devices --commit      # actually delete
"""
from __future__ import annotations

import argparse
import asyncio
import os
import re
from typing import List

from motor.motor_asyncio import AsyncIOMotorClient

# Names that match these patterns are test ephemera. Add prefixes here as
# new test files land.
TEST_PREFIX_RE = re.compile(
    r"^(TEST-|FIX-DEV-|CLEAR-TEST-|HEALTHY-|MTLS-TEST-|ANOMALY-TEST-|FIX-DEV)",
    re.IGNORECASE,
)

# Real devices we must NEVER touch.
PROTECTED_NAMES = {"POSEIDON-BUOY", "AETHER-STATION", "SOIL-WATCH"}


async def main(commit: bool) -> None:
    client = AsyncIOMotorClient(os.environ["MONGO_URL"])
    db = client[os.environ["DB_NAME"]]

    devices = db["robot_devices"]
    telemetry = db["robot_telemetry"]
    commands = db["robot_commands"]
    twins = db["digital_twins"]
    fires = db["sentinel_autonomic_fires"]

    cursor = devices.find({}, {"_id": 0, "id": 1, "name": 1, "twin_id": 1})
    to_drop_devices: List[str] = []
    twin_candidates: List[str] = []
    # Twin IDs that ANY protected device references — we must never drop these
    protected_twin_ids: set[str] = set()
    keep = 0
    async for d in cursor:
        if d["name"] in PROTECTED_NAMES:
            keep += 1
            if d.get("twin_id"):
                protected_twin_ids.add(d["twin_id"])
            continue
        if TEST_PREFIX_RE.match(d["name"]):
            to_drop_devices.append(d["id"])
            if d.get("twin_id"):
                twin_candidates.append(d["twin_id"])
    # Only drop twins that NO protected device references.
    to_drop_twins = [t for t in twin_candidates if t not in protected_twin_ids]

    print(f"protected (kept):     {keep}")
    print(f"test devices to drop: {len(to_drop_devices)}")
    print(f"orphan twins to drop: {len(to_drop_twins)}")

    if not commit:
        print("\n(dry-run — pass --commit to actually delete)")
        client.close()
        return

    if to_drop_devices:
        r1 = await devices.delete_many({"id": {"$in": to_drop_devices}})
        r2 = await telemetry.delete_many({"device_id": {"$in": to_drop_devices}})
        r3 = await commands.delete_many({"device_id": {"$in": to_drop_devices}})
        r4 = await fires.delete_many({"device_id": {"$in": to_drop_devices}})
        print(f"deleted devices={r1.deleted_count} telemetry={r2.deleted_count} "
              f"commands={r3.deleted_count} autonomic_fires={r4.deleted_count}")
    if to_drop_twins:
        r5 = await twins.delete_many({"id": {"$in": to_drop_twins}})
        print(f"deleted twins={r5.deleted_count}")

    client.close()


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--commit", action="store_true",
                   help="Actually delete (otherwise just print what would happen).")
    args = p.parse_args()
    asyncio.run(main(args.commit))
