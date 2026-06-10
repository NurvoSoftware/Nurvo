import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import type { User } from '@/types/game'

const TOKEN_KEY = 'nurvo_token'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const token = ref<string | null>(localStorage.getItem(TOKEN_KEY))

  const isAuthenticated = computed(() => !!token.value && !!user.value)

  async function fetchMe(): Promise<void> {
    if (!token.value) return
    try {
      const res = await fetch('/api/auth/me', {
        headers: { Authorization: `Bearer ${token.value}` },
      })
      if (!res.ok) {
        // Token invalid or expired — clear it
        logout()
        return
      }
      user.value = await res.json()
    } catch {
      logout()
    }
  }

  async function init(): Promise<void> {
    if (token.value) {
      await fetchMe()
    }
  }

  function setToken(newToken: string): void {
    token.value = newToken
    localStorage.setItem(TOKEN_KEY, newToken)
  }

  function loginWithGoogle(): void {
    window.location.href = '/api/auth/google/login'
  }

  async function loginWithEmail(email: string, password: string): Promise<void> {
    const res = await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    })
    if (!res.ok) {
      const body = await res.json().catch(() => null)
      throw new Error(body?.detail || '帳號或密碼錯誤')
    }
    const data = await res.json()
    setToken(data.access_token)
    await fetchMe()
  }

  function logout(): void {
    token.value = null
    user.value = null
    localStorage.removeItem(TOKEN_KEY)
  }

  return { user, token, isAuthenticated, init, fetchMe, setToken, loginWithGoogle, loginWithEmail, logout }
})
