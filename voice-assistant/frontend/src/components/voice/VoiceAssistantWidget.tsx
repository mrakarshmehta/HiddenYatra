'use client';

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { VoiceOrbVisualizer } from './VoiceOrbVisualizer';
import { useVoiceAssistant } from '../../hooks/useVoiceAssistant';

export const VoiceAssistantWidget: React.FC = () => {
  const [isExpanded, setIsExpanded] = useState(false);
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

  return (
    <div className="fixed bottom-6 right-6 z-50 flex flex-col items-end">
      {/* Expanded Live Assistant Modal */}
      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ opacity: 0, y: 40, scale: 0.9 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 40, scale: 0.9 }}
            className="w-96 h-[540px] bg-slate-950/90 backdrop-blur-2xl border border-slate-800/80 rounded-3xl shadow-2xl overflow-hidden flex flex-col mb-4 p-5 text-white"
          >
            {/* Header */}
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div className="flex items-center space-x-2">
                <span className={`w-3 h-3 rounded-full ${isConnected ? 'bg-emerald-400 animate-pulse' : 'bg-rose-500'}`} />
                <h3 className="font-semibold text-lg bg-gradient-to-r from-cyan-400 to-indigo-400 bg-clip-text text-transparent">
                  Gemini Live Voice AI
                </h3>
              </div>
              <div className="flex items-center space-x-2">
                <a href="/settings" className="text-slate-400 hover:text-white text-xs px-2 py-1 bg-slate-800/60 rounded-lg">
                  Settings
                </a>
                <button
                  onClick={() => setIsExpanded(false)}
                  className="text-slate-400 hover:text-white p-1"
                >
                  ✕
                </button>
              </div>
            </div>

            {/* Orb Visualizer Container */}
            <div className="flex-1 flex flex-col items-center justify-center relative py-4">
              <VoiceOrbVisualizer state={voiceState} audioLevel={audioLevel} size={200} />
              <p className="text-xs uppercase tracking-widest text-slate-400 mt-2 font-medium">
                {voiceState === 'idle' && 'Click Mic to Start'}
                {voiceState === 'listening' && 'Listening...'}
                {voiceState === 'thinking' && 'Thinking...'}
                {voiceState === 'speaking' && 'Speaking...'}
                {voiceState === 'interrupted' && 'Interrupted'}
              </p>
            </div>

            {/* Live Transcript Log */}
            <div className="h-32 bg-slate-900/60 rounded-2xl p-3 overflow-y-auto space-y-2 text-xs border border-slate-800/60 mb-4">
              {transcripts.slice(-3).map((t) => (
                <div key={t.id} className={`flex ${t.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <span
                    className={`px-3 py-1.5 rounded-xl max-w-[85%] ${
                      t.role === 'user'
                        ? 'bg-cyan-600/80 text-white rounded-br-none'
                        : 'bg-slate-800 text-slate-200 rounded-bl-none'
                    }`}
                  >
                    {t.text}
                  </span>
                </div>
              ))}
              {currentAiResponse && voiceState === 'speaking' && (
                <div className="flex justify-start">
                  <span className="px-3 py-1.5 rounded-xl bg-slate-800 text-cyan-300 rounded-bl-none italic">
                    {currentAiResponse}...
                  </span>
                </div>
              )}
            </div>

            {/* Action Buttons Toolbar */}
            <div className="flex items-center justify-around bg-slate-900/80 p-3 rounded-2xl border border-slate-800/80">
              <button
                onClick={toggleAssistant}
                className={`p-3.5 rounded-full transition-all duration-300 ${
                  isRecording
                    ? 'bg-rose-500 shadow-lg shadow-rose-500/40 text-white scale-105'
                    : 'bg-gradient-to-r from-cyan-500 to-blue-600 text-white hover:opacity-90'
                }`}
              >
                🎤
              </button>

              {voiceState === 'speaking' && (
                <button
                  onClick={interruptAi}
                  className="px-4 py-2 bg-amber-500/20 text-amber-300 border border-amber-500/40 rounded-xl text-xs font-semibold hover:bg-amber-500/30 transition-all"
                >
                  ⚡ Interrupt AI
                </button>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Floating Trigger Button */}
      <motion.button
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-16 h-16 rounded-full bg-gradient-to-r from-cyan-500 via-indigo-500 to-purple-600 p-0.5 shadow-2xl flex items-center justify-center cursor-pointer"
      >
        <div className="w-full h-full bg-slate-950 rounded-full flex items-center justify-center text-2xl">
          ✨
        </div>
      </motion.button>
    </div>
  );
};
