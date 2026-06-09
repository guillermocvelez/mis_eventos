import { createPinia, setActivePinia } from 'pinia'

import { useAuthStore, type UserRole } from '@/stores/auth'
import type { EventDTO, SessionDTO, SpeakerDTO } from '@/types/events'
import type { UserProfileDTO } from '@/types/profile'
import type { UserDTO } from '@/types/users'

export function activatePinia() {
  const pinia = createPinia()
  setActivePinia(pinia)
  return pinia
}

export function createAuthToken(payload: Record<string, unknown>) {
  const encodedPayload = btoa(JSON.stringify(payload))
    .replace(/\+/g, '-')
    .replace(/\//g, '_')
    .replace(/=+$/, '')

  return `header.${encodedPayload}.signature`
}

export function authenticate(role: UserRole = 'attendee', sub = `${role}@example.com`) {
  const authStore = useAuthStore()
  authStore.token = createAuthToken({ role, sub })
  authStore.tokenType = 'Bearer'
  return authStore
}

export function jsonResponse(body: unknown, init: ResponseInit = {}) {
  return new Response(JSON.stringify(body), {
    headers: { 'Content-Type': 'application/json' },
    status: 200,
    ...init,
  })
}

export function makeEvent(overrides: Partial<EventDTO> = {}): EventDTO {
  return {
    id: 'event-1',
    name: 'Vue Conf',
    description: null,
    date: '2026-02-10T14:00:00Z',
    end_date: null,
    location: 'Bogota',
    capacity: 10,
    registered_count: 2,
    status: 'published',
    created_by: 'user-1',
    created_at: '2026-01-01T00:00:00Z',
    ...overrides,
  }
}

export function makeSpeaker(overrides: Partial<SpeakerDTO> = {}): SpeakerDTO {
  return {
    id: 'speaker-1',
    name: 'Ada Lovelace',
    bio: null,
    email: 'ada@example.com',
    ...overrides,
  }
}

export function makeSession(overrides: Partial<SessionDTO> = {}): SessionDTO {
  return {
    id: 'session-1',
    event_id: 'event-1',
    title: 'Arquitectura limpia',
    speaker: null,
    start_time: '2026-02-10T14:00:00Z',
    end_time: '2026-02-10T15:00:00Z',
    capacity: 10,
    registered_count: 1,
    ...overrides,
  }
}

export function makeUser(overrides: Partial<UserDTO> = {}): UserDTO {
  return {
    id: 'user-1',
    email: 'ana@example.com',
    name: 'Ana Gomez',
    role: 'admin',
    is_active: true,
    created_at: '2026-01-01T00:00:00Z',
    ...overrides,
  }
}

export function makeProfile(overrides: Partial<UserProfileDTO> = {}): UserProfileDTO {
  return {
    id: 'user-1',
    email: 'ana@example.com',
    name: 'Ana Gomez',
    role: 'admin',
    created_at: '2026-01-01T00:00:00Z',
    is_active: true,
    organized_count: 4,
    registered_count: 2,
    ...overrides,
  }
}
