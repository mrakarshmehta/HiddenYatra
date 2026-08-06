import asyncio
import logging
from typing import Callable, Optional, Dict, Any

from app.engine.stt.deepgram_stt import DeepgramSTTEngine
from app.engine.stt.whisper_stt import WhisperSTTEngine
from app.engine.llm.openai_llm import OpenAILLEngine
from app.engine.llm.gemini_llm import GeminiLLEngine
from app.engine.tts.elevenlabs_tts import ElevenLabsTTSEngine
from app.engine.tts.openai_tts import OpenAITTSEngine
from app.engine.tools.registry import tool_registry
from app.engine.memory.manager import MemoryManager
from app.config import settings

logger = logging.getLogger(__name__)

class MasterVoicePipeline:
    """
    Master Real-Time Voice Pipeline Controller.
    Manages end-to-end audio streaming, STT, LLM reasoning, TTS synthesis, and barge-in interrupts.
    """

    def __init__(
        self,
        session_id: str,
        user_id: str,
        send_event_callback: Callable[[str, Dict[str, Any]], None],
        send_audio_callback: Callable[[bytes], None]
    ):
        self.session_id = session_id
        self.user_id = user_id
        self.send_event_callback = send_event_callback
        self.send_audio_callback = send_audio_callback

        # Initialize engines
        self.stt_engine = DeepgramSTTEngine()
        self.llm_engine = OpenAILLEngine(model_name="gpt-4o")
        self.tts_engine = ElevenLabsTTSEngine()
        self.memory = MemoryManager(user_id=user_id)

        # Async Tasks & State
        self.active_pipeline_task: Optional[asyncio.Task] = None
        self.is_interrupted = False
        self.state = "listening"  # listening | thinking | speaking

    async def update_state(self, new_state: str):
        self.state = new_state
        await self.send_event_callback("ai_state", {"state": new_state})

    async def process_audio_chunk(self, audio_bytes: bytes):
        """Ingests user PCM audio chunk."""
        if self.is_interrupted:
            return

        async def on_partial_transcript(text: str, is_final: bool):
            await self.send_event_callback("user_transcript", {"text": text, "isFinal": is_final})

        await self.stt_engine.process_audio_chunk(audio_bytes, on_partial_transcript)

    async def handle_user_speech_finished(self):
        """Called when VAD signals end of user speech turn."""
        final_user_transcript = await self.stt_engine.finish_stream()
        if not final_user_transcript.strip():
            return

        logger.info(f"User finished speaking: {final_user_transcript}")
        self.memory.add_message("user", final_user_transcript)

        # Cancel any previous running AI turn task
        if self.active_pipeline_task and not self.active_pipeline_task.done():
            self.active_pipeline_task.cancel()

        # Launch new AI reasoning & speech synthesis task
        self.is_interrupted = False
        self.active_pipeline_task = asyncio.create_task(self._run_ai_turn())

    async def interrupt(self):
        """Immediately halts ongoing LLM generation and audio streaming upon user barge-in."""
        logger.info(f"User interrupted session {self.session_id}!")
        self.is_interrupted = True
        
        if self.active_pipeline_task and not self.active_pipeline_task.done():
            self.active_pipeline_task.cancel()
            self.active_pipeline_task = None

        await self.stt_engine.reset()
        await self.update_state("listening")
        await self.send_event_callback("ai:interrupt", {"status": "interrupted"})

    async def _run_ai_turn(self):
        try:
            await self.update_state("thinking")
            messages = self.memory.get_messages_for_llm()
            system_prompt = self.memory.get_system_prompt()
            tools = tool_registry.get_openai_tools_schema()

            full_assistant_response = ""
            text_queue = asyncio.Queue()

            # Producer task: Stream LLM tokens & check tool calls
            async def llm_producer():
                nonlocal full_assistant_response
                async for item in self.llm_engine.generate_stream(messages, tools=tools, system_prompt=system_prompt):
                    if self.is_interrupted:
                        break

                    if item["type"] == "content":
                        delta = item["delta"]
                        full_assistant_response += delta
                        await text_queue.put(delta)
                        await self.send_event_callback("ai_transcript", {"deltaText": delta, "fullText": full_assistant_response})

                    elif item["type"] == "tool_call":
                        tool_name = item["name"]
                        tool_args = item["args"]
                        tool_id = item["id"]
                        
                        logger.info(f"AI triggered tool call: {tool_name} with args: {tool_args}")
                        
                        if tool_registry.is_client_tool(tool_name):
                            # Dispatch to frontend client
                            await self.send_event_callback("execute_client_action", {
                                "toolCallId": tool_id,
                                "actionName": tool_name,
                                "args": tool_args
                            })
                        else:
                            # Execute server tool
                            tool_result = await tool_registry.execute(tool_name, tool_args)
                            self.memory.add_message("tool", str(tool_result))

                await text_queue.put(None)  # Sentinel to signal end of stream

            # Consumer task: Synthesize speech from streamed text queue
            async def tts_consumer():
                async def text_stream_gen():
                    while True:
                        item = await text_queue.get()
                        if item is None:
                            break
                        yield item

                await self.update_state("speaking")
                async for audio_chunk in self.tts_engine.generate_audio_stream(text_stream_gen()):
                    if self.is_interrupted:
                        break
                    await self.send_audio_callback(audio_chunk)

            # Run LLM producer & TTS consumer concurrently
            producer_task = asyncio.create_task(llm_producer())
            consumer_task = asyncio.create_task(tts_consumer())
            await asyncio.gather(producer_task, consumer_task)

            if full_assistant_response and not self.is_interrupted:
                self.memory.add_message("assistant", full_assistant_response)

            await self.update_state("listening")

        except asyncio.CancelledError:
            logger.info(f"Pipeline task cancelled for session {self.session_id}")
        except Exception as e:
            logger.error(f"Pipeline execution error: {e}")
            await self.send_event_callback("error_event", {"message": str(e)})
            await self.update_state("listening")
