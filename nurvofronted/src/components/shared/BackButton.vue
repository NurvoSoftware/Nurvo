<script setup lang="ts">
import { useRouter, type RouteLocationRaw } from 'vue-router'

const props = defineProps<{
  to: RouteLocationRaw
  label: string
  /** Ask first when leaving throws work away (e.g. an in-progress game). */
  confirmMessage?: string
  /** 'forward' puts a → after the label, for "go on" links styled like the back link. */
  arrow?: 'back' | 'forward'
}>()

const emit = defineEmits<{
  /** Fired after the user agrees to leave, before navigating — the place to reset state. */
  leave: []
}>()

const router = useRouter()

function goBack(): void {
  if (props.confirmMessage && !window.confirm(props.confirmMessage)) return
  emit('leave')
  router.push(props.to)
}
</script>

<template>
  <button
    class="back-button"
    :class="{ 'back-button--forward': arrow === 'forward' }"
    type="button"
    @click="goBack"
  >
    <span v-if="arrow !== 'forward'" class="back-button__arrow" aria-hidden="true">←</span>
    <span class="back-button__label">{{ label }}</span>
    <span v-if="arrow === 'forward'" class="back-button__arrow" aria-hidden="true">→</span>
  </button>
</template>

<style scoped>
/* The one look for every "back" link: plain text, underlined label, arrow in front. */
.back-button {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  margin: 0 0 14px;
  padding: 2px 0;
  border: none;
  background: none;
  color: #1d4ed8;
  font-size: 15px;
  font-weight: 500;
  cursor: pointer;
}

.back-button__label {
  text-decoration: underline;
  text-underline-offset: 4px;
  text-decoration-thickness: 1px;
}

.back-button:hover {
  color: #1e40af;
}

.back-button:hover .back-button__arrow {
  transform: translateX(-2px);
}

.back-button--forward:hover .back-button__arrow {
  transform: translateX(2px);
}

.back-button__arrow {
  transition: transform 0.15s;
}
</style>
