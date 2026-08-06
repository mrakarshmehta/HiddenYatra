import time
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class UserSession:
    """Represents a connected user voice session."""
    def __init__(self, sid: str, user_id: str, user_data: Dict[str, Any]):
        self.sid = sid
        self.user_id = user_id
        self.user_data = user_data
        self.started_at = time.time()
        self.last_heartbeat = time.time()
        self.is_voice_active = False

    def touch(self):
        self.last_heartbeat = time.time()

class SessionManager:
    """Manages active user voice sessions and heartbeat monitoring."""
    def __init__(self):
        self._sessions: Dict[str, UserSession] = {}
        self._user_to_sid: Dict[str, str] = {}

    def create_session(self, sid: str, user_id: str, user_data: Dict[str, Any]) -> UserSession:
        # Enforce one session per user
        if user_id in self._user_to_sid:
            old_sid = self._user_to_sid[user_id]
            self.remove_session(old_sid)

        session = UserSession(sid=sid, user_id=user_id, user_data=user_data)
        self._sessions[sid] = session
        self._user_to_sid[user_id] = sid
        logger.info(f"Created voice session {sid} for user {user_id}")
        return session

    def get_session(self, sid: str) -> Optional[UserSession]:
        return self._sessions.get(sid)

    def remove_session(self, sid: str) -> Optional[UserSession]:
        session = self._sessions.pop(sid, None)
        if session:
            self._user_to_sid.pop(session.user_id, None)
            logger.info(f"Cleaned up voice session {sid} for user {session.user_id}")
        return session

session_manager = SessionManager()
