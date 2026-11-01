import { flushPromises, mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import BackButton from '@/components/shared/BackButton.vue'
import HistoryView from '@/views/HistoryView.vue'
import CookbookView from '@/views/CookbookView.vue'
import BriefingView from '@/views/BriefingView.vue'
import RecordView from '@/views/RecordView.vue'
import LevelSelectView from '@/views/LevelSelectView.vue'
import LoginView from '@/views/LoginView.vue'
import HistoryDetailView from '@/views/HistoryDetailView.vue'
import { useChatStore } from '@/stores/chatStore'
import { useGameStore } from '@/stores/gameStore'
import { useScenarioStore } from '@/stores/scenarioStore'
import type { Scenario } from '@/types/game'

const routerMock = vi.hoisted(() => ({ push: vi.fn(), replace: vi.fn() }))

vi.mock('vue-router', () => ({
  useRouter: () => routerMock,
  useRoute: () => ({ params: {}, query: {} }),
}))

vi.mock('@/services/apiService', () => ({
  fetchHistory: vi.fn().mockResolvedValue([]),
  fetchHistoryDetail: vi.fn().mockRejectedValue(new Error('Report not found')),
  fetchLatestRecord: vi.fn().mockResolvedValue(null),
  generateScenario: vi.fn(),
  fetchBackgroundImage: vi.fn(),
  submitRecord: vi.fn(),
}))

// NavBar's public-dir logo compiles to an import that vitest can't resolve on Windows.
vi.mock('@/components/shared/NavBar.vue', () => ({ default: { template: '<nav />' } }))
vi.mock('/Nurvo_logo.png', () => ({ default: '/Nurvo_logo.png' }))

const scenario = {
  id: 'scenario-1',
  patient_profile: {
    name: '李大華',
    age: 70,
    gender: '男',
    diagnosis: '腰椎間盤突出',
    medications: [],
    medical_history: [],
    allergies: [],
  },
  pain_details: {
    location: '腰部',
    severity: 7,
    type: '刺痛',
    duration: '一天',
    onset: '搬重物後',
    aggravating_factors: [],
    relieving_factors: [],
    associated_symptoms: [],
  },
  family_members: [],
  communication_challenges: [],
  correct_answers: {
    expected_info_gathered: [],
    ideal_empathy_phrases: [],
    ideal_questioning_sequence: [],
    family_calming_strategies: [],
  },
  time_limit_seconds: 480,
  created_at: '2026-05-01T00:00:00Z',
} as Scenario

const confirmSpy = vi.spyOn(window, 'confirm')

beforeEach(() => {
  setActivePinia(createPinia())
  routerMock.push.mockReset()
  routerMock.replace.mockReset()
  confirmSpy.mockReset()
})

afterEach(() => {
  confirmSpy.mockReset()
})

describe('BackButton', () => {
  it('navigates straight to its target when no confirmation is needed', async () => {
    const wrapper = mount(BackButton, { props: { to: '/', label: '返回首頁' } })

    // Arrow and label are separate so only the label is underlined.
    expect(wrapper.find('.back-button__arrow').text()).toBe('←')
    expect(wrapper.find('.back-button__label').text()).toBe('返回首頁')
    await wrapper.trigger('click')

    expect(confirmSpy).not.toHaveBeenCalled()
    expect(routerMock.push).toHaveBeenCalledWith('/')
  })

  it('can point forward, with the arrow after the label', () => {
    const wrapper = mount(BackButton, { props: { to: '/', label: '進入訓練', arrow: 'forward' } })

    const spans = wrapper.findAll('span').map((s) => s.text())
    expect(spans).toEqual(['進入訓練', '→'])
  })

  it('stays put (and emits nothing) when the confirmation is declined', async () => {
    confirmSpy.mockReturnValue(false)
    const wrapper = mount(BackButton, { props: { to: '/', label: '離開', confirmMessage: '確定？' } })

    await wrapper.trigger('click')

    expect(confirmSpy).toHaveBeenCalledWith('確定？')
    expect(wrapper.emitted('leave')).toBeUndefined()
    expect(routerMock.push).not.toHaveBeenCalled()
  })

  it('emits leave before navigating once confirmed', async () => {
    confirmSpy.mockReturnValue(true)
    const order: string[] = []
    routerMock.push.mockImplementation(() => order.push('push'))
    const wrapper = mount(BackButton, {
      props: { to: '/', label: '離開', confirmMessage: '確定？', onLeave: () => order.push('leave') },
    })

    await wrapper.trigger('click')

    expect(order).toEqual(['leave', 'push'])
  })
})

describe('every page has a way back', () => {
  it('level select goes home', async () => {
    const wrapper = mount(LevelSelectView, { global: { stubs: { Teleport: true } } })
    await flushPromises()

    await wrapper.findComponent(BackButton).trigger('click')
    expect(routerMock.push).toHaveBeenCalledWith('/')
  })

  it('login goes home', async () => {
    const wrapper = mount(LoginView)

    await wrapper.findComponent(BackButton).trigger('click')
    expect(routerMock.push).toHaveBeenCalledWith('/')
  })

  it('history report goes back to the list, even when it failed to load', async () => {
    const wrapper = mount(HistoryDetailView)
    await flushPromises()

    await wrapper.findComponent(BackButton).trigger('click')
    expect(routerMock.push).toHaveBeenCalledWith('/history')
  })

  it('history list goes home', async () => {
    const wrapper = mount(HistoryView)
    await flushPromises()

    await wrapper.findComponent(BackButton).trigger('click')
    expect(routerMock.push).toHaveBeenCalledWith('/')
  })

  it('cookbook goes back to level select', async () => {
    const wrapper = mount(CookbookView)

    await wrapper.findComponent(BackButton).trigger('click')
    expect(routerMock.push).toHaveBeenCalledWith({ name: 'level-select' })
  })

  it('briefing confirms, drops the generated scenario, and goes back to level select', async () => {
    confirmSpy.mockReturnValue(true)
    const scenarioStore = useScenarioStore()
    scenarioStore.scenario = scenario
    const gameStore = useGameStore()
    gameStore.sessionId = 'sess-1'

    const wrapper = mount(BriefingView, { global: { stubs: { PatientCard: true } } })
    await wrapper.findComponent(BackButton).trigger('click')

    expect(confirmSpy).toHaveBeenCalled()
    expect(scenarioStore.scenario).toBeNull()
    expect(gameStore.sessionId).toBe('')
    expect(routerMock.push).toHaveBeenCalledWith({ name: 'level-select' })
  })

  it('record confirms, abandons the game, and goes home', async () => {
    confirmSpy.mockReturnValue(true)
    const gameStore = useGameStore()
    gameStore.sessionId = 'sess-1'
    useScenarioStore().scenario = scenario
    const chatStore = useChatStore()
    const resetChat = vi.spyOn(chatStore, 'reset')

    const wrapper = mount(RecordView)
    await wrapper.findComponent(BackButton).trigger('click')

    expect(gameStore.sessionId).toBe('')
    expect(resetChat).toHaveBeenCalled()
    expect(routerMock.push).toHaveBeenCalledWith('/')
  })
})
