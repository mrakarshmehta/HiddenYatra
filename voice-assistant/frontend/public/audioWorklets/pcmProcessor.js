class PCMProcessor extends AudioWorkletProcessor {
  constructor() {
    super();
    this.buffer = new Float32Array(0);
  }

  process(inputs, outputs, parameters) {
    const input = inputs[0];
    if (!input || input.length === 0) return true;

    const channelData = input[0];
    if (!channelData) return true;

    // Convert Float32 PCM to Int16 PCM (16kHz Mono)
    const int16Chunk = new Int16Array(channelData.length);
    let energy = 0;

    for (let i = 0; i < channelData.length; i++) {
      const s = Math.max(-1, Math.min(1, channelData[i]));
      int16Chunk[i] = s < 0 ? s * 0x8000 : s * 0x7FFF;
      energy += Math.abs(s);
    }

    const avgEnergy = energy / channelData.length;

    // Send audio buffer and energy to main UI thread
    this.port.postMessage({
      audioBuffer: int16Chunk.buffer,
      energy: avgEnergy
    }, [int16Chunk.buffer]);

    return true;
  }
}

registerProcessor('pcm-processor', PCMProcessor);
