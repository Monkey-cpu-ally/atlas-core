"""
atlas_core/core/ui/voice_input.py

Voice input transcription.
"""

from fastapi import UploadFile


async def transcribe_stub(audio: UploadFile) -> str:
    return f"(voice transcript stub) audio='{audio.filename}'"
