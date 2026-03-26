<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
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
const remainingSeconds = ref<number>(0)
const timerExpired = ref<boolean>(false)
let timerInterval: ReturnType<typeof setInterval> | null = null

const charCount = computed<number>(() => content.value.trim().length)
const isValid = computed<boolean>(() => charCount.value > 0)

const formattedTime = computed<string>(() => {
  const minutes: number = Math.floor(remainingSeconds.value / 60)
  const seconds: number = remainingSeconds.value % 60
  return `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`
})

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

function startTimer(): void {
  if (!scenarioStore.scenario) return
  remainingSeconds.value = scenarioStore.scenario.time_limit_seconds

  timerInterval = setInterval(() => {
    if (remainingSeconds.value > 0) {
      remainingSeconds.value--
    } else {
      if (timerInterval) clearInterval(timerInterval)
    }
  }, 1000)
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

  startTimer()
})

onBeforeUnmount(() => {
  if (timerInterval) {
    clearInterval(timerInterval)
  }
})
</script>

<template>
  <div class="record-page">
    <NavBar :step="2" />

    <div class="nurvo-page-container nurvo-page-container--narrow">
      <!-- Header -->
      <header class="record-header">
        <h1 class="nurvo-page-title">病患記錄</h1>
        <p class="nurvo-page-subtitle">根據對話內容撰寫評估摘要</p>
      </header>

      <!-- Timer-expired alert (conditional) -->
      <div v-if="timerExpired" class="record-alert">
        <div class="record-alert__icon">&#x23F0;</div>
        <div class="record-alert__body">
          <div class="record-alert__title">時間到！</div>
          <div class="record-alert__text">請完成以下病患記錄</div>
        </div>
      </div>

      <!-- Patient reminder card -->
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

      <!-- Textarea card -->
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

      <!-- Error message -->
      <div v-if="errorMsg" class="record-error">
        {{ errorMsg }}
      </div>

      <!-- Submit button -->
      <div class="record-submit">
        <button
          class="nurvo-btn-primary"
          :disabled="!isValid || submitting"
          @click="handleSubmit"
        >
          <span v-if="submitting" class="nurvo-spinner"></span>
          <template v-else>提交記錄 &rarr;</template>
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.record-page {
  min-height: 100vh;
  background: var(--nurvo-white);
}

/* Header */
.record-header {
  text-align: center;
  margin-bottom: 20px;
}

/* Timer-expired alert */
.record-alert {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  background: var(--nurvo-warning-light);
  border: 1px solid var(--nurvo-warning-border);
  border-radius: var(--nurvo-radius-md);
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
  font-size: var(--nurvo-font-size-lg);
  font-weight: 700;
  color: var(--nurvo-warning-darker);
}

.record-alert__text {
  font-size: var(--nurvo-font-size-base);
  color: var(--nurvo-warning-dark);
}

/* Patient reminder */
.record-patient {
  display: flex;
  align-items: center;
  gap: 10px;
  background: var(--nurvo-white);
  border: 1px solid var(--nurvo-border);
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
  font-size: var(--nurvo-font-size-base);
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

/* Textarea card */
.record-textarea-card {
  background: var(--nurvo-white);
  border: 1px solid var(--nurvo-border);
  border-radius: var(--nurvo-radius-lg);
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
  font-size: var(--nurvo-font-size-md);
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
  font-size: var(--nurvo-font-size-base);
  line-height: 1.7;
  color: var(--nurvo-text-primary);
  background: transparent;
  transition: background 0.2s;
}

.record-textarea::placeholder {
  color: var(--nurvo-text-muted);
}

.record-textarea:focus {
  background: var(--nurvo-surface);
}

.record-textarea-card__footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 16px;
  border-top: 1px solid var(--nurvo-border-light);
}

.record-textarea-card__hint {
  font-size: var(--nurvo-font-size-sm);
  color: var(--nurvo-text-muted);
}

.record-textarea-card__count {
  font-size: var(--nurvo-font-size-sm);
  color: var(--nurvo-text-muted);
  font-variant-numeric: tabular-nums;
}

.record-textarea-card__count--valid {
  color: var(--nurvo-success-dark);
  font-weight: 600;
}

/* Error */
.record-error {
  background: var(--nurvo-danger-light);
  color: var(--nurvo-danger-dark);
  border: 1px solid var(--nurvo-danger-border);
  border-radius: var(--nurvo-radius-md);
  padding: 10px 14px;
  font-size: var(--nurvo-font-size-base);
  margin-bottom: 16px;
}

/* Submit */
.record-submit {
  display: flex;
  justify-content: center;
}
</style>
