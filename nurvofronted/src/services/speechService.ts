/**
 * Speech recognition service using MediaRecorder + ElevenLabs Scribe API.
 * Records audio from the microphone, sends to backend for transcription.
 */

import { transcribeAudio } from '@/services/apiService'

let mediaRecorder: MediaRecorder | null = null
let audioChunks: Blob[] = []
let isListening = false

/**
 * Check if the browser supports MediaRecorder (required for recording).
 */
export function isSupported(): boolean {
  return (
    typeof navigator !== 'undefined' &&
    typeof window !== 'undefined' &&
    !!navigator.mediaDevices?.getUserMedia &&
    'MediaRecorder' in window
  )
}

/**
 * Start recording audio from the microphone.
 * When stopped, the audio is sent to the backend for ElevenLabs STT.
 *
 * @param onResult - callback invoked with the transcribed text
 * @param onError - optional callback invoked on error
 */
export async function start(
  onResult: (text: string) => void,
  onError?: (error: string) => void,
): Promise<void> {
  if (!isSupported()) {
    console.warn('[speechService] 瀏覽器不支援錄音功能')
    onError?.('瀏覽器不支援錄音功能')
    return
  }

  if (isListening) {
    stop()
  }

  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true })

    audioChunks = []
    mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm' })

    mediaRecorder.ondataavailable = (event: BlobEvent) => {
      if (event.data.size > 0) {
        audioChunks.push(event.data)
      }
    }

    mediaRecorder.onstop = async () => {
      // Stop all tracks to release the microphone
      stream.getTracks().forEach((track) => track.stop())

      if (audioChunks.length === 0) {
        isListening = false
        return
      }

      const audioBlob = new Blob(audioChunks, { type: 'audio/webm' })
      audioChunks = []

      try {
        const text = await transcribeAudio(audioBlob)
        if (text) {
          onResult(text)
        }
      } catch (err: any) {
        console.error('[speechService] STT 失敗:', err)
        onError?.(err.message || '語音辨識失敗')
      }
    }

    mediaRecorder.onerror = () => {
      console.error('[speechService] 錄音錯誤')
      isListening = false
      stream.getTracks().forEach((track) => track.stop())
      onError?.('錄音發生錯誤')
    }

    mediaRecorder.start()
    isListening = true
  } catch (err: any) {
    console.error('[speechService] 無法啟動錄音:', err)
    isListening = false
    onError?.(err.message || '無法取得麥克風權限')
  }
}

/**
 * Stop recording. This triggers the onstop handler which sends audio for transcription.
 */
export function stop(): void {
  if (mediaRecorder && mediaRecorder.state !== 'inactive') {
    try {
      mediaRecorder.stop()
    } catch {
      // already stopped
    }
  }
  isListening = false
}

/**
 * Whether speech recording is currently active.
 */
export function getIsListening(): boolean {
  return isListening
}
