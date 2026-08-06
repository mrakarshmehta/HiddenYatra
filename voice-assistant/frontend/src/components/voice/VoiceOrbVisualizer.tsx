'use client';

import React, { useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import { VoiceState } from '../../types/voice';

interface VoiceOrbVisualizerProps {
  state: VoiceState;
  audioLevel: number;
  size?: number;
}

export const VoiceOrbVisualizer: React.FC<VoiceOrbVisualizerProps> = ({
  state,
  audioLevel,
  size = 240,
}) => {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let animationFrameId: number;
    let phase = 0;

    const render = () => {
      ctx.clearRect(0, 0, size, size);
      const centerX = size / 2;
      const centerY = size / 2;
      const baseRadius = size * 0.3 + audioLevel * 25;

      phase += 0.05;

      // Color scheme according to state
      let colorGradients: string[] = ['#00F2FE', '#4FACFE', '#000000'];
      if (state === 'thinking') {
        colorGradients = ['#7F00FF', '#E100FF', '#000000'];
      } else if (state === 'speaking') {
        colorGradients = ['#FF0844', '#FFB199', '#000000'];
      } else if (state === 'interrupted') {
        colorGradients = ['#FF4E50', '#F9D423', '#000000'];
      }

      // Draw multi-layered liquid wave orb
      for (let layer = 0; layer < 3; layer++) {
        ctx.beginPath();
        const numPoints = 64;
        for (let i = 0; i <= numPoints; i++) {
          const angle = (i / numPoints) * Math.PI * 2;
          const wave = Math.sin(angle * (3 + layer) + phase + layer) * (8 + audioLevel * 20);
          const r = baseRadius + wave;
          const x = centerX + Math.cos(angle) * r;
          const y = centerY + Math.sin(angle) * r;

          if (i === 0) ctx.moveTo(x, y);
          else ctx.lineTo(x, y);
        }
        ctx.closePath();

        const grad = ctx.createRadialGradient(
          centerX,
          centerY,
          baseRadius * 0.2,
          centerX,
          centerY,
          baseRadius * 1.4
        );
        grad.addColorStop(0, colorGradients[0]);
        grad.addColorStop(0.7, colorGradients[1]);
        grad.addColorStop(1, 'transparent');

        ctx.fillStyle = grad;
        ctx.globalAlpha = 0.6 - layer * 0.15;
        ctx.shadowBlur = 30;
        ctx.shadowColor = colorGradients[0];
        ctx.fill();
      }

      animationFrameId = requestAnimationFrame(render);
    };

    render();

    return () => {
      cancelAnimationFrame(animationFrameId);
    };
  }, [state, audioLevel, size]);

  return (
    <div className="relative flex items-center justify-center">
      <motion.div
        animate={{
          scale: state === 'thinking' ? [1, 1.08, 1] : state === 'speaking' ? [1, 1.12, 1] : 1,
        }}
        transition={{ repeat: Infinity, duration: state === 'thinking' ? 1.2 : 0.8 }}
        className="relative"
      >
        <canvas
          ref={canvasRef}
          width={size}
          height={size}
          className="drop-shadow-2xl rounded-full"
        />
      </motion.div>
    </div>
  );
};
