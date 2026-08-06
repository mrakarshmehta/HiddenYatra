import logging
import io
import wave
from typing import Callable

try:
    from openai import AsyncOpenAI
except ImportError:
    AsyncOpenAI = None

from app.engine.stt.base import BaseSTTEngine
from app.config import settings

logger = logging.getLogger(__name__)

class WhisperSTTEngine(BaseSTTEngine):
    """OpenAI Whisper STT Engine Implementation."""

    def __init__(self, api_key: str = "", sample_rate: int = 16000, language: str = "en"):
        super().__init__(sample_rate=sample_rate, language=language)
        self.client = AsyncOpenAI(api_key=api_key or settings.OPENAI_API_KEY)
        self.audio_buffer = bytearray()

    async def process_audio_chunk(
        self, 
        audio_bytes: bytes, 
        on_transcript_callback: Callable[[str, bool], None]
    ) -> None:
        self.audio_buffer.extend(audio_bytes)

    async def finish_stream(self) -> str:
        if not self.audio_buffer:
            return ""

        try:
            # Wrap raw PCM 16kHz mono audio into WAV format in-memory
            wav_io = io.BytesIO()
            with wave.open(wav_io, 'wb') as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)  # 16-bit
                wav_file.setframerate(self.sample_rate)
                wav_file.writeframes(bytes(self.audio_buffer))
            
            wav_io.seek(0)
            wav_io.name = "speech.wav"

            response = await self.client.audio.transcriptions.create(
                model="whisper-1",
                file=wav_io,
                language=self.language.split("-")[0]
            )

            transcript = response.text.strip()
            self.audio_buffer.clear()
            return transcript
        except Exception as e:
            logger.error(f"Whisper STT Error: {e}")
            self.audio_buffer.clear()
            return ""

    async def reset(self) -> None:
        self.audio_buffer.clear()
