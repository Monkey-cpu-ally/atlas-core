import json
from pathlib import Path

from creative_intelligence.creative_memory import CreativeMemory
from creative_intelligence.creative_memory_sqlite import SQLiteCreativeMemory
from creative_intelligence.media_analysis.config import MediaAnalysisSettings
from creative_intelligence.media_analysis.providers import VisionRequest
from creative_intelligence.media_analysis.runtime import HTTPJSONVisionTransport, build_memory


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self):
        return json.dumps(self.payload).encode("utf-8")


def test_http_json_transport_normalizes_analysis_response():
    captured = {}

    def opener(request, timeout):
        captured["authorization"] = request.headers.get("Authorization")
        captured["timeout"] = timeout
        return FakeResponse({"analysis": {"lighting": ["hard rim light"]}})

    transport = HTTPJSONVisionTransport(
        api_base="https://vision.example.test/analyze",
        model="atlas-vision",
        api_key="secret",
        opener=opener,
    )
    result = transport(
        VisionRequest(
            source_name="frame.jpg",
            mime_type="image/jpeg",
            data_url="data:image/jpeg;base64,ZmFrZQ==",
            instruction="analyze",
        )
    )

    assert result["lighting"] == ["hard rim light"]
    assert captured["authorization"] == "Bearer secret"
    assert captured["timeout"] == 60.0


def test_runtime_builds_requested_memory_backend(tmp_path: Path):
    memory_settings = MediaAnalysisSettings(creative_memory_backend="memory")
    assert isinstance(build_memory(memory_settings), CreativeMemory)

    sqlite_settings = MediaAnalysisSettings(
        creative_memory_backend="sqlite",
        creative_memory_path=str(tmp_path / "creative.sqlite3"),
    )
    assert isinstance(build_memory(sqlite_settings), SQLiteCreativeMemory)
