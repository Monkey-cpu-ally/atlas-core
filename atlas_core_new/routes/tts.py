import os
import base64
from fastapi import APIRouter, Depends
from fastapi.responses import Response
from pydantic import BaseModel
from atlas_core_new.utils.error_handling import sanitize_error
from atlas_core_new.utils.rate_limiter import rate_limit_strict
from atlas_core_new.routes._shared import openai_client

router = APIRouter(tags=["tts"])

ELEVENLABS_VOICES = {
    "ajani": "lT0cY7s5qxD6j9GweKIr",
    "minerva": "jBpfuIE2acCO8z3wKNLl",
    "hermes": "iP95p4xoKVk53GoZ742B",
    "counsel": "lT0cY7s5qxD6j9GweKIr"
}

OPENAI_VOICES = {
    "ajani": "onyx",
    "minerva": "nova",
    "hermes": "echo",
    "counsel": "alloy"
}

ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY")
elevenlabs_client = None
print(f"ElevenLabs API key present: {bool(ELEVENLABS_API_KEY)}")
if ELEVENLABS_API_KEY:
    try:
        from elevenlabs.client import ElevenLabs
        elevenlabs_client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
        print("ElevenLabs client initialized successfully")
    except Exception as e:
        print(f"ElevenLabs setup failed: {e}")
else:
    print("No ElevenLabs API key found, will use OpenAI fallback")


class TTSRequest(BaseModel):
    text: str
    persona: str = "ajani"


@router.post("/tts", dependencies=[Depends(rate_limit_strict)])
def text_to_speech(req: TTSRequest):
    persona = req.persona.lower()

    if elevenlabs_client:
        try:
            voice_id = ELEVENLABS_VOICES.get(persona, ELEVENLABS_VOICES["ajani"])

            audio = elevenlabs_client.text_to_speech.convert(
                text=req.text,
                voice_id=voice_id,
                model_id="eleven_flash_v2_5",
                output_format="mp3_44100_128"
            )

            audio_bytes = b"".join(audio)

            return Response(
                content=audio_bytes,
                media_type="audio/mpeg",
                headers={"Content-Disposition": "inline; filename=speech.mp3"}
            )
        except Exception as e:
            print(f"ElevenLabs TTS error: {e}")

    if not openai_client:
        return {"error": "No TTS service configured"}

    voice = OPENAI_VOICES.get(persona, "alloy")

    try:
        response = openai_client.chat.completions.create(
            model="gpt-audio",
            modalities=["text", "audio"],
            audio={"voice": voice, "format": "mp3"},
            messages=[
                {"role": "system", "content": "You are an assistant that performs text-to-speech. Repeat the user's text exactly as given, with natural expression."},
                {"role": "user", "content": f"Read this aloud: {req.text}"},
            ],
        )

        audio_data = getattr(response.choices[0].message, "audio", None)
        if audio_data and hasattr(audio_data, "data"):
            audio_bytes = base64.b64decode(audio_data.data)
            return Response(
                content=audio_bytes,
                media_type="audio/mpeg",
                headers={"Content-Disposition": "inline; filename=speech.mp3"}
            )
        return {"error": "No audio generated"}
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": sanitize_error(e)}
