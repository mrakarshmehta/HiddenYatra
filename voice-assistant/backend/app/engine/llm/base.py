from abc import ABC, abstractmethod
from typing import AsyncGenerator, List, Dict, Any, Optional

class BaseLLMEngine(ABC):
    """Abstract Base Class for Multi-Model LLM Engines with Tool Calling."""

    def __init__(self, model_name: str, temperature: float = 0.7):
        self.model_name = model_name
        self.temperature = temperature

    @abstractmethod
    async def generate_stream(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        system_prompt: Optional[str] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Generates streaming LLM tokens or tool calls.
        Yields dict objects:
          {"type": "content", "delta": "hello"}
          {"type": "tool_call", "name": "navigate_page", "args": {"url": "/profile"}, "id": "call_123"}
        """
        pass
