<script setup lang="ts">
import { shallowRef } from 'vue'
import { useLoop } from '@tresjs/core'

export interface CharacterColors {
  head: string
  body: string
  arms: string
  legs: string
  accent: string
}

const props = withDefaults(defineProps<{
  type: 'nurse' | 'patient' | 'family'
  position?: [number, number, number]
  rotation?: [number, number, number]
  colors: CharacterColors
  animationState?: 'idle' | 'speaking' | 'waving'
  label: string
  isClickable?: boolean
}>(), {
  position: () => [0, 0, 0] as [number, number, number],
  rotation: () => [0, 0, 0] as [number, number, number],
  animationState: 'idle',
  isClickable: false,
})

const emit = defineEmits<{
  click: []
}>()

const groupRef = shallowRef()
const rightArmRef = shallowRef()

const { onBeforeRender } = useLoop()

onBeforeRender(({ elapsed }) => {
  if (!groupRef.value) return

  if (props.animationState === 'idle') {
    // Gentle breathing: small Y oscillation
    groupRef.value.position.y = props.position[1] + Math.sin(elapsed * 2) * 0.02
  }

  if (props.animationState === 'speaking') {
    // Speaking: slight body scale pulse
    const s = 1 + Math.sin(elapsed * 6) * 0.015
    groupRef.value.scale.set(s, 1, s)
  } else {
    groupRef.value.scale.set(1, 1, 1)
  }

  if (props.animationState === 'waving' && rightArmRef.value) {
    // Waving: rotate right arm
    rightArmRef.value.rotation.z = Math.sin(elapsed * 5) * 0.5
  } else if (rightArmRef.value) {
    rightArmRef.value.rotation.z = 0
  }
})

function onClick(): void {
  if (props.isClickable) {
    emit('click')
  }
}

function onPointerEnter(): void {
  if (props.isClickable) {
    document.body.style.cursor = 'pointer'
  }
}

function onPointerLeave(): void {
  document.body.style.cursor = 'default'
}
</script>

<template>
  <TresGroup ref="groupRef" :position="position" :rotation="rotation">
    <!-- Head -->
    <TresMesh :position="[0, 1.6, 0]">
      <TresSphereGeometry :args="[0.25, 16, 16]" />
      <TresMeshStandardMaterial :color="colors.head" />
    </TresMesh>

    <!-- Body / Torso -->
    <TresMesh
      :position="[0, 1.0, 0]"
      @click="onClick"
      @pointer-enter="onPointerEnter"
      @pointer-leave="onPointerLeave"
    >
      <TresCapsuleGeometry :args="[0.2, 0.6, 8, 16]" />
      <TresMeshStandardMaterial :color="colors.body" />
    </TresMesh>

    <!-- Left Arm -->
    <TresMesh :position="[-0.35, 1.0, 0]">
      <TresCylinderGeometry :args="[0.06, 0.06, 0.5, 8]" />
      <TresMeshStandardMaterial :color="colors.arms" />
    </TresMesh>

    <!-- Right Arm -->
    <TresMesh ref="rightArmRef" :position="[0.35, 1.0, 0]">
      <TresCylinderGeometry :args="[0.06, 0.06, 0.5, 8]" />
      <TresMeshStandardMaterial :color="colors.arms" />
    </TresMesh>

    <!-- Left Leg -->
    <TresMesh :position="[-0.12, 0.25, 0]">
      <TresCylinderGeometry :args="[0.07, 0.07, 0.5, 8]" />
      <TresMeshStandardMaterial :color="colors.legs" />
    </TresMesh>

    <!-- Right Leg -->
    <TresMesh :position="[0.12, 0.25, 0]">
      <TresCylinderGeometry :args="[0.07, 0.07, 0.5, 8]" />
      <TresMeshStandardMaterial :color="colors.legs" />
    </TresMesh>

    <!-- Nurse accent mark -->
    <TresMesh v-if="type === 'nurse'" :position="[0, 1.15, 0.21]">
      <TresBoxGeometry :args="[0.1, 0.1, 0.02]" />
      <TresMeshStandardMaterial :color="colors.accent" />
    </TresMesh>
  </TresGroup>
</template>
