/**
 * Speech recognition service using Web Speech API.
 * Provides voice-to-text input for the chat panel.
 */

type SpeechRecognitionType = typeof window extends { SpeechRecognition: infer T } ? T : any

let recognition: any = null
let isListening = false

/**
 * Check if the browser supports Web Speech API.
 */
export function isSupported(): boolean {
  return !!(
    (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition
  )
}

/**
 * Start speech recognition.
 * @param onResult - callback invoked with the recognized text
 */
export function start(onResult: (text: string) => void): void {
  if (!isSupported()) {
    console.warn('[speechService] 瀏覽器不支援語音辨識')
    return
  }

  if (isListening) {
    stop()
  }

  const SpeechRecognition =
    (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition

  recognition = new SpeechRecognition()
  recognition.lang = 'zh-TW'
  recognition.interimResults = false
  recognition.continuous = false
  recognition.maxAlternatives = 1

  recognition.onresult = (event: any) => {
    const transcript = event.results[0]?.[0]?.transcript ?? ''
    if (transcript) {
      onResult(transcript)
    }
  }

  recognition.onerror = (event: any) => {
    // 'no-speech' and 'aborted' are not real errors
    if (event.error !== 'no-speech' && event.error !== 'aborted') {
      console.error('[speechService] 語音辨識錯誤:', event.error)
    }
    isListening = false
  }

  recognition.onend = () => {
    isListening = false
  }

  try {
    recognition.start()
    isListening = true
  } catch (err) {
    console.error('[speechService] 無法啟動語音辨識:', err)
    isListening = false
  }
}

/**
 * Stop speech recognition.
 */
export function stop(): void {
  if (recognition) {
    try {
      recognition.stop()
    } catch {
      // already stopped
    }
    recognition = null
  }
  isListening = false
}

/**
 * Whether speech recognition is currently active.
 */
export function getIsListening(): boolean {
  return isListening
}
