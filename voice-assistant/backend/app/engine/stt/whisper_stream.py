import asyncio
import io
import wave
import logging
from typing import Callable, Optional

try:
    from openai import AsyncOpenAI
except ImportError:
    AsyncOpenAI = None

from app.config import settings

logger = logging.getLogger(__name__)

class WhisperStreamingSTT:
    """Whisper Streaming STT Service with real-time partial & final transcription emission."""

    def __init__(self, api_key: str = "", sample_rate: int = 16000, language: str = "en"):
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.sample_rate = sample_rate
        self.language = language
        self.client = AsyncOpenAI(api_key=self.api_key) if (AsyncOpenAI and self.api_key) else None
        self.audio_buffer = bytearray()
        self.last_transcript = ""

    async def add_audio_chunk(
        self, 
        audio_chunk: bytes, 
        on_partial: Callable[[str], None]
    ):
        """Buffers audio chunk and emits partial transcripts when buffer reaches threshold."""
        self.audio_buffer.extend(audio_chunk)

        # Trigger partial STT transcription when buffer exceeds ~400ms frame
        if len(self.audio_buffer) >= self.sample_rate * 2 * 0.4:
            text = await self._transcribe_buffer(bytes(self.audio_buffer))
            if text and text != self.last_transcript:
                self.last_transcript = text
                if callable(on_partial):
                    import inspect
                    if inspect.iscoroutinefunction(on_partial):
                        await on_partial(text)
                    else:
                        on_partial(text)

    async def finalize(self) -> str:
        """Flushes audio buffer and returns final complete transcript."""
        if not self.audio_buffer:
            return ""
        final_text = await self._transcribe_buffer(bytes(self.audio_buffer))
        self.reset()
        return final_text

    async def _transcribe_buffer(self, pcm_bytes: bytes) -> str:
        if not self.client:
            return ""
        try:
            wav_io = io.BytesIO()
            with wave.open(wav_io, 'wb') as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)
                wav_file.setframerate(self.sample_rate)
                wav_file.writeframes(pcm_bytes)
            
            wav_io.seek(0)
            wav_io.name = "audio.wav"

            response = await self.client.audio.transcriptions.create(
                model="whisper-1",
                file=wav_io,
                language=self.language
            )
            return response.text.strip()
        except Exception as e:
            logger.error(f"Whisper streaming error: {e}")
            return ""

    def reset(self):
        self.audio_buffer.clear()
        self.last_transcript = ""
