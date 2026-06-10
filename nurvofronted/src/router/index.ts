import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import HomeView from '../views/HomeView.vue'

const PROTECTED = new Set(['level-select', 'briefing', 'scene', 'record', 'dashboard'])

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    {
      path: '/auth/callback',
      name: 'auth-callback',
      component: () => import('../views/AuthCallbackView.vue'),
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/LoginView.vue'),
    },
    {
      path: '/briefing',
      name: 'briefing',
      component: () => import('../views/BriefingView.vue'),
    },
    {
      path: '/level-select',
      name: 'level-select',
      component: () => import('../views/LevelSelectView.vue'),
    },
    {
      path: '/scene',
      name: 'scene',
      component: () => import('../views/SceneView.vue'),
    },
    {
      path: '/record',
      name: 'record',
      component: () => import('../views/RecordView.vue'),
    },
    {
      path: '/dashboard',
      name: 'dashboard',
      component: () => import('../views/DashboardView.vue'),
    },
  ],
})

router.beforeEach((to) => {
  if (PROTECTED.has(to.name as string)) {
    const authStore = useAuthStore()
    if (!authStore.isAuthenticated) {
      sessionStorage.setItem('nurvo_redirect', to.fullPath)
      return { name: 'login' }
    }
  }
})

export default router
