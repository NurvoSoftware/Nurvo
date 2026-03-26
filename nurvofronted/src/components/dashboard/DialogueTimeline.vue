<script setup lang="ts">
import type { KeyMoment } from '@/types/game'

defineProps<{
  moments: KeyMoment[]
}>()

function formatTime(seconds: number): string {
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
}

function dotColor(quality: string): string {
  return quality === 'good' ? '#22c55e' : '#eab308'
}

function badgeBg(quality: string): string {
  return quality === 'good' ? 'rgba(34,197,94,0.1)' : 'rgba(234,179,8,0.1)'
}

function badgeColor(quality: string): string {
  return quality === 'good' ? '#16a34a' : '#ca8a04'
}

function badgeText(quality: string): string {
  return quality === 'good' ? '表現良好' : '待改善'
}
</script>

<template>
  <div class="dialogue-timeline">
    <div v-for="(moment, index) in moments" :key="index" class="timeline-item">
      <!-- Vertical line -->
      <div class="timeline-rail">
        <div
          class="timeline-dot"
          :style="{ backgroundColor: dotColor(moment.quality) }"
        />
        <div v-if="index < moments.length - 1" class="timeline-line" />
      </div>

      <!-- Content -->
      <div class="timeline-content">
        <div class="timeline-meta">
          <span class="timeline-time">{{ formatTime(moment.elapsed_seconds) }}</span>
          <span
            class="timeline-badge"
            :style="{
              backgroundColor: badgeBg(moment.quality),
              color: badgeColor(moment.quality),
            }"
          >
            {{ badgeText(moment.quality) }}
          </span>
        </div>
        <p class="timeline-desc">{{ moment.description }}</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.dialogue-timeline {
  display: flex;
  flex-direction: column;
}

.timeline-item {
  display: flex;
  gap: 14px;
  min-height: 56px;
}

.timeline-rail {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 12px;
  flex-shrink: 0;
}

.timeline-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  border: 2px solid #ffffff;
  box-shadow: 0 0 0 1px #e2e8f0;
  flex-shrink: 0;
}

.timeline-line {
  width: 2px;
  flex: 1;
  background: #e2e8f0;
  margin-top: 2px;
}

.timeline-content {
  flex: 1;
  padding-bottom: 20px;
}

.timeline-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}

.timeline-time {
  font-size: 10px;
  color: #64748b;
  font-family: 'SF Mono', 'Fira Code', 'Cascadia Code', monospace;
}

.timeline-badge {
  font-size: 10px;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 9999px;
  line-height: 1.4;
}

.timeline-desc {
  font-size: 13px;
  color: #334155;
  line-height: 1.6;
  margin: 4px 0 0 0;
}
</style>
