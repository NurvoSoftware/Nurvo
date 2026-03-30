<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount, defineAsyncComponent } from 'vue'
import { useRouter } from 'vue-router'
import { useScenarioStore } from '@/stores/scenarioStore'
import { useGameStore } from '@/stores/gameStore'
import { useChatStore } from '@/stores/chatStore'
import { connect, disconnect, onTimerUpdate, onTimerExpired } from '@/services/wsService'
import { stop as stopAudio } from '@/services/audioService'
import SceneFallback2D from '@/components/game/SceneFallback2D.vue'
import ChatPanel from '@/components/game/ChatPanel.vue'
import PatientCard from '@/components/game/PatientCard.vue'
import TimerBar from '@/components/game/TimerBar.vue'
import Dialog from 'primevue/dialog'
import type { ChatMessage, FamilySender } from '@/types/game'

const SceneCanvas3D = defineAsyncComponent(() => import('@/components/game/SceneCanvas3D.vue'))

function isWebGL2Available(): boolean {
  try {
    const canvas = document.createElement('canvas')
    return !!canvas.getContext('webgl2')
  } catch { return false }
}

const webglSupported = isWebGL2Available()

const router = useRouter()
const scenarioStore = useScenarioStore()
const gameStore = useGameStore()
const chatStore = useChatStore()

const showPatientInfo = ref<boolean>(false)
const remainingSeconds = ref<number>(480)
let timerInterval: ReturnType<typeof setInterval> | null = null

const scenarioTitle = computed<string>(() => {
  if (!scenarioStore.scenario) return ''
  return `${scenarioStore.scenario.patient_profile.name} - ${scenarioStore.scenario.patient_profile.diagnosis}`
})

const latestNpcMessage = computed<ChatMessage | null>(() => {
  const npcMessages = chatStore.messages.filter((m: ChatMessage) => m.sender !== 'nurse')
  return npcMessages.length > 0 ? npcMessages[npcMessages.length - 1] : null
})

function handleSelectTarget(target: 'patient' | FamilySender): void {
  chatStore.setTarget(target)
}

function handleTimerExpired(): void {
  stopAudio()
  gameStore.setStatus('recording')
  router.push({ path: '/record', query: { expired: '1' } })
}

onMounted(() => {
  if (!scenarioStore.scenario || !gameStore.sessionId) {
    router.replace('/')
    return
  }

  if (scenarioStore.scenario) {
    remainingSeconds.value = scenarioStore.scenario.time_limit_seconds
  }

  chatStore.clearMessages()
  connect(gameStore.sessionId)

  timerInterval = setInterval(() => {
    if (remainingSeconds.value > 0) {
      remainingSeconds.value--
    } else {
      if (timerInterval) clearInterval(timerInterval)
    }
  }, 1000)

  onTimerUpdate((seconds: number) => {
    remainingSeconds.value = seconds
  })

  onTimerExpired(() => {
    handleTimerExpired()
  })
})

onBeforeUnmount(() => {
  if (timerInterval) {
    clearInterval(timerInterval)
  }
  disconnect()
})
</script>

<template>
  <div class="scene" v-if="scenarioStore.scenario">
    <!-- Custom Toolbar -->
    <div class="scene-toolbar">
      <div class="toolbar-left">
        <div class="toolbar-logo">
          <div class="nurvo-nav-logo-icon">N</div>
          <span class="toolbar-title">{{ scenarioTitle }}</span>
        </div>
        <div class="toolbar-divider"></div>
        <div class="toolbar-status">
          <div class="status-dot" :class="{ 'status-dot--connected': chatStore.isConnected }"></div>
          <span class="status-text" :class="{ 'status-text--connected': chatStore.isConnected }">
            {{ chatStore.isConnected ? '已連線' : '連線中...' }}
          </span>
        </div>
      </div>
      <div class="toolbar-right">
        <button class="patient-info-btn" @click="showPatientInfo = true">
          &#x1F4CB; 病患資訊
        </button>
        <TimerBar
          :remaining-seconds="remainingSeconds"
          @expired="handleTimerExpired"
        />
      </div>
    </div>

    <!-- Patient info Dialog -->
    <Dialog
      v-model:visible="showPatientInfo"
      header="病患資訊"
      modal
      appendTo="body"
      :style="{ width: '500px' }"
    >
      <PatientCard
        :patient="scenarioStore.scenario.patient_profile"
        :pain-severity="scenarioStore.scenario.pain_details.severity"
      />
    </Dialog>

    <!-- Main layout: 60/40 split -->
    <div class="scene-layout">
      <div class="scene-left">
        <SceneCanvas3D
          v-if="webglSupported"
          :patient-name="scenarioStore.scenario.patient_profile.name"
          :family-members="scenarioStore.scenario.family_members"
          :latest-message="latestNpcMessage"
          @select-target="handleSelectTarget"
        />
        <SceneFallback2D
          v-else
          :patient-name="scenarioStore.scenario.patient_profile.name"
          :family-members="scenarioStore.scenario.family_members"
          :latest-message="latestNpcMessage"
          @select-target="handleSelectTarget"
        />
      </div>
      <div class="scene-right">
        <ChatPanel />
      </div>
    </div>
  </div>
</template>

<style scoped>
.scene {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--nurvo-white);
  overflow: hidden;
}

/* Toolbar */
.scene-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 16px;
  background: var(--nurvo-white);
  border-bottom: 1px solid var(--nurvo-border);
  flex-shrink: 0;
}

.toolbar-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.toolbar-logo {
  display: flex;
  align-items: center;
  gap: 6px;
}

.toolbar-title {
  font-size: 12px;
  font-weight: 600;
  color: var(--nurvo-text-primary);
}

.toolbar-divider {
  width: 1px;
  height: 16px;
  background: var(--nurvo-border);
}

.toolbar-status {
  display: flex;
  align-items: center;
  gap: 4px;
}

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--nurvo-warning);
}

.status-dot--connected {
  background: var(--nurvo-success);
}

.status-text {
  font-size: 10px;
  color: var(--nurvo-warning);
  font-weight: 500;
}

.status-text--connected {
  color: var(--nurvo-success);
}

.toolbar-right {
  display: flex;
  align-items: center;
  gap: 10px;
}

.patient-info-btn {
  background: var(--nurvo-surface);
  padding: 4px 10px;
  border-radius: var(--nurvo-radius-sm);
  font-size: 10px;
  color: var(--nurvo-text-secondary);
  border: 1px solid var(--nurvo-border);
  cursor: pointer;
  font-family: var(--nurvo-font-family);
  transition: background 0.2s;
}

.patient-info-btn:hover {
  background: var(--nurvo-border-light);
}

/* Main layout */
.scene-layout {
  flex: 1;
  display: flex;
  overflow: hidden;
}

.scene-left {
  flex: 6;
  overflow: hidden;
  border-right: 1px solid var(--nurvo-border);
}

.scene-right {
  flex: 4;
  min-width: 300px;
}
</style>
