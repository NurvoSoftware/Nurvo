<script setup lang="ts">
import { onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useScenarioStore } from '@/stores/scenarioStore'
import { useGameStore } from '@/stores/gameStore'
import NavBar from '@/components/shared/NavBar.vue'
import PatientCard from '@/components/game/PatientCard.vue'
import { unlock as unlockAudio } from '@/services/audioService'

const router = useRouter()
const scenarioStore = useScenarioStore()
const gameStore = useGameStore()

const timeLimit = computed<number>(() => {
  if (!scenarioStore.scenario) return 0
  return Math.floor(scenarioStore.scenario.time_limit_seconds / 60)
})

const painSeverity = computed<number | undefined>(() => {
  return scenarioStore.scenario?.pain_details?.severity
})

onMounted(() => {
  if (!scenarioStore.scenario) {
    console.warn('[BriefingView] No scenario data found, redirecting to home')
    router.replace('/')
  }
})

function enterScene(): void {
  unlockAudio()
  gameStore.setStatus('playing')
  router.push('/scene')
}
</script>

<template>
  <div class="briefing-page" v-if="scenarioStore.scenario">
    <NavBar :step="1" />

    <div class="briefing-container">
      <!-- Header -->
      <header class="briefing-header">
        <h1 class="briefing-title">任務簡報</h1>
        <p class="briefing-subtitle">請仔細閱讀以下病患資料，準備進入溝通場景</p>
      </header>

      <!-- Patient card -->
      <PatientCard
        :patient="scenarioStore.scenario.patient_profile"
        :pain-severity="painSeverity"
      />

      <!-- Family members row -->
      <div class="family-row">
        <div
          v-for="(fm, idx) in scenarioStore.scenario.family_members"
          :key="idx"
          class="info-card family-card"
        >
          <div class="info-card-header">
            <div class="family-avatar">&#x1F464;</div>
            <div class="family-name-block">
              <span class="family-name">{{ fm.name }}</span>
              <span class="family-rel">{{ fm.relationship }}</span>
            </div>
          </div>
          <div class="family-tags">
            <span class="ftag">{{ fm.personality }}</span>
            <span class="ftag">{{ fm.emotional_state }}</span>
          </div>
        </div>
      </div>

      <!-- Communication goals card -->
      <div class="two-col-row">
        <div class="info-card goals-card">
          <div class="goals-title">&#x1F3AF; 溝通挑戰</div>
          <ul class="goals-list">
            <li
              v-for="challenge in scenarioStore.scenario.communication_challenges"
              :key="challenge"
            >{{ challenge }}</li>
          </ul>
        </div>
      </div>

      <!-- Bottom action bar -->
      <div class="action-bar">
        <div class="time-info">
          <span class="time-icon">&#x23F1;</span>
          <span class="time-text">限時 {{ timeLimit }} 分鐘</span>
        </div>
        <button class="cta-button" @click="enterScene">
          進入場景 <span class="cta-arrow">&rarr;</span>
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.briefing-page {
  min-height: 100vh;
  background: var(--nurvo-white);
}

.briefing-container {
  max-width: 680px;
  margin: 0 auto;
  padding: 24px 20px 40px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* ---- Header ---- */
.briefing-header {
  text-align: center;
  margin-bottom: 4px;
}

.briefing-title {
  font-size: var(--nurvo-font-size-2xl);
  font-weight: 700;
  color: var(--nurvo-text-primary);
  margin: 0 0 6px 0;
}

.briefing-subtitle {
  font-size: var(--nurvo-font-size-md);
  color: var(--nurvo-text-secondary);
  margin: 0;
}

/* ---- Family members row ---- */
.family-row {
  display: flex;
  gap: 14px;
}

/* ---- Two-column row ---- */
.two-col-row {
  display: flex;
  gap: 14px;
}

.info-card {
  flex: 1;
  border: 1px solid var(--nurvo-border);
  border-radius: var(--nurvo-radius-md);
  padding: 16px;
  box-shadow: var(--nurvo-shadow-xs);
}

/* Family card */
.family-card {
  background: var(--nurvo-family-bg);
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.info-card-header {
  display: flex;
  align-items: center;
  gap: 10px;
}

.family-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--nurvo-family), var(--nurvo-family-dark));
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 15px;
  flex-shrink: 0;
}

.family-name-block {
  display: flex;
  flex-direction: column;
  gap: 1px;
}

.family-name {
  font-size: var(--nurvo-font-size-lg);
  font-weight: 700;
  color: var(--nurvo-text-primary);
  line-height: 1.3;
}

.family-rel {
  font-size: var(--nurvo-font-size-base);
  color: var(--nurvo-family-text);
  line-height: 1.3;
}

.family-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.ftag {
  display: inline-block;
  font-size: var(--nurvo-font-size-base);
  font-weight: 500;
  padding: 3px 10px;
  border-radius: var(--nurvo-radius-pill);
  background: var(--nurvo-warning-bg);
  color: var(--nurvo-warning-darker);
  border: 1px solid var(--nurvo-warning-border);
  line-height: 1.5;
}

/* Goals card */
.goals-card {
  background: var(--nurvo-white);
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.goals-title {
  font-size: var(--nurvo-font-size-lg);
  font-weight: 700;
  color: var(--nurvo-text-primary);
}

.goals-list {
  margin: 0;
  padding-left: 18px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.goals-list li {
  font-size: var(--nurvo-font-size-md);
  color: var(--nurvo-text-secondary);
  line-height: 1.5;
}

/* ---- Action bar ---- */
.action-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: var(--nurvo-surface);
  border: 1px solid var(--nurvo-border);
  border-radius: var(--nurvo-radius-md);
  padding: 14px 20px;
  margin-top: 4px;
}

.time-info {
  display: flex;
  align-items: center;
  gap: 6px;
}

.time-icon {
  font-size: 18px;
}

.time-text {
  font-size: var(--nurvo-font-size-md);
  font-weight: 600;
  color: var(--nurvo-text-secondary);
}

.cta-button {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: var(--nurvo-gradient-primary);
  color: var(--nurvo-white);
  border: none;
  border-radius: var(--nurvo-radius-sm);
  padding: 10px 24px;
  font-size: var(--nurvo-font-size-lg);
  font-weight: 700;
  cursor: pointer;
  box-shadow: var(--nurvo-shadow-button);
  transition: opacity 0.15s ease, transform 0.15s ease;
}

.cta-button:hover {
  opacity: 0.92;
  transform: translateY(-1px);
}

.cta-button:active {
  transform: translateY(0);
}

.cta-arrow {
  font-size: 16px;
}

/* ---- Responsive ---- */
@media (max-width: 540px) {
  .family-row {
    flex-direction: column;
  }

  .two-col-row {
    flex-direction: column;
  }

  .action-bar {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
    text-align: center;
  }

  .time-info {
    justify-content: center;
  }
}
</style>
