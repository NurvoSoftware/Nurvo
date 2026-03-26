import { ref } from 'vue'
import { defineStore } from 'pinia'
import type { ScoreResult } from '@/types/game'
import { evaluateScore } from '@/services/apiService'

export const useScoreStore = defineStore('score', () => {
  const scoreResult = ref<ScoreResult | null>(null)
  const loading = ref(false)

  async function fetchScore(sessionId: string) {
    loading.value = true
    try {
      scoreResult.value = await evaluateScore(sessionId)
    } catch (error: any) {
      throw error
    } finally {
      loading.value = false
    }
  }

  function reset() {
    scoreResult.value = null
    loading.value = false
  }

  return { scoreResult, loading, fetchScore, reset }
})
