<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useGameStore } from '@/stores/gameStore'
import NavBar from '@/components/shared/NavBar.vue'

const router = useRouter()
const gameStore = useGameStore()

const highlights = [
  'AI 動態情境，每次練習都不同',
  '病患 + 家屬雙角色即時互動',
  '結束即生成可執行回饋',
]

function startGame() {
  gameStore.reset()
  router.push('/level-select')
}
</script>

<template>
  <div class="home">
    <div class="bg-glow bg-glow--left"></div>
    <div class="bg-glow bg-glow--right"></div>

    <NavBar />

    <main class="hero">
      <section class="hero-left">
        <div class="brand-hero">
          <h1 class="brand-title">Nurvo</h1>
        </div>

        <p class="eyebrow">Clinical Communication Training Platform</p>
        
        <h2 class="tagline">
          AI 驅動護理對話訓練平台
        </h2>

        <p class="description">
          讓每次護理對話都成為可量化的進步。
          <br />
          與 AI 病患及家屬互動，從同理心到問診流程，即時獲得專業回饋。
        </p>

        <button class="cta-primary" @click="startGame">開始訓練</button>
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
  </div>
</template>

<style scoped>
.home {
  min-height: 100vh;
  position: relative;
  overflow: hidden;
  background:
    radial-gradient(circle at 20% 12%, #dbeafe 0%, transparent 30%),
    radial-gradient(circle at 85% 8%, #e0f2fe 0%, transparent 32%),
    #f8fbff;
  padding: 20px 40px 60px;
}

.bg-glow {
  position: absolute;
  border-radius: 50%;
  filter: blur(50px);
  pointer-events: none;
  opacity: 0.4;
}

.bg-glow--left {
  width: 280px;
  height: 280px;
  left: -90px;
  top: 42px;
  background: #60a5fa;
}

.bg-glow--right {
  width: 320px;
  height: 320px;
  right: -120px;
  top: 24px;
  background: #7dd3fc;
}

.hero {
  position: relative;
  z-index: 1;
  max-width: 1400px;
  margin: 30px auto 0;
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

.brand-hero {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 20px;
}

.brand-logo-large {
  width: 120px;
  height: 120px;
  border-radius: 24px;
  background: var(--nurvo-gradient-logo);
  color: var(--nurvo-white);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 56px;
  font-weight: 900;
  box-shadow: 0 20px 50px rgba(37, 99, 235, 0.3);
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0px);
  }
  50% {
    transform: translateY(-8px);
  }
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
  transition: transform 0.2s ease, box-shadow 0.2s ease, opacity 0.2s ease;
}

.cta-primary:hover:not(:disabled) {
  transform: translateY(-3px);
  box-shadow: 0 16px 36px rgba(37, 99, 235, 0.4);
}

.cta-primary:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.spinner {
  width: 20px;
  height: 20px;
  border: 2px solid rgba(255, 255, 255, 0.35);
  border-top-color: var(--nurvo-white);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.error-alert {
  display: flex;
  align-items: center;
  gap: 8px;
  width: fit-content;
  max-width: 100%;
  padding: 10px 12px;
  background: rgba(254, 242, 242, 0.95);
  border: 1px solid var(--nurvo-danger-border);
  border-radius: var(--nurvo-radius-sm);
  margin: 0 auto;
}

.error-icon {
  flex-shrink: 0;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: var(--nurvo-danger);
  color: var(--nurvo-white);
  font-size: 12px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  line-height: 1;
}

.error-text {
  font-size: 12px;
  color: var(--nurvo-danger-dark);
  line-height: 1.4;
}

.features {
  display: flex;
  flex-direction: column;
  gap: 14px;
  margin: 0;
  padding: 0;
  list-style: none;
  max-width: 500px;
}

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
  color: var(--nurvo-text-primary);
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

.features-container {
  background: rgba(255, 255, 255, 0.5);
  backdrop-filter: blur(8px);
  border: 1px solid #dbeafe;
  border-radius: 20px;
  padding: 40px;
  width: 100%;
  box-shadow: 0 20px 40px rgba(37, 99, 235, 0.1);
  transition: all 0.4s ease;
  position: relative;
  overflow: hidden;
}

.features-container::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.02) 0%, rgba(6, 182, 212, 0.02) 100%);
  opacity: 0;
  transition: opacity 0.4s ease;
  pointer-events: none;
}

.hero-right:hover .features-container::before {
  opacity: 1;
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

@media (max-width: 1024px) {
  .hero {
    gap: 50px;
  }

  .brand-title {
    font-size: 72px;
  }

  .tagline {
    font-size: 36px;
  }

  .description {
    font-size: 16px;
  }
}

@media (max-width: 768px) {
  .home {
    padding: 16px 20px 40px;
  }

  .hero {
    flex-direction: column;
    gap: 40px;
    min-height: auto;
    padding-top: 20px;
  }

  .hero-left {
    gap: 20px;
  }

  .hero-right {
    align-items: stretch;
  }

  .brand-logo-large {
    width: 100px;
    height: 100px;
    font-size: 48px;
  }

  .brand-title {
    font-size: 56px;
  }

  .tagline {
    font-size: 28px;
  }

  .description {
    font-size: 15px;
  }

  .cta-primary {
    padding: 14px 32px;
    min-height: 48px;
    font-size: 15px;
  }

  .features {
    gap: 12px;
    max-width: 100%;
  }

  .feature-item {
    font-size: 14px;
  }

  .features-container {
    padding: 28px;
  }

  .features-title {
    font-size: 22px;
    margin-bottom: 20px;
  }
}

@media (max-width: 420px) {
  .brand-title {
    font-size: 42px;
  }

  .tagline {
    font-size: 22px;
  }

  .description {
    font-size: 13px;
  }

  .feature-item {
    font-size: 13px;
    gap: 8px;
  }

  .features-container {
    padding: 20px;
  }

  .features-title {
    font-size: 18px;
    margin-bottom: 16px;
  }
}
</style>
