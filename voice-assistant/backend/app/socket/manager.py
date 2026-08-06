import socketio
import logging
import time
from typing import Dict, Any

from app.middleware.auth import verify_jwt_token
from app.services.session_service import session_manager

logger = logging.getLogger(__name__)

# Create Socket.IO server with ping timeout and interval
sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins="*",
    ping_timeout=60,
    ping_interval=25
)

@sio.event
async def connect(sid, environ, auth=None):
    """Socket.IO client connection with JWT authentication."""
    token = None
    if auth and isinstance(auth, dict):
        token = auth.get("token")
    
    user_payload = verify_jwt_token(token) if token else {"sub": f"guest_{sid[:8]}"}
    user_id = user_payload.get("sub", f"guest_{sid[:8]}")

    session_manager.create_session(sid, user_id, user_payload)
    await sio.emit("connected", {"status": "authenticated", "userId": user_id, "sid": sid}, room=sid)
    logger.info(f"Socket connected & authenticated: sid={sid}, user_id={user_id}")

@sio.event
async def disconnect(sid):
    """Socket.IO client disconnection cleanup."""
    session_manager.remove_session(sid)
    logger.info(f"Socket disconnected: sid={sid}")

@sio.event
async def voice_start(sid, data=None):
    """Handles 'voice:start' event."""
    session = session_manager.get_session(sid)
    if session:
        session.is_voice_active = True
        session.touch()
        await sio.emit("ai:thinking", {"status": "listening"}, room=sid)

@sio.event
async def voice_audio(sid, data):
    """Handles 'voice:audio' raw audio chunk event."""
    session = session_manager.get_session(sid)
    if session:
        session.touch()
        # Audio processing pipeline handles PCM16 chunk stream

@sio.event
async def voice_stop(sid, data=None):
    """Handles 'voice:stop' event."""
    session = session_manager.get_session(sid)
    if session:
        session.is_voice_active = False

@sio.event
async def ping(sid, data=None):
    """Heartbeat ping event."""
    session = session_manager.get_session(sid)
    if session:
        session.touch()
    await sio.emit("pong", {"timestamp": time.time()}, room=sid)
