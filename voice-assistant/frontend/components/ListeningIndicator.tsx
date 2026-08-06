import React from 'react';
import { motion } from 'framer-motion';

interface ListeningIndicatorProps {
  isListening: boolean;
}

export const ListeningIndicator: React.FC<ListeningIndicatorProps> = ({ isListening }) => {
  return (
    <div className="flex items-center space-x-2 text-xs font-semibold uppercase tracking-wider">
      <motion.span
        className={`w-2.5 h-2.5 rounded-full ${isListening ? 'bg-cyan-400' : 'bg-slate-500'}`}
        animate={isListening ? { scale: [1, 1.4, 1], opacity: [0.6, 1, 0.6] } : { scale: 1 }}
        transition={{ repeat: Infinity, duration: 1.2 }}
      />
      <span className={isListening ? 'text-cyan-400' : 'text-slate-400'}>
        {isListening ? 'Listening Continuously...' : 'Microphone Inactive'}
      </span>
    </div>
  );
};
