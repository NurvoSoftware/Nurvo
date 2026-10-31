<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import NavBar from '@/components/shared/NavBar.vue'

const router = useRouter()

const steps: Array<{ icon: string; title: string; points: string[]; tip: string }> = [
  {
    icon: '🎯',
    title: '選擇難度',
    points: [
      '入門、標準、進階三種難度，時限分別是 10、8、6 分鐘',
      '每次生成教案會扣 30 點，頁面右上方可以看到剩餘點數',
      '練習過之後，這一頁會顯示「上次練習回顧」，提醒你上次的弱項',
    ],
    tip: '第一次練習建議從「入門」開始。',
  },
  {
    icon: '📄',
    title: '閱讀任務簡報',
    points: [
      '簡報會介紹病患的基本資料、診斷，以及在場的三位家屬',
      '留意家屬的個性與情緒，等一下他們會插話',
      '準備好後按「進入場景」，計時就會開始',
    ],
    tip: '先想好要問哪些疼痛相關問題，進場後會更從容。',
  },
  {
    icon: '💬',
    title: '與病患和家屬對話',
    points: [
      '在下方輸入框打字，或按麥克風用說的',
      '點上方的人物，或輸入「@」選擇要對誰說話（病患或某位家屬）',
      '家屬會主動插話，適時回應、安撫他們的情緒也會計分',
    ],
    tip: '用開放式問題開場，再逐步問清楚疼痛的部位、程度與持續時間。',
  },
  {
    icon: '📝',
    title: '撰寫病患記錄',
    points: [
      '問診完成後按「完成並記錄」；時間到也會自動進入這一步',
      '在評估摘要寫下病患狀況、你的評估與護理計畫',
      '摘要會依 SBAR（情境、背景、評估、建議）四個面向分析',
    ],
    tip: '照 S → B → A → R 的順序寫，最不容易漏掉重點。',
  },
  {
    icon: '📊',
    title: '查看成果報告',
    points: [
      'AI 會依五大溝通面向評分：同理心、引導式提問、家屬安撫、資訊採集、回應流暢度',
      '報告會列出優勢、待改進項目、SBAR 分析與關鍵時刻',
      '下次選難度時，系統會提醒你上次最需要加強的地方',
    ],
    tip: '每次練習專注改善一個弱項，進步最快。',
  },
]

const current = ref(0)
const step = computed(() => steps[current.value]!)
const isLast = computed(() => current.value === steps.length - 1)

function next(): void {
  if (!isLast.value) current.value++
}

function prev(): void {
  if (current.value > 0) current.value--
}

function goToLevelSelect(): void {
  router.push({ name: 'level-select' })
}
</script>

<template>
  <div class="cookbook-page">
    <NavBar />

    <main class="cookbook-container">
      <header class="cookbook-header">
        <h1 class="title">操作指引</h1>
        <p class="subtitle">五個步驟帶你走過一次完整的練習流程</p>
      </header>

      <ol class="step-dots" aria-label="步驟進度">
        <li
          v-for="(s, i) in steps"
          :key="s.title"
          class="step-dot"
          :class="{ active: i === current, done: i < current }"
        >
          <button :aria-label="`第 ${i + 1} 步：${s.title}`" @click="current = i">{{ i + 1 }}</button>
        </li>
      </ol>

      <section class="step-card">
        <p class="step-counter">{{ current + 1 }} / {{ steps.length }}</p>
        <div class="step-icon">{{ step.icon }}</div>
        <h2 class="step-title">{{ step.title }}</h2>
        <ul class="step-points">
          <li v-for="point in step.points" :key="point">{{ point }}</li>
        </ul>
        <p class="step-tip">💡 {{ step.tip }}</p>
      </section>

      <footer class="actions">
        <button class="btn-skip" @click="goToLevelSelect">略過指引</button>
        <div class="actions-right">
          <button class="btn-prev" :disabled="current === 0" @click="prev">上一步</button>
          <button v-if="!isLast" class="btn-next" @click="next">下一步</button>
          <button v-else class="btn-start" @click="goToLevelSelect">開始第一次練習 →</button>
        </div>
      </footer>
    </main>
  </div>
</template>

<style scoped>
.cookbook-page {
  min-height: 100vh;
  background: radial-gradient(circle at 16% 10%, #dbeafe 0%, transparent 24%), #f8fbff;
}

.cookbook-container {
  max-width: 720px;
  margin: 0 auto;
  padding: 40px 16px 56px;
}

.cookbook-header {
  text-align: center;
}

.title {
  margin: 0;
  font-size: 30px;
  font-weight: 800;
  color: var(--nurvo-text-primary);
}

.subtitle {
  margin: 10px 0 0;
  color: var(--nurvo-text-secondary);
  font-size: 15px;
}

.step-dots {
  list-style: none;
  display: flex;
  justify-content: center;
  gap: 10px;
  padding: 0;
  margin: 28px 0 20px;
}

.step-dot button {
  width: 34px;
  height: 34px;
  border-radius: 50%;
  border: 2px solid #bfdbfe;
  background: #ffffff;
  color: #64748b;
  font-weight: 700;
  cursor: pointer;
}

.step-dot.done button {
  border-color: #93c5fd;
  background: #dbeafe;
  color: #1d4ed8;
}

.step-dot.active button {
  border-color: var(--nurvo-primary);
  background: var(--nurvo-primary);
  color: #ffffff;
}

.step-card {
  position: relative;
  border: 1px solid #dbeafe;
  border-radius: 18px;
  background: #ffffff;
  padding: 32px 32px 24px;
  box-shadow: 0 10px 30px rgba(37, 99, 235, 0.08);
}

.step-counter {
  position: absolute;
  top: 16px;
  right: 20px;
  margin: 0;
  font-size: 13px;
  font-weight: 700;
  color: #94a3b8;
}

.step-icon {
  font-size: 40px;
}

.step-title {
  margin: 8px 0 16px;
  font-size: 22px;
  font-weight: 800;
  color: var(--nurvo-text-primary);
}

.step-points {
  margin: 0;
  padding-left: 20px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  font-size: 15px;
  line-height: 1.7;
  color: #334155;
}

.step-tip {
  margin: 20px 0 0;
  padding: 12px 14px;
  border-radius: 10px;
  background: #f0f9ff;
  color: #0369a1;
  font-size: 14px;
  font-weight: 600;
}

.actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 22px;
}

.actions-right {
  display: flex;
  gap: 10px;
}

.actions button {
  border: none;
  border-radius: 10px;
  padding: 10px 18px;
  font-weight: 700;
  cursor: pointer;
}

.btn-skip {
  background: transparent;
  color: #64748b;
}

.btn-prev {
  background: #e2e8f0;
  color: #334155;
}

.btn-prev:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-next,
.btn-start {
  background: var(--nurvo-gradient-primary);
  color: var(--nurvo-white);
  box-shadow: 0 8px 20px rgba(37, 99, 235, 0.28);
}
</style>
