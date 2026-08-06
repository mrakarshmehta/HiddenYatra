import json
import logging
from typing import AsyncGenerator, List, Dict, Any, Optional
import aiohttp

from app.engine.llm.base import BaseLLMEngine
from app.config import settings

logger = logging.getLogger(__name__)

class GeminiLLEngine(BaseLLMEngine):
    """Google Gemini 2.5 Streaming LLM Engine."""

    def __init__(self, api_key: str = "", model_name: str = "gemini-2.5-flash", temperature: float = 0.7):
        super().__init__(model_name=model_name, temperature=temperature)
        self.api_key = api_key or settings.GEMINI_API_KEY

    async def generate_stream(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        system_prompt: Optional[str] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:streamGenerateContent?key={self.api_key}&alt=sse"
        
        contents = []
        for msg in messages:
            role = "user" if msg["role"] == "user" else "model"
            contents.append({
                "role": role,
                "parts": [{"text": msg.get("content", "")}]
            })

        payload = {
            "contents": contents,
            "generationConfig": {"temperature": self.temperature}
        }
        if system_prompt:
            payload["systemInstruction"] = {"parts": [{"text": system_prompt}]}

        try:
            headers = {"Content-Type": "application/json"}
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=payload) as resp:
                    async for line in resp.content:
                        line_str = line.decode('utf-8').strip()
                        if line_str.startswith("data: "):
                            data_json = line_str[6:]
                            if data_json == "[DONE]":
                                break
                            try:
                                chunk = json.loads(data_json)
                                candidates = chunk.get("candidates", [])
                                if candidates and "content" in candidates[0]:
                                    parts = candidates[0]["content"].get("parts", [])
                                    for part in parts:
                                        if "text" in part:
                                            yield {"type": "content", "delta": part["text"]}
                                        elif "functionCall" in part:
                                            fc = part["functionCall"]
                                            yield {
                                                "type": "tool_call",
                                                "id": f"gemini_{fc.get('name')}",
                                                "name": fc.get("name"),
                                                "args": fc.get("args", {})
                                            }
                            except Exception:
                                continue
        except Exception as e:
            logger.error(f"Gemini LLM Stream error: {e}")
            yield {"type": "content", "delta": f" (Gemini Error: {str(e)})"}
