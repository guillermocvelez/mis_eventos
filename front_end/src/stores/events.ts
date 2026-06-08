import { computed, ref } from 'vue'
import { defineStore } from 'pinia'

import {
  createEvent as createEventRequest,
  fetchEventDetail as fetchEventDetailRequest,
  fetchEvents as fetchEventsRequest,
} from '@/services/eventsApi'
import type { EventCreatePayload, EventDTO, FetchEventsOptions, SessionDTO } from '@/types/events'

export type {
  EventCreatePayload,
  EventDTO,
  EventStatus,
  SessionDTO,
  SpeakerDTO,
} from '@/types/events'

export const useEventsStore = defineStore('events', () => {
  const items = ref<EventDTO[]>([])
  const selectedEvent = ref<EventDTO | null>(null)
  const sessions = ref<SessionDTO[]>([])
  const total = ref(0)
  const page = ref(1)
  const limit = ref(6)
  const pages = ref(1)
  const search = ref('')
  const isLoading = ref(false)
  const isDetailLoading = ref(false)
  const error = ref('')
  const detailError = ref('')

  const hasEvents = computed(() => items.value.length > 0)

  async function fetchEvents(options: FetchEventsOptions = {}) {
    isLoading.value = true
    error.value = ''

    const nextPage = options.page ?? page.value
    const nextLimit = options.limit ?? limit.value
    const nextSearch = options.search ?? search.value
    try {
      const data = await fetchEventsRequest({
        limit: nextLimit,
        page: nextPage,
        search: nextSearch,
      })

      items.value = data.items
      total.value = data.total
      page.value = data.page
      limit.value = data.limit
      pages.value = data.pages
      search.value = nextSearch
    } catch (caughtError) {
      const message = caughtError instanceof Error ? caughtError.message : ''
      error.value = message || 'No pudimos cargar los eventos. Inténtalo de nuevo.'
    } finally {
      isLoading.value = false
    }
  }

  async function createEvent(payload: EventCreatePayload) {
    error.value = ''
    return createEventRequest(payload)
  }

  async function fetchEventDetail(eventId: string) {
    isDetailLoading.value = true
    detailError.value = ''
    selectedEvent.value = null
    sessions.value = []

    try {
      const data = await fetchEventDetailRequest(eventId)

      selectedEvent.value = data.event
      sessions.value = data.sessions
    } catch (caughtError) {
      const message = caughtError instanceof Error ? caughtError.message : ''
      detailError.value = message || 'No pudimos cargar el detalle del evento. Inténtalo de nuevo.'
    } finally {
      isDetailLoading.value = false
    }
  }

  async function clearSearch() {
    search.value = ''
    await fetchEvents({ page: 1, search: '' })
  }

  return {
    clearSearch,
    createEvent,
    detailError,
    error,
    fetchEventDetail,
    fetchEvents,
    hasEvents,
    isDetailLoading,
    isLoading,
    items,
    limit,
    page,
    pages,
    search,
    selectedEvent,
    sessions,
    total,
  }
})
