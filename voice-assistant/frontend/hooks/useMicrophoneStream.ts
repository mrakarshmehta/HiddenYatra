import { useState, useRef, useCallback, useEffect } from 'react';
import { Socket } from 'socket.io-client';

interface UseMicrophoneStreamProps {
  socket: Socket | null;
  onSilenceDetected?: () => void;
  noiseSuppression?: boolean;
  echoCancellation?: boolean;
}

export function useMicrophoneStream({
  socket,
  onSilenceDetected,
  noiseSuppression = true,
  echoCancellation = true,
}: UseMicrophoneStreamProps) {
  const [isCapturing, setIsCapturing] = useState(false);
  const [audioLevel, setAudioLevel] = useState(0);
  const [permissionError, setPermissionError] = useState<string | null>(null);

  const audioCtxRef = useRef<AudioContext | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const workletRef = useRef<AudioWorkletNode | null>(null);
  const silenceTimerRef = useRef<NodeJS.Timeout | null>(null);

  const startStreaming = useCallback(async () => {
    setPermissionError(null);
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          sampleRate: 16000,
          channelCount: 1,
          echoCancellation,
          noiseSuppression,
          autoGainControl: true,
        },
      });

      streamRef.current = stream;
      const audioCtx = new (window.AudioContext || (window as any).webkitAudioContext)({ sampleRate: 16000 });
      audioCtxRef.current = audioCtx;

      await audioCtx.audioWorklet.addModule('/audioWorklets/pcmProcessor.js');
      const source = audioCtx.createMediaStreamSource(stream);
      const workletNode = new AudioWorkletNode(audioCtx, 'pcm-processor');
      workletRef.current = workletNode;

      // Signal server voice capture start
      if (socket && socket.connected) {
        socket.emit('voice:start');
      }

      workletNode.port.onmessage = (event) => {
        const { audioBuffer, energy } = event.data;
        setAudioLevel(Math.min(1, energy * 6));

        // Stream 20-100ms PCM16 raw audio chunk via Socket.IO
        if (socket && socket.connected) {
          socket.emit('voice:audio', audioBuffer);
        }

        // Automatic silence detection (VAD threshold)
        if (energy > 0.03) {
          if (silenceTimerRef.current) {
            clearTimeout(silenceTimerRef.current);
            silenceTimerRef.current = null;
          }
        } else if (!silenceTimerRef.current) {
          silenceTimerRef.current = setTimeout(() => {
            if (onSilenceDetected) onSilenceDetected();
            silenceTimerRef.current = null;
          }, 750);
        }
      };

      source.connect(workletNode);
      workletNode.connect(audioCtx.destination);
      setIsCapturing(true);
    } catch (err: any) {
      console.error('Microphone permission or capture error:', err);
      setPermissionError(err.message || 'Microphone permission denied');
      setIsCapturing(false);
    }
  }, [socket, echoCancellation, noiseSuppression, onSilenceDetected]);

  const stopStreaming = useCallback(() => {
    if (workletRef.current) {
      workletRef.current.disconnect();
      workletRef.current = null;
    }
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    }
    if (audioCtxRef.current) {
      audioCtxRef.current.close();
      audioCtxRef.current = null;
    }
    if (socket && socket.connected) {
      socket.emit('voice:stop');
    }
    setIsCapturing(false);
    setAudioLevel(0);
  }, [socket]);

  return {
    isCapturing,
    audioLevel,
    permissionError,
    startStreaming,
    stopStreaming,
  };
}
