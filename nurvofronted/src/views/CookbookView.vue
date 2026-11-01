<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import NavBar from '@/components/shared/NavBar.vue'
import BackButton from '@/components/shared/BackButton.vue'
import levelShot from '@/assets/cookbook/level.jpg'
import briefingShot from '@/assets/cookbook/briefing.jpg'
import chatShot from '@/assets/cookbook/chat.jpg'
import recordShot from '@/assets/cookbook/record.jpg'
import reportShot from '@/assets/cookbook/report.jpg'

const router = useRouter()

type StepKey = 'level' | 'briefing' | 'chat' | 'record' | 'report'

/** Where the real button sits in the capture, as % of the image (measured when it was taken). */
interface Target {
  left: number
  top: number
  width: number
  height: number
}

const steps: Array<{
  key: StepKey
  icon: string
  title: string
  points: string[]
  tip: string
  hint: string
  shot: string
  target: Target
}> = [
  {
    key: 'level',
    icon: '🎯',
    title: '選擇難度',
    points: [
      '入門、標準、進階三種難度，時限分別是 10、8、6 分鐘',
      '每次生成教案會扣 30 點，頁面右上方可以看到剩餘點數',
      '練習過之後，這一頁會顯示黃色的「上次練習回顧」，點它可以看上次的完整報告',
    ],
    tip: '第一次練習建議從「入門」開始。',
    hint: '點「生成教案」試試看',
    shot: levelShot,
    target: { left: 81.3, top: 91.83, width: 6.98, height: 3.74 },
  },
  {
    key: 'briefing',
    icon: '📄',
    title: '閱讀任務簡報',
    points: [
      '簡報會介紹病患的基本資料、診斷，以及在場的三位家屬',
      '留意家屬的個性與情緒，等一下他們會插話',
      '準備好後按「進入場景」，計時就會開始',
    ],
    tip: '先想好要問哪些疼痛相關問題，進場後會更從容。',
    hint: '點「進入場景」試試看',
    shot: briefingShot,
    target: { left: 70.63, top: 87.42, width: 10.47, height: 3.93 },
  },
  {
    key: 'chat',
    icon: '💬',
    title: '與病患和家屬對話',
    points: [
      '在下方輸入框打字，或按麥克風用說的',
      '點上方的人物，或輸入「@」選擇要對誰說話（病患或某位家屬）',
      '家屬會主動插話，適時回應、安撫他們的情緒也會計分',
    ],
    tip: '用開放式問題開場，再逐步問清楚疼痛的部位、程度與持續時間。',
    hint: '點右下角的「送出」試試看',
    shot: chatShot,
    target: { left: 92.57, top: 87.13, width: 2.81, height: 4.5 },
  },
  {
    key: 'record',
    icon: '📝',
    title: '撰寫病患記錄',
    points: [
      '問診完成後按「完成並記錄」；時間到也會自動進入這一步',
      '在評估摘要寫下病患狀況、你的評估與護理計畫',
      '摘要會依 SBAR（情境、背景、評估、建議）四個面向分析',
    ],
    tip: '照 S → B → A → R 的順序寫，最不容易漏掉重點。',
    hint: '點「提交記錄」試試看',
    shot: recordShot,
    target: { left: 42.58, top: 76.22, width: 14.84, height: 6 },
  },
  {
    key: 'report',
    icon: '📊',
    title: '查看成果報告',
    points: [
      'AI 會依五大溝通面向評分：同理心、引導式提問、家屬安撫、資訊採集、回應流暢度',
      '報告會列出優勢、待改進項目、SBAR 分析與關鍵時刻',
      '下次選難度時，系統會提醒你上次最需要加強的地方',
    ],
    tip: '每次練習專注改善一個弱項，進步最快。',
    hint: '點「再玩一次」，開始你的第一次練習',
    shot: reportShot,
    target: { left: 39.91, top: 91.27, width: 10.72, height: 3.22 },
  },
]

const current = ref(0)
const step = computed(() => steps[current.value]!)
const isLast = computed(() => current.value === steps.length - 1)
// Positioned by its centre, so the CSS minimum tap size grows evenly around the real button.
const targetStyle = computed(() => {
  const t = step.value.target
  return {
    left: `${t.left + t.width / 2}%`,
    top: `${t.top + t.height / 2}%`,
    width: `${t.width}%`,
    height: `${t.height}%`,
  }
})

/** The highlighted spot in the mini screen: advance, or start real practice on the last step. */
function hitTarget(): void {
  if (isLast.value) {
    goToLevelSelect()
  } else {
    current.value++
  }
}

function prev(): void {
  if (current.value > 0) current.value--
}

function goToLevelSelect(): void {
  router.push({ name: 'level-select' })
}

const viewport = ref<HTMLElement | null>(null)

/** Tall pages scroll inside the frame like the real page; bring the button into view once loaded. */
function scrollToTarget(): void {
  const el = viewport.value
  if (!el) return
  const targetY = (step.value.target.top / 100) * el.scrollHeight
  const reduceMotion = window.matchMedia?.('(prefers-reduced-motion: reduce)').matches
  el.scrollTo({
    top: Math.max(0, targetY - el.clientHeight * 0.6),
    behavior: reduceMotion ? 'auto' : 'smooth',
  })
}
</script>

<template>
  <div class="cookbook-page">
    <NavBar />

    <main class="cookbook-container">
      <BackButton :to="{ name: 'level-select' }" label="返回選擇難度" />

      <header class="cookbook-header">
        <h1 class="title">操作指引</h1>
        <p class="subtitle">跟著閃爍的提示點一次，走過完整的練習流程</p>
      </header>

      <ol class="step-dots" aria-label="步驟進度">
        <li
          v-for="(s, i) in steps"
          :key="s.key"
          class="step-dot"
          :class="{ active: i === current, done: i < current }"
        >
          <button :aria-label="`第 ${i + 1} 步：${s.title}`" @click="current = i">{{ i + 1 }}</button>
        </li>
      </ol>

      <section class="step-card">
        <p class="step-counter">{{ current + 1 }} / {{ steps.length }}</p>

        <div class="step-layout">
          <!-- Explanation comes first in the DOM so screen readers hear it before the button. -->
          <div class="step-text" aria-live="polite">
            <div class="step-icon">{{ step.icon }}</div>
            <h2 class="step-title">{{ step.title }}</h2>
            <ul class="step-points">
              <li v-for="point in step.points" :key="point">{{ point }}</li>
            </ul>
            <p class="step-tip">💡 {{ step.tip }}</p>
          </div>

          <div class="mock-wrap">
            <!-- A capture of the real page. Only .mock-target (over the real button) reacts to clicks. -->
            <div class="mock-screen" role="group" :aria-label="step.title + ' 模擬畫面'">
              <div class="mock-bar"><span /><span /><span /></div>
              <div ref="viewport" class="mock-viewport">
                <div class="mock-page">
                  <img
                    :key="step.key"
                    :src="step.shot"
                    :alt="step.title + ' 畫面'"
                    draggable="false"
                    @load="scrollToTarget"
                  />
                  <button
                    class="mock-target"
                    :aria-label="step.hint"
                    :style="targetStyle"
                    @click="hitTarget"
                  />
                </div>
              </div>
            </div>
            <p class="mock-hint">👆 {{ step.hint }}</p>
          </div>
        </div>
      </section>

      <footer class="actions">
        <button class="btn-skip" @click="goToLevelSelect">略過指引</button>
        <button class="btn-prev" :disabled="current === 0" @click="prev">上一步</button>
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
  max-width: 1480px;
  margin: 0 auto;
  padding: 24px 16px 40px;
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
  margin: 18px 0 14px;
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
  padding: 24px;
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

.step-layout {
  display: grid;
  grid-template-columns: minmax(0, 7fr) minmax(0, 3fr);
  gap: 24px;
  align-items: center;
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

/* ── Capture of the real page ───────────────────── */
/* Visually on the left (and on top when stacked), though it follows the text in the DOM. */
.mock-wrap {
  order: -1;
}

.mock-screen {
  border: 1px solid #cbd5e1;
  border-radius: 12px;
  background: #f8fbff;
  overflow: hidden;
  box-shadow: 0 8px 24px rgba(15, 23, 42, 0.12);
  user-select: none;
}

.mock-bar {
  display: flex;
  gap: 5px;
  padding: 8px 10px;
  background: #e2e8f0;
}

.mock-bar span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #94a3b8;
}

/* Same shape as the 1280×800 window the captures were taken in. */
.mock-viewport {
  aspect-ratio: 16 / 10;
  overflow-y: auto;
}

.mock-page {
  position: relative;
}

.mock-page img {
  display: block;
  width: 100%;
  height: auto;
}

/* The one clickable spot, laid over the real button: pulsing ring so it's obvious. */
.mock-target {
  position: absolute;
  transform: translate(-50%, -50%);
  min-width: 24px;
  min-height: 24px;
  padding: 0;
  border: none;
  border-radius: 8px;
  background: transparent;
  outline: 3px solid #f97316;
  outline-offset: 3px;
  cursor: pointer;
  animation: mock-pulse 1.4s ease-out infinite;
}

@keyframes mock-pulse {
  0% { box-shadow: 0 0 0 0 rgba(249, 115, 22, 0.7); }
  100% { box-shadow: 0 0 0 14px rgba(249, 115, 22, 0); }
}

.mock-hint {
  margin: 10px 0 0;
  text-align: center;
  font-size: 14px;
  font-weight: 700;
  color: #ea580c;
}

/* ── Footer ─────────────────────────────────────── */
.actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 22px;
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

@media (max-width: 860px) {
  .step-layout {
    grid-template-columns: 1fr;
  }
}

@media (prefers-reduced-motion: reduce) {
  .mock-target {
    animation: none;
    box-shadow: 0 0 0 3px rgba(249, 115, 22, 0.6);
  }
}
</style>
