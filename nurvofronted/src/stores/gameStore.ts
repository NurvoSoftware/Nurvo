import { ref } from 'vue'
import { defineStore } from 'pinia'
import type { GameStatus } from '@/types/game'

export const useGameStore = defineStore('game', () => {
  const status = ref<GameStatus>('idle')
  const sessionId = ref<string>('')
  const errorMessage = ref<string>('')

  function setStatus(newStatus: GameStatus) {
    status.value = newStatus
    if (newStatus !== 'error') {
      errorMessage.value = ''
    }
  }

  function setSessionId(id: string) {
    sessionId.value = id
  }

  function setError(message: string) {
    status.value = 'error'
    errorMessage.value = message
  }

  function reset() {
    status.value = 'idle'
    sessionId.value = ''
    errorMessage.value = ''
  }

  return { status, sessionId, errorMessage, setStatus, setSessionId, setError, reset }
})
