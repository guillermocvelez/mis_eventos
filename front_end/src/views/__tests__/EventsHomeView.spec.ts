import { mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import { activatePinia, authenticate, makeEvent } from '@/__tests__/helpers'
import EventsHomeView from '@/views/events/EventsHomeView.vue'
import { useEventsStore } from '@/stores/events'
import type { UserRole } from '@/stores/auth'

const routerPush = vi.hoisted(() => vi.fn())

vi.mock('vue-router', () => ({
  useRouter: () => ({
    push: routerPush,
  }),
}))

const event = makeEvent({
  end_date: '2026-02-10T20:00:00Z',
  registered_count: 7,
})

type MountHomeOptions = {
  error?: string
  isLoading?: boolean
  items?: typeof event[]
  role?: UserRole
}

function mountHome(options: MountHomeOptions = {}) {
  const { error = '', isLoading = false, items = [event], role = 'attendee' } = options
  const pinia = activatePinia()

  const authStore = authenticate(role)
  const eventsStore = useEventsStore()

  eventsStore.items = items
  eventsStore.total = items.length
  eventsStore.error = error
  eventsStore.isLoading = isLoading

  vi.spyOn(eventsStore, 'fetchEvents').mockResolvedValue(undefined)
  vi.spyOn(eventsStore, 'clearSearch').mockResolvedValue(undefined)

  const wrapper = mount(EventsHomeView, {
    global: {
      plugins: [pinia],
      stubs: {
        EventsEmptyState: { template: '<button data-test="clear" @click="$emit(\'clear-search\')">clear</button>' },
        EventsErrorState: { props: ['message'], template: '<button data-test="retry" @click="$emit(\'retry\')">{{ message }}</button>' },
        EventsGrid: { props: ['events'], template: '<button data-test="detail" @click="$emit(\'view-detail\', events[0].id)">{{ events[0].title }}</button>' },
        EventsLoadingState: { template: '<p>Cargando...</p>' },
        EventsToolbar: { props: ['modelValue'], template: '<input data-test="search" :value="modelValue" @input="$emit(\'update:modelValue\', $event.target.value)" />' },
      },
    },
  })

  return { authStore, eventsStore, wrapper }
}

describe('EventsHomeView', () => {
  beforeEach(() => {
    routerPush.mockReset()
    vi.useRealTimers()
  })

  it('loads only published events for attendees', () => {
    const { eventsStore } = mountHome({ role: 'attendee' })

    expect(eventsStore.fetchEvents).toHaveBeenCalledWith({
      limit: 6,
      page: 1,
      status: 'published',
    })
  })

  it('lets organizers create events and see all statuses', async () => {
    const { eventsStore, wrapper } = mountHome({ role: 'organizer' })

    expect(eventsStore.fetchEvents).toHaveBeenCalledWith({
      limit: 6,
      page: 1,
      status: undefined,
    })

    await wrapper.get('button.btn').trigger('click')

    expect(routerPush).toHaveBeenCalledWith('/eventos/crear')
  })

  it('navigates to event detail from the grid', async () => {
    const { wrapper } = mountHome()

    await wrapper.get('[data-test="detail"]').trigger('click')

    expect(routerPush).toHaveBeenCalledWith({
      name: 'event-detail',
      params: { eventId: 'event-1' },
    })
  })

  it('debounces search changes before fetching events', async () => {
    vi.useFakeTimers()

    const { eventsStore, wrapper } = mountHome()

    await wrapper.get('[data-test="search"]').setValue('vue')

    expect(eventsStore.fetchEvents).toHaveBeenCalledTimes(1)

    vi.advanceTimersByTime(350)
    await Promise.resolve()

    expect(eventsStore.fetchEvents).toHaveBeenLastCalledWith({
      limit: 6,
      page: 1,
      search: 'vue',
      status: 'published',
    })

    vi.useRealTimers()
  })

  it('renders loading, error and empty states', async () => {
    const loading = mountHome({ isLoading: true }).wrapper

    expect(loading.text()).toContain('Cargando...')

    const errorState = mountHome({ error: 'API caída' })

    expect(errorState.wrapper.text()).toContain('API caída')

    await errorState.wrapper.get('[data-test="retry"]').trigger('click')

    expect(errorState.eventsStore.fetchEvents).toHaveBeenLastCalledWith({
      limit: 6,
      page: 1,
    })

    const emptyState = mountHome({ items: [] })

    await emptyState.wrapper.get('[data-test="clear"]').trigger('click')

    expect(emptyState.eventsStore.clearSearch).toHaveBeenCalled()
  })

  it('redirects to login when auth is lost', async () => {
    const { authStore } = mountHome()

    authStore.logout()
    await Promise.resolve()

    expect(routerPush).toHaveBeenCalledWith('/login')
  })
})
