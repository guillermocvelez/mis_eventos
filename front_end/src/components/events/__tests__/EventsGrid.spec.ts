import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import EventsGrid from '../EventsGrid.vue'
import type { EventCardItem } from '../eventCardTypes'
import type { EventStatus } from '@/stores/events'

const events: EventCardItem[] = [
  {
    id: 'event-1',
    title: 'Vue Conf',
    date: 'Inicio 10 feb 2026',
    endDate: '',
    timeRange: 'Inicia 9:00',
    attendees: 3,
    capacity: 10,
    capacityPercent: 30,
    capacityTone: 'green',
    coverClass: 'cv-published',
    icon: 'VU',
    location: 'Bogota',
    status: 'published',
  },
]

const statusLabels: Record<EventStatus, string> = {
  cancelled: 'Cancelado',
  draft: 'Borrador',
  finished: 'Finalizado',
  published: 'Publicado',
}

const statusVariants = {
  cancelled: 'danger',
  draft: 'neutral',
  finished: 'info',
  published: 'success',
} as const

describe('EventsGrid', () => {
  it('renders cards and forwards detail events', async () => {
    const wrapper = mount(EventsGrid, {
      props: {
        events,
        statusLabels,
        statusVariants,
      },
    })

    expect(wrapper.text()).toContain('Vue Conf')

    await wrapper.get('button').trigger('click')

    expect(wrapper.emitted('view-detail')).toEqual([['event-1']])
  })
})

