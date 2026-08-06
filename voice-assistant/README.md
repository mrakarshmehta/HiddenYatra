# Gemini Live-Style Voice AI Assistant System

An enterprise-grade, real-time Voice AI system featuring full-duplex WebSocket streaming, WebAudio VAD, instant barge-in interruption handling, multi-model abstractions (OpenAI, Gemini, Claude, ElevenLabs, Deepgram), function calling engine, and 60FPS Siri/Gemini Live animated voice orb UI.

---

## 🌟 Key Features

- ⚡ **Full Duplex Audio Streaming**: 16kHz PCM audio chunk capture over Socket.IO WebSockets.
- 🛑 **Instant Barge-In Interruption**: AI speech and LLM token generation immediately halt when the user interrupts speaking.
- 🎙️ **Multi-Provider STT**: Deepgram Nova-2, OpenAI Whisper, and Google Cloud STT support.
- 🧠 **Multi-Model LLM Abstraction**: OpenAI GPT-4o, Google Gemini 2.5, Anthropic Claude, and Local Ollama.
- 🔊 **Streaming TTS**: ElevenLabs, OpenAI Speech, and Azure Cognitive Speech.
- 🛠️ **Deep App Function Calling**: Execute backend tools (`search_hotels`, `create_itinerary`, `search_nearby`) and dispatch client-side actions (`navigate_pages`, `open_profile`, `fill_form`).
- 🎨 **60FPS Animated Orb UI**: Canvas + Framer Motion liquid animated orb visualizer with WebAudio frequency reactivity.
- 📊 **Admin Dashboard**: Real-time analytics, pipeline latency metrics (STT/LLM/TTS breakdown), voice minutes, and model usage metrics.

---

## 🚀 Quick Start

### 1. Configure Environment Variables (`.env`)

```env
OPENAI_API_KEY=your_openai_key
GEMINI_API_KEY=your_gemini_key
DEEPGRAM_API_KEY=your_deepgram_key
ELEVENLABS_API_KEY=your_elevenlabs_key
```

### 2. Run with Docker Compose

```bash
docker-compose up --build
```

- **Backend FastAPI + Socket.IO Server**: `http://localhost:8000`
- **Interactive OpenAPI Docs**: `http://localhost:8000/docs`
- **Voice AI Settings**: `http://localhost:8000/api/v1/voice/settings`
- **Admin Dashboard API**: `http://localhost:8000/api/v1/analytics/usage`

---

## 🔌 Socket.IO WebSocket Protocol

- **Endpoint**: `/ws/socket.io`
- **Client to Server**:
  - `start_session`: Initializes full duplex session (`{ userId }`)
  - `audio_chunk`: Raw 16kHz mono PCM buffer chunk
  - `user_interrupt`: Signal client barge-in interrupt
  - `end_speech_turn`: User VAD finish signal
- **Server to Client**:
  - `ai_state`: Updates UI state (`listening`, `thinking`, `speaking`, `interrupted`)
  - `user_transcript`: Live STT transcription stream
  - `ai_transcript`: Real-time streaming LLM response tokens
  - `audio_response_chunk`: Real-time streaming TTS audio frames
  - `execute_client_action`: Triggers client-side UI action (`navigate_pages`, `fill_form`)

---

## 🏛️ System Architecture

```
User Voice -> WebAudio AudioWorklet -> Socket.IO -> Deepgram STT
                                                          |
Audio Queue Player <- ElevenLabs TTS <- GPT-4o / Gemini 2.5 LLM
        |
60FPS Orb UI
```
