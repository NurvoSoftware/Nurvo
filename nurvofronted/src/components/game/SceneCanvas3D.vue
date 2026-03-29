<script setup lang="ts">
import { computed } from 'vue'
import type { ChatMessage } from '@/types/game'
import { TresCanvas } from '@tresjs/core'
import { Html } from '@tresjs/cientos'
import CharacterModel from './CharacterModel.vue'

const props = defineProps<{
  patientName?: string
  familyName?: string
  latestMessage?: ChatMessage | null
}>()

const emit = defineEmits<{
  (e: 'select-target', target: 'patient' | 'family'): void
}>()

const showPatientBubble = computed(() => props.latestMessage?.sender === 'patient')
const showFamilyBubble = computed(() => props.latestMessage?.sender === 'family')
const truncatedContent = computed(() => {
  if (!props.latestMessage) return ''
  const content = props.latestMessage.content
  return content.length > 60 ? content.slice(0, 60) + '...' : content
})

const patientAnimState = computed(() =>
  props.latestMessage?.sender === 'patient' ? 'speaking' : 'idle'
)
const familyAnimState = computed(() =>
  props.latestMessage?.sender === 'family' ? 'speaking' : 'idle'
)
</script>

<template>
  <div class="scene-3d-container">
    <TresCanvas shadows :style="{ background: 'linear-gradient(180deg, #e6f0fa 0%, #edf6ff 42%, #d8e2ee 100%)' }">
      <!-- Camera -->
      <TresPerspectiveCamera :position="[0, 3, 6]" :look-at="[0, 1, 0]" />

      <!-- Lighting -->
      <TresAmbientLight :intensity="0.68" />
      <TresDirectionalLight :position="[3, 5, 4]" :intensity="0.76" cast-shadow />

      <!-- Floor -->
      <TresMesh :rotation="[-Math.PI / 2, 0, 0]" :position="[0, 0, 0]" receive-shadow>
        <TresPlaneGeometry :args="[10, 8]" />
        <TresMeshStandardMaterial color="#d6dde7" />
      </TresMesh>

      <!-- Back Wall -->
      <TresMesh :position="[0, 2, -4]">
        <TresPlaneGeometry :args="[10, 4]" />
        <TresMeshStandardMaterial color="#e5eff9" />
      </TresMesh>

      <!-- Window on back wall -->
      <TresMesh :position="[3, 2.5, -3.98]">
        <TresPlaneGeometry :args="[1.5, 1.2]" />
        <TresMeshStandardMaterial color="#c7e7ff" />
      </TresMesh>
      <TresMesh :position="[3, 2.5, -3.97]">
        <TresPlaneGeometry :args="[1.6, 1.3]" />
        <TresMeshStandardMaterial color="#8da0b6" />
      </TresMesh>

      <!-- Hospital Bed -->
      <TresGroup :position="[-0.5, 0.4, -1]">
        <TresMesh :position="[0, 0, 0]">
          <TresBoxGeometry :args="[2, 0.15, 1]" />
          <TresMeshStandardMaterial color="#ffffff" />
        </TresMesh>
        <TresMesh :position="[-1.05, 0.3, 0]">
          <TresBoxGeometry :args="[0.1, 0.75, 1]" />
          <TresMeshStandardMaterial color="#94a3b8" />
        </TresMesh>
        <TresMesh :position="[1.05, 0.15, 0]">
          <TresBoxGeometry :args="[0.1, 0.45, 1]" />
          <TresMeshStandardMaterial color="#94a3b8" />
        </TresMesh>
        <TresMesh :position="[-0.9, -0.25, 0.4]">
          <TresCylinderGeometry :args="[0.03, 0.03, 0.3, 8]" />
          <TresMeshStandardMaterial color="#64748b" />
        </TresMesh>
        <TresMesh :position="[0.9, -0.25, 0.4]">
          <TresCylinderGeometry :args="[0.03, 0.03, 0.3, 8]" />
          <TresMeshStandardMaterial color="#64748b" />
        </TresMesh>
        <TresMesh :position="[-0.9, -0.25, -0.4]">
          <TresCylinderGeometry :args="[0.03, 0.03, 0.3, 8]" />
          <TresMeshStandardMaterial color="#64748b" />
        </TresMesh>
        <TresMesh :position="[0.9, -0.25, -0.4]">
          <TresCylinderGeometry :args="[0.03, 0.03, 0.3, 8]" />
          <TresMeshStandardMaterial color="#64748b" />
        </TresMesh>
      </TresGroup>

      <!-- Patient Character -->
      <CharacterModel
        type="patient"
        :position="[-0.5, 0.6, -1]"
        :rotation="[0, 0, Math.PI / 2]"
        :colors="{ head: '#fbbf24', body: '#7dd3fc', arms: '#7dd3fc', legs: '#64748b', accent: '#7dd3fc' }"
        :animation-state="patientAnimState"
        :label="patientName || '病患'"
        :is-clickable="true"
        @click="emit('select-target', 'patient')"
      />

      <!-- Family Character -->
      <CharacterModel
        type="family"
        :position="[2, 0, -0.5]"
        :rotation="[0, -0.3, 0]"
        :colors="{ head: '#fbbf24', body: '#fde68a', arms: '#fde68a', legs: '#64748b', accent: '#fde68a' }"
        :animation-state="familyAnimState"
        :label="familyName || '家屬'"
        :is-clickable="true"
        @click="emit('select-target', 'family')"
      />

      <!-- Nurse Character -->
      <CharacterModel
        type="nurse"
        :position="[0, 0, 2]"
        :rotation="[0, Math.PI, 0]"
        :colors="{ head: '#fbbf24', body: '#dbeafe', arms: '#dbeafe', legs: '#64748b', accent: '#2563eb' }"
        animation-state="idle"
        label="護理師（你）"
        :is-clickable="false"
      />

      <!-- Speech Bubbles -->
      <TresGroup v-if="showPatientBubble" :position="[-0.5, 2.5, -1]">
        <Html center :distance-factor="8">
          <div class="speech-bubble speech-bubble--patient">
            <p>{{ truncatedContent }}</p>
          </div>
        </Html>
      </TresGroup>

      <TresGroup v-if="showFamilyBubble" :position="[2, 2.5, -0.5]">
        <Html center :distance-factor="8">
          <div class="speech-bubble speech-bubble--family">
            <p>{{ truncatedContent }}</p>
          </div>
        </Html>
      </TresGroup>
    </TresCanvas>
  </div>
</template>

<style scoped>
.scene-3d-container {
  width: 100%;
  height: 100%;
  min-height: 500px;
  overflow: hidden;
  position: relative;
}

.speech-bubble {
  padding: 8px 14px;
  border-radius: 10px;
  font-size: 11px;
  max-width: 200px;
  min-width: 100px;
  text-align: center;
  pointer-events: none;
  animation: fadeIn 0.3s ease;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.speech-bubble p {
  margin: 0;
  line-height: 1.4;
}

.speech-bubble--patient {
  background: white;
  color: var(--nurvo-text-primary, #0f172a);
  border: 1px solid #e2e8f0;
}

.speech-bubble--family {
  background: #fffbeb;
  color: #713f12;
  border: 1px solid #fde68a;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(5px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
