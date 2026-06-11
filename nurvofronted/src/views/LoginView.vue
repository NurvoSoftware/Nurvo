<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'

const router = useRouter()
const authStore = useAuthStore()

const email = ref('')
const password = ref('')
const errorMsg = ref('')
const loading = ref(false)

function getRedirect(): string {
  return sessionStorage.getItem('nurvo_redirect') || '/level-select'
}

function handleGoogleLogin() {
  authStore.loginWithGoogle()
}

async function handleEmailLogin() {
  if (!email.value || !password.value) {
    errorMsg.value = '請輸入信箱與密碼'
    return
  }
  errorMsg.value = ''
  loading.value = true
  try {
    await authStore.loginWithEmail(email.value, password.value)
    const redirect = getRedirect()
    sessionStorage.removeItem('nurvo_redirect')
    router.push(redirect)
  } catch (err: any) {
    errorMsg.value = err.message || '登入失敗，請稍後再試'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="login-page">

    <!-- Left panel: image placeholder -->
    <!-- 圖片來源：public/nurvo_login_bg.png -->
    <div class="panel-left">
      <div class="hero-overlay">
        <img src="/Nurvo_logo.png" class="hero-logo" alt="Nurvo" />
        <p class="hero-tagline">護理溝通 AI 訓練平台</p>
      </div>
    </div>

    <!-- Right panel: login form -->
    <div class="panel-right">
      <div class="login-card">
        <div class="card-header">
          <h1 class="title">登入 Nurvo</h1>
          <p class="subtitle">歡迎回來，請選擇登入方式</p>
        </div>

        <button class="btn-google" @click="handleGoogleLogin">
          <svg viewBox="0 0 24 24" width="20" height="20" class="google-icon">
            <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
            <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
            <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l3.66-2.84z"/>
            <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
          </svg>
          使用 Google 帳號登入
        </button>

        <div class="divider"><span>或</span></div>

        <form class="email-form" @submit.prevent="handleEmailLogin">
          <div class="field">
            <label for="email">電子信箱</label>
            <input
              id="email"
              v-model="email"
              type="email"
              placeholder="you@example.com"
              autocomplete="email"
              :disabled="loading"
            />
          </div>
          <div class="field">
            <label for="password">密碼</label>
            <input
              id="password"
              v-model="password"
              type="password"
              placeholder="請輸入密碼"
              autocomplete="current-password"
              :disabled="loading"
            />
          </div>

          <p v-if="errorMsg" class="error-msg">{{ errorMsg }}</p>

          <button type="submit" class="btn-submit" :disabled="loading">
            <span v-if="loading" class="spinner" />
            {{ loading ? '登入中…' : '登入' }}
          </button>
        </form>

        <p class="back-link">
          <router-link to="/">← 返回首頁</router-link>
        </p>
      </div>
    </div>

  </div>
</template>

<style scoped>
/* ── Layout ─────────────────────────────────────────── */
.login-page {
  min-height: 100vh;
  display: grid;
  grid-template-columns: 1fr 1fr;
}

/* ── Left panel ─────────────────────────────────────── */
.panel-left {
  position: relative;
  overflow: hidden;
  /* fallback gradient；放入 public/login-hero.jpg 後圖片會蓋住漸層 */
  background:
    url('/nurvo_login_bg.png') center / cover no-repeat,
    linear-gradient(160deg, #1e40af 0%, #0369a1 50%, #0e7490 100%);
}

.hero-overlay {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-end;
  padding: 40px;
  background: linear-gradient(to top, rgba(10, 30, 70, 0.72) 0%, transparent 55%);
}

.hero-logo {
  width: 52px;
  height: 52px;
  object-fit: contain;
  border-radius: 12px;
  margin-bottom: 12px;
}

.hero-tagline {
  font-size: 15px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.88);
  letter-spacing: 0.04em;
  margin: 0;
}

/* ── Right panel ─────────────────────────────────────── */
.panel-right {
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f8fbff;
  padding: 40px 24px;
}

.login-card {
  width: 100%;
  max-width: 400px;
}

.card-header {
  margin-bottom: 28px;
}

.title {
  font-size: 26px;
  font-weight: 800;
  color: #1e3a5f;
  margin: 0 0 6px;
}

.subtitle {
  font-size: 14px;
  color: #64748b;
  margin: 0;
}

/* ── Google button ───────────────────────────────────── */
.btn-google {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 12px 20px;
  background: #fff;
  border: 1.5px solid #e2e8f0;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 600;
  color: #1e293b;
  cursor: pointer;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
  transition: border-color 0.2s, box-shadow 0.2s;
}
.btn-google:hover {
  border-color: #93c5fd;
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.1);
}
.google-icon { flex-shrink: 0; }

/* ── Divider ─────────────────────────────────────────── */
.divider {
  display: flex;
  align-items: center;
  gap: 12px;
  margin: 20px 0;
  color: #94a3b8;
  font-size: 13px;
}
.divider::before,
.divider::after {
  content: '';
  flex: 1;
  height: 1px;
  background: #e2e8f0;
}

/* ── Email form ──────────────────────────────────────── */
.email-form {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.field label {
  font-size: 13px;
  font-weight: 600;
  color: #475569;
}

.field input {
  padding: 10px 14px;
  border: 1.5px solid #e2e8f0;
  border-radius: 10px;
  font-size: 14px;
  color: #1e293b;
  background: #fff;
  outline: none;
  transition: border-color 0.2s, box-shadow 0.2s;
}
.field input:focus {
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.12);
}
.field input:disabled {
  background: #f8fafc;
  color: #94a3b8;
}

.error-msg {
  font-size: 13px;
  color: #ef4444;
  margin: 0;
  padding: 8px 12px;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 8px;
}

.btn-submit {
  width: 100%;
  padding: 12px 20px;
  background: linear-gradient(135deg, #2563eb, #1d4ed8);
  color: #fff;
  border: none;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 700;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: opacity 0.2s, box-shadow 0.2s;
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
}
.btn-submit:hover:not(:disabled) {
  opacity: 0.9;
  box-shadow: 0 6px 16px rgba(37, 99, 235, 0.4);
}
.btn-submit:disabled {
  opacity: 0.65;
  cursor: not-allowed;
}

.spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.4);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.back-link {
  text-align: center;
  margin: 20px 0 0;
  font-size: 13px;
}
.back-link a {
  color: #3b82f6;
  text-decoration: none;
  font-weight: 500;
}
.back-link a:hover { text-decoration: underline; }

/* ── Mobile: single column ───────────────────────────── */
@media (max-width: 768px) {
  .login-page { grid-template-columns: 1fr; }
  .panel-left { display: none; }
  .panel-right { padding: 40px 20px; background: linear-gradient(135deg, #eff6ff, #dbeafe); }
}
</style>
