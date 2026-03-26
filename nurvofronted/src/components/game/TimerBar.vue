<script setup lang="ts">
import { computed, watch } from 'vue'

const props = defineProps<{
  remainingSeconds: number
}>()

const emit = defineEmits<{
  expired: []
}>()

const formattedTime = computed(() => {
  const total = Math.max(0, props.remainingSeconds)
  const minutes = Math.floor(total / 60)
  const seconds = total % 60
  return `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`
})

const isDanger = computed(() => props.remainingSeconds < 60)
const isWarn = computed(() => props.remainingSeconds <= 180 && !isDanger.value)
const isPulsing = computed(() => props.remainingSeconds < 60 && props.remainingSeconds > 0)

watch(
  () => props.remainingSeconds,
  (val) => {
    if (val <= 0) {
      emit('expired')
    }
  },
)
</script>

<template>
  <div
    class="timer-pill"
    :class="{
      'timer-pill--danger': isDanger,
      'timer-pill--warn': isWarn,
      'timer-pill--pulsing': isPulsing,
    }"
  >
    <div class="timer-dot"></div>
    <span class="timer-value">{{ formattedTime }}</span>
  </div>
</template>

<style scoped>
.timer-pill {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  border-radius: 10px;
  background: var(--nurvo-success-light);
  border: 1px solid var(--nurvo-success-border);
}

.timer-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--nurvo-success);
}

.timer-value {
  font-size: 13px;
  font-weight: 700;
  color: var(--nurvo-success-dark);
  font-variant-numeric: tabular-nums;
  line-height: 1;
}

/* Warning state */
.timer-pill--warn {
  background: var(--nurvo-warning-light);
  border-color: var(--nurvo-warning-border);
}

.timer-pill--warn .timer-dot {
  background: var(--nurvo-warning);
}

.timer-pill--warn .timer-value {
  color: var(--nurvo-warning-dark);
}

/* Danger state */
.timer-pill--danger {
  background: var(--nurvo-danger-light);
  border-color: var(--nurvo-danger-border);
}

.timer-pill--danger .timer-dot {
  background: var(--nurvo-danger);
}

.timer-pill--danger .timer-value {
  color: var(--nurvo-danger-dark);
}

/* Pulsing */
.timer-pill--pulsing {
  animation: timerPulse 1s ease-in-out infinite;
}

@keyframes timerPulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.7; transform: scale(1.03); }
}
</style>
