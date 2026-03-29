<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useGameStore } from '@/stores/gameStore'
import { useScenarioStore } from '@/stores/scenarioStore'
import { submitRecord } from '@/services/apiService'
import NavBar from '@/components/shared/NavBar.vue'

const router = useRouter()
const route = useRoute()
const gameStore = useGameStore()
const scenarioStore = useScenarioStore()

const content = ref<string>('')
const submitting = ref<boolean>(false)
const errorMsg = ref<string>('')
const timerExpired = ref<boolean>(false)

const charCount = computed<number>(() => content.value.trim().length)
const isValid = computed<boolean>(() => charCount.value > 0)

async function handleSubmit(): Promise<void> {
  if (!isValid.value || submitting.value) return

  submitting.value = true
  errorMsg.value = ''

  try {
    await submitRecord(gameStore.sessionId, content.value)
    gameStore.setStatus('scoring')
    router.push('/dashboard')
  } catch (error: unknown) {
    const err = error as Error
    errorMsg.value = err.message || '提交失敗，請稍後再試'
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  if (!gameStore.sessionId) {
    router.replace('/')
    return
  }

  // Check if redirected by timer expiration
  if (route.query.expired === '1') {
    timerExpired.value = true
  }
})
</script>

<template>
  <div class="record-page">
    <div class="bg-glow bg-glow--left"></div>
    <div class="bg-glow bg-glow--right"></div>

    <NavBar />

    <main class="record-shell">
      <section class="record-glass">
        <header class="record-header">
          <p class="record-eyebrow">Clinical Record Summary</p>
          <h1 class="record-title">病患記錄</h1>
          <p class="record-subtitle">根據對話內容撰寫評估摘要，完成後提交進入評分</p>
        </header>

        <div v-if="timerExpired" class="record-alert">
          <div class="record-alert__icon">&#x23F0;</div>
          <div class="record-alert__body">
            <div class="record-alert__title">時間到！</div>
            <div class="record-alert__text">請完成以下病患記錄</div>
          </div>
        </div>

        <div v-if="scenarioStore.scenario" class="record-patient">
          <div class="record-patient__avatar">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
              <circle cx="12" cy="7" r="4" />
            </svg>
          </div>
          <div class="record-patient__info">
            <span class="record-patient__name">{{ scenarioStore.scenario.patient_profile.name }}</span>
            <span class="record-patient__sep">&middot;</span>
            <span class="record-patient__diagnosis">{{ scenarioStore.scenario.patient_profile.diagnosis }}</span>
          </div>
        </div>

        <div class="record-textarea-card">
          <div class="record-textarea-card__header">
            <span class="record-textarea-card__label">&#x1F4DD; 評估摘要</span>
          </div>
          <textarea
            v-model="content"
            class="record-textarea"
            placeholder="請描述病患的疼痛狀況、位置、程度、持續時間、你的評估與護理計畫..."
          ></textarea>
          <div class="record-textarea-card__footer">
            <span class="record-textarea-card__hint">請輸入內容</span>
            <span
              class="record-textarea-card__count"
              :class="{ 'record-textarea-card__count--valid': charCount > 0 }"
            >{{ charCount }} 字</span>
          </div>
        </div>

        <div v-if="errorMsg" class="record-error">
          {{ errorMsg }}
        </div>

        <div class="record-submit">
          <button
            class="record-btn-primary"
            :disabled="!isValid || submitting"
            @click="handleSubmit"
          >
            <span v-if="submitting" class="record-spinner"></span>
            <template v-else>提交記錄 &rarr;</template>
          </button>
        </div>
      </section>
    </main>
  </div>
</template>

<style scoped>
.record-page {
  min-height: 100vh;
  position: relative;
  overflow: hidden;
  background-image:
    linear-gradient(180deg, rgba(8, 47, 73, 0.08) 0%, rgba(2, 6, 23, 0.2) 100%),
    url('/hospital_bg.jpg');
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
}

.bg-glow {
  position: absolute;
  border-radius: 50%;
  filter: blur(52px);
  pointer-events: none;
  opacity: 0.28;
}

.bg-glow--left {
  width: 300px;
  height: 300px;
  left: -96px;
  top: 72px;
  background: #60a5fa;
}

.bg-glow--right {
  width: 330px;
  height: 330px;
  right: -110px;
  top: 68px;
  background: #7dd3fc;
}

.record-shell {
  position: relative;
  z-index: 1;
  max-width: 1040px;
  margin: 18px auto 0;
  padding: 0 20px 38px;
}

.record-glass {
  max-width: 780px;
  margin: 0 auto;
  border-radius: 24px;
  border: 1px solid rgba(219, 234, 254, 0.88);
  background: linear-gradient(160deg, rgba(255, 255, 255, 0.56) 0%, rgba(255, 255, 255, 0.3) 100%);
  backdrop-filter: blur(16px) saturate(120%);
  -webkit-backdrop-filter: blur(16px) saturate(120%);
  box-shadow: 0 24px 52px rgba(15, 23, 42, 0.2);
  padding: 24px;
}

.record-header {
  text-align: center;
  margin-bottom: 16px;
}

.record-eyebrow {
  margin: 0 0 8px;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: #1e40af;
}

.record-title {
  margin: 0;
  font-size: clamp(30px, 4.4vw, 40px);
  font-weight: 800;
  letter-spacing: -0.03em;
  color: #0f172a;
}

.record-subtitle {
  margin: 8px 0 0;
  font-size: 15px;
  color: #334155;
}

.record-alert {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  background: rgba(255, 251, 235, 0.88);
  border: 1px solid rgba(252, 211, 77, 0.8);
  border-radius: 14px;
  padding: 14px 16px;
  margin-bottom: 16px;
}

.record-alert__icon {
  font-size: 20px;
  line-height: 1;
  flex-shrink: 0;
}

.record-alert__body {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.record-alert__title {
  font-size: 16px;
  font-weight: 700;
  color: var(--nurvo-warning-darker);
}

.record-alert__text {
  font-size: 14px;
  color: var(--nurvo-warning-dark);
}

.record-patient {
  display: flex;
  align-items: center;
  gap: 10px;
  background: rgba(255, 255, 255, 0.72);
  border: 1px solid rgba(203, 213, 225, 0.9);
  border-radius: 14px;
  padding: 10px 14px;
  margin-bottom: 16px;
}

.record-patient__avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: var(--nurvo-patient-bg);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--nurvo-patient-dark);
  flex-shrink: 0;
}

.record-patient__info {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  color: var(--nurvo-text-secondary);
}

.record-patient__name {
  font-weight: 600;
  color: var(--nurvo-text-primary);
}

.record-patient__sep {
  color: var(--nurvo-text-muted);
}

.record-patient__diagnosis {
  color: var(--nurvo-text-secondary);
}

.record-textarea-card {
  background: rgba(255, 255, 255, 0.78);
  border: 1px solid rgba(203, 213, 225, 0.9);
  border-radius: 18px;
  overflow: hidden;
  margin-bottom: 20px;
}

.record-textarea-card__header {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid var(--nurvo-border-light);
}

.record-textarea-card__label {
  font-size: 14px;
  font-weight: 600;
  color: var(--nurvo-text-primary);
}

.record-textarea {
  display: block;
  width: 100%;
  min-height: 180px;
  padding: 14px 16px;
  border: none;
  outline: none;
  resize: vertical;
  font-family: var(--nurvo-font-family);
  font-size: 15px;
  line-height: 1.7;
  color: var(--nurvo-text-primary);
  background: transparent;
  transition: background 0.2s;
}

.record-textarea::placeholder {
  color: var(--nurvo-text-muted);
}

.record-textarea:focus {
  background: rgba(248, 250, 252, 0.82);
}

.record-textarea-card__footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 16px;
  border-top: 1px solid var(--nurvo-border-light);
}

.record-textarea-card__hint {
  font-size: 12px;
  color: var(--nurvo-text-muted);
}

.record-textarea-card__count {
  font-size: 12px;
  color: var(--nurvo-text-muted);
  font-variant-numeric: tabular-nums;
}

.record-textarea-card__count--valid {
  color: var(--nurvo-success-dark);
  font-weight: 600;
}

.record-error {
  background: rgba(254, 242, 242, 0.92);
  color: var(--nurvo-danger-dark);
  border: 1px solid var(--nurvo-danger-border);
  border-radius: 12px;
  padding: 10px 14px;
  font-size: 14px;
  margin-bottom: 16px;
}

.record-submit {
  display: flex;
  justify-content: center;
}

.record-btn-primary {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 48px;
  min-width: 190px;
  padding: 12px 26px;
  border: none;
  border-radius: 12px;
  background: var(--nurvo-gradient-primary);
  color: var(--nurvo-white);
  font-size: 15px;
  font-weight: 700;
  cursor: pointer;
  box-shadow: 0 12px 26px rgba(37, 99, 235, 0.28);
  transition: transform 0.2s ease, box-shadow 0.2s ease, opacity 0.2s ease;
}

.record-btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 16px 32px rgba(37, 99, 235, 0.34);
}

.record-btn-primary:disabled {
  opacity: 0.72;
  cursor: not-allowed;
}

.record-spinner {
  width: 18px;
  height: 18px;
  border: 2px solid rgba(255, 255, 255, 0.4);
  border-top-color: var(--nurvo-white);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

@media (max-width: 768px) {
  .record-shell {
    padding: 0 12px 24px;
  }

  .record-glass {
    padding: 18px;
    border-radius: 18px;
  }

  .record-title {
    font-size: 30px;
  }

  .record-subtitle {
    font-size: 14px;
  }

  .record-patient__info {
    flex-wrap: wrap;
  }
}
</style>
