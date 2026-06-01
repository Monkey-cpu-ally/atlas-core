"""Backend tests for /api/sandbox/* endpoints (iteration 9)."""
import os
import time
import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "https://youthful-archimedes-7.preview.emergentagent.com").rstrip("/")
API = f"{BASE_URL}/api/sandbox"


@pytest.fixture(scope="module")
def s():
    sess = requests.Session()
    sess.headers.update({"Content-Type": "application/json"})
    return sess


# ----- Mastery curve runs ---------------------------------------------------
class TestRuns:
    LAB = f"TEST_pytest_{int(time.time())}"  # unique lab_key so we don't collide with real data

    def test_record_run_above_threshold(self, s):
        payload = {"lab_key": self.LAB, "values": {"sunlight": 80}, "score": 80, "output": 55.0, "stability": 78.0, "failure": False}
        r = s.post(f"{API}/runs", json=payload, timeout=15)
        assert r.status_code == 200, r.text
        d = r.json()
        assert d["recorded"] is True
        assert d["kept_today"] >= 1
        assert "day" in d

    def test_record_run_below_threshold(self, s):
        payload = {"lab_key": self.LAB, "values": {"sunlight": 10}, "score": 20, "failure": False}
        r = s.post(f"{API}/runs", json=payload, timeout=15)
        assert r.status_code == 200
        assert r.json()["recorded"] is False

    def test_top3_cap_keeps_top_scores(self, s):
        lab = f"TEST_top3_{int(time.time())}"
        # Submit 5 runs scores 50,60,70,80,90
        for sc in [50, 60, 70, 80, 90]:
            r = s.post(f"{API}/runs", json={"lab_key": lab, "values": {"x": sc}, "score": sc}, timeout=15)
            assert r.status_code == 200, r.text
            assert r.json()["recorded"] is True
        # Read back
        r = s.get(f"{API}/runs/{lab}", timeout=15)
        assert r.status_code == 200
        d = r.json()
        # Filter to today's runs
        today_scores = [run["score"] for run in d["runs"] if run.get("day")]
        assert len(today_scores) <= 3, f"Expected ≤3 runs today, got {today_scores}"
        # Sort to compare top-3
        assert sorted(today_scores) == [70, 80, 90], f"Expected top-3 [70,80,90], got {sorted(today_scores)}"

    def test_runs_returned_chronological_ascending(self, s):
        lab = f"TEST_chrono_{int(time.time())}"
        for sc in [50, 70, 90]:
            s.post(f"{API}/runs", json={"lab_key": lab, "values": {"x": sc}, "score": sc}, timeout=15)
            time.sleep(0.05)
        r = s.get(f"{API}/runs/{lab}?limit=10", timeout=15)
        assert r.status_code == 200
        runs = r.json()["runs"]
        timestamps = [run["created_at"] for run in runs]
        assert timestamps == sorted(timestamps), f"Runs not chronologically ascending: {timestamps}"

    def test_runs_limit_honoured(self, s):
        r = s.get(f"{API}/runs/{self.LAB}?limit=1", timeout=15)
        assert r.status_code == 200
        assert len(r.json()["runs"]) <= 1


# ----- Saved configs --------------------------------------------------------
class TestSaved:
    @pytest.fixture(autouse=True)
    def _state(self):
        TestSaved.lab = f"TEST_saved_{int(time.time())}"
        TestSaved.created_ids = []

    def test_save_config_and_no_id_leak(self, s):
        payload = {"name": "TEST_My Best Solar", "lab_key": self.lab, "values": {"sunlight": 80, "angle": 35, "temperature": 78, "battery": 12}}
        r = s.post(f"{API}/saved", json=payload, timeout=15)
        assert r.status_code == 200, r.text
        d = r.json()
        assert "id" in d and isinstance(d["id"], str)
        assert "_id" not in d
        assert d["name"] == "TEST_My Best Solar"
        assert d["values"]["sunlight"] == 80
        TestSaved.created_ids.append(d["id"])

    def test_list_saved_no_id_leak(self, s):
        # create one first
        payload = {"name": "TEST_ListA", "lab_key": self.lab, "values": {"a": 1}}
        rc = s.post(f"{API}/saved", json=payload, timeout=15)
        assert rc.status_code == 200
        TestSaved.created_ids.append(rc.json()["id"])

        r = s.get(f"{API}/saved/{self.lab}", timeout=15)
        assert r.status_code == 200
        d = r.json()
        assert d["lab_key"] == self.lab
        assert any(c["name"] == "TEST_ListA" for c in d["configs"])
        for c in d["configs"]:
            assert "_id" not in c
            assert "id" in c

    def test_delete_saved_then_404(self, s):
        rc = s.post(f"{API}/saved", json={"name": "TEST_DeleteMe", "lab_key": self.lab, "values": {"a": 1}}, timeout=15)
        cid = rc.json()["id"]
        rd = s.delete(f"{API}/saved/{cid}", timeout=15)
        assert rd.status_code == 200
        assert rd.json() == {"deleted": cid}
        # Delete non-existent
        r404 = s.delete(f"{API}/saved/does-not-exist-{int(time.time())}", timeout=15)
        assert r404.status_code == 404

    def test_cleanup(self, s):
        # Best-effort delete of remaining TEST configs
        for cid in TestSaved.created_ids:
            s.delete(f"{API}/saved/{cid}", timeout=10)


# ----- AI Suggest -----------------------------------------------------------
class TestSuggest:
    def _power_payload(self, persona="ajani"):
        return {
            "lab_key": "power",
            "title": "Solar Power Lab",
            "persona": persona,
            "controls": [
                {"key": "sunlight", "label": "Sunlight", "min": 0, "max": 100, "unit": "%", "default": 50, "current": 30},
                {"key": "angle", "label": "Angle", "min": 0, "max": 90, "unit": "°", "default": 30, "current": 10},
                {"key": "temperature", "label": "Cell Temp", "min": 20, "max": 120, "unit": "°C", "default": 40, "current": 105},
                {"key": "battery", "label": "Battery", "min": 1, "max": 24, "unit": "h", "default": 8, "current": 3},
            ],
            "metrics": {"score": 18, "output": 15.0, "stability": 22.0, "failure": True},
            "failure_modes": ["temperature > 95°C melts the array", "battery < 5h cannot cover overnight load"],
            "mission": "Power a small Lagos clinic for 24h.",
        }

    def test_suggest_valid_power_failing(self, s):
        r = s.post(f"{API}/suggest", json=self._power_payload("ajani"), timeout=45)
        assert r.status_code == 200, r.text
        d = r.json()
        assert d["persona"] == "ajani"
        assert d["model"] == "claude-sonnet-4-5-20250929"
        assert d["control"] in {"sunlight", "angle", "temperature", "battery"}
        # within range
        ranges = {"sunlight": (0, 100), "angle": (0, 90), "temperature": (20, 120), "battery": (1, 24)}
        lo, hi = ranges[d["control"]]
        assert lo <= d["value"] <= hi
        assert isinstance(d["reason"], str) and len(d["reason"]) > 0

    def test_suggest_invalid_persona_falls_back(self, s):
        r = s.post(f"{API}/suggest", json=self._power_payload("foo_invalid"), timeout=45)
        assert r.status_code == 200, r.text
        d = r.json()
        # persona echoed as lowercased input, fallback is internal
        assert d["control"] in {"sunlight", "angle", "temperature", "battery"}

    def test_suggest_missing_controls_returns_422(self, s):
        bad = {"lab_key": "power", "title": "x", "persona": "ajani",
               "metrics": {"score": 50}, "failure_modes": []}
        r = s.post(f"{API}/suggest", json=bad, timeout=15)
        assert r.status_code == 422, r.text
