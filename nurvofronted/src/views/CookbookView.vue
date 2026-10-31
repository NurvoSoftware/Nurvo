<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import NavBar from '@/components/shared/NavBar.vue'

const router = useRouter()

type StepKey = 'level' | 'briefing' | 'chat' | 'record' | 'report'

const steps: Array<{ key: StepKey; icon: string; title: string; points: string[]; tip: string; hint: string }> = [
  {
    key: 'level',
    icon: '🎯',
    title: '選擇難度',
    points: [
      '入門、標準、進階三種難度，時限分別是 10、8、6 分鐘',
      '每次生成教案會扣 30 點，頁面右上方可以看到剩餘點數',
      '練習過之後，這一頁會顯示「上次練習回顧」，提醒你上次的弱項',
    ],
    tip: '第一次練習建議從「入門」開始。',
    hint: '點「生成教案」',
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
    hint: '點「進入場景」',
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
    hint: '點「送出」',
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
    hint: '點「提交記錄」',
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
    hint: '點「開始第一次練習」',
  },
]

const current = ref(0)
const step = computed(() => steps[current.value]!)
const isLast = computed(() => current.value === steps.length - 1)

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
</script>

<template>
  <div class="cookbook-page">
    <NavBar />

    <main class="cookbook-container">
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
          <div class="step-text">
            <div class="step-icon">{{ step.icon }}</div>
            <h2 class="step-title">{{ step.title }}</h2>
            <ul class="step-points">
              <li v-for="point in step.points" :key="point">{{ point }}</li>
            </ul>
            <p class="step-tip">💡 {{ step.tip }}</p>
          </div>

          <div class="mock-wrap">
            <!-- Mini replica of the real screen. Only .mock-target reacts to clicks. -->
            <div class="mock-screen" :aria-label="`${step.title} 模擬畫面`">
              <div class="mock-bar"><span /><span /><span /></div>

              <div v-if="step.key === 'level'" class="mock-body">
                <p class="mock-heading">選擇關卡難度</p>
                <div class="mock-cards">
                  <div class="mock-card">入門</div>
                  <div class="mock-card mock-card--active">標準</div>
                  <div class="mock-card">進階</div>
                </div>
                <div class="mock-actions">
                  <span class="mock-btn">返回首頁</span>
                  <button class="mock-target mock-btn mock-btn--primary" @click="hitTarget">生成教案</button>
                </div>
              </div>

              <div v-else-if="step.key === 'briefing'" class="mock-body">
                <p class="mock-heading">任務簡報</p>
                <div class="mock-panel">
                  <p><b>病患：</b>李大華，70 歲，腰椎間盤突出</p>
                  <p><b>家屬：</b>陳太太（焦慮）、李小明、李小美</p>
                </div>
                <div class="mock-actions">
                  <span class="mock-muted">⏱ 限時 8 分鐘</span>
                  <button class="mock-target mock-btn mock-btn--primary" @click="hitTarget">進入場景 →</button>
                </div>
              </div>

              <div v-else-if="step.key === 'chat'" class="mock-body">
                <div class="mock-chips">
                  <span class="mock-chip mock-chip--on">病患</span>
                  <span class="mock-chip">陳太太</span>
                  <span class="mock-chip">李小明</span>
                </div>
                <div class="mock-bubble">病患：我這邊好痛……</div>
                <div class="mock-bubble mock-bubble--family">陳太太：護理師他到底怎麼了？</div>
                <div class="mock-input">
                  <span class="mock-input-text">請問哪裡最不舒服呢？</span>
                  <span class="mock-mic">🎤</span>
                  <button class="mock-target mock-send" aria-label="送出" @click="hitTarget">➤</button>
                </div>
              </div>

              <div v-else-if="step.key === 'record'" class="mock-body">
                <p class="mock-heading">病患記錄</p>
                <div class="mock-textarea">
                  S：腰部刺痛 7 分，搬重物後開始<br>
                  B：高血壓病史<br>
                  A：疼痛影響活動，需處置<br>
                  R：通知醫師評估止痛藥
                </div>
                <div class="mock-actions">
                  <span />
                  <button class="mock-target mock-btn mock-btn--primary" @click="hitTarget">提交記錄 →</button>
                </div>
              </div>

              <div v-else class="mock-body">
                <p class="mock-heading">成果報告</p>
                <div class="mock-report">
                  <p class="mock-score">72<small>/100</small></p>
                  <div class="mock-bars">
                    <span style="width: 80%" /><span style="width: 55%" /><span style="width: 70%" />
                  </div>
                </div>
                <div class="mock-sbar">
                  <span class="ok">S</span><span class="mid">B</span><span class="bad">A</span><span class="ok">R</span>
                </div>
                <div class="mock-actions">
                  <span />
                  <button class="mock-target mock-btn mock-btn--primary" @click="hitTarget">開始第一次練習 →</button>
                </div>
              </div>
            </div>
            <p class="mock-hint">👆 {{ step.hint }}試試看</p>
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
  max-width: 960px;
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
  padding: 32px;
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
  grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
  gap: 28px;
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

/* ── Mini mock screen ───────────────────────────── */
.mock-screen {
  border: 1px solid #cbd5e1;
  border-radius: 12px;
  background: #f8fbff;
  overflow: hidden;
  box-shadow: 0 8px 24px rgba(15, 23, 42, 0.08);
  font-size: 12px;
  color: #334155;
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

.mock-body {
  padding: 14px;
  min-height: 190px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.mock-heading {
  margin: 0;
  font-size: 14px;
  font-weight: 800;
  color: #0f172a;
  text-align: center;
}

.mock-cards {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 6px;
}

.mock-card {
  padding: 16px 0;
  border: 1px solid #dbeafe;
  border-radius: 8px;
  background: #ffffff;
  text-align: center;
  font-weight: 700;
}

.mock-card--active {
  border-color: #60a5fa;
  background: #eff6ff;
}

.mock-panel,
.mock-textarea {
  padding: 10px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  background: #ffffff;
  line-height: 1.7;
}

.mock-panel p {
  margin: 0;
}

.mock-actions {
  margin-top: auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.mock-btn {
  border: none;
  border-radius: 7px;
  padding: 6px 12px;
  font-size: 12px;
  font-weight: 700;
  background: #e2e8f0;
  color: #334155;
}

.mock-btn--primary {
  background: var(--nurvo-gradient-primary);
  color: #ffffff;
}

.mock-muted {
  color: #64748b;
}

.mock-chips {
  display: flex;
  gap: 6px;
}

.mock-chip {
  padding: 3px 10px;
  border-radius: 999px;
  background: #ffffff;
  border: 1px solid #e2e8f0;
}

.mock-chip--on {
  border-color: #60a5fa;
  background: #eff6ff;
  color: #1d4ed8;
}

.mock-bubble {
  align-self: flex-start;
  padding: 6px 10px;
  border-radius: 10px;
  background: #ffffff;
  border: 1px solid #e2e8f0;
}

.mock-bubble--family {
  background: #fef9c3;
  border-color: #fde68a;
}

.mock-input {
  margin-top: auto;
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 6px 6px 10px;
  border: 1px solid #cbd5e1;
  border-radius: 10px;
  background: #ffffff;
}

.mock-input-text {
  flex: 1;
}

.mock-send {
  border: none;
  width: 28px;
  height: 28px;
  border-radius: 8px;
  background: var(--nurvo-primary);
  color: #ffffff;
}

.mock-report {
  display: flex;
  gap: 14px;
  align-items: center;
}

.mock-score {
  margin: 0;
  font-size: 28px;
  font-weight: 800;
  color: #2563eb;
}

.mock-score small {
  font-size: 12px;
  color: #94a3b8;
}

.mock-bars {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.mock-bars span {
  display: block;
  height: 6px;
  border-radius: 3px;
  background: #3b82f6;
}

.mock-sbar {
  display: flex;
  gap: 6px;
}

.mock-sbar span {
  width: 26px;
  height: 26px;
  border-radius: 6px;
  display: grid;
  place-items: center;
  font-weight: 800;
  color: #ffffff;
}

.mock-sbar .ok { background: #22c55e; }
.mock-sbar .mid { background: #eab308; }
.mock-sbar .bad { background: #ef4444; }

/* The one clickable spot: pulsing ring so it's obvious where to click. */
.mock-target {
  cursor: pointer;
  position: relative;
  animation: mock-pulse 1.4s ease-out infinite;
}

@keyframes mock-pulse {
  0% { box-shadow: 0 0 0 0 rgba(249, 115, 22, 0.7); }
  100% { box-shadow: 0 0 0 10px rgba(249, 115, 22, 0); }
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

@media (max-width: 760px) {
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
