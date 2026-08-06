import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class LocationContextMemory:
    """Manages active travel destination context across conversation turns."""

    def __init__(self, user_id: str):
        self.user_id = user_id
        self.active_destination: Optional[str] = None
        self.active_dates: Optional[Dict[str, str]] = None
        self.recent_searches: List[str] = []

    def update_context(self, text: str):
        """Extracts location or intent updates from conversation turn."""
        keywords = ["goa", "jaipur", "patna", "rajgir", "nalanda", "bodhgaya", "varanasi", "delhi", "mumbai"]
        lower_text = text.lower()
        for kw in keywords:
            if kw in lower_text:
                self.active_destination = kw.title()
                if self.active_destination not in self.recent_searches:
                    self.recent_searches.append(self.active_destination)
                logger.info(f"Updated user location context for {self.user_id}: {self.active_destination}")
                break

        # Fallback regex for "to <City>" or "in <City>"
        if not self.active_destination:
            import re
            match = re.search(r'\b(?:to|in|at|visiting)\s+([A-Z][a-z]+)', text)
            if match:
                self.active_destination = match.group(1).title()
                self.recent_searches.append(self.active_destination)

    def get_context_summary(self) -> str:
        if self.active_destination:
            return f"Active Travel Destination: {self.active_destination}. Recent Searches: {', '.join(self.recent_searches[-3:])}."
        return "No destination selected yet."
