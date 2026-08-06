import asyncio
import json
import logging
from typing import AsyncGenerator, List, Dict, Any, Optional

from app.engine.llm.openai_llm import OpenAILLEngine
from app.engine.llm.gemini_llm import GeminiLLEngine
from app.config import settings

logger = logging.getLogger(__name__)

class LLMStreamService:
    """Configurable Multi-Model LLM Stream Service (GPT / Gemini)."""

    def __init__(self, provider: str = "openai", model_name: str = "gpt-4o"):
        self.provider = provider
        self.model_name = model_name
        
        if provider == "gemini":
            self.engine = GeminiLLEngine(model_name=model_name)
        else:
            self.engine = OpenAILLEngine(model_name=model_name)

    async def stream_ai_response(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        system_prompt: Optional[str] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Streams LLM response items:
          {"type": "content", "delta": "word"}
          {"type": "tool_call", "name": "search_hotels", "args": {...}, "id": "call_1"}
        """
        async for chunk in self.engine.generate_stream(messages, tools=tools, system_prompt=system_prompt):
            yield chunk
