<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useScenarioStore } from '@/stores/scenarioStore'
import { useGameStore } from '@/stores/gameStore'

const router = useRouter()
const scenarioStore = useScenarioStore()
const gameStore = useGameStore()

const loading = ref(false)
const errorMsg = ref('')

async function startGame() {
  if (loading.value) return
  loading.value = true
  errorMsg.value = ''

  try {
    gameStore.reset()
    scenarioStore.reset()
    await scenarioStore.fetchScenario()
    router.push('/briefing')
  } catch (error: any) {
    errorMsg.value = error.message || '情境生成失敗，請稍後再試'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="home">
    <!-- Nav -->
    <nav class="nav">
      <div class="nav-brand">
        <div class="nav-logo">N</div>
        <span class="nav-name">Nurvo</span>
      </div>
    </nav>

    <!-- Split Hero -->
    <main class="hero">
      <!-- Left: Text + CTA -->
      <div class="hero-left">
        <h1 class="headline">護理溝通模擬訓練</h1>
        <p class="description">
          透過 AI 驅動的擬真情境，練習與病患及家屬的溝通技巧。<br />
          提升同理心表達、疼痛評估與臨床應對能力。
        </p>

        <button
          class="cta-button"
          :disabled="loading"
          @click="startGame"
        >
          <span v-if="loading" class="spinner" />
          <span v-else>開始訓練 &rarr;</span>
        </button>

        <div v-if="errorMsg" class="error-alert">
          <span class="error-icon">!</span>
          <span class="error-text">{{ errorMsg }}</span>
        </div>
      </div>

      <!-- Right: Preview Panel -->
      <div class="hero-right">
        <div class="preview-panel">
          <div class="chat-card">
            <div class="chat-header">
              <div class="chat-header-dot" />
              <span class="chat-header-title">對話預覽</span>
            </div>
            <div class="chat-messages">
              <div class="msg msg-patient">
                <span class="msg-label">病患</span>
                <div class="msg-bubble msg-bubble-patient">
                  護理師，我的傷口又開始痛了，比早上還嚴重...
                </div>
              </div>
              <div class="msg msg-nurse">
                <span class="msg-label">護理師</span>
                <div class="msg-bubble msg-bubble-nurse">
                  我了解這讓您很不舒服。可以幫我描述一下疼痛的感覺嗎？像是刺痛、悶痛還是脹痛呢？
                </div>
              </div>
              <div class="msg msg-patient">
                <span class="msg-label">病患</span>
                <div class="msg-bubble msg-bubble-patient">
                  就是一陣一陣的刺痛，翻身的時候特別明顯。
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<style scoped>
.home {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--nurvo-white);
}

/* ── Nav ── */
.nav {
  display: flex;
  align-items: center;
  padding: 16px 32px;
}

.nav-brand {
  display: flex;
  align-items: center;
  gap: 8px;
}

.nav-logo {
  width: 32px;
  height: 32px;
  border-radius: var(--nurvo-radius-sm);
  background: var(--nurvo-gradient-logo);
  color: var(--nurvo-white);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  font-weight: 800;
  line-height: 1;
}

.nav-name {
  font-size: 16px;
  font-weight: 700;
  color: var(--nurvo-text-primary);
}

/* ── Hero Split ── */
.hero {
  flex: 1;
  display: flex;
  align-items: center;
  padding: 0 48px 48px;
  gap: 48px;
}

.hero-left {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 20px;
  max-width: 480px;
}

.headline {
  font-size: 30px;
  font-weight: 800;
  color: var(--nurvo-text-primary);
  line-height: 1.3;
  letter-spacing: -0.01em;
  margin: 0;
}

.description {
  font-size: 15px;
  color: var(--nurvo-text-secondary);
  line-height: 1.75;
  margin: 0;
}

/* ── CTA Button ── */
.cta-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  align-self: flex-start;
  padding: 12px 28px;
  border: none;
  border-radius: 12px;
  background: var(--nurvo-gradient-primary);
  color: var(--nurvo-white);
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  box-shadow: var(--nurvo-shadow-button);
  transition: opacity 0.2s, transform 0.15s;
  min-width: 140px;
  min-height: 44px;
}

.cta-button:hover:not(:disabled) {
  opacity: 0.92;
  transform: translateY(-1px);
}

.cta-button:active:not(:disabled) {
  transform: translateY(0);
}

.cta-button:disabled {
  cursor: not-allowed;
  opacity: 0.8;
}

/* ── Spinner ── */
.spinner {
  width: 20px;
  height: 20px;
  border: 2.5px solid rgba(255, 255, 255, 0.35);
  border-top-color: var(--nurvo-white);
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* ── Error Alert ── */
.error-alert {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px;
  background: var(--nurvo-danger-light);
  border: 1px solid var(--nurvo-danger-border);
  border-radius: var(--nurvo-radius-sm);
  max-width: 380px;
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
  font-size: 13px;
  color: var(--nurvo-danger-dark);
  line-height: 1.4;
}

/* ── Right Panel ── */
.hero-right {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  max-width: 520px;
}

.preview-panel {
  width: 100%;
  padding: 40px;
  background: var(--nurvo-gradient-hero);
  border-radius: var(--nurvo-radius-xl);
}

/* ── Chat Card ── */
.chat-card {
  background: var(--nurvo-white);
  border-radius: var(--nurvo-radius-lg);
  box-shadow: var(--nurvo-shadow-lg);
  overflow: hidden;
}

.chat-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 14px 18px;
  border-bottom: 1px solid var(--nurvo-border-light);
}

.chat-header-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--nurvo-success);
}

.chat-header-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--nurvo-text-secondary);
}

.chat-messages {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 18px;
}

.msg {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.msg-label {
  font-size: 11px;
  font-weight: 600;
  color: var(--nurvo-text-muted);
  padding-left: 2px;
}

.msg-nurse {
  align-items: flex-end;
}

.msg-nurse .msg-label {
  padding-right: 2px;
  padding-left: 0;
}

.msg-bubble {
  padding: 10px 14px;
  border-radius: var(--nurvo-radius-md);
  font-size: 13px;
  line-height: 1.6;
  max-width: 88%;
}

.msg-bubble-patient {
  background: var(--nurvo-patient-bubble);
  color: var(--nurvo-patient-darkest);
  align-self: flex-start;
}

.msg-bubble-nurse {
  background: var(--nurvo-nurse-bubble);
  color: var(--nurvo-nurse-text);
  align-self: flex-end;
}

/* ── Responsive ── */
@media (max-width: 768px) {
  .hero {
    flex-direction: column;
    padding: 24px;
    gap: 32px;
  }

  .hero-left {
    max-width: 100%;
    align-items: center;
    text-align: center;
  }

  .cta-button {
    align-self: center;
  }

  .error-alert {
    max-width: 100%;
  }

  .hero-right {
    max-width: 100%;
    width: 100%;
  }

  .headline {
    font-size: 26px;
  }

  .nav {
    padding: 12px 20px;
  }
}
</style>
