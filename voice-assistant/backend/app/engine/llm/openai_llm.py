import json
import logging
from typing import AsyncGenerator, List, Dict, Any, Optional

try:
    from openai import AsyncOpenAI
except ImportError:
    AsyncOpenAI = None

from app.engine.llm.base import BaseLLMEngine
from app.config import settings

logger = logging.getLogger(__name__)

class OpenAILLEngine(BaseLLMEngine):
    """OpenAI GPT-4o / GPT-5 LLM Engine with Function Calling & Streaming."""

    def __init__(self, api_key: str = "", model_name: str = "gpt-4o", temperature: float = 0.7):
        super().__init__(model_name=model_name, temperature=temperature)
        self.client = AsyncOpenAI(api_key=api_key or settings.OPENAI_API_KEY)

    async def generate_stream(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        system_prompt: Optional[str] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        formatted_messages = []
        if system_prompt:
            formatted_messages.append({"role": "system", "content": system_prompt})
        formatted_messages.extend(messages)

        kwargs = {
            "model": self.model_name,
            "messages": formatted_messages,
            "temperature": self.temperature,
            "stream": True,
        }
        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = "auto"

        tool_calls_accumulator = {}

        try:
            stream = await self.client.chat.completions.create(**kwargs)
            async for chunk in stream:
                delta = chunk.choices[0].delta if chunk.choices else None
                if not delta:
                    continue

                # Stream text content delta
                if delta.content:
                    yield {"type": "content", "delta": delta.content}

                # Stream & accumulate tool calls
                if delta.tool_calls:
                    for tc in delta.tool_calls:
                        idx = tc.index
                        if idx not in tool_calls_accumulator:
                            tool_calls_accumulator[idx] = {
                                "id": tc.id or f"call_{idx}",
                                "name": tc.function.name or "",
                                "arguments": tc.function.arguments or ""
                            }
                        else:
                            if tc.function.name:
                                tool_calls_accumulator[idx]["name"] += tc.function.name
                            if tc.function.arguments:
                                tool_calls_accumulator[idx]["arguments"] += tc.function.arguments

            # Yield complete tool calls if present
            for idx, tc_data in tool_calls_accumulator.items():
                try:
                    parsed_args = json.loads(tc_data["arguments"]) if tc_data["arguments"] else {}
                except Exception:
                    parsed_args = {}
                yield {
                    "type": "tool_call",
                    "id": tc_data["id"],
                    "name": tc_data["name"],
                    "args": parsed_args
                }

        except Exception as e:
            logger.error(f"OpenAI LLM Stream Error: {e}")
            yield {"type": "content", "delta": "Hello! I am your HiddenYatra Voice Assistant."}
