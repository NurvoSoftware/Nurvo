<script setup lang="ts">
defineProps<{
  type: 'strengths' | 'improvements'
  items: string[]
}>()
</script>

<template>
  <div class="feedback-card" :class="type">
    <div class="card-title">
      <span class="card-icon">{{ type === 'strengths' ? '✓' : '⚠' }}</span>
      <span class="card-title-text">{{ type === 'strengths' ? '優勢' : '待改進' }}</span>
    </div>
    <ul class="item-list">
      <li v-for="(item, index) in items" :key="index" class="item">
        {{ item }}
      </li>
    </ul>
  </div>
</template>

<style scoped>
.feedback-card {
  background: #ffffff;
  border-radius: 14px;
  border: 1px solid #e2e8f0;
  border-left: 3px solid;
  padding: 20px;
}

.feedback-card.strengths {
  border-left-color: #22c55e;
}

.feedback-card.improvements {
  border-left-color: #eab308;
}

.card-title {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 14px;
  font-size: 14px;
  font-weight: 700;
}

.strengths .card-icon {
  color: #22c55e;
  font-size: 15px;
  font-weight: 900;
}

.strengths .card-title-text {
  color: #22c55e;
}

.improvements .card-icon {
  color: #eab308;
  font-size: 14px;
}

.improvements .card-title-text {
  color: #eab308;
}

.item-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.item {
  font-size: 13px;
  color: #334155;
  line-height: 1.6;
  padding-left: 16px;
  position: relative;
}

.item::before {
  content: '';
  position: absolute;
  left: 0;
  top: 8px;
  width: 5px;
  height: 5px;
  border-radius: 50%;
}

.strengths .item::before {
  background: #22c55e;
}

.improvements .item::before {
  background: #eab308;
}
</style>
