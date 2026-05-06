"""Atlas Core backend API regression tests."""
import io
import os
import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "https://youthful-archimedes-7.preview.emergentagent.com").rstrip("/")


@pytest.fixture(scope="module")
def client():
    s = requests.Session()
    return s


# ---------- Health ----------
def test_root(client):
    r = client.get(f"{BASE_URL}/api/")
    assert r.status_code == 200, r.text
    assert "message" in r.json()


# ---------- Knowledge ----------
def test_knowledge_subjects_list(client):
    r = client.get(f"{BASE_URL}/api/knowledge/subjects")
    assert r.status_code == 200, r.text
    data = r.json()
    assert "total" in data and "subjects" in data
    assert data["total"] > 0
    assert isinstance(data["subjects"], list)


def test_knowledge_teach_valid(client):
    # Use first subject returned to stay flexible
    subj_resp = client.get(f"{BASE_URL}/api/knowledge/subjects").json()
    first = subj_resp["subjects"][0]
    subject = first if isinstance(first, str) else first.get("subject") or first.get("name")
    payload = {"subject": subject, "topic": "introduction", "persona": "all"}
    r = client.post(f"{BASE_URL}/api/knowledge/teach", json=payload)
    # 200 or 404 (topic not found) acceptable; but never 500
    assert r.status_code in (200, 404), r.text
    if r.status_code == 200:
        d = r.json()
        assert d["subject"] and "teaching" in d


def test_knowledge_teach_unknown_subject(client):
    r = client.post(
        f"{BASE_URL}/api/knowledge/teach",
        json={"subject": "NotARealSubject_TEST", "topic": "zzz", "persona": "ajani"},
    )
    assert r.status_code in (404, 500)


# ---------- Files ----------
def test_files_list(client):
    r = client.get(f"{BASE_URL}/api/files/list")
    assert r.status_code == 200, r.text
    assert isinstance(r.json(), list)


def test_files_upload_then_list_and_delete(client):
    content = b"Atlas test file content\n"
    files = {"file": ("TEST_atlas.txt", io.BytesIO(content), "text/plain")}
    up = client.post(f"{BASE_URL}/api/files/upload", files=files)
    assert up.status_code == 200, up.text
    data = up.json()
    assert data["success"] is True
    file_id = data["file_id"]
    assert file_id

    # Verify it appears in list
    listing = client.get(f"{BASE_URL}/api/files/list").json()
    assert any(f.get("id") == file_id for f in listing)

    # Cleanup
    d = client.delete(f"{BASE_URL}/api/files/{file_id}")
    assert d.status_code == 200


def test_files_stats(client):
    r = client.get(f"{BASE_URL}/api/files/stats")
    assert r.status_code == 200
    data = r.json()
    assert "total_files" in data


# ---------- Chat ----------
def test_chat_invalid_persona(client):
    r = client.post(
        f"{BASE_URL}/api/chat/send",
        json={"persona": "not_real", "message": "hi"},
    )
    assert r.status_code == 400


def test_chat_send_ajani(client):
    """Real LLM call - may take several seconds."""
    r = client.post(
        f"{BASE_URL}/api/chat/send",
        json={"persona": "ajani", "message": "Say hello in 3 words."},
        timeout=60,
    )
    # 503 means LLM key missing; treat as skip
    if r.status_code == 503:
        pytest.skip("EMERGENT_LLM_KEY not configured")
    assert r.status_code == 200, r.text
    d = r.json()
    assert d["persona"] == "ajani"
    assert isinstance(d["response"], str) and len(d["response"]) > 0
    assert d["conversation_id"]


def test_chat_conversations_list(client):
    r = client.get(f"{BASE_URL}/api/chat/conversations")
    assert r.status_code == 200
    assert "conversations" in r.json()
