<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import NavBar from '@/components/shared/NavBar.vue'
import BackButton from '@/components/shared/BackButton.vue'
import RadarChart from '@/components/dashboard/RadarChart.vue'
import ScoreChart from '@/components/dashboard/ScoreChart.vue'
import FeedbackCard from '@/components/dashboard/FeedbackCard.vue'
import DialogueTimeline from '@/components/dashboard/DialogueTimeline.vue'
import SbarCard from '@/components/dashboard/SbarCard.vue'
import { fetchHistoryDetail } from '@/services/apiService'
import type { ScoreResult } from '@/types/game'

const router = useRouter()
const route = useRoute()
const sessionId = route.params.sessionId as string

const loading = ref(true)
const error = ref('')
const patientName = ref('')
const diagnosis = ref('')
const difficulty = ref('')
const playedAt = ref('')
const result = ref<ScoreResult | null>(null)

onMounted(async () => {
  try {
    const data = await fetchHistoryDetail(sessionId)
    patientName.value = data.patient_name
    diagnosis.value = data.patient_diagnosis
    difficulty.value = data.difficulty
    playedAt.value = data.completed_at
    result.value = data.score
  } catch {
    error.value = '無法載入報告，請返回歷史紀錄頁面'
  } finally {
    loading.value = false
  }
})

const levelSeverity = computed<'success' | 'info' | 'warn' | 'danger'>(() => {
  if (!result.value) return 'info'
  const s = result.value.overall_score
  if (s >= 85) return 'success'
  if (s >= 70) return 'info'
  if (s >= 55) return 'warn'
  return 'danger'
})

const scoreColorClass = computed(() => {
  if (!result.value) return ''
  const s = result.value.overall_score
  if (s >= 85) return 'score-excellent'
  if (s >= 70) return 'score-good'
  if (s >= 55) return 'score-fair'
  return 'score-poor'
})

const levelGradient = computed(() => {
  switch (levelSeverity.value) {
    case 'success': return 'linear-gradient(135deg, #22c55e, #16a34a)'
    case 'info':    return 'linear-gradient(135deg, #3b82f6, #2563eb)'
    case 'warn':    return 'linear-gradient(135deg, #eab308, #ca8a04)'
    case 'danger':  return 'linear-gradient(135deg, #ef4444, #dc2626)'
  }
})

const difficultyLabel: Record<string, string> = {
  easy: '入門', medium: '標準', hard: '進階',
}

function formatDate(iso: string) {
  const d = new Date(iso)
  return `${d.getFullYear()}/${String(d.getMonth() + 1).padStart(2, '0')}/${String(d.getDate()).padStart(2, '0')}`
}
</script>

<template>
  <div class="detail-page">
    <div class="bg-glow bg-glow--left"></div>
    <div class="bg-glow bg-glow--right"></div>

    <NavBar />

    <main class="detail-shell">
      <div class="detail-container">
        <div class="detail-topbar">
          <BackButton to="/history" label="返回歷史紀錄" />
          <BackButton :to="{ name: 'level-select' }" label="進入訓練" arrow="forward" />
        </div>

        <div v-if="loading" class="state-box">
          <div class="spinner" />
          <p>載入報告中...</p>
        </div>

        <div v-else-if="error" class="state-box">
          <p class="error-text">{{ error }}</p>
          <button class="btn btn-secondary" @click="router.push('/history')">返回歷史紀錄</button>
        </div>

        <template v-else-if="result">
          <!-- Header -->
          <section class="report-heading">
            <div class="heading-meta">
              <div class="meta-chips">
                <span class="chip">{{ formatDate(playedAt) }}</span>
                <span class="chip">{{ difficultyLabel[difficulty] ?? difficulty }}</span>
                <span v-if="patientName" class="chip">{{ patientName }} · {{ diagnosis }}</span>
              </div>
            </div>
            <h2 class="report-title">成果報告</h2>
          </section>

          <!-- Score Hero -->
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

          <!-- Feedback -->
          <section class="feedback-section">
            <FeedbackCard type="strengths" :items="result.strengths" />
            <FeedbackCard type="improvements" :items="result.improvements" />
          </section>

          <section v-if="result.sbar_analysis" class="sbar-section">
            <SbarCard :analysis="result.sbar_analysis" />
          </section>

          <!-- Key Moments -->
          <section class="moments-section">
            <h3 class="section-title">📍 關鍵時刻</h3>
            <DialogueTimeline :moments="result.key_moments" />
          </section>

          <section class="action-buttons">
            <button class="btn btn-secondary" @click="router.push('/history')">返回歷史紀錄</button>
            <button class="btn btn-primary" @click="router.push('/')">回首頁</button>
          </section>
        </template>

      </div>
    </main>
  </div>
</template>

<style scoped>
.sbar-section {
  margin-bottom: 22px;
}

.detail-page {
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
.bg-glow--left  { width: 320px; height: 320px; left: -100px; top: 72px; background: #60a5fa; }
.bg-glow--right { width: 340px; height: 340px; right: -120px; top: 64px; background: #7dd3fc; }

.detail-shell {
  position: relative;
  z-index: 1;
  max-width: 1320px;
  margin: 0 auto;
  padding: 0 20px 48px;
}

.detail-container {
  max-width: 1120px;
  margin: 0 auto;
  padding: 28px;
  border-radius: 24px;
  border: 1px solid rgba(219,234,254,0.88);
  background: linear-gradient(160deg, rgba(255,255,255,0.56) 0%, rgba(255,255,255,0.3) 100%);
  backdrop-filter: blur(16px);
  box-shadow: 0 24px 52px rgba(15,23,42,0.18);
}

.state-box {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
  min-height: 300px;
  color: #64748b;
}

.spinner {
  width: 36px; height: 36px;
  border: 3px solid #e2e8f0;
  border-top-color: #2563eb;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

.error-text { color: #dc2626; }

/* Header */
.report-heading { margin-bottom: 20px; }

.detail-topbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

/* The links carry their own bottom margin for stacked layouts; not needed in this row. */
.detail-topbar :deep(.back-button) {
  margin: 0;
}

.heading-meta {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 12px;
  flex-wrap: wrap;
}

.meta-chips { display: flex; gap: 8px; flex-wrap: wrap; }

.chip {
  display: inline-block;
  padding: 3px 10px;
  border-radius: 9999px;
  background: #f1f5f9;
  color: #475569;
  font-size: 12px;
  font-weight: 600;
}

.report-title {
  margin: 0;
  font-size: clamp(24px, 4vw, 32px);
  font-weight: 800;
  color: #0f172a;
  letter-spacing: -0.02em;
}

/* Reuse dashboard styles */
.score-hero {
  display: flex;
  align-items: center;
  gap: 34px;
  background: rgba(255,255,255,0.78);
  border-radius: 22px;
  border: 1px solid rgba(203,213,225,0.9);
  padding: 32px;
  margin-bottom: 22px;
  box-shadow: 0 14px 30px rgba(15,23,42,0.08);
}
.score-hero-left { flex-shrink: 0; display: flex; align-items: center; justify-content: center; }
.score-hero-right { flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 14px; }
.score-display { display: flex; align-items: baseline; gap: 2px; }
.score-number { font-size: 56px; font-weight: 800; line-height: 1; }
.score-excellent { color: #16a34a; }
.score-good      { color: #2563eb; }
.score-fair      { color: #ca8a04; }
.score-poor      { color: #dc2626; }
.score-max { font-size: 20px; font-weight: 600; color: #94a3b8; }
.level-badge {
  display: inline-flex;
  align-self: flex-start;
  padding: 6px 16px;
  border-radius: 9999px;
  color: #fff;
  font-size: 13px;
  font-weight: 700;
}

.feedback-section { display: flex; gap: 18px; margin-bottom: 22px; }
.feedback-section > * { flex: 1; min-width: 0; }

.moments-section {
  background: rgba(255,255,255,0.78);
  border-radius: 18px;
  border: 1px solid rgba(203,213,225,0.9);
  padding: 24px;
  margin-bottom: 30px;
  box-shadow: 0 12px 26px rgba(15,23,42,0.08);
}
.section-title { font-size: 18px; font-weight: 700; color: #1e293b; margin: 0 0 18px; }

.action-buttons { display: flex; justify-content: center; gap: 14px; }
.btn {
  padding: 12px 30px;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 700;
  cursor: pointer;
  border: none;
  transition: opacity 0.15s;
}
.btn-primary {
  background: linear-gradient(135deg, #2563eb, #0ea5e9);
  color: #fff;
  box-shadow: 0 10px 24px rgba(37,99,235,0.28);
}
.btn-secondary {
  background: rgba(255,255,255,0.9);
  color: #475569;
  border: 1px solid rgba(203,213,225,0.9);
}

@media (max-width: 640px) {
  .score-hero { flex-direction: column; padding: 20px; gap: 20px; }
  .feedback-section { flex-direction: column; }
  .score-number { font-size: 42px; }
  .action-buttons { flex-direction: column; }
  .btn { width: 100%; }
}
</style>
