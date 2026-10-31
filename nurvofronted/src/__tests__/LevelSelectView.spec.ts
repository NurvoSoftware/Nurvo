import { flushPromises, mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import LevelSelectView from '@/views/LevelSelectView.vue'
import { useAuthStore } from '@/stores/authStore'
import type { LatestRecord, Scenario, User } from '@/types/game'

const routerMock = vi.hoisted(() => ({
  push: vi.fn(),
}))

const apiMocks = vi.hoisted(() => ({
  generateScenario: vi.fn(),
  fetchBackgroundImage: vi.fn(),
  fetchLatestRecord: vi.fn(),
}))

vi.mock('vue-router', () => ({
  useRouter: () => routerMock,
}))

vi.mock('@/services/apiService', () => apiMocks)

// NavBar's `/Nurvo_logo.png` import can't be resolved by vitest on Windows; a
// stub alone doesn't help because the module is still imported.
vi.mock('@/components/shared/NavBar.vue', () => ({ default: { template: '<nav />' } }))

const scenario: Scenario = {
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
}

describe('LevelSelectView', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.useFakeTimers()
    routerMock.push.mockReset()
    apiMocks.generateScenario.mockReset()
    apiMocks.fetchBackgroundImage.mockReset()
    apiMocks.fetchBackgroundImage.mockResolvedValue({ pending: true, url: null })
    apiMocks.fetchLatestRecord.mockReset()
    apiMocks.fetchLatestRecord.mockResolvedValue(null)
    localStorage.clear()
    // Most tests are about other things — treat the cookbook as already seen.
    localStorage.setItem('nurvo_cookbook_seen', '1')
  })

  const mountView = () =>
    mount(LevelSelectView, { global: { stubs: { NavBar: true, Teleport: true } } })

  const latest: LatestRecord = {
    session_id: 'prev-1',
    difficulty: 'medium',
    completed_at: '2026-10-30T08:00:00Z',
    overall_score: 72,
    level_label: '良好',
    dimension_scores: {
      empathy: 80,
      guided_questioning: 55,
      family_calming: 70,
      info_gathering: 75,
      response_fluency: 85,
    },
    improvements: ['多用開放式問題', '先回應家屬情緒', '確認疼痛持續時間', '第四項不顯示'],
    sbar_analysis: {
      situation: { rating: 'complete', feedback: 'ok' },
      background: { rating: 'partial', feedback: '缺病史' },
      assessment: { rating: 'missing', feedback: '沒寫評估' },
      recommendation: { rating: 'complete', feedback: 'ok' },
    },
  }

  it('shows last session review with weakest dimension, top improvements and SBAR gaps', async () => {
    apiMocks.fetchLatestRecord.mockResolvedValue(latest)

    const wrapper = mountView()
    await flushPromises()

    const card = wrapper.find('.last-record')
    expect(card.exists()).toBe(true)
    expect(card.text()).toContain('72')
    expect(card.text()).toContain('引導式提問')
    expect(card.findAll('.last-record-improvements li')).toHaveLength(3)
    expect(card.text()).not.toContain('第四項不顯示')
    const gaps = card.find('.last-record-sbar').text()
    expect(gaps).toContain('背景')
    expect(gaps).toContain('評估')
    expect(gaps).not.toContain('情境')
  })

  it('hides the review card for a first-time player', async () => {
    const wrapper = mountView()
    await flushPromises()

    expect(apiMocks.fetchLatestRecord).toHaveBeenCalled()
    expect(wrapper.find('.last-record').exists()).toBe(false)
  })

  it('still works when the latest record request fails', async () => {
    apiMocks.fetchLatestRecord.mockRejectedValue(new Error('boom'))

    const wrapper = mountView()
    await flushPromises()

    expect(wrapper.find('.last-record').exists()).toBe(false)
    expect(wrapper.find('.error-alert').exists()).toBe(false)
  })

  it('prompts a first-time visitor to open the cookbook', async () => {
    localStorage.removeItem('nurvo_cookbook_seen')

    const wrapper = mountView()
    await flushPromises()

    expect(wrapper.find('.cookbook-prompt').exists()).toBe(true)
    await wrapper.find('.cookbook-prompt .modal-btn--confirm').trigger('click')
    expect(routerMock.push).toHaveBeenCalledWith({ name: 'cookbook' })
    expect(localStorage.getItem('nurvo_cookbook_seen')).toBe('1')
  })

  it('lets the visitor skip the cookbook and does not ask again', async () => {
    localStorage.removeItem('nurvo_cookbook_seen')

    const wrapper = mountView()
    await flushPromises()
    await wrapper.find('.cookbook-prompt .modal-btn--cancel').trigger('click')

    expect(wrapper.find('.cookbook-prompt').exists()).toBe(false)
    expect(localStorage.getItem('nurvo_cookbook_seen')).toBe('1')
    expect(mountView().find('.cookbook-prompt').exists()).toBe(false)
  })

  it('reports a navigation failure after a scenario has been generated', async () => {
    apiMocks.generateScenario.mockResolvedValue({
      session_id: 'session-1',
      scenario,
    })
    routerMock.push.mockRejectedValue(new Error('navigation failed'))
    useAuthStore().user = { credits: 100 } as User

    const wrapper = mountView()

    await wrapper.find('button.primary-btn').trigger('click')
    await wrapper.find('.modal-btn--confirm').trigger('click')
    await flushPromises()

    expect(routerMock.push).toHaveBeenCalledWith({ name: 'briefing' })
    expect(wrapper.find('.error-alert').text()).toContain('教案已生成，但無法進入任務簡報')
  })
})
