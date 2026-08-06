'use client';

import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { LiveWaveform } from './LiveWaveform';
import { ListeningIndicator } from './ListeningIndicator';

interface GeminiLiveUIProps {
  isConnected: boolean;
  isCapturing: boolean;
  audioLevel: number;
  aiState: 'idle' | 'listening' | 'thinking' | 'speaking' | 'interrupted';
  userTranscript: string;
  aiTranscript: string;
  onToggleMic: () => void;
  onInterrupt: () => void;
}

export const GeminiLiveUI: React.FC<GeminiLiveUIProps> = ({
  isConnected,
  isCapturing,
  audioLevel,
  aiState,
  userTranscript,
  aiTranscript,
  onToggleMic,
  onInterrupt,
}) => {
  return (
    <div className="min-h-screen bg-slate-950 text-white flex flex-col items-center justify-between p-6 relative overflow-hidden">
      {/* Background Fluid Glow */}
      <div className="absolute inset-0 pointer-events-none opacity-20">
        <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-cyan-500 rounded-full blur-3xl" />
        <div className="absolute bottom-1/4 left-1/2 -translate-x-1/2 translate-y-1/2 w-96 h-96 bg-indigo-600 rounded-full blur-3xl" />
      </div>

      {/* Connection Header */}
      <div className="w-full max-w-md flex items-center justify-between z-10 bg-slate-900/60 p-3.5 rounded-2xl border border-slate-800 backdrop-blur-xl">
        <div className="flex items-center space-x-2">
          <span className={`w-2.5 h-2.5 rounded-full ${isConnected ? 'bg-emerald-400 animate-pulse' : 'bg-rose-500'}`} />
          <span className="text-xs font-semibold tracking-wide uppercase text-slate-300">
            {isConnected ? 'Gemini Live Connected' : 'Disconnected'}
          </span>
        </div>
        <ListeningIndicator isListening={isCapturing} />
      </div>

      {/* Center AI Avatar & Animation */}
      <div className="flex flex-col items-center justify-center z-10 space-y-6 my-auto">
        <motion.div
          className="relative w-48 h-48 rounded-full flex items-center justify-center bg-gradient-to-tr from-cyan-500 via-indigo-500 to-purple-600 p-1 shadow-2xl shadow-cyan-500/20"
          animate={{
            scale: aiState === 'speaking' ? [1, 1.06, 1] : aiState === 'thinking' ? [1, 1.03, 1] : 1,
            rotate: aiState === 'thinking' ? 360 : 0,
          }}
          transition={{ repeat: Infinity, duration: aiState === 'thinking' ? 4 : 1.5 }}
        >
          <div className="w-full h-full bg-slate-950 rounded-full flex flex-col items-center justify-center p-4 text-center">
            <span className="text-4xl mb-2">✨</span>
            <span className="text-xs font-semibold uppercase tracking-widest text-cyan-400">
              {aiState}
            </span>
          </div>
        </motion.div>

        {/* Live Audio Waveform */}
        <LiveWaveform audioLevel={audioLevel} barCount={16} />
      </div>

      {/* Live Transcript Bubbles */}
      <div className="w-full max-w-md z-10 space-y-3 mb-6">
        <AnimatePresence>
          {userTranscript && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-cyan-600/80 p-3.5 rounded-2xl rounded-br-none text-xs text-white shadow-lg"
            >
              <p className="font-semibold text-[10px] text-cyan-200 uppercase tracking-wider mb-0.5">You</p>
              {userTranscript}
            </motion.div>
          )}

          {aiTranscript && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-slate-900 border border-slate-800 p-3.5 rounded-2xl rounded-bl-none text-xs text-slate-200 shadow-lg"
            >
              <p className="font-semibold text-[10px] text-indigo-400 uppercase tracking-wider mb-0.5">Gemini AI</p>
              {aiTranscript}
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Control Toolbar */}
      <div className="w-full max-w-md z-10 flex items-center justify-around bg-slate-900/80 p-4 rounded-3xl border border-slate-800 backdrop-blur-xl">
        <motion.button
          whileTap={{ scale: 0.9 }}
          onClick={onToggleMic}
          className={`p-4 rounded-full text-xl text-white transition-all shadow-xl ${
            isCapturing
              ? 'bg-rose-500 shadow-rose-500/40 animate-pulse'
              : 'bg-gradient-to-r from-cyan-500 to-indigo-600'
          }`}
        >
          🎤
        </motion.button>

        {aiState === 'speaking' && (
          <button
            onClick={onInterrupt}
            className="px-4 py-2.5 bg-amber-500/20 text-amber-300 border border-amber-500/40 rounded-2xl text-xs font-semibold hover:bg-amber-500/30 transition-all"
          >
            ⚡ Interrupt
          </button>
        )}
      </div>
    </div>
  );
};
