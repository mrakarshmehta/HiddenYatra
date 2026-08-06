import logging
from typing import AsyncGenerator

try:
    from openai import AsyncOpenAI
except ImportError:
    AsyncOpenAI = None

from app.engine.tts.base import BaseTTSEngine
from app.config import settings

logger = logging.getLogger(__name__)

class OpenAITTSEngine(BaseTTSEngine):
    """OpenAI TTS (tts-1 / tts-1-hd) Streaming Engine."""

    def __init__(
        self, 
        api_key: str = "", 
        voice_id: str = "alloy",  # alloy, echo, fable, onyx, nova, shimmer
        speech_speed: float = 1.0,
        pitch: float = 1.0
    ):
        super().__init__(voice_id=voice_id, speech_speed=speech_speed, pitch=pitch)
        self.client = AsyncOpenAI(api_key=api_key or settings.OPENAI_API_KEY)

    async def generate_audio_stream(self, text_stream: AsyncGenerator[str, None]) -> AsyncGenerator[bytes, None]:
        full_text = ""
        async for chunk in text_stream:
            full_text += chunk
            if len(full_text) >= 40 and any(p in full_text for p in [".", "!", "?", "\n"]):
                sentence = full_text
                full_text = ""
                try:
                    response = await self.client.audio.speech.create(
                        model="tts-1",
                        voice=self.voice_id,
                        input=sentence,
                        speed=self.speech_speed
                    )
                    async for audio_chunk in response.iter_bytes(chunk_size=1024):
                        yield audio_chunk
                except Exception as e:
                    logger.error(f"OpenAI TTS Error: {e}")

        if full_text.strip():
            try:
                response = await self.client.audio.speech.create(
                    model="tts-1",
                    voice=self.voice_id,
                    input=full_text.strip(),
                    speed=self.speech_speed
                )
                async for audio_chunk in response.iter_bytes(chunk_size=1024):
                    yield audio_chunk
            except Exception as e:
                logger.error(f"OpenAI TTS Flush Error: {e}")
