import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    {
      path: '/briefing',
      name: 'briefing',
      component: () => import('../views/BriefingView.vue'),
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

export default router
