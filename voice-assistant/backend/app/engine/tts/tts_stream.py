import asyncio
import logging
from typing import AsyncGenerator

from app.engine.tts.elevenlabs_tts import ElevenLabsTTSEngine
from app.engine.tts.openai_tts import OpenAITTSEngine
from app.config import settings

logger = logging.getLogger(__name__)

class TTSStreamService:
    """Configurable TTS Stream Service (ElevenLabs / OpenAI TTS)."""

    def __init__(self, provider: str = "elevenlabs", voice_id: str = "21m00Tcm4TlvDq8ikWAM"):
        self.provider = provider
        self.voice_id = voice_id

        if provider == "openai":
            self.engine = OpenAITTSEngine(voice_id=voice_id)
        else:
            self.engine = ElevenLabsTTSEngine(voice_id=voice_id)

    async def stream_audio_from_text(self, text_stream: AsyncGenerator[str, None]) -> AsyncGenerator[bytes, None]:
        """Synthesizes and yields streaming audio bytes from async text stream."""
        async for audio_chunk in self.engine.generate_audio_stream(text_stream):
            yield audio_chunk
