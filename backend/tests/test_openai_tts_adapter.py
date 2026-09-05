import pytest

from emergentintegrations.llm.openai import OpenAITextToSpeech


def test_tts_adapter_requires_key():
    client = OpenAITextToSpeech(api_key="")

    with pytest.raises(RuntimeError, match="missing API key"):
        import asyncio

        asyncio.run(client.generate_speech(text="hello"))


def test_tts_adapter_rejects_blank_text():
    client = OpenAITextToSpeech(api_key="test-key")

    with pytest.raises(ValueError, match="text is required"):
        import asyncio

        asyncio.run(client.generate_speech(text="   "))
