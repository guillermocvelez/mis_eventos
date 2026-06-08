import { useAuthStore } from '@/stores/auth'
import type {
  EventCreatePayload,
  EventDTO,
  EventDetailDTO,
  FetchEventsOptions,
  PaginatedEventsDTO,
  SessionDTO,
} from '@/types/events'

const DEFAULT_API_BASE_URL = 'http://localhost:8000'

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

export async function fetchEvents(options: Required<FetchEventsOptions>) {
  const params = new URLSearchParams({
    page: String(options.page),
    limit: String(options.limit),
  })

  if (options.search.trim()) {
    params.set('search', options.search.trim())
  }

  const response = await fetchWithAuth(`/events/?${params.toString()}`)
  return (await response.json()) as PaginatedEventsDTO
}

export async function createEvent(payload: EventCreatePayload) {
  const response = await fetchWithAuth('/events/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  })

  return (await response.json()) as EventDTO
}

export async function fetchEventDetail(eventId: string): Promise<EventDetailDTO> {
  const [eventResponse, sessionsResponse] = await Promise.all([
    fetchWithAuth(`/events/${eventId}`),
    fetchWithAuth(`/events/${eventId}/sessions/`),
  ])

  return {
    event: (await eventResponse.json()) as EventDTO,
    sessions: (await sessionsResponse.json()) as SessionDTO[],
  }
}
