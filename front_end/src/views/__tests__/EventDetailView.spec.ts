import { flushPromises, mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import { activatePinia, authenticate, makeEvent, makeSession, makeSpeaker } from '@/__tests__/helpers'
import EventDetailView from '@/views/events/EventDetailView.vue'
import type { UserRole } from '@/stores/auth'
import { useEventsStore } from '@/stores/events'
import type { SessionCreatePayload } from '@/types/events'

const routerPush = vi.hoisted(() => vi.fn())
const routeState = vi.hoisted(() => ({
  name: 'event-detail' as string,
  params: { eventId: 'event-1' },
}))

vi.mock('vue-router', () => ({
  useRoute: () => routeState,
  useRouter: () => ({
    push: routerPush,
  }),
}))

const event = makeEvent({
  description: 'Evento de Vue',
  created_by: 'creator-123456',
})
const session = makeSession({
  title: 'Testing',
  start_time: '2026-02-10T15:00:00Z',
  end_time: '2026-02-10T16:00:00Z',
})
const speaker = makeSpeaker()
const sessionPayload: SessionCreatePayload = {
  title: 'Nueva sesión',
  speaker_id: 'speaker-1',
  start_time: '2026-02-10T17:00:00.000Z',
  end_time: '2026-02-10T18:00:00.000Z',
  capacity: 20,
}

function mountDetail(role: UserRole = 'attendee') {
  const pinia = activatePinia()

  const authStore = authenticate(role)
  const eventsStore = useEventsStore()

  eventsStore.selectedEvent = event
  eventsStore.sessions = [session]

  vi.spyOn(eventsStore, 'fetchEventDetail').mockResolvedValue(undefined)
  vi.spyOn(eventsStore, 'fetchMyRegistrations').mockResolvedValue([])
  vi.spyOn(eventsStore, 'fetchMySessionRegistrations').mockResolvedValue([])
  vi.spyOn(eventsStore, 'fetchEventRegistrants').mockResolvedValue(undefined)
  vi.spyOn(eventsStore, 'fetchSpeakers').mockResolvedValue(undefined)
  vi.spyOn(eventsStore, 'registerToEvent').mockResolvedValue({
    id: 'registration-1',
    event_id: 'event-1',
    registered_at: '2026-01-01T00:00:00Z',
    user_id: 'user-1',
  })
  vi.spyOn(eventsStore, 'cancelEventRegistration').mockResolvedValue(undefined)
  vi.spyOn(eventsStore, 'registerToSession').mockResolvedValue({
    id: 'registration-2',
    event_id: 'event-1',
    registered_at: '2026-01-01T00:00:00Z',
    user_id: 'user-1',
  })
  vi.spyOn(eventsStore, 'deleteSession').mockResolvedValue(undefined)
  vi.spyOn(eventsStore, 'createSession').mockResolvedValue(makeSession({ ...sessionPayload, speaker }))
  vi.spyOn(eventsStore, 'updateSession').mockResolvedValue(
    makeSession({ ...sessionPayload, id: 'session-1', speaker }),
  )

  const wrapper = mount(EventDetailView, {
    global: {
      plugins: [pinia],
      stubs: {
        EventRegistrationPanel: {
          props: ['error', 'event', 'isRegistered'],
          template:
            '<aside><p>{{ error }}</p><button data-test="register-event" @click="$emit(\'register\')">register</button><button data-test="cancel-event" @click="$emit(\'cancel-registration\')">cancel</button></aside>',
        },
        EventSessionModal: {
          props: ['session'],
          template:
            '<button data-test="save-session" @click="$emit(\'save\', { title: \'Nueva sesión\', speaker_id: \'speaker-1\', start_time: \'2026-02-10T17:00:00.000Z\', end_time: \'2026-02-10T18:00:00.000Z\', capacity: 20 })">save {{ session?.id }}</button>',
          methods: {
            setSubmitError: vi.fn(),
          },
        },
        EventSessionsSection: {
          props: ['sessions'],
          template:
            '<section><button data-test="add-session" @click="$emit(\'add-session\')">add</button><button data-test="edit-session" @click="$emit(\'edit-session\', sessions[0])">edit</button><button data-test="register-session" @click="$emit(\'register-session\', sessions[0])">register session</button><button data-test="delete-session" @click="$emit(\'delete-session\', sessions[0])">delete</button></section>',
        },
        UiToast: { template: '<div />' },
      },
    },
  })

  return { authStore, eventsStore, wrapper }
}

describe('EventDetailView', () => {
  beforeEach(() => {
    routeState.name = 'event-detail'
    routeState.params = { eventId: 'event-1' }
    routerPush.mockReset()
  })

  it('loads detail, event registrations and session registrations on mount', () => {
    const { eventsStore } = mountDetail()

    expect(eventsStore.fetchEventDetail).toHaveBeenCalledWith('event-1')
    expect(eventsStore.fetchMyRegistrations).toHaveBeenCalled()
    expect(eventsStore.fetchMySessionRegistrations).toHaveBeenCalled()
  })

  it('loads registrants on the registrants route', async () => {
    routeState.name = 'event-registrants'

    const { eventsStore } = mountDetail('admin')

    await flushPromises()

    expect(eventsStore.fetchEventRegistrants).toHaveBeenCalledWith('event-1')
  })

  it('renders registrants route states', async () => {
    routeState.name = 'event-registrants'
    const { eventsStore, wrapper } = mountDetail('admin')

    eventsStore.eventRegistrants = [
      {
        email: 'ana@example.com',
        registered_at: '2026-01-01T00:00:00Z',
        role: 'attendee',
        user_id: 'user-1',
      },
    ]
    await wrapper.vm.$nextTick()

    expect(wrapper.text()).toContain('Registrados · 1')
    expect(wrapper.text()).toContain('ana@example.com')
    expect(wrapper.text()).toContain('Asistente')

    eventsStore.eventRegistrants = []
    eventsStore.eventRegistrantsError = 'No se pudieron cargar registrados.'
    await wrapper.vm.$nextTick()

    expect(wrapper.text()).toContain('No se pudieron cargar registrados.')
  })

  it('registers and cancels event registrations from the panel', async () => {
    const { eventsStore, wrapper } = mountDetail()

    await wrapper.get('[data-test="register-event"]').trigger('click')
    await wrapper.get('[data-test="cancel-event"]').trigger('click')

    expect(eventsStore.registerToEvent).toHaveBeenCalledWith('event-1')
    expect(eventsStore.cancelEventRegistration).toHaveBeenCalledWith('event-1')
  })

  it('shows errors when event registration actions fail', async () => {
    const { eventsStore, wrapper } = mountDetail()

    vi.mocked(eventsStore.registerToEvent).mockRejectedValueOnce(new Error('Evento lleno'))
    vi.mocked(eventsStore.cancelEventRegistration).mockRejectedValueOnce(new Error('No se pudo cancelar'))

    await wrapper.get('[data-test="register-event"]').trigger('click')
    await flushPromises()

    expect(wrapper.text()).toContain('Evento lleno')

    await wrapper.get('[data-test="cancel-event"]').trigger('click')
    await flushPromises()

    expect(wrapper.text()).toContain('No se pudo cancelar')
  })

  it('refreshes registrations when the API says the user is already registered', async () => {
    const { eventsStore, wrapper } = mountDetail()

    vi.mocked(eventsStore.registerToEvent).mockRejectedValueOnce(new Error('Ya está registrado'))

    await wrapper.get('[data-test="register-event"]').trigger('click')
    await flushPromises()

    expect(eventsStore.fetchMyRegistrations).toHaveBeenCalledTimes(2)
    expect(wrapper.text()).not.toContain('Ya está registrado')
  })

  it('registers to a session and opens speaker loading for managers', async () => {
    const { eventsStore, wrapper } = mountDetail('organizer')

    await wrapper.get('[data-test="register-session"]').trigger('click')
    await wrapper.get('[data-test="add-session"]').trigger('click')

    expect(eventsStore.registerToSession).toHaveBeenCalledWith('session-1')
    expect(eventsStore.fetchSpeakers).toHaveBeenCalled()
  })

  it('creates and updates sessions from the session modal', async () => {
    const { eventsStore, wrapper } = mountDetail('organizer')

    await wrapper.get('[data-test="add-session"]').trigger('click')
    await wrapper.get('[data-test="save-session"]').trigger('click')
    await flushPromises()

    expect(eventsStore.createSession).toHaveBeenCalledWith('event-1', sessionPayload)

    await wrapper.get('[data-test="edit-session"]').trigger('click')
    await wrapper.get('[data-test="save-session"]').trigger('click')
    await flushPromises()

    expect(eventsStore.updateSession).toHaveBeenCalledWith('event-1', 'session-1', sessionPayload)
  })

  it('opens delete confirmation and deletes a session', async () => {
    const { eventsStore, wrapper } = mountDetail('organizer')

    await wrapper.get('[data-test="delete-session"]').trigger('click')

    expect(wrapper.text()).toContain('Eliminar sesión')
    expect(wrapper.text()).toContain('Testing')

    await wrapper.findAll('button').find((button) => button.text().includes('Eliminar sesión'))!.trigger('click')
    await flushPromises()

    expect(eventsStore.deleteSession).toHaveBeenCalledWith('event-1', 'session-1')
  })

  it('shows session registration errors and refreshes already-registered sessions', async () => {
    const { eventsStore, wrapper } = mountDetail()

    vi.mocked(eventsStore.registerToSession).mockRejectedValueOnce(new Error('Sesión llena'))

    await wrapper.get('[data-test="register-session"]').trigger('click')
    await flushPromises()

    expect(wrapper.text()).toContain('Sesión llena')

    vi.mocked(eventsStore.registerToSession).mockRejectedValueOnce(new Error('Ya está registrado'))

    await wrapper.get('[data-test="register-session"]').trigger('click')
    await flushPromises()

    expect(eventsStore.fetchMySessionRegistrations).toHaveBeenCalledTimes(2)
  })

  it('redirects to login when auth is lost', async () => {
    const { authStore } = mountDetail()

    authStore.logout()
    await Promise.resolve()

    expect(routerPush).toHaveBeenCalledWith('/login')
  })
})
