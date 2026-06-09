import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import EventSessionsSection from '../EventSessionsSection.vue'
import type { SessionDTO } from '@/stores/events'

const sessions: SessionDTO[] = [
  {
    id: 'session-1',
    event_id: 'event-1',
    title: 'Arquitectura limpia',
    speaker: {
      id: 'speaker-1',
      name: 'Ada Lovelace',
      bio: null,
      email: 'ada@example.com',
    },
    start_time: '2026-02-10T14:00:00Z',
    end_time: '2026-02-10T15:00:00Z',
    capacity: 2,
    registered_count: 1,
  },
  {
    id: 'session-2',
    event_id: 'event-1',
    title: 'Testing frontend',
    speaker: null,
    start_time: '2026-02-10T16:00:00Z',
    end_time: '2026-02-10T17:00:00Z',
    capacity: 1,
    registered_count: 1,
  },
]

function mountSection(props: Partial<InstanceType<typeof EventSessionsSection>['$props']> = {}) {
  return mount(EventSessionsSection, {
    props: {
      canManageEvents: false,
      sessions,
      ...props,
    },
  })
}

describe('EventSessionsSection', () => {
  it('renders sessions with speakers and capacity labels', () => {
    const wrapper = mountSection()

    expect(wrapper.text()).toContain('Sesiones · 2')
    expect(wrapper.text()).toContain('Arquitectura limpia')
    expect(wrapper.text()).toContain('Ada Lovelace')
    expect(wrapper.text()).toContain('Sin ponente asignado')
    expect(wrapper.text()).toContain('1 / 2 plazas')
  })

  it('emits management actions when the user can manage events', async () => {
    const wrapper = mountSection({ canManageEvents: true })

    await wrapper.get('.detail-section-head button').trigger('click')
    const actionButtons = wrapper.findAll('.detail-actions button')

    await actionButtons[0]!.trigger('click')
    await actionButtons[1]!.trigger('click')

    expect(wrapper.emitted('add-session')).toHaveLength(1)
    expect(wrapper.emitted('edit-session')?.[0]).toEqual([sessions[0]])
    expect(wrapper.emitted('delete-session')?.[0]).toEqual([sessions[0]])
  })

  it('shows registration controls only for non-registered sessions', async () => {
    const wrapper = mountSection({
      canRegisterToSessions: true,
      registeredSessionIds: ['session-1'],
    })

    expect(wrapper.text()).toContain('Inscrito')

    const registerButtons = wrapper.findAll('button').filter((button) => button.text() === 'Sesión llena')

    expect(registerButtons).toHaveLength(1)
    expect(registerButtons[0]!.attributes('disabled')).toBeDefined()
  })

  it('emits register-session for an available session', async () => {
    const wrapper = mountSection({ canRegisterToSessions: true })
    const registerButton = wrapper.findAll('button').find((button) => button.text() === 'Registrarme')

    expect(registerButton).toBeDefined()

    await registerButton?.trigger('click')

    expect(wrapper.emitted('register-session')?.[0]).toEqual([sessions[0]])
  })

  it('renders the empty state when there are no sessions', () => {
    const wrapper = mountSection({ sessions: [] })

    expect(wrapper.text()).toContain('Este evento aún no tiene sesiones publicadas.')
  })
})
