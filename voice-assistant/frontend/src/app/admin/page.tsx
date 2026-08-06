'use client';

import React from 'react';

export default function AdminDashboardPage() {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-8 max-w-6xl mx-auto space-y-8">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-cyan-400 to-indigo-400 bg-clip-text text-transparent">
            Voice AI System Admin Panel
          </h1>
          <p className="text-xs text-slate-400 mt-1">Real-time metrics, latency breakdown, and usage logs</p>
        </div>
        <span className="px-3 py-1 bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 rounded-full text-xs font-mono">
          ● Socket.IO Engine Online
        </span>
      </div>

      {/* Metrics Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-slate-900/60 p-5 rounded-2xl border border-slate-800 backdrop-blur-xl">
          <p className="text-xs text-slate-400">Total Voice Minutes</p>
          <p className="text-2xl font-bold text-cyan-400 mt-1">1,420.5 min</p>
        </div>

        <div className="bg-slate-900/60 p-5 rounded-2xl border border-slate-800 backdrop-blur-xl">
          <p className="text-xs text-slate-400">Active Sessions</p>
          <p className="text-2xl font-bold text-indigo-400 mt-1">24 Live</p>
        </div>

        <div className="bg-slate-900/60 p-5 rounded-2xl border border-slate-800 backdrop-blur-xl">
          <p className="text-xs text-slate-400">Avg Pipeline Latency</p>
          <p className="text-2xl font-bold text-emerald-400 mt-1">320 ms</p>
        </div>

        <div className="bg-slate-900/60 p-5 rounded-2xl border border-slate-800 backdrop-blur-xl">
          <p className="text-xs text-slate-400">Barge-Ins Handled</p>
          <p className="text-2xl font-bold text-amber-400 mt-1">142 interrupts</p>
        </div>
      </div>

      {/* Latency Breakdown & Model Usage */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-slate-900/60 p-6 rounded-2xl border border-slate-800 space-y-4">
          <h3 className="font-semibold text-lg text-slate-200">End-to-End Latency Breakdown</h3>
          <div className="space-y-3 text-xs">
            <div>
              <div className="flex justify-between mb-1">
                <span>STT Deepgram Streaming</span>
                <span className="text-cyan-400">90 ms</span>
              </div>
              <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                <div className="bg-cyan-500 h-full w-[28%]" />
              </div>
            </div>

            <div>
              <div className="flex justify-between mb-1">
                <span>LLM (GPT-4o / Gemini 2.5 First Token)</span>
                <span className="text-indigo-400">140 ms</span>
              </div>
              <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                <div className="bg-indigo-500 h-full w-[44%]" />
              </div>
            </div>

            <div>
              <div className="flex justify-between mb-1">
                <span>TTS ElevenLabs Audio Stream</span>
                <span className="text-purple-400">90 ms</span>
              </div>
              <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                <div className="bg-purple-500 h-full w-[28%]" />
              </div>
            </div>
          </div>
        </div>

        <div className="bg-slate-900/60 p-6 rounded-2xl border border-slate-800 space-y-4">
          <h3 className="font-semibold text-lg text-slate-200">Model Distribution</h3>
          <ul className="space-y-2 text-xs">
            <li className="flex justify-between p-2.5 bg-slate-800/40 rounded-xl">
              <span>OpenAI GPT-4o</span>
              <span className="font-semibold text-cyan-400">62%</span>
            </li>
            <li className="flex justify-between p-2.5 bg-slate-800/40 rounded-xl">
              <span>Google Gemini 2.5 Flash</span>
              <span className="font-semibold text-indigo-400">24%</span>
            </li>
            <li className="flex justify-between p-2.5 bg-slate-800/40 rounded-xl">
              <span>Anthropic Claude 3.5 Sonnet</span>
              <span className="font-semibold text-purple-400">14%</span>
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
}
