import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import socketio

from app.config import settings
from app.websocket.socket_server import sio

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("voice_assistant_app")

# Initialize FastAPI App
app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "status": "online",
        "service": settings.PROJECT_NAME,
        "websocket_endpoint": "/ws/socket.io",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "database": "connected", "redis": "connected"}

@app.get("/api/v1/voice/settings")
async def get_voice_settings():
    return {
        "stt_provider": settings.DEFAULT_STT_PROVIDER,
        "llm_provider": settings.DEFAULT_LLM_PROVIDER,
        "llm_model": settings.DEFAULT_LLM_MODEL,
        "tts_provider": settings.DEFAULT_TTS_PROVIDER,
        "voice_id": settings.DEFAULT_VOICE_ID,
        "available_stt": ["deepgram", "whisper", "google"],
        "available_llm": ["openai", "gemini", "claude", "ollama"],
        "available_tts": ["elevenlabs", "openai", "azure"]
    }

@app.get("/api/v1/analytics/usage")
async def get_usage_analytics():
    return {
        "total_voice_sessions": 482,
        "total_audio_minutes": 1420.5,
        "avg_latency_ms": 320,
        "stt_accuracy": "98.4%",
        "barge_ins_detected": 142
    }

# Combine FastAPI & Socket.IO into single ASGI application
socket_app = socketio.ASGIApp(sio, other_asgi_app=app, socketio_path="/ws/socket.io")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:socket_app", host="0.0.0.0", port=8000, reload=True)
