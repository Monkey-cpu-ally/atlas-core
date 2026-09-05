"""Regression coverage for the local OpenAI TTS compatibility adapter."""

import pytest

from emergentintegrations.llm.openai import OpenAITextToSpeech


@pytest.mark.asyncio
async def test_tts_adapter_avoids_external_calls_in_test_mode(monkeypatch):
    monkeypatch.setenv("ATLAS_TEST_MODE", "1")
    client = OpenAITextToSpeech(api_key="test-key-not-used")
    audio = await client.generate_speech(text="ATLAS CI", voice="onyx")
    assert audio.startswith(b"ID3")
    assert len(audio) > 5000


def test_ai_services_imports_with_local_tts_adapter():
    from routes import ai_services

    assert ai_services.OpenAITextToSpeech is OpenAITextToSpeech
