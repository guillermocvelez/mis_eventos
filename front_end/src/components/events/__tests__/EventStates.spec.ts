import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import EventsEmptyState from '../EventsEmptyState.vue'
import EventsErrorState from '../EventsErrorState.vue'
import EventsLoadingState from '../EventsLoadingState.vue'

describe('event state components', () => {
  it('emits clear-search from the empty state', async () => {
    const wrapper = mount(EventsEmptyState)

    await wrapper.get('button').trigger('click')

    expect(wrapper.text()).toContain('No encontramos eventos')
    expect(wrapper.emitted('clear-search')).toHaveLength(1)
  })

  it('renders errors and emits retry', async () => {
    const wrapper = mount(EventsErrorState, {
      props: {
        message: 'API caída',
      },
    })

    await wrapper.get('button').trigger('click')

    expect(wrapper.text()).toContain('API caída')
    expect(wrapper.emitted('retry')).toHaveLength(1)
  })

  it('renders loading copy', () => {
    const wrapper = mount(EventsLoadingState)

    expect(wrapper.text()).toContain('Cargando eventos')
  })
})

