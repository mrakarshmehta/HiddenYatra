'use client';

import React, { useState } from 'react';

export default function SettingsPage() {
  const [settings, setSettings] = useState({
    sttProvider: 'deepgram',
    llmProvider: 'openai',
    llmModel: 'gpt-4o',
    ttsProvider: 'elevenlabs',
    voiceId: '21m00Tcm4TlvDq8ikWAM',
    language: 'en-US',
    speechSpeed: 1.0,
    pitch: 1.0,
    volume: 1.0,
    noiseSuppression: true,
    echoCancellation: true,
    autoListen: true,
    themeDark: true,
  });

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-8 max-w-4xl mx-auto">
      <h1 className="text-3xl font-bold bg-gradient-to-r from-cyan-400 to-indigo-400 bg-clip-text text-transparent mb-8">
        Voice AI Assistant Settings
      </h1>

      <div className="space-y-6 bg-slate-900/60 p-6 rounded-3xl border border-slate-800 backdrop-blur-xl">
        {/* Model Providers */}
        <section className="space-y-4">
          <h2 className="text-xl font-semibold text-cyan-400">Model Providers</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-xs text-slate-400 mb-1">STT Provider</label>
              <select
                value={settings.sttProvider}
                onChange={(e) => setSettings({ ...settings, sttProvider: e.target.value })}
                className="w-full bg-slate-800 border border-slate-700 rounded-xl p-2.5 text-sm"
              >
                <option value="deepgram">Deepgram (Streaming)</option>
                <option value="whisper">OpenAI Whisper</option>
                <option value="google">Google STT</option>
              </select>
            </div>

            <div>
              <label className="block text-xs text-slate-400 mb-1">LLM Provider</label>
              <select
                value={settings.llmProvider}
                onChange={(e) => setSettings({ ...settings, llmProvider: e.target.value })}
                className="w-full bg-slate-800 border border-slate-700 rounded-xl p-2.5 text-sm"
              >
                <option value="openai">OpenAI (GPT-4o)</option>
                <option value="gemini">Google Gemini 2.5</option>
                <option value="claude">Anthropic Claude</option>
                <option value="ollama">Local Ollama</option>
              </select>
            </div>

            <div>
              <label className="block text-xs text-slate-400 mb-1">TTS Provider</label>
              <select
                value={settings.ttsProvider}
                onChange={(e) => setSettings({ ...settings, ttsProvider: e.target.value })}
                className="w-full bg-slate-800 border border-slate-700 rounded-xl p-2.5 text-sm"
              >
                <option value="elevenlabs">ElevenLabs</option>
                <option value="openai">OpenAI TTS</option>
                <option value="azure">Azure Speech</option>
              </select>
            </div>
          </div>
        </section>

        {/* Voice Parameters */}
        <section className="space-y-4 border-t border-slate-800 pt-4">
          <h2 className="text-xl font-semibold text-indigo-400">Voice Synthesis Parameters</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div>
              <div className="flex justify-between text-xs text-slate-400 mb-1">
                <span>Speed</span>
                <span>{settings.speechSpeed}x</span>
              </div>
              <input
                type="range"
                min="0.5"
                max="2.0"
                step="0.1"
                value={settings.speechSpeed}
                onChange={(e) => setSettings({ ...settings, speechSpeed: parseFloat(e.target.value) })}
                className="w-full accent-cyan-400"
              />
            </div>

            <div>
              <div className="flex justify-between text-xs text-slate-400 mb-1">
                <span>Pitch</span>
                <span>{settings.pitch}x</span>
              </div>
              <input
                type="range"
                min="0.5"
                max="1.5"
                step="0.1"
                value={settings.pitch}
                onChange={(e) => setSettings({ ...settings, pitch: parseFloat(e.target.value) })}
                className="w-full accent-cyan-400"
              />
            </div>

            <div>
              <div className="flex justify-between text-xs text-slate-400 mb-1">
                <span>Volume</span>
                <span>{Math.round(settings.volume * 100)}%</span>
              </div>
              <input
                type="range"
                min="0"
                max="1.0"
                step="0.05"
                value={settings.volume}
                onChange={(e) => setSettings({ ...settings, volume: parseFloat(e.target.value) })}
                className="w-full accent-cyan-400"
              />
            </div>
          </div>
        </section>

        {/* Audio Capture Filters */}
        <section className="space-y-4 border-t border-slate-800 pt-4">
          <h2 className="text-xl font-semibold text-purple-400">Audio Processing</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <label className="flex items-center space-x-3 bg-slate-800/40 p-3 rounded-xl cursor-pointer">
              <input
                type="checkbox"
                checked={settings.noiseSuppression}
                onChange={(e) => setSettings({ ...settings, noiseSuppression: e.target.checked })}
                className="w-4 h-4 accent-cyan-400 rounded"
              />
              <span className="text-sm">WebAudio Noise Suppression</span>
            </label>

            <label className="flex items-center space-x-3 bg-slate-800/40 p-3 rounded-xl cursor-pointer">
              <input
                type="checkbox"
                checked={settings.echoCancellation}
                onChange={(e) => setSettings({ ...settings, echoCancellation: e.target.checked })}
                className="w-4 h-4 accent-cyan-400 rounded"
              />
              <span className="text-sm">WebAudio Echo Cancellation</span>
            </label>
          </div>
        </section>

        <div className="pt-4 flex justify-end">
          <button className="px-6 py-2.5 bg-gradient-to-r from-cyan-500 to-indigo-600 rounded-xl font-semibold hover:opacity-90 transition-all">
            Save Voice Settings
          </button>
        </div>
      </div>
    </div>
  );
}
