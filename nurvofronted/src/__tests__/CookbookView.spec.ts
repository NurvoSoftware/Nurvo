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

  it('walks through every step in order and ends on the start-practice action', async () => {
    const wrapper = mountView()
    const total = wrapper.findAll('.step-dot').length
    expect(total).toBeGreaterThanOrEqual(5)
    expect(wrapper.find('.step-title').text()).toContain('選擇難度')
    expect(wrapper.find('.btn-prev').attributes('disabled')).toBeDefined()

    for (let i = 1; i < total; i++) {
      await wrapper.find('.btn-next').trigger('click')
    }

    expect(wrapper.find('.step-counter').text()).toContain(`${total} / ${total}`)
    expect(wrapper.find('.step-title').text()).toContain('成果報告')
    await wrapper.find('.btn-start').trigger('click')
    expect(routerMock.push).toHaveBeenCalledWith({ name: 'level-select' })
  })

  it('goes back a step', async () => {
    const wrapper = mountView()
    await wrapper.find('.btn-next').trigger('click')
    await wrapper.find('.btn-prev').trigger('click')

    expect(wrapper.find('.step-counter').text()).toMatch(/^1 \//)
  })

  it('can be left at any time', async () => {
    const wrapper = mountView()
    await wrapper.find('.btn-skip').trigger('click')

    expect(routerMock.push).toHaveBeenCalledWith({ name: 'level-select' })
  })
})
