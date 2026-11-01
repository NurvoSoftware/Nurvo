import { mount, RouterLinkStub } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import LastRecordCard from '@/components/dashboard/LastRecordCard.vue'
import type { LatestRecord } from '@/types/game'

const record: LatestRecord = {
  session_id: 'sess-9',
  difficulty: 'medium',
  completed_at: '2026-10-31T06:03:00Z',
  overall_score: 56,
  level_label: '尚可',
  dimension_scores: {
    empathy: 40,
    guided_questioning: 70,
    family_calming: 30,
    info_gathering: 60,
    response_fluency: 70,
  },
  improvements: ['多安撫家屬'],
  sbar_analysis: null,
}

describe('LastRecordCard', () => {
  it('links the whole card to that session’s full report', () => {
    const wrapper = mount(LastRecordCard, {
      props: { record },
      global: { stubs: { RouterLink: RouterLinkStub } },
    })

    const link = wrapper.findComponent(RouterLinkStub)
    expect(link.props('to')).toEqual({ name: 'history-detail', params: { sessionId: 'sess-9' } })
    expect(link.text()).toContain('家屬安撫')
    expect(link.text()).toContain('查看完整報告')
  })
})
