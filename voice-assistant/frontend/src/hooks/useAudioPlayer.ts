import { useRef, useCallback, useState } from 'react';

export function useAudioPlayer() {
  const [isPlaying, setIsPlaying] = useState(false);
  const audioContextRef = useRef<AudioContext | null>(null);
  const audioQueueRef = useRef<ArrayBuffer[]>([]);
  const isProcessingRef = useRef(false);

  const stopPlayback = useCallback(() => {
    audioQueueRef.current = [];
    isProcessingRef.current = false;
    if (audioContextRef.current) {
      audioContextRef.current.close();
      audioContextRef.current = null;
    }
    setIsPlaying(false);
  }, []);

  const playChunk = useCallback(async (audioBuffer: ArrayBuffer) => {
    audioQueueRef.current.push(audioBuffer);
    if (!isProcessingRef.current) {
      processQueue();
    }
  }, []);

  const processQueue = async () => {
    if (audioQueueRef.current.length === 0) {
      isProcessingRef.current = false;
      setIsPlaying(false);
      return;
    }

    isProcessingRef.current = true;
    setIsPlaying(true);

    if (!audioContextRef.current) {
      audioContextRef.current = new (window.AudioContext || (window as any).webkitAudioContext)();
    }

    const chunk = audioQueueRef.current.shift();
    if (!chunk) return;

    try {
      const decodedData = await audioContextRef.current.decodeAudioData(chunk.slice(0));
      const source = audioContextRef.current.createBufferSource();
      source.buffer = decodedData;
      source.connect(audioContextRef.current.destination);

      source.onended = () => {
        processQueue();
      };

      source.start();
    } catch (e) {
      console.error('Audio chunk decode error:', e);
      processQueue();
    }
  };

  return {
    isPlaying,
    playChunk,
    stopPlayback,
  };
}
