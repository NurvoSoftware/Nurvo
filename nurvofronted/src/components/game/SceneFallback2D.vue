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
  background-image:
    linear-gradient(180deg, rgba(8, 47, 73, 0.08) 0%, rgba(2, 6, 23, 0.18) 100%),
    url('/hospital_bg.jpg');
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  overflow: hidden;
  position: relative;
}

.room {
  width: 100%;
  height: 100%;
  position: relative;
}

.wall,
.floor,
.bed,
.person-head,
.person-body,
.person-legs,
.character.nurse {
  display: none;
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
  justify-content: flex-end;
  width: 110px;
  height: 130px;
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

.character.patient { top: 36%; left: 28%; }
.character.family { top: 34%; left: 44%; }

.character-label {
  margin-top: 0;
  font-size: 14px;
  color: #0f172a;
  font-weight: 700;
  white-space: nowrap;
  background: rgba(255, 255, 255, 0.92);
  padding: 6px 10px;
  border-radius: 999px;
  border: 1px solid rgba(186, 230, 253, 0.95);
  box-shadow: 0 8px 18px rgba(15, 23, 42, 0.16);
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
  font-size: 13px;
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
