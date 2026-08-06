from abc import ABC, abstractmethod
from typing import AsyncGenerator, Callable, Optional, Dict, Any

class BaseSTTEngine(ABC):
    """Abstract Base Class for Speech-to-Text Engines."""

    def __init__(self, sample_rate: int = 16000, language: str = "en-US"):
        self.sample_rate = sample_rate
        self.language = language

    @abstractmethod
    async def process_audio_chunk(
        self, 
        audio_bytes: bytes, 
        on_transcript_callback: Callable[[str, bool], None]
    ) -> None:
        """
        Process an incoming raw audio chunk.
        Calls on_transcript_callback(text, is_final) whenever a partial or final transcript is ready.
        """
        pass

    @abstractmethod
    async def finish_stream() -> str:
        """Flushes remaining audio buffers and returns final transcription text."""
        pass

    @abstractmethod
    async def reset() -> None:
        """Resets stream buffer for new speech turn."""
        pass
