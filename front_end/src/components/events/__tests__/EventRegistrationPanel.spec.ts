import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import EventRegistrationPanel from '../EventRegistrationPanel.vue'
import type { EventDTO } from '@/stores/events'

const baseEvent: EventDTO = {
  id: 'event-1',
  name: 'Vue Conf',
  description: null,
  date: '2026-02-10T14:00:00Z',
  end_date: null,
  location: 'Bogota',
  capacity: 10,
  registered_count: 4,
  status: 'published',
  created_by: 'admin-1',
  created_at: '2026-01-01T00:00:00Z',
}

function mountPanel(props: Partial<InstanceType<typeof EventRegistrationPanel>['$props']> = {}) {
  return mount(EventRegistrationPanel, {
    props: {
      event: baseEvent,
      ...props,
    },
  })
}

describe('EventRegistrationPanel', () => {
  it('shows available seats and emits register for published events', async () => {
    const wrapper = mountPanel()

    expect(wrapper.text()).toContain('6 plazas')
    expect(wrapper.find('.donut').attributes('style')).toContain('--progress: 40%')

    await wrapper.get('button').trigger('click')

    expect(wrapper.emitted('register')).toHaveLength(1)
  })

  it('disables registration when the event is full', () => {
    const wrapper = mountPanel({
      event: {
        ...baseEvent,
        capacity: 2,
        registered_count: 5,
      },
    })

    const button = wrapper.get('button')

    expect(wrapper.text()).toContain('0 plazas')
    expect(button.text()).toBe('Evento lleno')
    expect(button.attributes('disabled')).toBeDefined()
  })

  it('shows registered status and emits cancellation', async () => {
    const wrapper = mountPanel({ isRegistered: true })

    expect(wrapper.text()).toContain('Ya estás registrado en este evento.')
    expect(wrapper.text()).not.toContain('Registrarme')

    await wrapper.get('button').trigger('click')

    expect(wrapper.emitted('cancel-registration')).toHaveLength(1)
  })

  it('prioritizes error messages over success messages', () => {
    const wrapper = mountPanel({
      error: 'No pudimos registrarte.',
      success: 'Registro exitoso.',
    })

    expect(wrapper.get('[role="alert"]').text()).toBe('No pudimos registrarte.')
    expect(wrapper.text()).not.toContain('Registro exitoso.')
  })
})

