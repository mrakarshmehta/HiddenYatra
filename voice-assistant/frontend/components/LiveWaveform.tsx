import React from 'react';
import { motion } from 'framer-motion';

interface LiveWaveformProps {
  audioLevel: number;
  barCount?: number;
}

export const LiveWaveform: React.FC<LiveWaveformProps> = ({ audioLevel, barCount = 12 }) => {
  return (
    <div className="flex items-center justify-center space-x-1 h-12">
      {Array.from({ length: barCount }).map((_, index) => {
        const heightMultiplier = Math.sin((index / barCount) * Math.PI);
        const dynamicHeight = Math.max(8, audioLevel * 48 * heightMultiplier);

        return (
          <motion.div
            key={index}
            className="w-1.5 bg-gradient-to-t from-cyan-500 to-indigo-500 rounded-full"
            animate={{ height: `${dynamicHeight}px` }}
            transition={{ type: 'spring', stiffness: 300, damping: 20 }}
          />
        );
      })}
    </div>
  );
};
