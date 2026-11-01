import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import SbarCard from '@/components/dashboard/SbarCard.vue'
import type { SbarAnalysis } from '@/types/game'

const analysis: SbarAnalysis = {
  situation: { rating: 'complete', feedback: '清楚說明疼痛 7 分' },
  background: { rating: 'partial', feedback: '缺少過去病史' },
  assessment: { rating: 'missing', feedback: '沒有寫出評估' },
  recommendation: { rating: 'partial', feedback: '建議要更具體' },
}

describe('SbarCard', () => {
  it('renders all four SBAR sections in order with rating and feedback', () => {
    const wrapper = mount(SbarCard, { props: { analysis } })

    const rows = wrapper.findAll('.sbar-row')
    expect(rows).toHaveLength(4)
    expect(rows.map((r) => r.find('.sbar-letter').text())).toEqual(['S', 'B', 'A', 'R'])
    expect(rows[0]!.text()).toContain('完整')
    expect(rows[1]!.text()).toContain('部分')
    expect(rows[2]!.text()).toContain('缺漏')
    expect(rows[2]!.text()).toContain('沒有寫出評估')
    expect(rows[2]!.classes()).toContain('missing')
  })
})
