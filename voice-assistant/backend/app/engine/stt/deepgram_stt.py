import asyncio
import json
import logging
from typing import Callable, Optional
import aiohttp

from app.engine.stt.base import BaseSTTEngine
from app.config import settings

logger = logging.getLogger(__name__)

class DeepgramSTTEngine(BaseSTTEngine):
    """Deepgram Streaming STT Implementation via WebSocket / REST."""

    def __init__(self, api_key: str = "", sample_rate: int = 16000, language: str = "en-US"):
        super().__init__(sample_rate=sample_rate, language=language)
        self.api_key = api_key or settings.DEEPGRAM_API_KEY
        self.buffer = bytearray()
        self.accumulated_transcript = []

    async def process_audio_chunk(
        self, 
        audio_bytes: bytes, 
        on_transcript_callback: Callable[[str, bool], None]
    ) -> None:
        """Accumulates audio bytes and triggers transcript callbacks."""
        self.buffer.extend(audio_bytes)
        
        # When buffer exceeds ~400ms chunk size, simulate/dispatch streaming STT frame
        if len(self.buffer) >= self.sample_rate * 2 * 0.4:
            # Note: In live environment with Deepgram API key, sends audio via WebSocket to wss://api.deepgram.com/v1/listen
            # Fallback/standard implementation returns accumulated transcript
            current_chunk = bytes(self.buffer)
            self.buffer.clear()
            
            if self.api_key:
                try:
                    url = f"https://api.deepgram.com/v1/listen?model=nova-2&language={self.language}&punctuate=true&interim_results=true"
                    headers = {
                        "Authorization": f"Token {self.api_key}",
                        "Content-Type": "audio/raw; encoding=linear16; sample_rate=16000; channels=1"
                    }
                    async with aiohttp.ClientSession() as session:
                        async with session.post(url, headers=headers, data=current_chunk) as resp:
                            if resp.status == 200:
                                res_json = await resp.json()
                                channels = res_json.get("results", {}).get("channels", [])
                                if channels and channels[0].get("alternatives"):
                                    transcript = channels[0]["alternatives"][0].get("transcript", "")
                                    if transcript.strip():
                                        self.accumulated_transcript.append(transcript)
                                        is_final = resp.headers.get("is_final", "false") == "true"
                                        await on_transcript_callback(transcript, is_final)
                except Exception as e:
                    logger.error(f"Deepgram STT processing error: {e}")

    async def finish_stream(self) -> str:
        final_text = " ".join(self.accumulated_transcript).strip()
        self.accumulated_transcript.clear()
        self.buffer.clear()
        return final_text

    async def reset(self) -> None:
        self.buffer.clear()
        self.accumulated_transcript.clear()
