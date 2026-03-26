/**
 * Audio playback service for TTS audio (base64-encoded).
 * Manages a playback queue so overlapping audio plays in sequence.
 */

let audioContext: AudioContext | null = null
let currentSource: AudioBufferSourceNode | null = null
let isPlaying = false
const queue: string[] = []

function getAudioContext(): AudioContext {
  if (!audioContext) {
    audioContext = new AudioContext()
  }
  return audioContext
}

function base64ToArrayBuffer(base64: string): ArrayBuffer {
  const binaryString = atob(base64)
  const bytes = new Uint8Array(binaryString.length)
  for (let i = 0; i < binaryString.length; i++) {
    bytes[i] = binaryString.charCodeAt(i)
  }
  return bytes.buffer
}

async function playBuffer(base64Audio: string): Promise<void> {
  const ctx = getAudioContext()

  // Resume context if suspended (browser autoplay policy)
  if (ctx.state === 'suspended') {
    await ctx.resume()
  }

  const arrayBuffer = base64ToArrayBuffer(base64Audio)
  const audioBuffer = await ctx.decodeAudioData(arrayBuffer)

  return new Promise<void>((resolve) => {
    const source = ctx.createBufferSource()
    source.buffer = audioBuffer
    source.connect(ctx.destination)
    currentSource = source

    source.onended = () => {
      currentSource = null
      resolve()
    }

    source.start(0)
  })
}

async function processQueue(): Promise<void> {
  if (isPlaying) return

  isPlaying = true
  while (queue.length > 0) {
    const next = queue.shift()!
    try {
      await playBuffer(next)
    } catch (err) {
      console.error('[audioService] 播放音訊失敗:', err)
    }
  }
  isPlaying = false
}

/**
 * Decode base64 audio and play it. If audio is already playing, queue it.
 */
export function decodeAndPlay(base64Audio: string): void {
  if (!base64Audio) return
  queue.push(base64Audio)
  processQueue()
}

/**
 * Stop current playback and clear the queue.
 */
export function stop(): void {
  queue.length = 0
  if (currentSource) {
    try {
      currentSource.stop()
    } catch {
      // already stopped
    }
    currentSource = null
  }
  isPlaying = false
}
