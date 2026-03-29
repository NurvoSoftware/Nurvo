<script setup lang="ts">
import { onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useScoreStore } from '@/stores/scoreStore'
import { useGameStore } from '@/stores/gameStore'
import { useScenarioStore } from '@/stores/scenarioStore'
import { useChatStore } from '@/stores/chatStore'
import NavBar from '@/components/shared/NavBar.vue'
import RadarChart from '@/components/dashboard/RadarChart.vue'
import ScoreChart from '@/components/dashboard/ScoreChart.vue'
import FeedbackCard from '@/components/dashboard/FeedbackCard.vue'
import DialogueTimeline from '@/components/dashboard/DialogueTimeline.vue'
import type { ScoreResult } from '@/types/game'

const router = useRouter()
const scoreStore = useScoreStore()
const gameStore = useGameStore()
const scenarioStore = useScenarioStore()
const chatStore = useChatStore()

const result = computed<ScoreResult | null>(() => scoreStore.scoreResult)

const scenarioName = computed<string>(() => {
  if (!scenarioStore.scenario) return ''
  const p = scenarioStore.scenario.patient_profile
  return `${p.name} - ${p.diagnosis}`
})

const elapsedDisplay = computed<string>(() => {
  if (!result.value) return ''
  const moments = result.value.key_moments
  if (moments.length > 0) {
    const maxElapsed: number = Math.max(...moments.map((m) => m.elapsed_seconds))
    const mins: number = Math.floor(maxElapsed / 60)
    const secs: number = Math.floor(maxElapsed % 60)
    return `${mins} 分 ${secs} 秒`
  }
  return ''
})

const levelSeverity = computed<'success' | 'info' | 'warn' | 'danger'>(() => {
  if (!result.value) return 'info'
  const s: number = result.value.overall_score
  if (s >= 85) return 'success'
  if (s >= 70) return 'info'
  if (s >= 55) return 'warn'
  return 'danger'
})

const scoreColorClass = computed<string>(() => {
  if (!result.value) return ''
  const s: number = result.value.overall_score
  if (s >= 85) return 'score-excellent'
  if (s >= 70) return 'score-good'
  if (s >= 55) return 'score-fair'
  return 'score-poor'
})

const levelGradient = computed<string>(() => {
  switch (levelSeverity.value) {
    case 'success':
      return 'linear-gradient(135deg, #22c55e, #16a34a)'
    case 'info':
      return 'linear-gradient(135deg, #3b82f6, #2563eb)'
    case 'warn':
      return 'linear-gradient(135deg, #eab308, #ca8a04)'
    case 'danger':
      return 'linear-gradient(135deg, #ef4444, #dc2626)'
  }
})

function resetAllStores(): void {
  scoreStore.reset()
  gameStore.reset()
  scenarioStore.reset()
  chatStore.reset()
}

async function playAgain(): Promise<void> {
  resetAllStores()
  router.push('/')
  setTimeout(async () => {
    try {
      await scenarioStore.fetchScenario()
      router.push('/briefing')
    } catch {
      // User can retry from home
    }
  }, 100)
}

function goHome(): void {
  resetAllStores()
  router.push('/')
}

onMounted(async () => {
  if (!scoreStore.scoreResult && gameStore.sessionId) {
    try {
      await scoreStore.fetchScore(gameStore.sessionId)
    } catch {
      // Error is handled by the loading state
    }
  }
})
</script>

<template>
  <div class="dashboard-page">
    <div class="bg-glow bg-glow--left"></div>
    <div class="bg-glow bg-glow--right"></div>

    <NavBar />

    <main class="dashboard-shell">
      <div class="dashboard-container">
      <!-- Loading State -->
      <div v-if="scoreStore.loading" class="loading-container">
        <div class="spinner" />
        <p class="loading-text">AI 正在評估您的表現...</p>
      </div>

      <!-- Error / No Data State -->
      <div v-else-if="!result" class="empty-container">
        <p class="empty-text">無法載入評分結果</p>
        <button class="btn btn-secondary" @click="goHome">回首頁</button>
      </div>

      <!-- Results -->
      <template v-else>
        <section class="report-heading">
          <h2 class="report-title">成果報告</h2>
          <p class="report-subtitle">感謝今天的完成，你很棒喔！讓我們一起看看這次的成果 ✨</p>
        </section>

        <!-- Score Hero Card -->
        <section class="score-hero">
          <div class="score-hero-left">
            <RadarChart :scores="result.dimension_scores" />
          </div>
          <div class="score-hero-right">
            <div class="score-display">
              <span class="score-number" :class="scoreColorClass">{{ result.overall_score }}</span>
              <span class="score-max">/100</span>
            </div>
            <span class="level-badge" :style="{ background: levelGradient }">
              {{ result.level_label }}
            </span>
            <div class="score-bars">
              <ScoreChart :scores="result.dimension_scores" />
            </div>
          </div>
        </section>

        <!-- Feedback Section -->
        <section class="feedback-section">
          <FeedbackCard type="strengths" :items="result.strengths" />
          <FeedbackCard type="improvements" :items="result.improvements" />
        </section>

        <!-- Key Moments Section -->
        <section class="moments-section">
          <h3 class="section-title">📍 關鍵時刻</h3>
          <DialogueTimeline :moments="result.key_moments" />
        </section>

        <!-- Action Buttons -->
        <section class="action-buttons">
          <button class="btn btn-primary" @click="playAgain">再玩一次 ↻</button>
          <button class="btn btn-secondary" @click="goHome">回首頁</button>
        </section>
      </template>
      </div>
    </main>
    </div>
</template>

<style scoped>
.dashboard-page {
  min-height: 100vh;
  position: relative;
  overflow: hidden;
  background:
    radial-gradient(circle at 18% 12%, #dbeafe 0%, transparent 30%),
    radial-gradient(circle at 84% 8%, #e0f2fe 0%, transparent 34%),
    #f8fbff;
}

.bg-glow {
  position: absolute;
  border-radius: 50%;
  filter: blur(52px);
  pointer-events: none;
  opacity: 0.3;
}

.bg-glow--left {
  width: 320px;
  height: 320px;
  left: -100px;
  top: 72px;
  background: #60a5fa;
}

.bg-glow--right {
  width: 340px;
  height: 340px;
  right: -120px;
  top: 64px;
  background: #7dd3fc;
}

.dashboard-shell {
  position: relative;
  z-index: 1;
  max-width: 1320px;
  margin: 18px auto 0;
  padding: 0 20px 42px;
}

.dashboard-container {
  max-width: 1120px;
  margin: 0 auto;
  padding: 28px;
  border-radius: 24px;
  border: 1px solid rgba(219, 234, 254, 0.88);
  background: linear-gradient(160deg, rgba(255, 255, 255, 0.56) 0%, rgba(255, 255, 255, 0.3) 100%);
  backdrop-filter: blur(16px) saturate(120%);
  -webkit-backdrop-filter: blur(16px) saturate(120%);
  box-shadow: 0 24px 52px rgba(15, 23, 42, 0.18);
}

/* Loading & Empty */
.loading-container,
.empty-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 60vh;
  gap: 16px;
}

.spinner {
  width: 36px;
  height: 36px;
  border: 3px solid #e2e8f0;
  border-top-color: #2563eb;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.loading-text {
  color: #475569;
  font-size: 16px;
  margin: 0;
}

.empty-text {
  color: #475569;
  font-size: 17px;
  margin: 0;
}

.report-heading {
  text-align: center;
  margin-bottom: 16px;
}

.report-title {
  margin: 0;
  font-size: clamp(28px, 4.2vw, 36px);
  font-weight: 800;
  letter-spacing: -0.02em;
  color: #0f172a;
}

.report-subtitle {
  margin: 8px 0 0;
  font-size: 15px;
  color: #334155;
}

/* Score Hero Card */
.score-hero {
  display: flex;
  align-items: center;
  gap: 34px;
  background: rgba(255, 255, 255, 0.78);
  border-radius: 22px;
  border: 1px solid rgba(203, 213, 225, 0.9);
  padding: 32px;
  margin-bottom: 22px;
  box-shadow: 0 14px 30px rgba(15, 23, 42, 0.08);
}

.score-hero-left {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.score-hero-right {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.score-display {
  display: flex;
  align-items: baseline;
  gap: 2px;
}

.score-number {
  font-size: 56px;
  font-weight: 800;
  line-height: 1;
}

.score-excellent {
  color: #16a34a;
}

.score-good {
  color: #2563eb;
}

.score-fair {
  color: #ca8a04;
}

.score-poor {
  color: #dc2626;
}

.score-max {
  font-size: 20px;
  font-weight: 600;
  color: #94a3b8;
}

.level-badge {
  display: inline-flex;
  align-self: flex-start;
  padding: 6px 16px;
  border-radius: 9999px;
  color: #ffffff;
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 0.02em;
}

.score-bars {
  margin-top: 4px;
}

/* Feedback Section */
.feedback-section {
  display: flex;
  gap: 18px;
  margin-bottom: 22px;
}

.feedback-section > * {
  flex: 1;
  min-width: 0;
}

/* Moments Section */
.moments-section {
  background: rgba(255, 255, 255, 0.78);
  border-radius: 18px;
  border: 1px solid rgba(203, 213, 225, 0.9);
  padding: 24px;
  margin-bottom: 30px;
  box-shadow: 0 12px 26px rgba(15, 23, 42, 0.08);
}

.section-title {
  font-size: 18px;
  font-weight: 700;
  color: #1e293b;
  margin: 0 0 18px 0;
}

/* Action Buttons */
.action-buttons {
  display: flex;
  justify-content: center;
  gap: 14px;
  padding-bottom: 8px;
}

.btn {
  padding: 12px 30px;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 700;
  cursor: pointer;
  border: none;
  transition: opacity 0.2s ease, transform 0.12s ease, box-shadow 0.2s ease;
}

.btn:active {
  transform: scale(0.97);
}

.btn-primary {
  background: var(--nurvo-gradient-primary);
  color: #ffffff;
  box-shadow: 0 10px 24px rgba(37, 99, 235, 0.28);
}

.btn-primary:hover {
  opacity: 0.96;
  box-shadow: 0 14px 30px rgba(37, 99, 235, 0.34);
}

.btn-secondary {
  background: rgba(255, 255, 255, 0.9);
  color: #475569;
  border: 1px solid rgba(203, 213, 225, 0.9);
}

.btn-secondary:hover {
  background: #ffffff;
}

/* Responsive */
@media (max-width: 640px) {
  .dashboard-shell {
    padding: 0 12px 24px;
  }

  .dashboard-container {
    padding: 18px;
    border-radius: 18px;
  }

  .score-hero {
    flex-direction: column;
    padding: 20px;
    gap: 20px;
  }

  .feedback-section {
    flex-direction: column;
  }

  .score-number {
    font-size: 42px;
  }

  .section-title {
    font-size: 16px;
  }

  .btn {
    width: 100%;
  }

  .action-buttons {
    flex-direction: column;
  }
}
</style>
