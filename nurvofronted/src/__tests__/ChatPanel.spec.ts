import { mount } from '@vue/test-utils'
import { nextTick } from 'vue'
import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import ChatPanel from '@/components/game/ChatPanel.vue'
import { useChatStore } from '@/stores/chatStore'
import { useScenarioStore } from '@/stores/scenarioStore'
import type { Scenario } from '@/types/game'
import { sendMessage } from '@/services/wsService'
import { decodeAndPlay } from '@/services/audioService'

vi.mock('vue-router', () => ({
  useRouter: () => ({ push: vi.fn() }),
}))

vi.mock('@/services/wsService', () => ({
  sendMessage: vi.fn(),
  sendActivity: vi.fn(),
}))

vi.mock('@/services/audioService', () => ({
  decodeAndPlay: vi.fn(),
  unlock: vi.fn(),
  onPlaybackStart: vi.fn(() => vi.fn()),
  onPlaybackEnd: vi.fn(() => vi.fn()),
}))

vi.mock('@/services/speechService', () => ({
  isSupported: () => false,
  start: vi.fn(),
  stop: vi.fn(),
}))

const scenario: Scenario = {
  id: 'scenario-1',
  patient_profile: {
    name: '林女士',
    age: 72,
    gender: '女',
    diagnosis: '術後疼痛',
    medications: [],
    medical_history: [],
    allergies: [],
  },
  pain_details: {
    location: '腹部',
    severity: 7,
    type: '刺痛',
    duration: '2 小時',
    onset: '翻身後',
    aggravating_factors: [],
    relieving_factors: [],
    associated_symptoms: [],
  },
  family_members: [
    {
      name: '林先生',
      gender: '男',
      relationship: '配偶',
      personality: '焦慮',
      emotional_state: '擔心',
      interjection_triggers: ['疼痛'],
    },
    {
      name: '林小姐',
      gender: '女',
      relationship: '女兒',
      personality: '急切',
      emotional_state: '緊張',
      interjection_triggers: ['等待過久'],
    },
    {
      name: '陳小姐',
      gender: '女',
      relationship: '媳婦',
      personality: '謹慎',
      emotional_state: '不安',
      interjection_triggers: ['資訊不清楚'],
    },
  ],
  communication_challenges: [],
  correct_answers: {
    expected_info_gathered: [],
    ideal_empathy_phrases: [],
    ideal_questioning_sequence: [],
    family_calming_strategies: [],
  },
  time_limit_seconds: 480,
  created_at: '2026-04-30T00:00:00.000Z',
}

describe('ChatPanel', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()

    const scenarioStore = useScenarioStore()
    scenarioStore.scenario = scenario

    const chatStore = useChatStore()
    chatStore.setConnected(true)
  })

  it('toggles a family chip via the tab button and sends to that target', async () => {
    const wrapper = mount(ChatPanel)
    const chatStore = useChatStore()

    const tabButtons = wrapper.findAll('button.tab-btn')
    await tabButtons[2]!.trigger('click') // family_1 = 林小姐

    expect(chatStore.selectedTargetIds).toEqual(['family_1'])
    expect(wrapper.find('.target-chip').text()).toContain('林小姐')

    await wrapper.find('textarea').setValue('請問現在可以說明一下嗎？')
    await wrapper.find('button.input-btn--send').trigger('click')

    expect(sendMessage).toHaveBeenCalledWith('family_1', '請問現在可以說明一下嗎？')
    const lastMessage = chatStore.messages[chatStore.messages.length - 1]
    expect(lastMessage).toMatchObject({
      sender: 'nurse',
      content: '請問現在可以說明一下嗎？',
    })
  })

  it('toggling the same tab button twice removes the chip', async () => {
    const wrapper = mount(ChatPanel)
    const chatStore = useChatStore()

    const tab = wrapper.findAll('button.tab-btn')[2]!
    await tab.trigger('click')
    expect(chatStore.selectedTargetIds).toEqual(['family_1'])
    await tab.trigger('click')
    expect(chatStore.selectedTargetIds).toEqual([])
    expect(wrapper.findAll('.target-chip')).toHaveLength(0)
  })

  it('selecting from the @ dropdown adds a chip and strips the @query from the text', async () => {
    const wrapper = mount(ChatPanel)
    const textarea = wrapper.find('textarea')

    await textarea.setValue('您好嗎 @林小')
    await textarea.trigger('input')

    const item = wrapper.findAll('.mention-item').find((i) => i.text().includes('林小姐'))
    expect(item).toBeTruthy()
    await item!.trigger('mousedown')

    expect(wrapper.find('.target-chip').text()).toContain('林小姐')
    expect((textarea.element as HTMLTextAreaElement).value).toBe('您好嗎 ')
  })

  it('removing a chip drops the target without touching the message text', async () => {
    const wrapper = mount(ChatPanel)
    const chatStore = useChatStore()

    await wrapper.findAll('button.tab-btn')[0]!.trigger('click') // patient
    await wrapper.find('textarea').setValue('一些文字')
    expect(chatStore.selectedTargetIds).toEqual(['patient'])

    await wrapper.find('.target-chip .chip-remove').trigger('click')

    expect(chatStore.selectedTargetIds).toEqual([])
    expect((wrapper.find('textarea').element as HTMLTextAreaElement).value).toBe('一些文字')
  })

  it('sends clean content (no @ token) once per selected target', async () => {
    const wrapper = mount(ChatPanel)

    await wrapper.findAll('button.tab-btn')[0]!.trigger('click') // patient
    await wrapper.findAll('button.tab-btn')[2]!.trigger('click') // family_1
    await wrapper.find('textarea').setValue('請問哪裡痛？')
    await wrapper.find('button.input-btn--send').trigger('click')

    expect(sendMessage).toHaveBeenCalledTimes(2)
    expect(sendMessage).toHaveBeenCalledWith('patient', '請問哪裡痛？')
    expect(sendMessage).toHaveBeenCalledWith('family_1', '請問哪裡痛？')
    for (const call of (sendMessage as ReturnType<typeof vi.fn>).mock.calls) {
      expect(call[1]).not.toContain('@')
    }
  })

  it('the 全部 broadcast chip sends to the patient and every family member', async () => {
    const wrapper = mount(ChatPanel)
    const textarea = wrapper.find('textarea')

    await textarea.setValue('@')
    await textarea.trigger('input')
    const allItem = wrapper.findAll('.mention-item').find((i) => i.text().includes('全部') || i.text().includes('@all'))
    await allItem!.trigger('mousedown')

    expect(wrapper.findAll('.target-chip')).toHaveLength(1)

    await textarea.setValue('大家好')
    await wrapper.find('button.input-btn--send').trigger('click')

    expect(sendMessage).toHaveBeenCalledTimes(4)
    expect(sendMessage).toHaveBeenCalledWith('patient', '大家好')
    expect(sendMessage).toHaveBeenCalledWith('family_0', '大家好')
    expect(sendMessage).toHaveBeenCalledWith('family_1', '大家好')
    expect(sendMessage).toHaveBeenCalledWith('family_2', '大家好')
  })

  it('defaults to the patient when no chip is selected', async () => {
    const wrapper = mount(ChatPanel)

    await wrapper.find('textarea').setValue('您好')
    await wrapper.find('button.input-btn--send').trigger('click')

    expect(sendMessage).toHaveBeenCalledTimes(1)
    expect(sendMessage).toHaveBeenCalledWith('patient', '您好')
  })

  it('auto-plays audio when TTS arrives after the NPC text', async () => {
    mount(ChatPanel)
    const chatStore = useChatStore()

    chatStore.addMessage({
      id: 'npc-1',
      sender: 'patient',
      content: '我這裡很痛',
      timestamp: new Date().toISOString(),
      elapsed_seconds: 3,
      is_interjection: false,
    })
    await nextTick()

    expect(decodeAndPlay).not.toHaveBeenCalled()

    chatStore.messages[0]!.audio_base64 = 'audio'
    await nextTick()

    expect(decodeAndPlay).toHaveBeenCalledWith('audio')
  })

  it('uses family gender for tab and message avatars', async () => {
    const wrapper = mount(ChatPanel)
    const chatStore = useChatStore()
    const maleAvatar = String.fromCodePoint(0x1f468)
    const femaleAvatar = String.fromCodePoint(0x1f469)

    const tabButtons = wrapper.findAll('button.tab-btn')
    expect(tabButtons[1]!.text()).toContain(maleAvatar)
    expect(tabButtons[2]!.text()).toContain(femaleAvatar)

    chatStore.addMessage({
      id: 'family-0-message',
      sender: 'family_0',
      content: '我是林先生',
      timestamp: new Date().toISOString(),
      elapsed_seconds: 5,
      is_interjection: false,
    })
    chatStore.addMessage({
      id: 'family-1-message',
      sender: 'family_1',
      content: '我是林小姐',
      timestamp: new Date().toISOString(),
      elapsed_seconds: 6,
      is_interjection: false,
    })
    await nextTick()

    const messageAvatars = wrapper.findAll('.bubble-row .bubble-avatar').map((avatar) => avatar.text())
    expect(messageAvatars).toContain(maleAvatar)
    expect(messageAvatars).toContain(femaleAvatar)
  })
})
