export type VoiceState = 'idle' | 'listening' | 'thinking' | 'speaking' | 'interrupted';

export type VoiceMode = 'push_to_talk' | 'hands_free' | 'wake_word';

export interface VoiceSettings {
  sttProvider: string;
  llmProvider: string;
  llmModel: string;
  ttsProvider: string;
  voiceId: string;
  language: string;
  speechSpeed: number;
  pitch: number;
  volume: number;
  noiseSuppression: boolean;
  echoCancellation: boolean;
  autoListen: boolean;
  wakeWordEnabled: boolean;
  themeDark: boolean;
}

export interface TranscriptMessage {
  id: string;
  role: 'user' | 'assistant' | 'system' | 'tool';
  text: string;
  isFinal?: boolean;
  timestamp: Date;
}

export interface ClientActionPayload {
  toolCallId: string;
  actionName: string;
  args: Record<string, any>;
}
