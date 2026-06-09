import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import UiPagination from '../UiPagination.vue'

describe('UiPagination', () => {
  it('renders a sliding page window and emits valid page changes', async () => {
    const wrapper = mount(UiPagination, {
      props: {
        currentPage: 6,
        itemsShown: 10,
        totalItems: 100,
        totalPages: 10,
      },
    })

    expect(wrapper.text()).toContain('Mostrando 10 de 100 usuarios')
    expect(wrapper.findAll('button').map((button) => button.text())).toEqual([
      '‹',
      '4',
      '5',
      '6',
      '7',
      '8',
      '›',
    ])

    const buttons = wrapper.findAll('button')

    await buttons[4]!.trigger('click')
    await buttons[3]!.trigger('click')

    expect(wrapper.emitted('page-change')).toEqual([[7]])
  })

  it('disables boundary navigation buttons', () => {
    const firstPage = mount(UiPagination, {
      props: {
        currentPage: 1,
        itemsShown: 5,
        totalItems: 12,
        totalPages: 3,
      },
    })
    const lastPage = mount(UiPagination, {
      props: {
        currentPage: 3,
        itemsShown: 2,
        totalItems: 12,
        totalPages: 3,
      },
    })

    const firstPageButtons = firstPage.findAll('button')
    const lastPageButtons = lastPage.findAll('button')

    expect(firstPageButtons[0]!.attributes('disabled')).toBeDefined()
    expect(lastPageButtons[lastPageButtons.length - 1]!.attributes('disabled')).toBeDefined()
  })
})
