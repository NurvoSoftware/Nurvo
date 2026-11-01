import { mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import CookbookView from '@/views/CookbookView.vue'

const routerMock = vi.hoisted(() => ({
  push: vi.fn(),
}))

vi.mock('vue-router', () => ({
  useRouter: () => routerMock,
}))

// NavBar's `/Nurvo_logo.png` import can't be resolved by vitest on Windows.
vi.mock('@/components/shared/NavBar.vue', () => ({ default: { template: '<nav />' } }))

const mountView = () => mount(CookbookView, { global: { stubs: { NavBar: true } } })

describe('CookbookView', () => {
  beforeEach(() => {
    routerMock.push.mockReset()
  })

  it('advances only when the highlighted spot in the mini screen is clicked', async () => {
    const wrapper = mountView()
    const total = wrapper.findAll('.step-dot').length
    expect(total).toBeGreaterThanOrEqual(5)
    expect(wrapper.find('.step-title').text()).toContain('選擇難度')
    expect(wrapper.find('.mock-screen').exists()).toBe(true)

    // Clicking somewhere that isn't the target does nothing.
    await wrapper.find('.mock-screen').trigger('click')
    expect(wrapper.find('.step-counter').text()).toMatch(/^1 \//)

    for (let i = 1; i < total; i++) {
      await wrapper.find('.mock-target').trigger('click')
    }

    expect(wrapper.find('.step-counter').text()).toContain(`${total} / ${total}`)
    expect(wrapper.find('.step-title').text()).toContain('成果報告')
  })

  it('shows a capture of the real page on the left and the explanation on the right', async () => {
    const wrapper = mountView()
    const layout = wrapper.find('.step-layout').element.children

    expect(layout[0]!.classList.contains('mock-wrap')).toBe(true)
    expect(layout[1]!.classList.contains('step-text')).toBe(true)

    const first = wrapper.find('.mock-screen img').attributes('src')
    await wrapper.find('.mock-target').trigger('click')
    expect(wrapper.find('.mock-screen img').attributes('src')).not.toBe(first)
  })

  it('every step has exactly one clickable target', async () => {
    const wrapper = mountView()
    const total = wrapper.findAll('.step-dot').length

    for (let i = 0; i < total; i++) {
      await wrapper.findAll('.step-dot button')[i]!.trigger('click')
      expect(wrapper.findAll('.mock-target')).toHaveLength(1)
    }
  })

  it('clicking the target on the last step starts real practice', async () => {
    const wrapper = mountView()
    const total = wrapper.findAll('.step-dot').length
    await wrapper.findAll('.step-dot button')[total - 1]!.trigger('click')

    await wrapper.find('.mock-target').trigger('click')

    expect(routerMock.push).toHaveBeenCalledWith({ name: 'level-select' })
  })

  it('goes back a step', async () => {
    const wrapper = mountView()
    await wrapper.find('.mock-target').trigger('click')
    await wrapper.find('.btn-prev').trigger('click')

    expect(wrapper.find('.step-counter').text()).toMatch(/^1 \//)
  })

  it('can be left at any time', async () => {
    const wrapper = mountView()
    await wrapper.find('.btn-skip').trigger('click')

    expect(routerMock.push).toHaveBeenCalledWith({ name: 'level-select' })
  })
})
