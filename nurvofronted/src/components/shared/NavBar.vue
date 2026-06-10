<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'

defineProps<{
  step?: number
  stepLabel?: string
}>()

const router = useRouter()
const authStore = useAuthStore()

function handleLogout() {
  authStore.logout()
  router.push('/')
}
</script>

<template>
  <nav class="topbar">
    <div class="brand">
      <img src="/Nurvo_logo.png" class="brand-logo-img" alt="Nurvo" />
      <span class="brand-name">Nurvo</span>
    </div>

    <div class="nav-auth">
      <template v-if="authStore.isAuthenticated">
        <img
          v-if="authStore.user?.picture_url"
          :src="authStore.user.picture_url"
          class="user-avatar"
          :alt="authStore.user.name ?? ''"
          referrerpolicy="no-referrer"
        />
        <span class="user-name">{{ authStore.user?.name }}</span>
        <button class="btn-logout" @click="handleLogout">登出</button>
      </template>
      <template v-else>
        <button class="btn-login" @click="router.push('/login')">登入</button>
      </template>
    </div>
  </nav>
</template>

<style scoped>
.topbar {
  position: relative;
  z-index: 2;
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 1400px;
  margin: 0 auto;
  padding: 6px 20px 26px;
}

.brand {
  display: flex;
  align-items: center;
  gap: 10px;
}

.brand-logo-img {
  width: 36px;
  height: 36px;
  object-fit: contain;
  border-radius: 8px;
}

.brand-name {
  font-size: 18px;
  font-weight: 800;
  letter-spacing: -0.01em;
  color: var(--nurvo-text-primary);
}

.nav-auth {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid #dbeafe;
}

.user-name {
  font-size: 14px;
  font-weight: 600;
  color: var(--nurvo-text-primary);
  max-width: 140px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.btn-logout {
  font-size: 13px;
  font-weight: 600;
  color: #64748b;
  background: none;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 6px 14px;
  cursor: pointer;
  transition: border-color 0.2s, color 0.2s;
}
.btn-logout:hover {
  border-color: #94a3b8;
  color: #334155;
}

.btn-login {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 600;
  color: #1e293b;
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 8px 16px;
  cursor: pointer;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
  transition: box-shadow 0.2s, border-color 0.2s;
}
.btn-login:hover {
  border-color: #93c5fd;
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.1);
}

@media (max-width: 768px) {
  .topbar { padding: 6px 16px 20px; }
  .user-name { display: none; }
  .btn-login { font-size: 13px; padding: 7px 12px; }
}
</style>
