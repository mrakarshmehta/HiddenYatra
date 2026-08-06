'use client';

import React from 'react';
import { GeminiLiveUI } from '../../components/GeminiLiveUI';
import { useVoiceAssistant } from '../hooks/useVoiceAssistant';

export default function HomePage() {
  const {
    isConnected,
    isRecording,
    voiceState,
    audioLevel,
    transcripts,
    currentAiResponse,
    toggleAssistant,
    interruptAi,
  } = useVoiceAssistant();

  const latestUserTranscript = transcripts.filter((t) => t.role === 'user').pop()?.text || '';

  return (
    <main className="w-full min-h-screen">
      <GeminiLiveUI
        isConnected={isConnected}
        isCapturing={isRecording}
        audioLevel={audioLevel}
        aiState={voiceState}
        userTranscript={latestUserTranscript}
        aiTranscript={currentAiResponse}
        onToggleMic={toggleAssistant}
        onInterrupt={interruptAi}
      />
    </main>
  );
}
