<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useGameStore } from '@/stores/gameStore'
import { useAuthStore } from '@/stores/authStore'
import NavBar from '@/components/shared/NavBar.vue'

const router = useRouter()
const gameStore = useGameStore()
const authStore = useAuthStore()

const activeFaq = ref<number | null>(null)
function toggleFaq(i: number) {
  activeFaq.value = activeFaq.value === i ? null : i
}

const faqs = [
  {
    q: 'Nurvo 是什麼？',
    a: 'Nurvo 是 AI 驅動的護理溝通訓練平台。學員透過與 AI 病患及家屬對話，在安全環境中練習臨床溝通技巧，結束後立即獲得多維度量化回饋報告。',
  },
  {
    q: '需要安裝任何軟體嗎？',
    a: '不需要。Nurvo 是純網頁平台，只要有現代瀏覽器即可開始訓練，無須下載或安裝任何應用程式。',
  },
  {
    q: '支援語音輸入嗎？',
    a: '支援。Nurvo 整合語音轉文字技術，讓學員可以用說話的方式與 AI 角色互動，更貼近真實臨床對話情境。',
  },
  {
    q: '適合哪些人使用？',
    a: '主要適合護理學生、新進護理師及在職護理人員。也歡迎護理學校、醫院、培訓機構洽詢團體授權方案。',
  },
  {
    q: '訓練記錄會儲存嗎？',
    a: '目前 MVP 階段，記錄儲存於當次工作階段，瀏覽器重整後清除。完整的資料持久化功能正在規劃中。',
  },
  {
    q: '如何洽談機構合作？',
    a: '請透過頁面下方「聯絡我們」與我們聯繫，我們將安排線上演示並提供客製化導入方案。',
  },
]

const highlights = [
  'AI 動態情境，每次練習都不同',
  '病患 + 家屬雙角色即時互動',
  '結束即生成可執行回饋',
]

const features = [
  { icon: '🧠', title: 'AI 動態情境生成', desc: '每次練習由 AI 即時生成臨床情境，確保訓練多樣性，告別死記固定劇本。' },
  { icon: '👨‍👩‍👧', title: '多角色即時互動', desc: '同時與 AI 病患及三位家屬對話，模擬真實護理溝通的複雜人際動態。' },
  { icon: '🎤', title: '語音文字雙模式', desc: '支援語音與文字輸入，全程繁體中文，貼近台灣臨床真實環境。' },
  { icon: '📊', title: '多維度量化回饋', desc: 'LLM 評分引擎從同理心、問診流程到溝通清晰度全面評估，每次都有數據。' },
  { icon: '🏥', title: '真實臨床場景設計', desc: '情境涵蓋急性、慢性、術後等多種護理情況，符合護理教育框架。' },
  { icon: '📈', title: '進步可視化追蹤', desc: '完整訓練記錄與趨勢分析，讓成長看得見、管理者看得懂。' },
]

const steps = [
  { num: '01', title: '選擇情境難度', desc: '根據學習目標選擇難度，系統即時生成專屬臨床案例與角色設定。' },
  { num: '02', title: '沉浸式對話練習', desc: '與 AI 病患及家屬進行自然對話，語音或文字均可，無須腳本。' },
  { num: '03', title: '獲得即時回饋', desc: '對話結束後立即收到多維度評分報告與具體改善建議，持續精進。' },
]

function startGame() {
  if (!authStore.isAuthenticated) {
    sessionStorage.setItem('nurvo_redirect', '/level-select')
    router.push('/login')
    return
  }
  gameStore.reset()
  router.push('/level-select')
}
</script>

<template>
  <div class="home">
    <div class="bg-glow bg-glow--left"></div>
    <div class="bg-glow bg-glow--right"></div>

    <NavBar />

    <!-- ── Hero ── -->
    <main class="hero">
      <section class="hero-left">
        <div class="brand-hero">
          <h1 class="brand-title">Nurvo</h1>
        </div>

        <p class="eyebrow">Clinical Communication Training Platform</p>

        <h2 class="tagline">AI 驅動護理對話訓練平台</h2>

        <p class="description">
          讓每次護理對話都成為可量化的進步。
          <br />
          與 AI 病患及家屬互動，從同理心到問診流程，即時獲得專業回饋。
        </p>

        <div class="hero-actions">
          <button class="cta-primary" @click="startGame">開始訓練</button>
          <a href="#contact" class="cta-secondary">聯絡我們</a>
        </div>
      </section>

      <section class="hero-right">
        <div class="features-container">
          <h3 class="features-title">系統特色</h3>
          <ul class="features">
            <li v-for="item in highlights" :key="item" class="feature-item">
              <span class="feature-icon">✓</span>
              <span>{{ item }}</span>
            </li>
          </ul>
        </div>
      </section>
    </main>

    <!-- ── How it works ── -->
    <section class="section steps-section">
      <div class="section-inner">
        <div class="section-header">
          <span class="section-eyebrow">流程</span>
          <h2 class="section-title">三步驟，即刻開始練習</h2>
          <p class="section-subtitle">從情境生成到回饋報告，整個學習循環在一個平台內完成。</p>
        </div>
        <div class="steps-grid">
          <div v-for="step in steps" :key="step.num" class="step-card">
            <span class="step-num">{{ step.num }}</span>
            <h3 class="step-title">{{ step.title }}</h3>
            <p class="step-desc">{{ step.desc }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- ── Features ── -->
    <section class="section feat-section">
      <div class="section-inner">
        <div class="section-header">
          <span class="section-eyebrow">功能</span>
          <h2 class="section-title">為現代護理教育設計</h2>
          <p class="section-subtitle">每一項功能都針對護理溝通訓練的核心痛點打造。</p>
        </div>
        <div class="feat-grid">
          <div v-for="feat in features" :key="feat.title" class="feat-card">
            <span class="feat-icon">{{ feat.icon }}</span>
            <h3 class="feat-title">{{ feat.title }}</h3>
            <p class="feat-desc">{{ feat.desc }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- ── FAQ ── -->
    <section class="section faq-section">
      <div class="section-inner">
        <div class="section-header">
          <span class="section-eyebrow">常見問題</span>
          <h2 class="section-title">你可能想知道</h2>
          <p class="section-subtitle">找不到答案？歡迎直接與我們聯繫。</p>
        </div>
        <div class="faq-list">
          <div
            v-for="(faq, i) in faqs"
            :key="i"
            class="faq-item"
            :class="{ 'faq-item--open': activeFaq === i }"
          >
            <button class="faq-q" @click="toggleFaq(i)" :aria-expanded="activeFaq === i">
              <span>{{ faq.q }}</span>
              <span class="faq-chevron" aria-hidden="true">
                <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                  <path d="M5 7.5L10 12.5L15 7.5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
              </span>
            </button>
            <div class="faq-a" :class="{ 'faq-a--open': activeFaq === i }">
              <p>{{ faq.a }}</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ── Contact ── -->
    <section class="section contact-section" id="contact">
      <div class="section-inner contact-inner">
        <div class="contact-info">
          <span class="section-eyebrow">聯絡我們</span>
          <h2 class="section-title">想了解更多？</h2>
          <p class="contact-desc">
            歡迎學校、醫院、護理培訓機構與我們聯繫，<br />探討合作導入方案。
          </p>
          <div class="contact-items">
            <a href="mailto:contact@nurvo.ai" class="contact-item">
              <span class="contact-item-icon">✉</span>
              <span>contact@nurvo.ai</span>
            </a>
            <div class="contact-item">
              <span class="contact-item-icon">📍</span>
              <span>Taiwan</span>
            </div>
          </div>
        </div>

        <div class="cta-card">
          <h3 class="cta-card-title">立即體驗 Nurvo</h3>
          <p class="cta-card-desc">免費試用 AI 護理溝通訓練平台，無須任何設定。</p>
          <button class="cta-primary" @click="startGame">開始免費訓練</button>
        </div>
      </div>
    </section>

    <!-- ── Footer ── -->
    <footer class="site-footer">
      <div class="footer-inner">
        <div class="footer-brand">
          <span class="footer-logo">Nurvo</span>
          <p class="footer-tagline">AI 驅動護理溝通訓練平台</p>
        </div>
        <nav class="footer-links">
          <a href="#" class="footer-link">關於我們</a>
          <a href="#contact" class="footer-link">聯絡</a>
          <a href="#" class="footer-link">隱私政策</a>
        </nav>
        <p class="footer-copy">© 2025 Nurvo. All rights reserved.</p>
      </div>
    </footer>
  </div>
</template>

<style scoped>
/* ── Base ── */
.home {
  min-height: 100vh;
  position: relative;
  overflow-x: hidden;
  background:
    radial-gradient(circle at 20% 12%, #dbeafe 0%, transparent 30%),
    radial-gradient(circle at 85% 8%, #e0f2fe 0%, transparent 32%),
    #f8fbff;
}

.bg-glow {
  position: absolute;
  border-radius: 50%;
  filter: blur(50px);
  pointer-events: none;
  opacity: 0.4;
  z-index: 0;
}
.bg-glow--left  { width: 280px; height: 280px; left: -90px;  top: 42px; background: #60a5fa; }
.bg-glow--right { width: 320px; height: 320px; right: -120px; top: 24px; background: #7dd3fc; }

/* ── Hero ── */
.hero {
  position: relative;
  z-index: 1;
  max-width: 1400px;
  margin: 30px auto 0;
  padding: 20px 40px 80px;
  display: flex;
  align-items: stretch;
  gap: 80px;
  min-height: calc(100vh - 220px);
}

.hero-left {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 24px;
  min-width: 0;
}

.hero-right {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: flex-start;
  min-width: 0;
}

.brand-hero { display: flex; flex-direction: column; align-items: flex-start; gap: 20px; }

.hero-logo {
  width: 96px;
  height: 96px;
  object-fit: contain;
  border-radius: 20px;
}

.brand-title {
  margin: 0;
  font-size: 96px;
  font-weight: 900;
  letter-spacing: -0.04em;
  background: linear-gradient(135deg, var(--nurvo-primary) 0%, #0ea5e9 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  line-height: 1;
}

.eyebrow {
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--nurvo-primary-dark);
  margin: 0;
}

.tagline {
  margin: 0;
  font-size: 42px;
  font-weight: 700;
  color: var(--nurvo-text-primary);
  line-height: 1.3;
}

.description {
  margin: 0;
  max-width: 600px;
  color: #475569;
  font-size: 18px;
  line-height: 1.8;
}

.hero-actions { display: flex; gap: 16px; align-items: center; flex-wrap: wrap; }

.cta-primary {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 16px 40px;
  min-height: 56px;
  border-radius: 14px;
  border: none;
  background: var(--nurvo-gradient-primary);
  color: var(--nurvo-white);
  font-size: 16px;
  font-weight: 700;
  letter-spacing: 0.01em;
  cursor: pointer;
  box-shadow: 0 12px 28px rgba(37, 99, 235, 0.32);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.cta-primary:hover {
  transform: translateY(-3px);
  box-shadow: 0 16px 36px rgba(37, 99, 235, 0.4);
}

.cta-secondary {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 15px 32px;
  min-height: 56px;
  border-radius: 14px;
  border: 2px solid #bfdbfe;
  background: rgba(255, 255, 255, 0.7);
  color: var(--nurvo-primary);
  font-size: 16px;
  font-weight: 600;
  text-decoration: none;
  transition: border-color 0.2s ease, background 0.2s ease, transform 0.2s ease;
}
.cta-secondary:hover {
  border-color: var(--nurvo-primary);
  background: rgba(219, 234, 254, 0.5);
  transform: translateY(-2px);
}

.features-container {
  background: rgba(255, 255, 255, 0.5);
  backdrop-filter: blur(8px);
  border: 1px solid #dbeafe;
  border-radius: 20px;
  padding: 40px;
  width: 100%;
  box-shadow: 0 20px 40px rgba(37, 99, 235, 0.1);
  transition: border-color 0.4s ease, box-shadow 0.4s ease, transform 0.4s ease;
}
.features-container:hover {
  border-color: #a5f3fc;
  box-shadow: 0 24px 48px rgba(37, 99, 235, 0.15);
  transform: translateY(-4px);
}

.features-title {
  margin: 0 0 28px;
  font-size: 28px;
  font-weight: 700;
  color: var(--nurvo-text-primary);
}

.features { display: flex; flex-direction: column; gap: 14px; margin: 0; padding: 0; list-style: none; }

.feature-item {
  display: flex;
  align-items: center;
  gap: 12px;
  color: #334155;
  font-size: 16px;
  font-weight: 500;
  padding: 12px 14px;
  border-radius: 12px;
  transition: all 0.3s ease;
}
.feature-item:hover {
  background: rgba(37, 99, 235, 0.05);
  transform: translateX(6px);
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.1);
}

.feature-icon {
  flex-shrink: 0;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: var(--nurvo-success-light);
  color: var(--nurvo-success-dark);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  font-weight: 700;
  box-shadow: 0 0 0 3px rgba(34, 197, 94, 0.1);
  transition: all 0.3s ease;
}
.feature-item:hover .feature-icon {
  transform: scale(1.15);
  box-shadow: 0 0 12px rgba(34, 197, 94, 0.3);
}

/* ── Shared Section Layout ── */
.section {
  position: relative;
  z-index: 1;
  padding: 96px 40px;
}

.section-inner {
  max-width: 1200px;
  margin: 0 auto;
}

.section-header {
  text-align: center;
  margin-bottom: 64px;
}

.section-eyebrow {
  display: inline-block;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.15em;
  text-transform: uppercase;
  color: var(--nurvo-primary);
  background: rgba(37, 99, 235, 0.08);
  padding: 6px 16px;
  border-radius: 99px;
  margin-bottom: 16px;
}

.section-title {
  margin: 0 0 16px;
  font-size: 38px;
  font-weight: 800;
  color: var(--nurvo-text-primary);
  line-height: 1.25;
}

.section-subtitle {
  margin: 0;
  font-size: 17px;
  color: #64748b;
  max-width: 520px;
  margin-inline: auto;
  line-height: 1.7;
}

/* ── Steps ── */
.steps-section {}

.steps-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 32px;
}

.step-card {
  position: relative;
  background: #fff;
  border: 1px solid #e2eafd;
  border-radius: 20px;
  padding: 40px 32px;
  transition: box-shadow 0.3s ease, transform 0.3s ease;
}
.step-card:hover {
  box-shadow: 0 16px 40px rgba(37, 99, 235, 0.12);
  transform: translateY(-6px);
}
.step-card:not(:last-child)::after {
  content: '→';
  position: absolute;
  right: -22px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 22px;
  color: #bfdbfe;
  pointer-events: none;
}

.step-num {
  display: block;
  font-size: 40px;
  font-weight: 900;
  letter-spacing: -0.04em;
  color: #bfdbfe;
  line-height: 1;
  margin-bottom: 16px;
}

.step-title {
  margin: 0 0 12px;
  font-size: 20px;
  font-weight: 700;
  color: var(--nurvo-text-primary);
}

.step-desc {
  margin: 0;
  font-size: 15px;
  color: #64748b;
  line-height: 1.7;
}

/* ── Features Grid ── */
.feat-section {}

.feat-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
}

.feat-card {
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(6px);
  border: 1px solid #dbeafe;
  border-radius: 18px;
  padding: 32px 28px;
  transition: box-shadow 0.3s ease, transform 0.3s ease, border-color 0.3s ease;
}
.feat-card:hover {
  border-color: #93c5fd;
  box-shadow: 0 12px 32px rgba(37, 99, 235, 0.12);
  transform: translateY(-4px);
}

.feat-icon {
  display: block;
  font-size: 32px;
  margin-bottom: 16px;
}

.feat-title {
  margin: 0 0 10px;
  font-size: 17px;
  font-weight: 700;
  color: var(--nurvo-text-primary);
}

.feat-desc {
  margin: 0;
  font-size: 14px;
  color: #64748b;
  line-height: 1.75;
}

/* ── FAQ ── */
.faq-list {
  max-width: 760px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.faq-item {
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(6px);
  border: 1px solid #dbeafe;
  border-radius: 16px;
  overflow: hidden;
  transition: border-color 0.25s ease, box-shadow 0.25s ease;
}
.faq-item--open {
  border-color: #93c5fd;
  box-shadow: 0 8px 24px rgba(37, 99, 235, 0.1);
}

.faq-q {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 20px 24px;
  background: none;
  border: none;
  cursor: pointer;
  font-size: 16px;
  font-weight: 600;
  color: var(--nurvo-text-primary);
  text-align: left;
  transition: color 0.2s ease;
}
.faq-item--open .faq-q { color: var(--nurvo-primary); }

.faq-chevron {
  flex-shrink: 0;
  color: #94a3b8;
  transition: transform 0.3s ease, color 0.2s ease;
  display: flex;
}
.faq-item--open .faq-chevron {
  transform: rotate(180deg);
  color: var(--nurvo-primary);
}

.faq-a {
  max-height: 0;
  overflow: hidden;
  transition: max-height 0.35s ease, padding 0.35s ease;
}
.faq-a--open {
  max-height: 200px;
}
.faq-a p {
  margin: 0;
  padding: 0 24px 20px;
  font-size: 15px;
  color: #475569;
  line-height: 1.75;
}

/* ── Contact ── */
.contact-section {
  background: linear-gradient(135deg, #1d4ed8 0%, #0284c7 100%);
}

.contact-section .section-eyebrow {
  color: #93c5fd;
  background: rgba(255, 255, 255, 0.12);
}

.contact-section .section-title {
  color: #fff;
}

.contact-inner {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 64px;
  align-items: center;
}

.contact-desc {
  margin: 16px 0 32px;
  font-size: 17px;
  color: rgba(255, 255, 255, 0.8);
  line-height: 1.7;
}

.contact-items {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.contact-item {
  display: flex;
  align-items: center;
  gap: 14px;
  color: rgba(255, 255, 255, 0.9);
  font-size: 16px;
  font-weight: 500;
  text-decoration: none;
  transition: color 0.2s ease;
}
.contact-item:hover { color: #fff; }

.contact-item-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.15);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  flex-shrink: 0;
}

.cta-card {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 24px;
  padding: 48px 40px;
  text-align: center;
}

.cta-card-title {
  margin: 0 0 12px;
  font-size: 26px;
  font-weight: 800;
  color: #fff;
}

.cta-card-desc {
  margin: 0 0 32px;
  font-size: 15px;
  color: rgba(255, 255, 255, 0.75);
  line-height: 1.6;
}

.cta-card .cta-primary {
  background: #fff;
  color: var(--nurvo-primary);
  box-shadow: 0 12px 28px rgba(0, 0, 0, 0.15);
}
.cta-card .cta-primary:hover {
  box-shadow: 0 16px 36px rgba(0, 0, 0, 0.2);
}

/* ── Footer ── */
.site-footer {
  background: #0f172a;
  padding: 48px 40px;
}

.footer-inner {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 24px;
}

.footer-logo {
  font-size: 22px;
  font-weight: 900;
  letter-spacing: -0.03em;
  background: linear-gradient(135deg, #60a5fa 0%, #38bdf8 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.footer-tagline {
  margin: 4px 0 0;
  font-size: 13px;
  color: #64748b;
}

.footer-links {
  display: flex;
  gap: 28px;
}

.footer-link {
  font-size: 14px;
  color: #94a3b8;
  text-decoration: none;
  transition: color 0.2s ease;
}
.footer-link:hover { color: #e2e8f0; }

.footer-copy {
  margin: 0;
  font-size: 13px;
  color: #475569;
  width: 100%;
  text-align: center;
  border-top: 1px solid #1e293b;
  padding-top: 24px;
  margin-top: 8px;
}

/* ── Responsive ── */
@media (max-width: 1024px) {
  .hero { gap: 50px; padding: 20px 32px 60px; }
  .brand-title { font-size: 72px; }
  .tagline { font-size: 36px; }
  .description { font-size: 16px; }
  .feat-grid { grid-template-columns: repeat(2, 1fr); }
  .section-title { font-size: 32px; }
}

@media (max-width: 768px) {
  .hero {
    flex-direction: column;
    gap: 40px;
    min-height: auto;
    padding: 20px 20px 48px;
  }
  .hero-right { align-items: stretch; }
  .brand-title { font-size: 56px; }
  .tagline { font-size: 28px; }
  .description { font-size: 15px; }
  .cta-primary, .cta-secondary { padding: 14px 28px; min-height: 50px; font-size: 15px; }
  .features-container { padding: 28px 20px; }
  .features-title { font-size: 22px; margin-bottom: 20px; }
  .feature-item { font-size: 14px; }

  .section { padding: 64px 20px; }
  .section-title { font-size: 28px; }
  .steps-grid { grid-template-columns: 1fr; gap: 16px; }
  .step-card::after { display: none; }
  .feat-grid { grid-template-columns: 1fr; gap: 16px; }

  .contact-inner { grid-template-columns: 1fr; gap: 40px; }
  .cta-card { padding: 32px 24px; }

  .footer-inner { flex-direction: column; align-items: flex-start; gap: 20px; }
  .footer-links { gap: 20px; }
  .footer-copy { text-align: left; }
}

@media (max-width: 420px) {
  .brand-title { font-size: 42px; }
  .tagline { font-size: 22px; }
  .description { font-size: 13px; }
  .section-title { font-size: 24px; }
}
</style>
