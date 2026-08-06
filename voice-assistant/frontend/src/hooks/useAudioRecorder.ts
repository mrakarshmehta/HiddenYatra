import { useState, useRef, useCallback } from 'react';

interface UseAudioRecorderProps {
  onAudioChunk: (buffer: ArrayBuffer) => void;
  onSpeechEnd: () => void;
  onUserInterrupted: () => void;
  isAiSpeaking: boolean;
  noiseSuppression?: boolean;
  echoCancellation?: boolean;
}

export function useAudioRecorder({
  onAudioChunk,
  onSpeechEnd,
  onUserInterrupted,
  isAiSpeaking,
  noiseSuppression = true,
  echoCancellation = true,
}: UseAudioRecorderProps) {
  const [isRecording, setIsRecording] = useState(false);
  const [audioLevel, setAudioLevel] = useState(0);

  const audioContextRef = useRef<AudioContext | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const workletNodeRef = useRef<AudioWorkletNode | null>(null);
  const silenceTimerRef = useRef<NodeJS.Timeout | null>(null);
  const isSpeakingRef = useRef(false);

  const startRecording = useCallback(async () => {
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
      audioContextRef.current = audioCtx;

      await audioCtx.audioWorklet.addModule('/audioWorklets/pcmProcessor.js');
      const source = audioCtx.createMediaStreamSource(stream);
      const workletNode = new AudioWorkletNode(audioCtx, 'pcm-processor');
      workletNodeRef.current = workletNode;

      workletNode.port.onmessage = (event) => {
        const { audioBuffer, energy } = event.data;
        setAudioLevel(Math.min(1, energy * 5));

        // Detect user speech start & barge-in interrupt
        if (energy > 0.04) {
          if (isAiSpeaking) {
            onUserInterrupted();
          }

          isSpeakingRef.current = true;
          if (silenceTimerRef.current) {
            clearTimeout(silenceTimerRef.current);
            silenceTimerRef.current = null;
          }
        } else if (isSpeakingRef.current && !silenceTimerRef.current) {
          // Silence timeout (600ms) to trigger speech completion
          silenceTimerRef.current = setTimeout(() => {
            isSpeakingRef.current = false;
            onSpeechEnd();
            silenceTimerRef.current = null;
          }, 600);
        }

        onAudioChunk(audioBuffer);
      };

      source.connect(workletNode);
      workletNode.connect(audioCtx.destination);
      setIsRecording(true);
    } catch (err) {
      console.error('Failed to start microphone:', err);
    }
  }, [echoCancellation, noiseSuppression, isAiSpeaking, onAudioChunk, onSpeechEnd, onUserInterrupted]);

  const stopRecording = useCallback(() => {
    if (workletNodeRef.current) {
      workletNodeRef.current.disconnect();
      workletNodeRef.current = null;
    }
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    }
    if (audioContextRef.current) {
      audioContextRef.current.close();
      audioContextRef.current = null;
    }
    if (silenceTimerRef.current) {
      clearTimeout(silenceTimerRef.current);
      silenceTimerRef.current = null;
    }
    setIsRecording(false);
    setAudioLevel(0);
  }, []);

  return {
    isRecording,
    audioLevel,
    startRecording,
    stopRecording,
  };
}
