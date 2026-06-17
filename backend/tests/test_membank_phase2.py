"""Phase 2 Memory Bank exhaustive tests — covers /api/membank/* +
wiring writes from /api/intake/transcript, /api/council/deliberate,
/api/ai/blueprint/generate."""
import os
import time
import uuid
import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL")
if not BASE_URL:
    # frontend env is the source of truth in this repo
    with open("/app/frontend/.env") as fh:
        for line in fh:
            if line.startswith("REACT_APP_BACKEND_URL="):
                BASE_URL = line.split("=", 1)[1].strip()
                break
BASE_URL = BASE_URL.rstrip("/")
MB = f"{BASE_URL}/api/membank"

# tag used to identify rows created by this test run for cleanup
RUN = f"TESTRUN_{uuid.uuid4().hex[:8]}"


@pytest.fixture(scope="module")
def s():
    sess = requests.Session()
    sess.headers.update({"Content-Type": "application/json"})
    yield sess
    # best-effort cleanup of memories we created (by tag)
    try:
        r = sess.get(f"{MB}/list", params={"limit": 200, "include_decayed": True}, timeout=30)
        for item in r.json().get("items", []):
            if RUN in (item.get("tags") or []) or RUN in (item.get("content") or ""):
                sess.delete(f"{MB}/{item['id']}", timeout=15)
    except Exception:
        pass


# ============================================================
# 1. /store basics
# ============================================================
def test_store_basic_returns_meta_no_embedding(s):
    r = s.post(f"{MB}/store", json={"content": f"{RUN} basic store row", "tags": [RUN]})
    assert r.status_code == 200, r.text
    d = r.json()
    assert d["content"] == f"{RUN} basic store row"
    assert d["persona"] == "council"          # default persona
    assert d["category"] == "manual"          # default category
    assert d["permanent"] is False            # manual is decaying
    assert d["pinned"] is False
    assert d["freshness"] == 1.0
    assert "embed_meta" in d and isinstance(d["embed_meta"], dict)
    assert "embedding" not in d, "raw vector must NOT be echoed"
    assert "id" in d and isinstance(d["id"], str)


@pytest.mark.parametrize("cat", ["user", "project", "blueprint", "council"])
def test_store_permanent_category_auto_pins(s, cat):
    r = s.post(f"{MB}/store", json={"content": f"{RUN} permanent {cat}", "category": cat, "tags": [RUN]})
    assert r.status_code == 200, r.text
    d = r.json()
    assert d["category"] == cat
    assert d["permanent"] is True
    assert d["pinned"] is True


@pytest.mark.parametrize("cat", ["research", "temporary"])
def test_store_decay_category_not_pinned(s, cat):
    r = s.post(f"{MB}/store", json={"content": f"{RUN} decay {cat}", "category": cat, "tags": [RUN]})
    assert r.status_code == 200, r.text
    d = r.json()
    assert d["category"] == cat
    assert d["permanent"] is False
    assert d["pinned"] is False


def test_store_invalid_category_coerces_to_manual(s):
    r = s.post(f"{MB}/store", json={"content": f"{RUN} coerce row",
                                    "category": "invalid_category", "tags": [RUN]})
    assert r.status_code == 200, r.text
    assert r.json()["category"] == "manual"


def test_store_short_content_returns_400(s):
    # Pydantic min_length=3 → FastAPI returns 422 by default. The route also has its own
    # ValueError → 400 for content < 3 chars (after strip). Accept either as "rejection".
    r = s.post(f"{MB}/store", json={"content": "ab"})
    assert r.status_code in (400, 422), r.text


# ============================================================
# 2. /search
# ============================================================
def test_search_returns_sim_freshness_score(s):
    # seed a unique row, then search for its unique token
    token = f"unicornglyph{uuid.uuid4().hex[:6]}"
    s.post(f"{MB}/store", json={"content": f"{RUN} {token} alpha beta gamma", "tags": [RUN]})
    r = s.get(f"{MB}/search", params={"q": token, "top_k": 5})
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["q"] == token
    assert body["count"] >= 1
    top = body["results"][0]
    for k in ("sim", "freshness_now", "score"):
        assert k in top, f"{k} missing in search result"
    # score == 0.85*sim + 0.15*freshness, rounded to 4 dp
    expected = round(0.85 * top["sim"] + 0.15 * top["freshness_now"], 4)
    assert abs(top["score"] - expected) <= 0.0002, \
        f"score formula mismatch: got {top['score']} expected {expected}"


def test_search_filter_by_category_user(s):
    tok = f"catfilter{uuid.uuid4().hex[:6]}"
    s.post(f"{MB}/store", json={"content": f"{RUN} {tok} userrow", "category": "user", "tags": [RUN]})
    s.post(f"{MB}/store", json={"content": f"{RUN} {tok} researchrow", "category": "research", "tags": [RUN]})
    r = s.get(f"{MB}/search", params={"q": tok, "category": "user", "top_k": 20})
    assert r.status_code == 200
    items = r.json()["results"]
    assert items, "expected at least 1 user-category match"
    assert all(it["category"] == "user" for it in items)


def test_search_filter_by_persona(s):
    tok = f"personafilter{uuid.uuid4().hex[:6]}"
    s.post(f"{MB}/store", json={"content": f"{RUN} {tok} ajani note", "persona": "ajani", "tags": [RUN]})
    s.post(f"{MB}/store", json={"content": f"{RUN} {tok} minerva note", "persona": "minerva", "tags": [RUN]})
    r = s.get(f"{MB}/search", params={"q": tok, "persona": "ajani", "top_k": 20})
    assert r.status_code == 200
    items = r.json()["results"]
    assert items
    assert all(it["persona"] == "ajani" for it in items)


# ============================================================
# 3. /list
# ============================================================
def test_list_by_category(s):
    s.post(f"{MB}/store", json={"content": f"{RUN} council listing", "category": "council", "tags": [RUN]})
    r = s.get(f"{MB}/list", params={"category": "council", "limit": 10})
    assert r.status_code == 200
    body = r.json()
    assert body["count"] >= 1
    assert all(item["category"] == "council" for item in body["items"])


def test_list_include_decayed_default_hides_dead(s):
    # we can at least confirm the endpoint returns OK with the param
    r = s.get(f"{MB}/list", params={"include_decayed": False, "limit": 50})
    assert r.status_code == 200
    for it in r.json()["items"]:
        # freshness_now should be > MIN_FRESHNESS (0.05) for visible rows
        assert it.get("freshness_now", 1.0) > 0.05


# ============================================================
# 4. /reinforce + DELETE
# ============================================================
def test_reinforce_bumps_freshness_and_count(s):
    # create a decay row, then check reinforce delta
    cr = s.post(f"{MB}/store", json={"content": f"{RUN} reinforce target",
                                     "category": "research", "tags": [RUN]})
    rid = cr.json()["id"]
    initial_fresh = cr.json()["freshness"]
    initial_ts = cr.json()["last_referenced"]
    time.sleep(0.05)
    rr = s.post(f"{MB}/reinforce/{rid}")
    assert rr.status_code == 200, rr.text
    d = rr.json()
    assert d["reinforce_count"] == 1
    assert d["freshness"] >= initial_fresh  # capped at 1.0
    assert d["freshness"] <= 1.0
    assert d["last_referenced"] >= initial_ts


def test_reinforce_unknown_returns_404(s):
    r = s.post(f"{MB}/reinforce/does-not-exist-{uuid.uuid4().hex}")
    assert r.status_code == 404


def test_delete_returns_deleted_then_404(s):
    cr = s.post(f"{MB}/store", json={"content": f"{RUN} delete target", "tags": [RUN]})
    rid = cr.json()["id"]
    d = s.delete(f"{MB}/{rid}")
    assert d.status_code == 200
    assert d.json() == {"deleted": rid}
    d2 = s.delete(f"{MB}/{rid}")
    assert d2.status_code == 404


# ============================================================
# 5. /categories
# ============================================================
def test_categories_layout(s):
    r = s.get(f"{MB}/categories")
    assert r.status_code == 200
    d = r.json()
    assert d["permanent"] == ["blueprint", "council", "project", "user"]
    assert d["decaying"] == ["chat", "intake", "lesson", "manual", "research", "sandbox", "temporary"]
    assert d["all"] == sorted(set(d["permanent"]) | set(d["decaying"]))


# ============================================================
# 6. /user + /research shortcuts
# ============================================================
def test_user_shortcut_creates_permanent_pinned(s):
    r = s.post(f"{MB}/user", json={"content": f"{RUN} architect note: prefer brevity", "tags": [RUN]})
    assert r.status_code == 200, r.text
    d = r.json()
    assert d["category"] == "user"
    assert d["permanent"] is True
    assert d["pinned"] is True
    # GET /user lists it
    lst = s.get(f"{MB}/user", params={"limit": 200})
    assert lst.status_code == 200
    assert any(item["id"] == d["id"] for item in lst.json()["items"])
    assert RUN in (next(it for it in lst.json()["items"] if it["id"] == d["id"])["tags"])


def test_research_shortcut_is_non_permanent(s):
    r = s.post(f"{MB}/research", json={"content": f"{RUN} hermes finding xyz", "tags": [RUN]})
    assert r.status_code == 200
    d = r.json()
    assert d["category"] == "research"
    assert d["permanent"] is False
    assert d["pinned"] is False


# ============================================================
# 7. Graph triples
# ============================================================
def test_triple_upsert_increments_hits(s):
    a = f"NODE_A_{RUN}"
    b = f"NODE_B_{RUN}"
    body = {"from_node": a, "to_node": b, "relation": "requires"}
    r1 = s.post(f"{MB}/graph/triple", json=body)
    assert r1.status_code == 200, r1.text
    h1 = r1.json().get("hits", 1)
    r2 = s.post(f"{MB}/graph/triple", json=body)
    assert r2.status_code == 200
    h2 = r2.json().get("hits", 0)
    assert h2 == h1 + 1, f"hits should increment from {h1} to {h1+1}, got {h2}"


def test_graph_list_by_node(s):
    a = f"NODE_X_{RUN}"
    b = f"NODE_Y_{RUN}"
    s.post(f"{MB}/graph/triple", json={"from_node": a, "to_node": b, "relation": "links"})
    r = s.get(f"{MB}/graph/list", params={"node": a})
    assert r.status_code == 200
    items = r.json()["items"]
    assert items
    assert all((it["from_node"] == a or it["to_node"] == a) for it in items)


def test_graph_list_by_relation(s):
    rel = f"rel_{uuid.uuid4().hex[:6]}"
    s.post(f"{MB}/graph/triple", json={"from_node": f"P_{RUN}", "to_node": f"Q_{RUN}", "relation": rel})
    r = s.get(f"{MB}/graph/list", params={"relation": rel})
    assert r.status_code == 200
    items = r.json()["items"]
    assert items
    assert all(it["relation"] == rel.lower() for it in items)


def test_graph_around_bfs(s):
    root = f"ROOT_{RUN}"
    mid = f"MID_{RUN}"
    leaf = f"LEAF_{RUN}"
    s.post(f"{MB}/graph/triple", json={"from_node": root, "to_node": mid, "relation": "links"})
    s.post(f"{MB}/graph/triple", json={"from_node": mid, "to_node": leaf, "relation": "links"})
    r1 = s.get(f"{MB}/graph/around", params={"node": root, "depth": 1})
    assert r1.status_code == 200
    d1 = r1.json()
    assert d1["root"] == root and d1["depth"] == 1
    assert root in d1["nodes"] and mid in d1["nodes"]
    assert leaf not in d1["nodes"], "depth=1 must not include leaf"
    r2 = s.get(f"{MB}/graph/around", params={"node": root, "depth": 2})
    d2 = r2.json()
    assert leaf in d2["nodes"], "depth=2 must include leaf"
    assert "edges" in d2


# ============================================================
# 8. Embed settings
# ============================================================
def test_embed_settings_shape(s):
    r = s.get(f"{MB}/embed-settings")
    assert r.status_code == 200
    d = r.json()
    for p in ("ajani", "minerva", "hermes", "council", "default"):
        assert p in d["personas"]
        assert "provider" in d["personas"][p]
        assert "model" in d["personas"][p]
    assert set(d["providers_available"]) == {"hash", "ollama", "emergent"}
    assert "notes" in d


def test_embed_settings_update_valid_and_invalid(s):
    # valid update
    r = s.put(f"{MB}/embed-settings",
              json={"updates": {"hermes": {"provider": "hash", "model": "atlas-hash-v1"}}})
    assert r.status_code == 200, r.text
    assert r.json().get("updated", 0) >= 1
    # invalid provider — all bad → 400
    r2 = s.put(f"{MB}/embed-settings",
               json={"updates": {"hermes": {"provider": "bogus"}}})
    assert r2.status_code == 400


# ============================================================
# 9. WIRING: intake/transcript → lesson + project + intake
# ============================================================
def test_wiring_intake_transcript_writes_three(s):
    def count(cat):
        r = s.get(f"{MB}/list", params={"category": cat, "limit": 200, "include_decayed": True})
        return r.json()["count"] if r.status_code == 200 else 0

    before = {c: count(c) for c in ("lesson", "project", "intake")}
    transcript = (
        f"{RUN} This is a fabricated transcript for testing the persistence pipeline. "
        "It discusses elemental kinetics, energy flow, and resonance principles. "
        "Memory bank wiring should auto-store one lesson, one project, and one intake row."
    )
    r = s.post(f"{BASE_URL}/api/intake/transcript",
               json={"transcript": transcript, "topic": f"{RUN}-elemental-flow",
                     "persist": True}, timeout=120)
    assert r.status_code == 200, r.text
    # learning.persist_pipeline is async (gather) — give it a beat
    time.sleep(2.0)
    after = {c: count(c) for c in ("lesson", "project", "intake")}
    for cat in ("lesson", "project", "intake"):
        assert after[cat] >= before[cat] + 1, \
            f"{cat} count did not increase ({before[cat]} -> {after[cat]})"


# ============================================================
# 10. WIRING: council/deliberate → council memory
# ============================================================
def test_wiring_council_deliberate_writes_council_memory(s):
    def count_with(topic_marker):
        r = s.get(f"{MB}/list", params={"category": "council", "limit": 200, "include_decayed": True})
        if r.status_code != 200:
            return 0
        return sum(1 for it in r.json()["items"] if topic_marker in (it.get("content") or ""))

    topic = f"{RUN}-council-topic"
    before = count_with(topic)
    r = s.post(f"{BASE_URL}/api/council/deliberate",
               json={"topic": topic}, timeout=180)
    if r.status_code == 503:
        pytest.skip("LLM backend offline (EMERGENT_LLM_KEY missing)")
    assert r.status_code == 200, r.text
    time.sleep(1.5)
    after = count_with(topic)
    assert after >= before + 1, "expected a new council memory containing the topic"
    # Verify the stored memory body contains the persona voices joined
    rows = s.get(f"{MB}/list", params={"category": "council", "limit": 200,
                                       "include_decayed": True}).json()["items"]
    matching = [it for it in rows if topic in (it.get("content") or "")][0]
    blob = matching["content"]
    # should mention COUNCIL header + at least one persona tag
    assert "COUNCIL" in blob
    assert any(tag in blob for tag in ("[AJANI]", "[MINERVA]", "[HERMES]"))


# ============================================================
# 11. WIRING: ai/blueprint/generate → blueprint memory
# ============================================================
def test_wiring_blueprint_generate_writes_blueprint_memory(s):
    def get_count():
        r = s.get(f"{MB}/list", params={"category": "blueprint", "limit": 200, "include_decayed": True})
        return r.json()["count"] if r.status_code == 200 else 0

    concept = f"{RUN}-resonant-lattice-engine"
    before = get_count()
    r = s.post(f"{BASE_URL}/api/ai/blueprint/generate",
               json={"concept": concept, "domain": "elemental_kinetics"}, timeout=180)
    if r.status_code == 503:
        pytest.skip("LLM backend offline (EMERGENT_LLM_KEY missing)")
    assert r.status_code == 200, r.text
    time.sleep(1.5)
    after = get_count()
    assert after >= before + 1, "blueprint memory count did not increase"
    rows = s.get(f"{MB}/list", params={"category": "blueprint", "limit": 200,
                                       "include_decayed": True}).json()["items"]
    matching = [it for it in rows if concept in (it.get("content") or "")]
    assert matching, "no blueprint memory row contained the concept"
    assert matching[0]["permanent"] is True
