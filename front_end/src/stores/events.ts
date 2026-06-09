import { computed, ref } from 'vue'
import { defineStore } from 'pinia'

import {
  cancelEventRegistration as cancelEventRegistrationRequest,
  createEvent as createEventRequest,
  createSession as createSessionRequest,
  deleteSession as deleteSessionRequest,
  fetchEventDetail as fetchEventDetailRequest,
  fetchEventRegistrants as fetchEventRegistrantsRequest,
  fetchEvents as fetchEventsRequest,
  fetchMyRegistrations as fetchMyRegistrationsRequest,
  fetchMySessionRegistrations as fetchMySessionRegistrationsRequest,
  fetchSpeakers as fetchSpeakersRequest,
  registerToEvent as registerToEventRequest,
  registerToSession as registerToSessionRequest,
  updateEvent as updateEventRequest,
  updateSession as updateSessionRequest,
} from '@/services/eventsApi'
import type {
  EventCreatePayload,
  EventDTO,
  EventRegistrantDTO,
  EventUpdatePayload,
  FetchEventsOptions,
  RegistrationDTO,
  SessionCreatePayload,
  SessionDTO,
  SessionUpdatePayload,
  SpeakerDTO,
} from '@/types/events'

export type {
  EventCreatePayload,
  EventDTO,
  EventRegistrantDTO,
  EventStatus,
  EventUpdatePayload,
  RegistrationDTO,
  SessionCreatePayload,
  SessionDTO,
  SessionUpdatePayload,
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
  const eventRegistrants = ref<EventRegistrantDTO[]>([])
  const eventRegistrantsError = ref('')
  const isEventRegistrantsLoading = ref(false)
  const speakers = ref<SpeakerDTO[]>([])
  const speakersError = ref('')
  const registeredEventIds = ref<string[]>([])
  const registeredSessionIds = ref<string[]>([])
  const isMyRegistrationsLoading = ref(false)
  const isMySessionRegistrationsLoading = ref(false)
  const myRegistrationsError = ref('')
  const mySessionRegistrationsError = ref('')

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

  async function updateEvent(eventId: string, payload: EventUpdatePayload) {
    const updatedEvent = await updateEventRequest(eventId, payload)

    if (selectedEvent.value?.id === updatedEvent.id) {
      selectedEvent.value = updatedEvent
    }

    items.value = items.value.map((event) => (event.id === updatedEvent.id ? updatedEvent : event))

    return updatedEvent
  }

  function withSessionSpeaker(
    session: SessionDTO,
    payload: SessionCreatePayload | SessionUpdatePayload,
    previousSession?: SessionDTO,
  ) {
    const speaker =
      session.speaker ??
      (payload.speaker_id === undefined
        ? (previousSession?.speaker ?? null)
        : (speakers.value.find((item) => item.id === payload.speaker_id) ?? null))

    return {
      ...session,
      speaker,
    }
  }

  async function createSession(eventId: string, payload: SessionCreatePayload) {
    const createdSession = await createSessionRequest(eventId, payload)
    const normalizedSession = withSessionSpeaker(createdSession, payload)

    sessions.value = [...sessions.value, normalizedSession]

    return normalizedSession
  }

  async function updateSession(eventId: string, sessionId: string, payload: SessionUpdatePayload) {
    const updatedSession = await updateSessionRequest(eventId, sessionId, payload)
    const previousSession = sessions.value.find((session) => session.id === sessionId)
    const normalizedSession = withSessionSpeaker(updatedSession, payload, previousSession)

    sessions.value = sessions.value.map((session) =>
      session.id === normalizedSession.id ? normalizedSession : session,
    )

    return normalizedSession
  }

  async function deleteSession(eventId: string, sessionId: string) {
    await deleteSessionRequest(eventId, sessionId)

    sessions.value = sessions.value.filter((session) => session.id !== sessionId)
  }

  async function fetchSpeakers() {
    speakersError.value = ''

    try {
      speakers.value = await fetchSpeakersRequest()
    } catch (caughtError) {
      const message = caughtError instanceof Error ? caughtError.message : ''
      speakersError.value = message || 'No pudimos cargar los ponentes.'
    }
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

  async function fetchEventRegistrants(eventId: string) {
    isEventRegistrantsLoading.value = true
    eventRegistrantsError.value = ''

    try {
      eventRegistrants.value = await fetchEventRegistrantsRequest(eventId)
    } catch (caughtError) {
      const message = caughtError instanceof Error ? caughtError.message : ''
      eventRegistrantsError.value =
        message || 'No pudimos cargar los usuarios registrados. Inténtalo de nuevo.'
    } finally {
      isEventRegistrantsLoading.value = false
    }
  }

  async function fetchMyRegistrations() {
    isMyRegistrationsLoading.value = true
    myRegistrationsError.value = ''

    try {
      const registeredEvents = await fetchMyRegistrationsRequest()
      registeredEventIds.value = registeredEvents.map((event) => event.id)
      return registeredEvents
    } catch (caughtError) {
      const message = caughtError instanceof Error ? caughtError.message : ''
      myRegistrationsError.value =
        message || 'No pudimos verificar tus registros. Inténtalo de nuevo.'
      return []
    } finally {
      isMyRegistrationsLoading.value = false
    }
  }

  async function fetchMySessionRegistrations() {
    isMySessionRegistrationsLoading.value = true
    mySessionRegistrationsError.value = ''

    try {
      const registeredSessions = await fetchMySessionRegistrationsRequest()
      registeredSessionIds.value = registeredSessions.map((session) => session.id)
      return registeredSessions
    } catch (caughtError) {
      const message = caughtError instanceof Error ? caughtError.message : ''
      mySessionRegistrationsError.value =
        message || 'No pudimos verificar tus registros a sesiones. Inténtalo de nuevo.'
      return []
    } finally {
      isMySessionRegistrationsLoading.value = false
    }
  }

  function isRegisteredToEvent(eventId: string) {
    return registeredEventIds.value.includes(eventId)
  }

  function isRegisteredToSession(sessionId: string) {
    return registeredSessionIds.value.includes(sessionId)
  }

  function updateSessionRegisteredCount(
    sessionId: string,
    nextRegisteredCount: (current: number) => number,
  ) {
    sessions.value = sessions.value.map((session) =>
      session.id === sessionId
        ? { ...session, registered_count: nextRegisteredCount(session.registered_count) }
        : session,
    )
  }

  function updateEventRegisteredCount(
    eventId: string,
    nextRegisteredCount: (current: number) => number,
  ) {
    if (selectedEvent.value?.id === eventId) {
      selectedEvent.value = {
        ...selectedEvent.value,
        registered_count: nextRegisteredCount(selectedEvent.value.registered_count),
      }
    }

    items.value = items.value.map((event) =>
      event.id === eventId
        ? { ...event, registered_count: nextRegisteredCount(event.registered_count) }
        : event,
    )
  }

  async function registerToEvent(eventId: string): Promise<RegistrationDTO> {
    const registration = await registerToEventRequest(eventId)

    updateEventRegisteredCount(eventId, (current) => current + 1)

    if (!registeredEventIds.value.includes(eventId)) {
      registeredEventIds.value = [...registeredEventIds.value, eventId]
    }

    return registration
  }

  async function cancelEventRegistration(eventId: string) {
    await cancelEventRegistrationRequest(eventId)

    registeredEventIds.value = registeredEventIds.value.filter((id) => id !== eventId)
    updateEventRegisteredCount(eventId, (current) => Math.max(current - 1, 0))
  }

  async function registerToSession(sessionId: string): Promise<RegistrationDTO> {
    const registration = await registerToSessionRequest(sessionId)

    updateSessionRegisteredCount(sessionId, (current) => current + 1)

    if (!registeredSessionIds.value.includes(sessionId)) {
      registeredSessionIds.value = [...registeredSessionIds.value, sessionId]
    }

    return registration
  }

  async function clearSearch() {
    search.value = ''
    await fetchEvents({ page: 1, search: '' })
  }

  return {
    cancelEventRegistration,
    clearSearch,
    createSession,
    createEvent,
    deleteSession,
    detailError,
    error,
    eventRegistrants,
    eventRegistrantsError,
    fetchEventDetail,
    fetchEventRegistrants,
    fetchEvents,
    fetchMyRegistrations,
    fetchMySessionRegistrations,
    fetchSpeakers,
    hasEvents,
    isDetailLoading,
    isEventRegistrantsLoading,
    isLoading,
    isMyRegistrationsLoading,
    isMySessionRegistrationsLoading,
    isRegisteredToSession,
    isRegisteredToEvent,
    items,
    limit,
    myRegistrationsError,
    mySessionRegistrationsError,
    page,
    pages,
    registeredSessionIds,
    registerToEvent,
    registerToSession,
    search,
    selectedEvent,
    sessions,
    speakers,
    speakersError,
    total,
    updateEvent,
    updateSession,
  }
})
