import asyncio
import logging
from typing import AsyncGenerator
import aiohttp

from app.engine.tts.base import BaseTTSEngine
from app.config import settings

logger = logging.getLogger(__name__)

class ElevenLabsTTSEngine(BaseTTSEngine):
    """ElevenLabs Real-Time Streaming Text-to-Speech Engine."""

    def __init__(
        self, 
        api_key: str = "", 
        voice_id: str = "21m00Tcm4TlvDq8ikWAM",  # Rachel
        speech_speed: float = 1.0,
        pitch: float = 1.0
    ):
        super().__init__(voice_id=voice_id, speech_speed=speech_speed, pitch=pitch)
        self.api_key = api_key or settings.ELEVENLABS_API_KEY

    async def generate_audio_stream(self, text_stream: AsyncGenerator[str, None]) -> AsyncGenerator[bytes, None]:
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{self.voice_id}/stream"
        headers = {
            "xi-api-key": self.api_key,
            "Content-Type": "application/json",
            "Accept": "audio/mpeg"
        }

        # Accumulate sentence fragments for natural TTS phrasing
        sentence_buffer = ""
        
        async for text_delta in text_stream:
            sentence_buffer += text_delta
            # Trigger audio chunk fetch on punctuation or buffer length
            if any(p in sentence_buffer for p in [".", "!", "?", "\n", ","]) or len(sentence_buffer) > 60:
                text_chunk = sentence_buffer.strip()
                sentence_buffer = ""
                if not text_chunk:
                    continue

                payload = {
                    "text": text_chunk,
                    "model_id": "eleven_monolingual_v1",
                    "voice_settings": {
                        "stability": 0.5,
                        "similarity_boost": 0.75
                    }
                }
                
                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.post(url, headers=headers, json=payload) as resp:
                            if resp.status == 200:
                                async for audio_chunk in resp.content.iter_chunked(1024):
                                    yield audio_chunk
                except Exception as e:
                    logger.error(f"ElevenLabs TTS Error: {e}")
                    yield b"\x00" * 1024

        # Flush any remaining text in buffer
        if sentence_buffer.strip():
            payload = {
                "text": sentence_buffer.strip(),
                "model_id": "eleven_monolingual_v1"
            }
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(url, headers=headers, json=payload) as resp:
                        if resp.status == 200:
                            async for audio_chunk in resp.content.iter_chunked(1024):
                                yield audio_chunk
            except Exception as e:
                logger.error(f"ElevenLabs TTS Flush Error: {e}")
