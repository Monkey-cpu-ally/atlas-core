from pathlib import Path

from creative_intelligence.media_analysis.providers import CallableVisionProvider


def test_callable_vision_provider_normalizes_response(tmp_path: Path):
    image = tmp_path / "frame.png"
    image.write_bytes(b"not-a-real-png-but-provider-does-not-decode-it")

    captured = {}

    def fake_live_model(request):
        captured["request"] = request
        return {
            "silhouette": "broad triangular mass",
            "color": ["muted base", "high-saturation accent"],
            "lighting": "hard rim light",
            "materials": ["painted metal", "fabric"],
        }

    provider = CallableVisionProvider(fake_live_model)
    result = provider.analyze_image(str(image))

    assert result["silhouette"] == ["broad triangular mass"]
    assert result["color"] == ["muted base", "high-saturation accent"]
    assert result["lighting"] == ["hard rim light"]
    assert result["shape_language"] == []
    assert captured["request"].data_url.startswith("data:image/png;base64,")
    assert "do not instruct imitation" in captured["request"].instruction
