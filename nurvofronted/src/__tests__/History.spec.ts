import { flushPromises, mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import HistoryView from '@/views/HistoryView.vue'
import HistoryDetailView from '@/views/HistoryDetailView.vue'
import NavBar from '@/components/shared/NavBar.vue'
import { useAuthStore } from '@/stores/authStore'
import type { HistoryDetail, HistoryItem } from '@/types/game'

const routerMock = vi.hoisted(() => ({ push: vi.fn() }))

const apiMocks = vi.hoisted(() => ({
  fetchHistory: vi.fn(),
  fetchHistoryDetail: vi.fn(),
}))

vi.mock('vue-router', () => ({
  useRouter: () => routerMock,
  useRoute: () => ({ params: { sessionId: 'sess-1' } }),
}))

vi.mock('@/services/apiService', () => apiMocks)

// NavBar's public-dir logo compiles to an import that vitest can't resolve on Windows.
vi.mock('/Nurvo_logo.png', () => ({ default: '/Nurvo_logo.png' }))

// Chart components pull in canvas/SVG libs that jsdom can't render; the report
// shape is what's under test, not the charts.
vi.mock('@/components/dashboard/RadarChart.vue', () => ({ default: { template: '<div />' } }))
vi.mock('@/components/dashboard/ScoreChart.vue', () => ({ default: { template: '<div />' } }))

const item: HistoryItem = {
  session_id: 'sess-1',
  difficulty: 'hard',
  completed_at: '2026-10-30T08:00:00Z',
  patient_name: '王先生',
  patient_diagnosis: '術後疼痛',
  overall_score: 72,
  level_label: '良好',
}

const detail: HistoryDetail = {
  session_id: 'sess-1',
  difficulty: 'hard',
  completed_at: '2026-10-30T08:00:00Z',
  patient_name: '王先生',
  patient_diagnosis: '術後疼痛',
  score: {
    session_id: 'sess-1',
    overall_score: 72,
    level_label: '良好',
    dimension_scores: {
      empathy: 80,
      guided_questioning: 55,
      family_calming: 70,
      info_gathering: 75,
      response_fluency: 85,
    },
    strengths: ['開場有同理'],
    improvements: ['多用開放式問題'],
    key_moments: [],
    sbar_analysis: {
      situation: { rating: 'complete', feedback: '' },
      background: { rating: 'complete', feedback: '' },
      assessment: { rating: 'partial', feedback: '' },
      recommendation: { rating: 'missing', feedback: '缺少後續處置建議' },
    },
  },
}

beforeEach(() => {
  setActivePinia(createPinia())
  routerMock.push.mockReset()
  apiMocks.fetchHistory.mockReset()
  apiMocks.fetchHistoryDetail.mockReset()
})

describe('HistoryView', () => {
  it('lists past sessions and opens a report', async () => {
    apiMocks.fetchHistory.mockResolvedValue([item])

    const wrapper = mount(HistoryView, { global: { stubs: { NavBar: true } } })
    await flushPromises()

    const row = wrapper.find('tbody tr')
    expect(row.text()).toContain('王先生')
    expect(row.text()).toContain('72')
    expect(row.text()).toContain('進階')

    await row.find('button').trigger('click')
    expect(routerMock.push).toHaveBeenCalledWith('/history/sess-1')
  })

  it('shows an empty state for a new player', async () => {
    apiMocks.fetchHistory.mockResolvedValue([])

    const wrapper = mount(HistoryView, { global: { stubs: { NavBar: true } } })
    await flushPromises()

    expect(wrapper.text()).toContain('還沒有遊玩紀錄')
  })

  it('shows an error when loading fails', async () => {
    apiMocks.fetchHistory.mockRejectedValue(new Error('boom'))

    const wrapper = mount(HistoryView, { global: { stubs: { NavBar: true } } })
    await flushPromises()

    expect(wrapper.text()).toContain('無法載入遊玩紀錄')
  })
})

describe('HistoryDetailView', () => {
  it('renders the stored scorecard for the route session', async () => {
    apiMocks.fetchHistoryDetail.mockResolvedValue(detail)

    const wrapper = mount(HistoryDetailView, { global: { stubs: { NavBar: true } } })
    await flushPromises()

    expect(apiMocks.fetchHistoryDetail).toHaveBeenCalledWith('sess-1')
    expect(wrapper.text()).toContain('72')
    expect(wrapper.text()).toContain('多用開放式問題')
    expect(wrapper.text()).toContain('缺少後續處置建議')
  })

  it('offers a way back when the report is missing', async () => {
    apiMocks.fetchHistoryDetail.mockRejectedValue(new Error('Report not found'))

    const wrapper = mount(HistoryDetailView, { global: { stubs: { NavBar: true } } })
    await flushPromises()

    expect(wrapper.text()).toContain('無法載入報告')
  })
})

describe('NavBar user menu', () => {
  it('opens a dropdown with history and logout', async () => {
    const auth = useAuthStore()
    auth.token = 'tok'
    auth.user = { id: 'u1', email: 'a@b.c', name: '小護士', picture_url: null, credits: 30 }

    const wrapper = mount(NavBar, { global: { stubs: { RouterLink: true } } })
    expect(wrapper.find('.dropdown').exists()).toBe(false)

    await wrapper.find('.user-menu-btn').trigger('click')
    const items = wrapper.findAll('.dropdown-item')
    expect(items.map((i) => i.text())).toEqual(['歷史遊玩報告', '登出'])

    await items[0]!.trigger('click')
    expect(routerMock.push).toHaveBeenCalledWith('/history')
    expect(wrapper.find('.dropdown').exists()).toBe(false)
  })
})
