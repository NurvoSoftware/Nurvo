<script setup lang="ts">
import { computed } from 'vue'
import type { DimensionScores } from '@/types/game'

const props = defineProps<{
  scores: DimensionScores
}>()

const cx = 100
const cy = 100
const radius = 70

const labels = ['同理心', '引導式提問', '家屬安撫', '資訊採集', '回應流暢度']
const keys: (keyof DimensionScores)[] = [
  'empathy',
  'guided_questioning',
  'family_calming',
  'info_gathering',
  'response_fluency',
]

function vertexAt(index: number, scale: number): { x: number; y: number } {
  // 5 vertices at 72-degree intervals, starting from top (270 degrees / -90 degrees)
  const angle = ((2 * Math.PI) / 5) * index - Math.PI / 2
  return {
    x: cx + radius * scale * Math.cos(angle),
    y: cy + radius * scale * Math.sin(angle),
  }
}

function pentagonPath(scale: number): string {
  const points = Array.from({ length: 5 }, (_, i) => {
    const v = vertexAt(i, scale)
    return `${v.x},${v.y}`
  })
  return `M${points.join('L')}Z`
}

const gridLevels = [0.25, 0.5, 0.75, 1.0]

const axisLines = computed(() =>
  Array.from({ length: 5 }, (_, i) => {
    const v = vertexAt(i, 1)
    return { x1: cx, y1: cy, x2: v.x, y2: v.y }
  }),
)

const dataPath = computed(() => {
  const points = keys.map((key, i) => {
    const score = props.scores[key] / 100
    const v = vertexAt(i, score)
    return `${v.x},${v.y}`
  })
  return `M${points.join('L')}Z`
})

const dataPoints = computed(() =>
  keys.map((key, i) => {
    const score = props.scores[key]
    const v = vertexAt(i, score / 100)
    return { x: v.x, y: v.y, score, key }
  }),
)

const labelPositions = computed(() =>
  Array.from({ length: 5 }, (_, i) => {
    const v = vertexAt(i, 1.22)
    return { x: v.x, y: v.y, text: labels[i] }
  }),
)
</script>

<template>
  <svg viewBox="0 0 200 200" class="radar-chart" xmlns="http://www.w3.org/2000/svg">
    <!-- Grid pentagons -->
    <path
      v-for="level in gridLevels"
      :key="level"
      :d="pentagonPath(level)"
      fill="none"
      :stroke="level % 0.5 === 0 ? '#e2e8f0' : '#f1f5f9'"
      stroke-width="0.8"
    />

    <!-- Axis lines -->
    <line
      v-for="(line, i) in axisLines"
      :key="'axis-' + i"
      :x1="line.x1"
      :y1="line.y1"
      :x2="line.x2"
      :y2="line.y2"
      stroke="#e2e8f0"
      stroke-width="0.6"
    />

    <!-- Data polygon -->
    <path :d="dataPath" fill="rgba(37,99,235,0.08)" stroke="#2563eb" stroke-width="1.5" />

    <!-- Data points -->
    <circle
      v-for="pt in dataPoints"
      :key="pt.key"
      :cx="pt.x"
      :cy="pt.y"
      r="4"
      :fill="pt.score >= 80 ? '#2563eb' : '#eab308'"
      stroke="#fff"
      stroke-width="1"
    />

    <!-- Labels -->
    <text
      v-for="(lbl, i) in labelPositions"
      :key="'label-' + i"
      :x="lbl.x"
      :y="lbl.y"
      text-anchor="middle"
      dominant-baseline="central"
      class="radar-label"
    >
      {{ lbl.text }}
    </text>
  </svg>
</template>

<style scoped>
.radar-chart {
  width: 100%;
  max-width: 200px;
  height: auto;
}

.radar-label {
  font-size: 7px;
  fill: #64748b;
  font-weight: 500;
}
</style>
