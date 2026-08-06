import { useState, useEffect, useRef, useCallback } from 'react';
import { io, Socket } from 'socket.io-client';
import { VoiceState, TranscriptMessage, ClientActionPayload } from '../types/voice';
import { useAudioRecorder } from './useAudioRecorder';
import { useAudioPlayer } from './useAudioPlayer';

const SOCKET_URL = process.env.NEXT_PUBLIC_SOCKET_URL || 'http://localhost:8000';

export function useVoiceAssistant(userId: string = 'guest_user') {
  const [voiceState, setVoiceState] = useState<VoiceState>('idle');
  const [transcripts, setTranscripts] = useState<TranscriptMessage[]>([]);
  const [currentAiResponse, setCurrentAiResponse] = useState('');
  const [isConnected, setIsConnected] = useState(false);

  const socketRef = useRef<Socket | null>(null);
  const { isPlaying, playChunk, stopPlayback } = useAudioPlayer();

  const handleAudioChunk = useCallback((buffer: ArrayBuffer) => {
    if (socketRef.current && socketRef.current.connected) {
      socketRef.current.emit('audio_chunk', buffer);
    }
  }, []);

  const handleSpeechEnd = useCallback(() => {
    if (socketRef.current && socketRef.current.connected) {
      socketRef.current.emit('end_speech_turn');
    }
  }, []);

  const handleUserInterrupted = useCallback(() => {
    stopPlayback();
    setVoiceState('interrupted');
    if (socketRef.current && socketRef.current.connected) {
      socketRef.current.emit('user_interrupt');
    }
  }, [stopPlayback]);

  const { isRecording, audioLevel, startRecording, stopRecording } = useAudioRecorder({
    onAudioChunk: handleAudioChunk,
    onSpeechEnd: handleSpeechEnd,
    onUserInterrupted: handleUserInterrupted,
    isAiSpeaking: voiceState === 'speaking' || isPlaying,
  });

  useEffect(() => {
    const socket = io(SOCKET_URL, {
      path: '/ws/socket.io',
      transports: ['websocket'],
    });

    socketRef.current = socket;

    socket.on('connect', () => {
      setIsConnected(true);
      socket.emit('start_session', { userId });
    });

    socket.on('disconnect', () => {
      setIsConnected(false);
      setVoiceState('idle');
    });

    socket.on('ai_state', (data: { state: VoiceState }) => {
      setVoiceState(data.state);
    });

    socket.on('user_transcript', (data: { text: string; isFinal: boolean }) => {
      setTranscripts((prev) => {
        const updated = [...prev];
        const lastIndex = updated.length - 1;
        if (lastIndex >= 0 && updated[lastIndex].role === 'user' && !updated[lastIndex].isFinal) {
          updated[lastIndex] = { ...updated[lastIndex], text: data.text, isFinal: data.isFinal };
        } else {
          updated.push({
            id: `usr_${Date.now()}`,
            role: 'user',
            text: data.text,
            isFinal: data.isFinal,
            timestamp: new Date(),
          });
        }
        return updated;
      });
    });

    socket.on('ai_transcript', (data: { deltaText: string; fullText: string }) => {
      setCurrentAiResponse(data.fullText);
    });

    socket.on('audio_response_chunk', (chunk: ArrayBuffer) => {
      playChunk(chunk);
    });

    socket.on('execute_client_action', (payload: ClientActionPayload) => {
      console.log('⚡ Executing Client AI Tool Action:', payload);
      if (payload.actionName === 'navigate_pages' && payload.args.path) {
        window.location.href = payload.args.path;
      }
    });

    return () => {
      socket.disconnect();
    };
  }, [userId, playChunk]);

  const toggleAssistant = useCallback(() => {
    if (isRecording) {
      stopRecording();
      stopPlayback();
      setVoiceState('idle');
    } else {
      startRecording();
      setVoiceState('listening');
    }
  }, [isRecording, startRecording, stopRecording, stopPlayback]);

  return {
    isConnected,
    isRecording,
    voiceState,
    audioLevel,
    transcripts,
    currentAiResponse,
    toggleAssistant,
    interruptAi: handleUserInterrupted,
  };
}
