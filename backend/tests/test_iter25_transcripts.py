"""Iteration 25 — Knowledge Bank Transcripts + Summaries."""
import os
import time

import requests
from pymongo import MongoClient

BACKEND = os.environ.get("ATLAS_BACKEND_URL", "http://localhost:8001")
MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.environ.get("DB_NAME", "test_database")
TIMEOUT = 20.0


def _sample_payload(tag: str) -> dict:
    return {
        "title": f"iter25 sample · {tag}",
        "text": (
            "Solid-state batteries replace the liquid electrolyte in a "
            "conventional lithium-ion cell with a solid electrolyte. They offer "
            "higher energy density via a lithium-metal anode, better safety "
            "because solid electrolytes are non-flammable, and longer cycle "
            "life through mechanical resistance to dendrite formation. The main "
            "open challenges are interfacial impedance, manufacturing scale, and "
            "supply chain for sulfide/oxide electrolytes."
        ),
        "source": "lecture",
        "source_url": f"https://example.test/{tag}-{int(time.time())}",
        "agent": "minerva",
        "subject_slug": "energy_systems",
        "tags": ["battery", "iter25"],
    }


def test_transcript_store_persists_and_lists():
    r = requests.post(f"{BACKEND}/api/transcripts",
                      json=_sample_payload("store"), timeout=TIMEOUT)
    assert r.status_code == 200, r.text
    tid = r.json()["id"]
    assert r.json()["word_count"] > 20

    r2 = requests.get(f"{BACKEND}/api/transcripts", timeout=TIMEOUT)
    assert r2.status_code == 200
    ids = [t["id"] for t in r2.json()["items"]]
    assert tid in ids

    # cleanup
    MongoClient(MONGO_URL)[DB_NAME]["transcripts"].delete_one({"id": tid})


def test_transcript_store_idempotent_by_url():
    """Repeating the same source_url must upsert, not duplicate."""
    payload = _sample_payload("idem")
    r1 = requests.post(f"{BACKEND}/api/transcripts", json=payload, timeout=TIMEOUT)
    assert r1.status_code == 200
    id1 = r1.json()["id"]

    r2 = requests.post(f"{BACKEND}/api/transcripts", json=payload, timeout=TIMEOUT)
    assert r2.status_code == 200
    id2 = r2.json()["id"]

    assert id1 == id2, "same source_url must return same id"
    MongoClient(MONGO_URL)[DB_NAME]["transcripts"].delete_one({"id": id1})


def test_transcript_summary_real_llm():
    """Real Claude call — verify structured JSON output + linkage."""
    r = requests.post(f"{BACKEND}/api/transcripts",
                      json=_sample_payload("summ"), timeout=TIMEOUT)
    tid = r.json()["id"]
    try:
        r2 = requests.post(f"{BACKEND}/api/transcripts/{tid}/summarise",
                           timeout=120)
        assert r2.status_code == 200, r2.text
        d = r2.json()
        assert d["ok"] is True
        s = d["summary"]
        assert s["transcript_id"] == tid
        assert isinstance(s["one_line"], str) and 5 < len(s["one_line"]) <= 220
        assert 3 <= len(s["key_points"]) <= 8
        # identified_subjects must be whitelisted against the 22 taxonomy
        rt = requests.get(f"{BACKEND}/api/subjects", timeout=TIMEOUT).json()
        allow = {sub["slug"] for sub in rt["items"]}
        assert set(s["identified_subjects"]) <= allow, \
            f"model returned non-whitelisted slugs: {set(s['identified_subjects']) - allow}"
        assert s["knowledge_record_id"], "expected knowledge_record link"
        # verify KR row exists in DB
        db = MongoClient(MONGO_URL)[DB_NAME]
        kr = db["knowledge_records"].find_one({"id": s["knowledge_record_id"]})
        assert kr is not None
        assert "transcript" in (kr.get("tags") or [])

        # /summary endpoint returns the same thing
        r3 = requests.get(f"{BACKEND}/api/transcripts/{tid}/summary", timeout=TIMEOUT)
        assert r3.status_code == 200
        assert r3.json()["id"] == s["id"]

        # cleanup
        db["transcripts"].delete_one({"id": tid})
        db["transcript_summaries"].delete_one({"id": s["id"]})
        db["knowledge_records"].delete_one({"id": s["knowledge_record_id"]})
    except Exception:
        MongoClient(MONGO_URL)[DB_NAME]["transcripts"].delete_one({"id": tid})
        raise


def test_transcript_stats_shape():
    r = requests.get(f"{BACKEND}/api/transcripts/stats", timeout=TIMEOUT)
    assert r.status_code == 200
    d = r.json()
    for k in ("transcripts_total", "summaries_total", "unsummarised", "by_source"):
        assert k in d


def test_transcript_get_404_for_unknown():
    r = requests.get(f"{BACKEND}/api/transcripts/NOT_A_REAL_ID_XYZ", timeout=TIMEOUT)
    assert r.status_code == 404


def test_summarise_missing_transcript_400():
    r = requests.post(f"{BACKEND}/api/transcripts/NOT_A_REAL_ID/summarise",
                      timeout=TIMEOUT)
    assert r.status_code == 400
