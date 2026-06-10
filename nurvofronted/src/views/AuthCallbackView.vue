<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'

const router = useRouter()
const authStore = useAuthStore()

onMounted(async () => {
  const hash = window.location.hash
  const token = new URLSearchParams(hash.replace('#', '?')).get('token')

  if (!token) {
    router.replace('/')
    return
  }

  authStore.setToken(token)
  await authStore.fetchMe()

  const redirect = sessionStorage.getItem('nurvo_redirect') || '/level-select'
  sessionStorage.removeItem('nurvo_redirect')
  router.replace(redirect)
})
</script>

<template>
  <div class="callback-page">
    <div class="callback-card">
      <img src="/Nurvo_logo.png" class="callback-logo" alt="Nurvo" />
      <p class="callback-text">登入中，請稍候…</p>
      <div class="spinner"></div>
    </div>
  </div>
</template>

<style scoped>
.callback-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background:
    radial-gradient(circle at 20% 12%, #dbeafe 0%, transparent 30%),
    #f8fbff;
}

.callback-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
  padding: 48px 56px;
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(12px);
  border: 1px solid #dbeafe;
  border-radius: 24px;
  box-shadow: 0 20px 48px rgba(37, 99, 235, 0.1);
}

.callback-logo {
  width: 72px;
  height: 72px;
  object-fit: contain;
  border-radius: 16px;
}

.callback-text {
  margin: 0;
  font-size: 17px;
  font-weight: 600;
  color: #334155;
}

.spinner {
  width: 28px;
  height: 28px;
  border: 3px solid #bfdbfe;
  border-top-color: #2563eb;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
