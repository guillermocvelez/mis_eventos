import { useAuthStore } from '@/stores/auth'
import type {
  EventCreatePayload,
  EventDTO,
  EventDetailDTO,
  EventRegistrantDTO,
  EventUpdatePayload,
  FetchEventsOptions,
  PaginatedEventsDTO,
  RegistrationDTO,
  SessionCreatePayload,
  SessionDTO,
  SessionUpdatePayload,
  SpeakerDTO,
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

export async function updateEvent(eventId: string, payload: EventUpdatePayload) {
  const response = await fetchWithAuth(`/events/${eventId}`, {
    method: 'PATCH',
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

export async function registerToEvent(eventId: string) {
  const response = await fetchWithAuth(`/registrations/${eventId}`, {
    method: 'POST',
  })

  return (await response.json()) as RegistrationDTO
}

export async function fetchMyRegistrations() {
  const response = await fetchWithAuth('/registrations/me')
  return (await response.json()) as EventDTO[]
}

export async function cancelEventRegistration(eventId: string) {
  await fetchWithAuth(`/registrations/${eventId}`, {
    method: 'DELETE',
  })
}

export async function fetchEventRegistrants(eventId: string) {
  const response = await fetchWithAuth(`/registrations/events/${eventId}/users`)
  return (await response.json()) as EventRegistrantDTO[]
}

export async function registerToSession(sessionId: string) {
  const response = await fetchWithAuth(`/session-registrations/${sessionId}`, {
    method: 'POST',
  })

  return (await response.json()) as RegistrationDTO
}

export async function fetchMySessionRegistrations() {
  const response = await fetchWithAuth('/session-registrations/me')
  return (await response.json()) as SessionDTO[]
}

export async function createSession(eventId: string, payload: SessionCreatePayload) {
  const response = await fetchWithAuth(`/events/${eventId}/sessions/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  })

  return (await response.json()) as SessionDTO
}

export async function updateSession(
  eventId: string,
  sessionId: string,
  payload: SessionUpdatePayload,
) {
  const response = await fetchWithAuth(`/events/${eventId}/sessions/${sessionId}`, {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  })

  return (await response.json()) as SessionDTO
}

export async function deleteSession(eventId: string, sessionId: string) {
  await fetchWithAuth(`/events/${eventId}/sessions/${sessionId}`, {
    method: 'DELETE',
  })
}

export async function fetchSpeakers() {
  const response = await fetchWithAuth('/speakers/')
  return (await response.json()) as SpeakerDTO[]
}
