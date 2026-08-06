from abc import ABC, abstractmethod
from typing import AsyncGenerator

class BaseTTSEngine(ABC):
    """Abstract Base Class for Text-to-Speech Streaming Engines."""

    def __init__(self, voice_id: str, speech_speed: float = 1.0, pitch: float = 1.0):
        self.voice_id = voice_id
        self.speech_speed = speech_speed
        self.pitch = pitch

    @abstractmethod
    async def generate_audio_stream(self, text_stream: AsyncGenerator[str, None]) -> AsyncGenerator[bytes, None]:
        """
        Takes an async stream of text deltas from LLM and yields streaming audio bytes (MP3/PCM).
        """
        pass
