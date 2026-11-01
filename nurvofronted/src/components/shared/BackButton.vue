<script setup lang="ts">
import { useRouter, type RouteLocationRaw } from 'vue-router'

const props = defineProps<{
  to: RouteLocationRaw
  label: string
  /** Ask first when leaving throws work away (e.g. an in-progress game). */
  confirmMessage?: string
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
  <button class="back-button" type="button" @click="goBack">← {{ label }}</button>
</template>

<style scoped>
.back-button {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 6px 12px;
  border: 1px solid #dbeafe;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.85);
  color: #2563eb;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s, border-color 0.15s;
}

.back-button:hover {
  background: #eff6ff;
  border-color: #93c5fd;
}
</style>
