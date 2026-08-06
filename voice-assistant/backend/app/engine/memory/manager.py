import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class MemoryManager:
    """Manages short-term conversation context and long-term user memory."""

    def __init__(self, user_id: str, max_short_term_turns: int = 10):
        self.user_id = user_id
        self.max_short_term_turns = max_short_term_turns
        self._short_term_history: List[Dict[str, Any]] = []
        self._long_term_memories: Dict[str, Any] = {
            "preferred_language": "English",
            "travel_style": "budget & heritage",
            "recent_searches": ["Patna", "Rajgir", "Nalanda"],
            "favorite_places": ["Mahabodhi Temple", "Nalanda University"]
        }

    def add_message(self, role: str, content: str, tool_calls: Optional[List[Dict[str, Any]]] = None):
        msg = {"role": role, "content": content}
        if tool_calls:
            msg["tool_calls"] = tool_calls
        self._short_term_history.append(msg)
        
        # Trim history if exceeds max turns
        if len(self._short_term_history) > self.max_short_term_turns * 2:
            self._short_term_history = self._short_term_history[-self.max_short_term_turns * 2:]

    def get_messages_for_llm(self) -> List[Dict[str, Any]]:
        return list(self._short_term_history)

    def get_system_prompt(self, user_name: str = "Traveler") -> str:
        prefs_summary = ", ".join([f"{k}: {v}" for k, v in self._long_term_memories.items()])
        return (
            f"You are Gemini Live Voice Assistant for HiddenYatra. You talk to {user_name} naturally, "
            f"concisely, and conversationally as if in a live phone call.\n"
            f"User Profile & Long Term Memory: [{prefs_summary}].\n"
            f"Guidelines:\n"
            f"- Keep responses brief, engaging, and friendly (1-3 natural sentences).\n"
            f"- Never use markdown formatting or lists in speech output unless requested.\n"
            f"- Trigger appropriate function calls when asked to navigate, search hotels, create trip, etc."
        )

    def clear(self):
        self._short_term_history.clear()
