import { ref } from 'vue'
import { defineStore } from 'pinia'
import type { Scenario, ScenarioDifficulty } from '@/types/game'
import { generateScenario, fetchBackgroundImage } from '@/services/apiService'
import { useGameStore } from './gameStore'

export const useScenarioStore = defineStore('scenario', () => {
  const scenario = ref<Scenario | null>(null)
  const loading = ref(false)

  async function pollBackgroundImage(sessionId: string) {
    for (let i = 0; i < 25; i++) {
      await new Promise<void>((r) => setTimeout(r, 3000))
      try {
        const { pending, url } = await fetchBackgroundImage(sessionId)
        if (!pending) {
          if (url && scenario.value) scenario.value.background_image_url = url
          return
        }
      } catch {
        return
      }
    }
  }

  async function fetchScenario(difficulty: ScenarioDifficulty = 'medium') {
    if (loading.value) return
    const gameStore = useGameStore()
    loading.value = true
    gameStore.setStatus('generating')

    try {
      const response = await generateScenario(difficulty)
      scenario.value = response.scenario
      gameStore.setSessionId(response.session_id)
      gameStore.setStatus('briefing')
      pollBackgroundImage(response.session_id)
    } catch (error: any) {
      gameStore.setError(error.message || '情境生成失敗，請稍後再試')
      throw error
    } finally {
      loading.value = false
    }
  }

  function reset() {
    scenario.value = null
    loading.value = false
  }

  return { scenario, loading, fetchScenario, reset }
})
