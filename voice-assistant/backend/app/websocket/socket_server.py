import socketio
import logging
from typing import Dict
from app.engine.pipeline import MasterVoicePipeline

logger = logging.getLogger(__name__)

# Create Socket.IO Async Server with CORS allowed
sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins="*",
    ping_timeout=60,
    ping_interval=25
)

# Active user sessions registry: sid -> MasterVoicePipeline
active_sessions: Dict[str, MasterVoicePipeline] = {}

@sio.event
async def connect(sid, environ):
    logger.info(f"Socket.IO Client connected: {sid}")

@sio.event
async def disconnect(sid):
    logger.info(f"Socket.IO Client disconnected: {sid}")
    if sid in active_sessions:
        pipeline = active_sessions.pop(sid)
        await pipeline.interrupt()

@sio.event
async def start_session(sid, data):
    user_id = data.get("userId", "guest_user")
    logger.info(f"Starting voice session for user {user_id} on sid {sid}")

    async def send_event(event_name: str, payload: dict):
        await sio.emit(event_name, payload, room=sid)

    async def send_audio(audio_bytes: bytes):
        await sio.emit("audio_response_chunk", audio_bytes, room=sid)

    pipeline = MasterVoicePipeline(
        session_id=sid,
        user_id=user_id,
        send_event_callback=send_event,
        send_audio_callback=send_audio
    )

    active_sessions[sid] = pipeline
    await sio.emit("session_started", {"sessionId": sid, "status": "active"}, room=sid)

@sio.event
async def audio_chunk(sid, data):
    """Handles raw 16kHz PCM audio chunk from client."""
    if sid in active_sessions:
        pipeline = active_sessions[sid]
        audio_bytes = data if isinstance(data, bytes) else bytes(data)
        await pipeline.process_audio_chunk(audio_bytes)

@sio.event
async def end_speech_turn(sid, data=None):
    """VAD signal that user finished speech turn."""
    if sid in active_sessions:
        pipeline = active_sessions[sid]
        await pipeline.handle_user_speech_finished()

@sio.event
async def user_interrupt(sid, data=None):
    """Immediate client barge-in event."""
    if sid in active_sessions:
        pipeline = active_sessions[sid]
        await pipeline.interrupt()

@sio.event
async def stop_session(sid, data=None):
    if sid in active_sessions:
        pipeline = active_sessions.pop(sid)
        await pipeline.interrupt()
        await sio.emit("session_stopped", {"sessionId": sid}, room=sid)
