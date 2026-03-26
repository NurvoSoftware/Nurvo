<script setup lang="ts">
import { computed } from 'vue'
import type { ChatMessage } from '@/types/game'

const props = defineProps<{
  patientName?: string
  familyName?: string
  latestMessage?: ChatMessage | null
}>()

const emit = defineEmits<{
  (e: 'select-target', target: 'patient' | 'family'): void
}>()

const showPatientBubble = computed<boolean>(() => props.latestMessage?.sender === 'patient')
const showFamilyBubble = computed<boolean>(() => props.latestMessage?.sender === 'family')
const truncatedContent = computed<string>(() => {
  if (!props.latestMessage) return ''
  const content: string = props.latestMessage.content
  return content.length > 60 ? content.slice(0, 60) + '...' : content
})
</script>

<template>
  <div class="scene-fallback-2d">
    <div class="fallback-banner">2D 簡化版場景</div>

    <div class="room">
      <!-- Wall -->
      <div class="wall">
        <div class="window">
          <div class="window-frame">
            <div class="window-pane"></div>
            <div class="window-pane"></div>
          </div>
        </div>
      </div>

      <!-- Floor -->
      <div class="floor"></div>

      <!-- Bed -->
      <div class="bed">
        <div class="bed-headboard"></div>
        <div class="bed-mattress"></div>
        <div class="bed-footboard"></div>
      </div>

      <!-- Patient -->
      <div
        class="character patient"
        role="button"
        :title="'點擊與' + (patientName || '病患') + '對話'"
        @click="emit('select-target', 'patient')"
      >
        <div v-if="showPatientBubble" class="speech-bubble speech-bubble--patient">
          <p>{{ truncatedContent }}</p>
        </div>
        <div class="person-head person-head--patient"></div>
        <div class="person-body person-body--patient"></div>
        <span class="character-label">{{ patientName || '病患' }}</span>
      </div>

      <!-- Family -->
      <div
        class="character family"
        role="button"
        :title="'點擊與' + (familyName || '家屬') + '對話'"
        @click="emit('select-target', 'family')"
      >
        <div v-if="showFamilyBubble" class="speech-bubble speech-bubble--family">
          <p>{{ truncatedContent }}</p>
        </div>
        <div class="person-head person-head--family"></div>
        <div class="person-body person-body--family"></div>
        <div class="person-legs"></div>
        <span class="character-label">{{ familyName || '家屬' }}</span>
      </div>

      <!-- Nurse -->
      <div class="character nurse">
        <div class="person-head person-head--nurse"></div>
        <div class="person-body person-body--nurse"></div>
        <div class="person-legs"></div>
        <span class="character-label">護理師（你）</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.scene-fallback-2d {
  width: 100%;
  height: 100%;
  min-height: 500px;
  background: var(--nurvo-patient-bg);
  overflow: hidden;
  position: relative;
}

.fallback-banner {
  position: absolute;
  top: 10px;
  left: 50%;
  transform: translateX(-50%);
  font-size: 11px;
  color: var(--nurvo-text-muted);
  background: rgba(255, 255, 255, 0.85);
  padding: 2px 12px;
  border-radius: var(--nurvo-radius-sm);
  z-index: 10;
  user-select: none;
}

.room {
  width: 100%;
  height: 100%;
  position: relative;
}

/* Wall */
.wall {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 55%;
  background: linear-gradient(180deg, var(--nurvo-patient-bg-alt) 0%, var(--nurvo-patient-light) 100%);
  border-bottom: 3px solid var(--nurvo-border);
}

.window {
  position: absolute;
  top: 15%;
  left: 10%;
  width: 120px;
  height: 100px;
  background: var(--nurvo-patient-bg);
  border: 4px solid var(--nurvo-text-muted);
  border-radius: var(--nurvo-radius-sm);
}

.window-frame {
  display: flex;
  width: 100%;
  height: 100%;
}

.window-pane {
  flex: 1;
  background: linear-gradient(135deg, var(--nurvo-patient-light), var(--nurvo-patient));
  border: 2px solid var(--nurvo-text-muted);
  opacity: 0.6;
}

/* Floor */
.floor {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 45%;
  background: linear-gradient(180deg, var(--nurvo-border) 0%, #cbd5e1 100%);
}

/* Bed */
.bed {
  position: absolute;
  top: 38%;
  left: 20%;
  width: 45%;
  height: 25%;
}

.bed-headboard {
  position: absolute;
  left: 0;
  top: 0;
  width: 8%;
  height: 100%;
  background: #a8a29e;
  border-radius: 4px 0 0 4px;
  border: 1px solid #78716c;
}

.bed-mattress {
  position: absolute;
  left: 8%;
  top: 15%;
  width: 84%;
  height: 70%;
  background: var(--nurvo-white);
  border: 2px solid #d1d5db;
  border-radius: 2px;
}

.bed-footboard {
  position: absolute;
  right: 0;
  top: 10%;
  width: 8%;
  height: 80%;
  background: #a8a29e;
  border-radius: 0 4px 4px 0;
  border: 1px solid #78716c;
}

/* Characters */
.character {
  position: absolute;
  display: flex;
  flex-direction: column;
  align-items: center;
  transition: transform 0.2s ease;
}

.character.patient,
.character.family {
  cursor: pointer;
}

.character.patient:hover,
.character.family:hover {
  transform: scale(1.05);
}

.character.patient { top: 34%; left: 32%; }
.character.family { top: 32%; right: 15%; }
.character.nurse { bottom: 8%; left: 50%; transform: translateX(-50%); cursor: default; }

/* Heads */
.person-head {
  border-radius: 50%;
  border: 2px solid;
}

.person-head--patient {
  width: 30px;
  height: 30px;
  background: var(--nurvo-patient);
  border-color: var(--nurvo-patient-dark);
}

.person-head--family {
  width: 28px;
  height: 28px;
  background: var(--nurvo-family);
  border-color: var(--nurvo-family-dark);
}

.person-head--nurse {
  width: 32px;
  height: 32px;
  background: var(--nurvo-nurse-light);
  border-color: var(--nurvo-primary);
}

/* Bodies */
.person-body--patient {
  width: 60px;
  height: 20px;
  background: var(--nurvo-patient-light);
  border-radius: 4px;
  margin-top: -2px;
  border: 1px solid var(--nurvo-patient);
}

.person-body--family {
  width: 36px;
  height: 40px;
  background: var(--nurvo-family);
  border-radius: 8px 8px 4px 4px;
  margin-top: 2px;
  border: 1px solid var(--nurvo-family-dark);
}

.person-body--nurse {
  width: 38px;
  height: 42px;
  background: var(--nurvo-white);
  border-radius: 8px 8px 4px 4px;
  margin-top: 2px;
  border: 1px solid var(--nurvo-border);
}

.person-legs {
  display: flex;
  gap: 6px;
  margin-top: 2px;
}

.person-legs::before,
.person-legs::after {
  content: '';
  width: 10px;
  height: 24px;
  background: var(--nurvo-text-muted);
  border-radius: 0 0 4px 4px;
}

.character-label {
  margin-top: 6px;
  font-size: 11px;
  color: var(--nurvo-text-secondary);
  white-space: nowrap;
  background: rgba(255, 255, 255, 0.85);
  padding: 2px 8px;
  border-radius: 4px;
}

.character.patient:hover .character-label,
.character.family:hover .character-label {
  color: var(--nurvo-text-primary);
  background: rgba(255, 255, 255, 0.95);
}

/* Speech bubbles */
.speech-bubble {
  position: absolute;
  bottom: 110%;
  left: 50%;
  transform: translateX(-50%);
  padding: 8px 12px;
  border-radius: var(--nurvo-radius-sm);
  font-size: 11px;
  max-width: 200px;
  min-width: 100px;
  text-align: center;
  animation: fadeInUp 0.3s ease;
  z-index: 5;
  box-shadow: var(--nurvo-shadow-sm);
}

.speech-bubble::after {
  content: '';
  position: absolute;
  bottom: -6px;
  left: 50%;
  transform: translateX(-50%);
  width: 0;
  height: 0;
  border-left: 6px solid transparent;
  border-right: 6px solid transparent;
}

.speech-bubble--patient {
  background: var(--nurvo-white);
  color: var(--nurvo-text-primary);
  border: 1px solid var(--nurvo-border);
}

.speech-bubble--patient::after {
  border-top: 6px solid var(--nurvo-white);
}

.speech-bubble--family {
  background: var(--nurvo-family-bg);
  color: var(--nurvo-family-text-dark);
  border: 1px solid var(--nurvo-warning-border);
}

.speech-bubble--family::after {
  border-top: 6px solid var(--nurvo-family-bg);
}

.speech-bubble p {
  margin: 0;
  line-height: 1.4;
}

@keyframes fadeInUp {
  from { opacity: 0; transform: translateX(-50%) translateY(8px); }
  to { opacity: 1; transform: translateX(-50%) translateY(0); }
}
</style>
