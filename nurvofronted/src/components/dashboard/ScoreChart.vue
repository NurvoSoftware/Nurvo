<script setup lang="ts">
import type { DimensionScores } from '@/types/game'

const props = defineProps<{
  scores: DimensionScores
}>()

const dimensions: { key: keyof DimensionScores; label: string }[] = [
  { key: 'empathy', label: '同理心' },
  { key: 'guided_questioning', label: '引導式提問' },
  { key: 'family_calming', label: '家屬安撫' },
  { key: 'info_gathering', label: '資訊採集' },
  { key: 'response_fluency', label: '回應流暢度' },
]

function barColor(score: number): string {
  return score >= 80 ? '#2563eb' : '#eab308'
}
</script>

<template>
  <div class="score-chart">
    <div v-for="dim in dimensions" :key="dim.key" class="bar-row">
      <span class="bar-label">{{ dim.label }}</span>
      <div class="bar-track">
        <div
          class="bar-fill"
          :style="{
            width: props.scores[dim.key] + '%',
            backgroundColor: barColor(props.scores[dim.key]),
          }"
        />
      </div>
      <span class="bar-value" :style="{ color: barColor(props.scores[dim.key]) }">
        {{ props.scores[dim.key] }}
      </span>
    </div>
  </div>
</template>

<style scoped>
.score-chart {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.bar-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.bar-label {
  font-size: 10px;
  color: #64748b;
  width: 70px;
  flex-shrink: 0;
  text-align: right;
}

.bar-track {
  flex: 1;
  height: 5px;
  background: #f1f5f9;
  border-radius: 3px;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.8s ease-out;
  min-width: 2px;
}

.bar-value {
  font-size: 10px;
  font-weight: 600;
  width: 28px;
  flex-shrink: 0;
  text-align: right;
}
</style>
