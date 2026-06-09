import { beforeEach, describe, expect, it, vi } from 'vitest'

import { activatePinia, makeEvent, makeSession, makeSpeaker } from '@/__tests__/helpers'
import {
  cancelEventRegistration,
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
} from '@/services/eventsApi'
import { useEventsStore } from '../events'

vi.mock('@/services/eventsApi', () => ({
  cancelEventRegistration: vi.fn(),
  createEvent: vi.fn(),
  createSession: vi.fn(),
  deleteSession: vi.fn(),
  fetchEventDetail: vi.fn(),
  fetchEventRegistrants: vi.fn(),
  fetchEvents: vi.fn(),
  fetchMyRegistrations: vi.fn(),
  fetchMySessionRegistrations: vi.fn(),
  fetchSpeakers: vi.fn(),
  registerToEvent: vi.fn(),
  registerToSession: vi.fn(),
  updateEvent: vi.fn(),
  updateSession: vi.fn(),
}))

const mockedCancelEventRegistration = vi.mocked(cancelEventRegistration)
const mockedCreateSession = vi.mocked(createSession)
const mockedDeleteSession = vi.mocked(deleteSession)
const mockedFetchEventDetail = vi.mocked(fetchEventDetail)
const mockedFetchEventRegistrants = vi.mocked(fetchEventRegistrants)
const mockedFetchEvents = vi.mocked(fetchEvents)
const mockedFetchMyRegistrations = vi.mocked(fetchMyRegistrations)
const mockedFetchMySessionRegistrations = vi.mocked(fetchMySessionRegistrations)
const mockedFetchSpeakers = vi.mocked(fetchSpeakers)
const mockedRegisterToEvent = vi.mocked(registerToEvent)
const mockedRegisterToSession = vi.mocked(registerToSession)
const mockedUpdateEvent = vi.mocked(updateEvent)
const mockedUpdateSession = vi.mocked(updateSession)

const event = makeEvent()
const secondEvent = makeEvent({
  id: 'event-2',
  name: 'Testing Summit',
  registered_count: 0,
})
const speaker = makeSpeaker()
const session = makeSession({ speaker })

describe('events store', () => {
  beforeEach(() => {
    activatePinia()
    vi.clearAllMocks()
  })

  it('fetches events and updates pagination state', async () => {
    mockedFetchEvents.mockResolvedValue({
      items: [event],
      limit: 5,
      page: 2,
      pages: 4,
      total: 18,
    })

    const store = useEventsStore()

    await store.fetchEvents({ limit: 5, page: 2, search: 'vue', status: 'published' })

    expect(mockedFetchEvents).toHaveBeenCalledWith({
      limit: 5,
      page: 2,
      search: 'vue',
      status: 'published',
    })
    expect(store.items).toEqual([event])
    expect(store.hasEvents).toBe(true)
    expect(store.total).toBe(18)
    expect(store.search).toBe('vue')
    expect(store.isLoading).toBe(false)
  })

  it('stores fetch errors and stops loading', async () => {
    mockedFetchEvents.mockRejectedValue(new Error('API caída'))

    const store = useEventsStore()

    await store.fetchEvents()

    expect(store.error).toBe('API caída')
    expect(store.isLoading).toBe(false)
  })

  it('clears search and reloads the first page', async () => {
    mockedFetchEvents.mockResolvedValue({
      items: [],
      limit: 6,
      page: 1,
      pages: 1,
      total: 0,
    })

    const store = useEventsStore()

    store.search = 'vue'

    await store.clearSearch()

    expect(store.search).toBe('')
    expect(mockedFetchEvents).toHaveBeenCalledWith({
      limit: 6,
      page: 1,
      search: '',
      status: undefined,
    })
  })

  it('loads event detail and sessions', async () => {
    mockedFetchEventDetail.mockResolvedValue({
      event,
      sessions: [session],
    })

    const store = useEventsStore()

    await store.fetchEventDetail('event-1')

    expect(store.selectedEvent).toEqual(event)
    expect(store.sessions).toEqual([session])
    expect(store.detailError).toBe('')
    expect(store.isDetailLoading).toBe(false)
  })

  it('stores event detail errors and clears stale detail state', async () => {
    mockedFetchEventDetail.mockRejectedValue(new Error('Detalle no disponible'))

    const store = useEventsStore()

    store.selectedEvent = event
    store.sessions = [session]

    await store.fetchEventDetail('event-1')

    expect(store.selectedEvent).toBeNull()
    expect(store.sessions).toEqual([])
    expect(store.detailError).toBe('Detalle no disponible')
    expect(store.isDetailLoading).toBe(false)
  })

  it('updates selected and listed events after editing', async () => {
    const updatedEvent = {
      ...event,
      name: 'Vue Conf Actualizada',
    }

    mockedUpdateEvent.mockResolvedValue(updatedEvent)

    const store = useEventsStore()

    store.items = [event, secondEvent]
    store.selectedEvent = event

    await store.updateEvent('event-1', { name: 'Vue Conf Actualizada' })

    expect(store.selectedEvent).toEqual(updatedEvent)
    expect(store.items).toEqual([updatedEvent, secondEvent])
  })

  it('keeps speaker data when creating and updating sessions', async () => {
    const createdSession = {
      ...session,
      id: 'session-2',
      speaker: null,
    }
    const updatedSession = {
      ...createdSession,
      title: 'Arquitectura hexagonal',
      speaker: null,
    }

    mockedCreateSession.mockResolvedValue(createdSession)
    mockedUpdateSession.mockResolvedValue(updatedSession)

    const store = useEventsStore()

    store.speakers = [speaker]

    const normalizedCreated = await store.createSession('event-1', {
      speaker_id: 'speaker-1',
      start_time: createdSession.start_time,
      end_time: createdSession.end_time,
      title: createdSession.title,
    })

    expect(normalizedCreated.speaker).toEqual(speaker)

    const normalizedUpdated = await store.updateSession('event-1', 'session-2', {
      title: 'Arquitectura hexagonal',
    })

    expect(normalizedUpdated.speaker).toEqual(speaker)
    expect(store.sessions[0]).toEqual(normalizedUpdated)
  })

  it('deletes sessions from local state', async () => {
    mockedDeleteSession.mockResolvedValue(undefined)

    const store = useEventsStore()

    store.sessions = [session, { ...session, id: 'session-2' }]

    await store.deleteSession('event-1', 'session-1')

    expect(mockedDeleteSession).toHaveBeenCalledWith('event-1', 'session-1')
    expect(store.sessions.map((item) => item.id)).toEqual(['session-2'])
  })

  it('loads speakers and registrants with error states', async () => {
    mockedFetchSpeakers.mockResolvedValue([speaker])
    mockedFetchEventRegistrants.mockResolvedValue([
      {
        email: 'ana@example.com',
        registered_at: '2026-01-01T00:00:00Z',
        role: 'attendee',
        user_id: 'user-1',
      },
    ])

    const store = useEventsStore()

    await store.fetchSpeakers()
    await store.fetchEventRegistrants('event-1')

    expect(store.speakers).toEqual([speaker])
    expect(store.eventRegistrants).toHaveLength(1)

    mockedFetchSpeakers.mockRejectedValue(new Error('Sin ponentes'))
    mockedFetchEventRegistrants.mockRejectedValue(new Error('Sin registrados'))

    await store.fetchSpeakers()
    await store.fetchEventRegistrants('event-1')

    expect(store.speakersError).toBe('Sin ponentes')
    expect(store.eventRegistrantsError).toBe('Sin registrados')
  })

  it('registers and cancels event registrations while updating counts', async () => {
    mockedRegisterToEvent.mockResolvedValue({
      id: 'registration-1',
      event_id: 'event-1',
      registered_at: '2026-01-01T00:00:00Z',
      user_id: 'user-1',
    })
    mockedCancelEventRegistration.mockResolvedValue(undefined)

    const store = useEventsStore()

    store.items = [event]
    store.selectedEvent = event

    await store.registerToEvent('event-1')

    expect(store.isRegisteredToEvent('event-1')).toBe(true)
    expect(store.items[0]!.registered_count).toBe(3)
    expect(store.selectedEvent?.registered_count).toBe(3)

    await store.cancelEventRegistration('event-1')

    expect(store.isRegisteredToEvent('event-1')).toBe(false)
    expect(store.items[0]!.registered_count).toBe(2)
    expect(store.selectedEvent?.registered_count).toBe(2)
  })

  it('loads registration ids and returns an empty list on failure', async () => {
    mockedFetchMyRegistrations.mockResolvedValue([event, secondEvent])

    const store = useEventsStore()

    await expect(store.fetchMyRegistrations()).resolves.toEqual([event, secondEvent])
    expect(store.isRegisteredToEvent('event-1')).toBe(true)
    expect(store.isRegisteredToEvent('event-2')).toBe(true)

    mockedFetchMyRegistrations.mockRejectedValue(new Error('No autorizado'))

    await expect(store.fetchMyRegistrations()).resolves.toEqual([])
    expect(store.myRegistrationsError).toBe('No autorizado')
  })

  it('registers sessions and tracks session registration ids', async () => {
    mockedRegisterToSession.mockResolvedValue({
      id: 'registration-1',
      event_id: 'event-1',
      registered_at: '2026-01-01T00:00:00Z',
      user_id: 'user-1',
    })
    mockedFetchMySessionRegistrations.mockResolvedValue([session])

    const store = useEventsStore()

    store.sessions = [session]

    await store.registerToSession('session-1')

    expect(store.registeredSessionIds).toEqual(['session-1'])
    expect(store.sessions[0]!.registered_count).toBe(2)
    expect(store.isRegisteredToSession('session-1')).toBe(true)

    await store.fetchMySessionRegistrations()

    expect(store.registeredSessionIds).toEqual(['session-1'])
  })

  it('returns an empty session registration list on failure', async () => {
    mockedFetchMySessionRegistrations.mockRejectedValue(new Error('No se pudo verificar'))

    const store = useEventsStore()

    await expect(store.fetchMySessionRegistrations()).resolves.toEqual([])

    expect(store.mySessionRegistrationsError).toBe('No se pudo verificar')
    expect(store.isMySessionRegistrationsLoading).toBe(false)
  })
})
