import { computed, ref } from 'vue'
import { defineStore } from 'pinia'

import { useAuthStore } from '@/stores/auth'

const DEFAULT_API_BASE_URL = 'http://localhost:8000'

export type EventStatus = 'cancelled' | 'draft' | 'finished' | 'published'

export type EventDTO = {
  id: string
  name: string
  description: string | null
  date: string
  end_date: string | null
  location: string | null
  capacity: number
  registered_count: number
  status: EventStatus
  created_by: string
  created_at: string
}

export type EventCreatePayload = {
  name: string
  description?: string | null
  date: string
  end_date?: string | null
  location?: string | null
  capacity: number
}

export type SpeakerDTO = {
  id: string
  name: string
  bio: string | null
  email: string | null
}

export type SessionDTO = {
  id: string
  event_id: string
  title: string
  speaker: SpeakerDTO | null
  start_time: string
  end_time: string
  capacity: number | null
  registered_count: number
}

type PaginatedEventsDTO = {
  items: EventDTO[]
  total: number
  page: number
  limit: number
  pages: number
}

type FetchEventsOptions = {
  limit?: number
  page?: number
  search?: string
}

function getApiBaseUrl() {
  return (import.meta.env.VITE_API_BASE_URL || DEFAULT_API_BASE_URL).replace(/\/$/, '')
}

async function readErrorMessage(response: Response) {
  const fallback = 'No pudimos cargar los eventos. Inténtalo de nuevo.'

  try {
    const data: unknown = await response.json()

    if (data && typeof data === 'object' && 'detail' in data) {
      const detail = (data as { detail: unknown }).detail
      if (typeof detail === 'string') return detail
    }
  } catch {
    return fallback
  }

  return fallback
}

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

  async function fetchWithAuth(path: string, init: RequestInit = {}) {
    const authStore = useAuthStore()
    const response = await fetch(`${getApiBaseUrl()}${path}`, {
      ...init,
      headers: {
        Authorization: authStore.authorizationHeader,
        ...init.headers,
      },
    })

    if (response.status === 401) {
      authStore.logout()
    }

    if (!response.ok) {
      throw new Error(await readErrorMessage(response))
    }

    return response
  }

  async function fetchEvents(options: FetchEventsOptions = {}) {
    isLoading.value = true
    error.value = ''

    const nextPage = options.page ?? page.value
    const nextLimit = options.limit ?? limit.value
    const nextSearch = options.search ?? search.value
    const params = new URLSearchParams({
      page: String(nextPage),
      limit: String(nextLimit),
    })

    if (nextSearch.trim()) {
      params.set('search', nextSearch.trim())
    }

    try {
      const response = await fetchWithAuth(`/events/?${params.toString()}`)
      const data = (await response.json()) as PaginatedEventsDTO

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

    const response = await fetchWithAuth('/events/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    })

    return (await response.json()) as EventDTO
  }

  async function fetchEventDetail(eventId: string) {
    isDetailLoading.value = true
    detailError.value = ''
    selectedEvent.value = null
    sessions.value = []

    try {
      const [eventResponse, sessionsResponse] = await Promise.all([
        fetchWithAuth(`/events/${eventId}`),
        fetchWithAuth(`/events/${eventId}/sessions/`),
      ])

      selectedEvent.value = (await eventResponse.json()) as EventDTO
      sessions.value = (await sessionsResponse.json()) as SessionDTO[]
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
