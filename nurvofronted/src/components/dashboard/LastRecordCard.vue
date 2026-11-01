<script setup lang="ts">
import { computed } from 'vue'
import { DIMENSION_LABELS, SBAR_RATING_LABEL, SBAR_SECTIONS } from '@/types/game'
import type { DimensionScores, LatestRecord } from '@/types/game'

const props = defineProps<{
  record: LatestRecord
}>()

const DIFFICULTY_LABEL: Record<LatestRecord['difficulty'], string> = {
  easy: '入門',
  medium: '標準',
  hard: '進階',
}

const completedDate = computed(() =>
  new Date(props.record.completed_at).toLocaleDateString('zh-TW', { month: 'long', day: 'numeric' }),
)

const weakest = computed(() => {
  const entries = Object.entries(props.record.dimension_scores) as [keyof DimensionScores, number][]
  const [key, score] = entries.reduce((min, cur) => (cur[1] < min[1] ? cur : min))
  return { label: DIMENSION_LABELS[key], score }
})

const topImprovements = computed(() => props.record.improvements.slice(0, 3))

const sbarGaps = computed(() => {
  const sbar = props.record.sbar_analysis
  if (!sbar) return []
  return SBAR_SECTIONS.filter((s) => sbar[s.key].rating !== 'complete').map((s) => ({
    ...s,
    rating: sbar[s.key].rating,
  }))
})
</script>

<template>
  <router-link
    class="last-record"
    :to="{ name: 'history-detail', params: { sessionId: record.session_id } }"
    :aria-label="`查看上次練習完整報告（${record.overall_score} 分，最需要加強：${weakest.label}）`"
  >
    <header class="last-record-head">
      <div>
        <p class="last-record-eyebrow">上次練習回顧</p>
        <p class="last-record-meta">
          {{ completedDate }} · {{ DIFFICULTY_LABEL[record.difficulty] }}難度 · {{ record.level_label }}
        </p>
      </div>
      <p class="last-record-score">{{ record.overall_score }}<span>/100</span></p>
    </header>

    <div class="last-record-body">
      <div class="last-record-weakest">
        <p class="block-label">最需要加強</p>
        <p class="weakest-name">{{ weakest.label }}</p>
        <p class="weakest-score">{{ weakest.score }} 分</p>
      </div>

      <div class="last-record-detail">
        <p v-if="topImprovements.length" class="block-label">這次可以注意</p>
        <ul v-if="topImprovements.length" class="last-record-improvements">
          <li v-for="(item, i) in topImprovements" :key="i">{{ item }}</li>
        </ul>
        <div v-if="sbarGaps.length" class="last-record-sbar">
          <span class="block-label">病患紀錄 SBAR 待補：</span>
          <span v-for="gap in sbarGaps" :key="gap.key" class="sbar-chip" :class="gap.rating">
            {{ gap.letter }} {{ gap.label }}（{{ SBAR_RATING_LABEL[gap.rating] }}）
          </span>
        </div>
      </div>
    </div>

    <p class="last-record-more">查看完整報告 →</p>
  </router-link>
</template>

<style scoped>
.last-record {
  display: block;
  text-decoration: none;
  color: inherit;
  cursor: pointer;
  transition: box-shadow 0.2s, transform 0.2s;
  border: 1px solid #fde68a;
  border-left: 4px solid #f59e0b;
  border-radius: 16px;
  background: #fffbeb;
  padding: 18px 20px;
  margin-bottom: 20px;
}

.last-record:hover {
  transform: translateY(-1px);
  box-shadow: 0 10px 24px rgba(245, 158, 11, 0.18);
}

.last-record-more {
  margin: 12px 0 0;
  text-align: right;
  font-size: 13px;
  font-weight: 700;
  color: #b45309;
}

.last-record-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 14px;
}

.last-record-eyebrow {
  margin: 0;
  font-size: 16px;
  font-weight: 800;
  color: #92400e;
}

.last-record-meta {
  margin: 4px 0 0;
  font-size: 13px;
  color: #78716c;
}

.last-record-score {
  margin: 0;
  font-size: 32px;
  font-weight: 800;
  color: #b45309;
  line-height: 1;
}

.last-record-score span {
  font-size: 14px;
  font-weight: 600;
  color: #a8a29e;
}

.last-record-body {
  display: flex;
  gap: 16px;
}

.last-record-weakest {
  flex-shrink: 0;
  min-width: 128px;
  padding: 12px;
  border-radius: 12px;
  background: #ffffff;
  text-align: center;
}

.block-label {
  margin: 0 0 6px;
  font-size: 12px;
  font-weight: 700;
  color: #a16207;
}

.weakest-name {
  margin: 0;
  font-size: 18px;
  font-weight: 800;
  color: #b91c1c;
}

.weakest-score {
  margin: 2px 0 0;
  font-size: 13px;
  color: #78716c;
}

.last-record-detail {
  flex: 1;
  min-width: 0;
}

.last-record-improvements {
  margin: 0 0 10px;
  padding-left: 18px;
  font-size: 14px;
  line-height: 1.7;
  color: #334155;
}

.last-record-sbar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 6px;
}

.last-record-sbar .block-label {
  margin: 0;
}

.sbar-chip {
  font-size: 12px;
  font-weight: 700;
  padding: 2px 10px;
  border-radius: 999px;
}

.sbar-chip.partial { background: #fef9c3; color: #a16207; }
.sbar-chip.missing { background: #fee2e2; color: #b91c1c; }

@media (max-width: 640px) {
  .last-record-body {
    flex-direction: column;
  }
}
</style>
