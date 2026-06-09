import { beforeEach, describe, expect, it, vi } from 'vitest'

import { activatePinia, jsonResponse, makeEvent, makeSession } from '@/__tests__/helpers'
import {
  cancelEventRegistration,
  createEvent,
  createSession,
  deleteSession,
  fetchEventDetail,
  fetchEventRegistrants,
  fetchEvents,
  fetchMyRegistrations,
  fetchMySessionRegistrations,
  fetchSpeakers,
  registerToEvent,
  registerToSession,
  updateEvent,
  updateSession,
} from '../eventsApi'
import { useAuthStore } from '@/stores/auth'

const event = makeEvent()
const session = makeSession({ capacity: null, registered_count: 0 })

describe('eventsApi', () => {
  beforeEach(() => {
    activatePinia()
    const authStore = useAuthStore()
    authStore.token = 'token'
    authStore.tokenType = 'Bearer'
    vi.restoreAllMocks()
  })

  it('fetches events with auth headers and normalized query params', async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      jsonResponse({
        items: [event],
        limit: 5,
        page: 2,
        pages: 1,
        total: 1,
      }),
    )

    vi.stubGlobal('fetch', fetchMock)

    const result = await fetchEvents({
      limit: 5,
      page: 2,
      search: '  Vue  ',
      status: 'published',
    })

    expect(fetchMock).toHaveBeenCalledWith(
      'http://localhost:8000/events/?page=2&limit=5&search=Vue&status=published',
      expect.objectContaining({
        headers: expect.objectContaining({
          Authorization: 'Bearer token',
        }),
      }),
    )
    expect(result.items).toEqual([event])
  })

  it('creates events with JSON payloads', async () => {
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse(event))

    vi.stubGlobal('fetch', fetchMock)

    await createEvent({
      capacity: 10,
      date: event.date,
      description: 'Evento',
      location: 'Bogota',
      name: 'Vue Conf',
    })

    expect(fetchMock).toHaveBeenCalledWith(
      'http://localhost:8000/events/',
      expect.objectContaining({
        body: JSON.stringify({
          capacity: 10,
          date: event.date,
          description: 'Evento',
          location: 'Bogota',
          name: 'Vue Conf',
        }),
        headers: expect.objectContaining({
          Authorization: 'Bearer token',
          'Content-Type': 'application/json',
        }),
        method: 'POST',
      }),
    )
  })

  it('updates events with PATCH payloads', async () => {
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse(event))

    vi.stubGlobal('fetch', fetchMock)

    await updateEvent('event-1', {
      capacity: 20,
      status: 'published',
    })

    expect(fetchMock).toHaveBeenCalledWith(
      'http://localhost:8000/events/event-1',
      expect.objectContaining({
        body: JSON.stringify({
          capacity: 20,
          status: 'published',
        }),
        method: 'PATCH',
      }),
    )
  })

  it('fetches event detail from event and sessions endpoints', async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(jsonResponse(event))
      .mockResolvedValueOnce(jsonResponse([session]))

    vi.stubGlobal('fetch', fetchMock)

    await expect(fetchEventDetail('event-1')).resolves.toEqual({
      event,
      sessions: [session],
    })

    expect(fetchMock).toHaveBeenNthCalledWith(
      1,
      'http://localhost:8000/events/event-1',
      expect.any(Object),
    )
    expect(fetchMock).toHaveBeenNthCalledWith(
      2,
      'http://localhost:8000/events/event-1/sessions/',
      expect.any(Object),
    )
  })

  it('registers and cancels event registrations', async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      jsonResponse({
        id: 'registration-1',
        event_id: 'event-1',
        registered_at: '2026-01-01T00:00:00Z',
        user_id: 'user-1',
      }),
    )

    vi.stubGlobal('fetch', fetchMock)

    await registerToEvent('event-1')
    await cancelEventRegistration('event-1')

    expect(fetchMock).toHaveBeenNthCalledWith(
      1,
      'http://localhost:8000/registrations/event-1',
      expect.objectContaining({ method: 'POST' }),
    )
    expect(fetchMock).toHaveBeenNthCalledWith(
      2,
      'http://localhost:8000/registrations/event-1',
      expect.objectContaining({ method: 'DELETE' }),
    )
  })

  it('fetches event registrants and session registrations', async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(jsonResponse([{ email: 'ana@example.com', role: 'attendee' }]))
      .mockResolvedValueOnce(jsonResponse([session]))

    vi.stubGlobal('fetch', fetchMock)

    await expect(fetchEventRegistrants('event-1')).resolves.toHaveLength(1)
    await expect(fetchMySessionRegistrations()).resolves.toEqual([session])

    expect(fetchMock).toHaveBeenNthCalledWith(
      1,
      'http://localhost:8000/registrations/events/event-1/users',
      expect.any(Object),
    )
    expect(fetchMock).toHaveBeenNthCalledWith(
      2,
      'http://localhost:8000/session-registrations/me',
      expect.any(Object),
    )
  })

  it('creates, updates and deletes sessions', async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(jsonResponse(session))
      .mockResolvedValueOnce(jsonResponse(session))
      .mockResolvedValueOnce(jsonResponse({}))

    vi.stubGlobal('fetch', fetchMock)

    await createSession('event-1', {
      capacity: 20,
      end_time: session.end_time,
      speaker_id: null,
      start_time: session.start_time,
      title: session.title,
    })
    await updateSession('event-1', 'session-1', { title: 'Actualizada' })
    await deleteSession('event-1', 'session-1')

    expect(fetchMock).toHaveBeenNthCalledWith(
      1,
      'http://localhost:8000/events/event-1/sessions/',
      expect.objectContaining({ method: 'POST' }),
    )
    expect(fetchMock).toHaveBeenNthCalledWith(
      2,
      'http://localhost:8000/events/event-1/sessions/session-1',
      expect.objectContaining({
        body: JSON.stringify({ title: 'Actualizada' }),
        method: 'PATCH',
      }),
    )
    expect(fetchMock).toHaveBeenNthCalledWith(
      3,
      'http://localhost:8000/events/event-1/sessions/session-1',
      expect.objectContaining({ method: 'DELETE' }),
    )
  })

  it('registers to sessions', async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      jsonResponse({
        id: 'registration-1',
        event_id: 'event-1',
        registered_at: '2026-01-01T00:00:00Z',
        user_id: 'user-1',
      }),
    )

    vi.stubGlobal('fetch', fetchMock)

    await registerToSession('session-1')

    expect(fetchMock).toHaveBeenCalledWith(
      'http://localhost:8000/session-registrations/session-1',
      expect.objectContaining({ method: 'POST' }),
    )
  })

  it('throws API detail messages for failed requests', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue(jsonResponse({ detail: 'No se pudo cargar.' }, { status: 500 })),
    )

    await expect(fetchSpeakers()).rejects.toThrow('No se pudo cargar.')
  })

  it('logs out on unauthorized responses', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue(jsonResponse({ detail: 'No autorizado.' }, { status: 401 })),
    )

    const authStore = useAuthStore()

    await expect(fetchMyRegistrations()).rejects.toThrow('No autorizado.')

    expect(authStore.token).toBe('')
    expect(authStore.authorizationHeader).toBe('')
  })
})
