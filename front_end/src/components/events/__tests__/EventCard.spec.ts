import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import EventCard from '../EventCard.vue'
import type { EventCardItem } from '../eventCardTypes'
import type { EventStatus } from '@/stores/events'

const event: EventCardItem = {
  id: 'event-1',
  title: 'Festival de producto',
  date: '10 feb 2026',
  endDate: '11 feb 2026',
  timeRange: '9:00 AM - 5:00 PM',
  attendees: 70,
  capacity: 100,
  capacityPercent: 70,
  capacityTone: 'yellow',
  coverClass: 'cover-indigo',
  icon: 'P',
  location: 'Medellin',
  status: 'published',
}

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

describe('EventCard', () => {
  it('renders event metadata and capacity progress', () => {
    const wrapper = mount(EventCard, {
      props: {
        event,
        statusLabels,
        statusVariants,
      },
    })

    expect(wrapper.text()).toContain('Festival de producto')
    expect(wrapper.text()).toContain('Publicado')
    expect(wrapper.text()).toContain('10 feb 2026')
    expect(wrapper.text()).toContain('11 feb 2026')
    expect(wrapper.text()).toContain('70 / 100')
    expect(wrapper.get('.cap-fill').attributes('style')).toContain('width: 70%')
  })

  it('emits view-detail with the event id', async () => {
    const wrapper = mount(EventCard, {
      props: {
        event,
        statusLabels,
        statusVariants,
      },
    })

    await wrapper.get('button').trigger('click')

    expect(wrapper.emitted('view-detail')).toEqual([['event-1']])
  })
})

