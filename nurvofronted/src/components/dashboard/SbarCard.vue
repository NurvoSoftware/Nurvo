<script setup lang="ts">
import { SBAR_RATING_LABEL, SBAR_SECTIONS } from '@/types/game'
import type { SbarAnalysis } from '@/types/game'

defineProps<{
  analysis: SbarAnalysis
}>()
</script>

<template>
  <div class="sbar-card">
    <div class="card-title">
      <span class="card-title-text">📋 病患紀錄 SBAR 分析</span>
    </div>
    <ul class="sbar-list">
      <li
        v-for="section in SBAR_SECTIONS"
        :key="section.key"
        class="sbar-row"
        :class="analysis[section.key].rating"
      >
        <span class="sbar-letter">{{ section.letter }}</span>
        <div class="sbar-body">
          <div class="sbar-head">
            <span class="sbar-label">{{ section.label }}</span>
            <span class="sbar-rating">{{ SBAR_RATING_LABEL[analysis[section.key].rating] }}</span>
          </div>
          <p class="sbar-feedback">{{ analysis[section.key].feedback }}</p>
        </div>
      </li>
    </ul>
  </div>
</template>

<style scoped>
.sbar-card {
  background: #ffffff;
  border-radius: 14px;
  border: 1px solid #e2e8f0;
  border-left: 3px solid #3b82f6;
  padding: 20px;
}

.card-title {
  margin-bottom: 14px;
  font-size: 14px;
  font-weight: 700;
  color: #2563eb;
}

.sbar-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.sbar-row {
  display: flex;
  gap: 12px;
  align-items: flex-start;
  padding: 12px;
  border-radius: 10px;
  background: #f8fafc;
}

.sbar-letter {
  flex-shrink: 0;
  width: 32px;
  height: 32px;
  border-radius: 8px;
  display: grid;
  place-items: center;
  font-weight: 800;
  color: #ffffff;
}

.complete .sbar-letter { background: #22c55e; }
.partial .sbar-letter { background: #eab308; }
.missing .sbar-letter { background: #ef4444; }

.sbar-head {
  display: flex;
  align-items: center;
  gap: 8px;
}

.sbar-label {
  font-size: 14px;
  font-weight: 700;
  color: #0f172a;
}

.sbar-rating {
  font-size: 12px;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 999px;
}

.complete .sbar-rating { background: #dcfce7; color: #15803d; }
.partial .sbar-rating { background: #fef9c3; color: #a16207; }
.missing .sbar-rating { background: #fee2e2; color: #b91c1c; }

.sbar-feedback {
  margin: 4px 0 0;
  font-size: 13px;
  line-height: 1.6;
  color: #334155;
}

@media (max-width: 640px) {
  .sbar-list {
    grid-template-columns: 1fr;
  }
}
</style>
