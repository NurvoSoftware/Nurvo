<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
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
import type { ChatMessage } from '@/types/game'

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
  const lastMessage = npcMessages[npcMessages.length - 1]
  return lastMessage ?? null
})

function handleSelectTarget(target: 'patient' | 'family'): void {
  chatStore.setTarget(target)
}

function handleTimerExpired(): void {
  stopAudio()
  gameStore.setStatus('recording')
  router.push({ path: '/record', query: { expired: '1' } })
}

function interruptGame(): void {
  const confirmed = window.confirm('確定要中斷本次遊戲嗎？目前進度將不會保留。')
  if (!confirmed) return

  stopAudio()
  chatStore.reset()
  scenarioStore.reset()
  gameStore.reset()
  router.push('/')
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
    <div class="bg-glow bg-glow--left"></div>
    <div class="bg-glow bg-glow--right"></div>

    <div class="scene-toolbar">
      <div class="toolbar-left">
        <div class="toolbar-logo">
          <div class="toolbar-logo-icon">N</div>
          <span class="toolbar-brand">Nurvo</span>
        </div>
        <div class="toolbar-title-wrap">
          <span class="toolbar-title">{{ scenarioTitle }}</span>
        </div>
        <div class="toolbar-status">
          <div class="status-dot" :class="{ 'status-dot--connected': chatStore.isConnected }"></div>
          <span class="status-text" :class="{ 'status-text--connected': chatStore.isConnected }">
            {{ chatStore.isConnected ? '已連線' : '連線中...' }}
          </span>
        </div>
      </div>
      <div class="toolbar-right">
        <button class="interrupt-btn" @click="interruptGame">中斷遊戲</button>
        <button class="patient-info-btn" @click="showPatientInfo = true">
          &#x1F4CB; 病患資訊
        </button>
        <TimerBar
          :remaining-seconds="remainingSeconds"
          @expired="handleTimerExpired"
        />
      </div>
    </div>

    <div class="scene-main">
      <div class="scene-map">
        <!--
        <SceneCanvas3D
          v-if="webglSupported"
          :patient-name="scenarioStore.scenario.patient_profile.name"
          :family-name="scenarioStore.scenario.family_member.name"
          :latest-message="latestNpcMessage"
          @select-target="handleSelectTarget"
        />
        -->
        <SceneFallback2D
          :patient-name="scenarioStore.scenario.patient_profile.name"
          :family-name="scenarioStore.scenario.family_member.name"
          :latest-message="latestNpcMessage"
          @select-target="handleSelectTarget"
        />
      </div>

      <aside class="chat-dock">
        <div class="chat-glass">
          <ChatPanel />
        </div>
      </aside>
    </div>

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

  </div>
</template>

<style scoped>
.scene {
  height: 100vh;
  display: flex;
  flex-direction: column;
  position: relative;
  background:
    radial-gradient(circle at 18% 12%, #dbeafe 0%, transparent 30%),
    radial-gradient(circle at 84% 8%, #e0f2fe 0%, transparent 34%),
    #f8fbff;
  overflow: hidden;
}

.bg-glow {
  position: absolute;
  border-radius: 50%;
  filter: blur(52px);
  pointer-events: none;
  opacity: 0.36;
}

.bg-glow--left {
  width: 290px;
  height: 290px;
  left: -100px;
  top: 74px;
  background: #60a5fa;
}

.bg-glow--right {
  width: 320px;
  height: 320px;
  right: -120px;
  top: 66px;
  background: #7dd3fc;
}

.scene-toolbar {
  position: relative;
  z-index: 3;
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 0;
  padding: 13px 20px;
  background: rgba(255, 255, 255, 0.9);
  border-bottom: 1px solid rgba(203, 213, 225, 0.85);
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
  gap: 8px;
}

.toolbar-logo-icon {
  width: 32px;
  height: 32px;
  border-radius: 10px;
  background: var(--nurvo-gradient-logo);
  color: var(--nurvo-white);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 15px;
  font-weight: 800;
  box-shadow: 0 10px 20px rgba(37, 99, 235, 0.24);
}

.toolbar-brand {
  font-size: 18px;
  font-weight: 800;
  letter-spacing: -0.01em;
  color: var(--nurvo-text-primary);
}

.toolbar-title-wrap {
  max-width: 520px;
}

.toolbar-title {
  display: block;
  font-size: 14px;
  font-weight: 600;
  color: #1e293b;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.toolbar-divider {
  display: none;
}

.toolbar-status {
  display: flex;
  align-items: center;
  gap: 5px;
}

.status-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: var(--nurvo-warning);
  box-shadow: 0 0 0 4px rgba(245, 158, 11, 0.15);
}

.status-dot--connected {
  background: var(--nurvo-success);
  box-shadow: 0 0 0 4px rgba(34, 197, 94, 0.16);
}

.status-text {
  font-size: 13px;
  color: var(--nurvo-warning);
  font-weight: 600;
}

.status-text--connected {
  color: var(--nurvo-success);
}

.toolbar-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.interrupt-btn {
  background: rgba(254, 242, 242, 0.95);
  padding: 7px 14px;
  border-radius: 10px;
  font-size: 13px;
  color: #b91c1c;
  border: 1px solid rgba(252, 165, 165, 0.85);
  cursor: pointer;
  font-family: var(--nurvo-font-family);
  font-weight: 700;
  transition: border-color 0.2s ease, transform 0.2s ease, background 0.2s ease;
}

.interrupt-btn:hover {
  background: #ffffff;
  border-color: #f87171;
  transform: translateY(-1px);
}

.patient-info-btn {
  background: rgba(248, 250, 252, 0.94);
  padding: 7px 14px;
  border-radius: 10px;
  font-size: 13px;
  color: #334155;
  border: 1px solid #dbeafe;
  cursor: pointer;
  font-family: var(--nurvo-font-family);
  transition: border-color 0.2s ease, transform 0.2s ease, background 0.2s ease;
}

.patient-info-btn:hover {
  background: #ffffff;
  border-color: #93c5fd;
  transform: translateY(-1px);
}

.scene-main {
  position: relative;
  flex: 1;
  min-height: 0;
  overflow: hidden;
}

.scene-map {
  height: 100%;
  border-top: 1px solid rgba(219, 234, 254, 0.7);
  overflow: hidden;
  background: linear-gradient(180deg, #edf6ff 0%, #eef2ff 42%, #e2e8f0 100%);
}

.chat-dock {
  position: absolute;
  top: 26px;
  right: clamp(26px, 3.6vw, 56px);
  width: min(420px, 34vw);
  height: calc(100% - 52px);
  z-index: 2;
}

.chat-glass {
  position: relative;
  height: 100%;
  border-radius: 18px;
  border: 1px solid rgba(191, 219, 254, 0.72);
  background: linear-gradient(
    160deg,
    rgba(255, 255, 255, 0.36) 0%,
    rgba(255, 255, 255, 0.2) 100%
  );
  backdrop-filter: blur(22px) saturate(130%);
  -webkit-backdrop-filter: blur(22px) saturate(130%);
  box-shadow: 0 18px 42px rgba(15, 23, 42, 0.14);
  overflow: hidden;
}

.chat-glass::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(
    180deg,
    rgba(255, 255, 255, 0.34) 0%,
    rgba(255, 255, 255, 0) 36%
  );
  pointer-events: none;
  z-index: 1;
}

.chat-glass > * {
  position: relative;
  z-index: 2;
}

@media (max-width: 980px) {
  .chat-dock {
    position: static;
    width: 100%;
    height: 340px;
    padding: 12px;
    background: transparent;
  }

  .scene-main {
    display: flex;
    flex-direction: column;
  }

  .scene-map {
    height: calc(100% - 340px);
    min-height: 280px;
  }
}

@media (max-width: 768px) {
  .scene-toolbar {
    padding: 10px 12px;
  }

  .toolbar-left {
    gap: 8px;
  }

  .toolbar-title-wrap,
  .toolbar-status {
    display: none;
  }

  .chat-dock {
    height: 46vh;
    min-height: 280px;
    padding: 8px;
  }

  .chat-glass {
    border-radius: 14px;
  }
}
</style>
