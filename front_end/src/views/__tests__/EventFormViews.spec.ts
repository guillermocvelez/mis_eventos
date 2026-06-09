import { flushPromises, mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import { activatePinia, authenticate, makeEvent } from '@/__tests__/helpers'
import EventCreateView from '@/views/events/EventCreateView.vue'
import EventEditView from '@/views/events/EventEditView.vue'
import { useEventsStore } from '@/stores/events'
import type { EventDTO } from '@/types/events'

const routerPush = vi.hoisted(() => vi.fn())
const routeState = vi.hoisted(() => ({
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
  date: '2026-07-10T14:00:00.000Z',
  end_date: '2026-07-10T20:00:00.000Z',
  capacity: 20,
  registered_count: 5,
  status: 'draft',
})

type MountFormOptions = {
  detailError?: string
  eventOverride?: EventDTO | null
  isDetailLoading?: boolean
}

function mountForm(
  component: typeof EventCreateView | typeof EventEditView,
  options: MountFormOptions = {},
) {
  const { detailError = '', eventOverride = event, isDetailLoading = false } = options
  const pinia = activatePinia()

  const authStore = authenticate('organizer')
  const eventsStore = useEventsStore()

  eventsStore.selectedEvent = eventOverride
  eventsStore.detailError = detailError
  eventsStore.isDetailLoading = isDetailLoading

  vi.spyOn(eventsStore, 'createEvent').mockResolvedValue(event)
  vi.spyOn(eventsStore, 'fetchEventDetail').mockResolvedValue(undefined)
  vi.spyOn(eventsStore, 'updateEvent').mockResolvedValue({
    ...event,
    name: 'Vue Conf Actualizada',
  })

  const wrapper = mount(component, {
    global: {
      plugins: [pinia],
    },
  })

  return { authStore, eventsStore, wrapper }
}

async function fillCreateForm(wrapper: ReturnType<typeof mount>) {
  await wrapper.get('#event-name').setValue('  Vue Conf  ')
  await wrapper.get('#event-capacity').setValue('25')
  await wrapper.get('#event-start-date').setValue('2099-01-01')
  await wrapper.findAll('input[type="time"]')[0]!.setValue('09:30')
  await wrapper.get('#event-end-date').setValue('2099-01-01')
  await wrapper.findAll('input[type="time"]')[1]!.setValue('12:00')
  await wrapper.get('#event-location').setValue('  Medellin  ')
  await wrapper.get('#event-description').setValue('  Descripcion del evento  ')
}

describe('event form views', () => {
  beforeEach(() => {
    routerPush.mockReset()
  })

  it('validates required create fields before submitting', async () => {
    const { eventsStore, wrapper } = mountForm(EventCreateView)

    await wrapper.get('form').trigger('submit')

    expect(wrapper.text()).toContain('Escribe el nombre del evento.')
    expect(eventsStore.createEvent).not.toHaveBeenCalled()
  })

  it('creates an event and navigates to its detail', async () => {
    const { eventsStore, wrapper } = mountForm(EventCreateView)

    await fillCreateForm(wrapper)
    await wrapper.get('form').trigger('submit')
    await flushPromises()

    expect(eventsStore.createEvent).toHaveBeenCalledWith(
      expect.objectContaining({
        name: 'Vue Conf',
        description: 'Descripcion del evento',
        location: 'Medellin',
        capacity: 25,
      }),
    )
    expect(routerPush).toHaveBeenCalledWith({
      name: 'event-detail',
      params: { eventId: 'event-1' },
    })
  })

  it('redirects non-managers away from create view', async () => {
    const { authStore } = mountForm(EventCreateView)

    authStore.token = authenticate('attendee').token
    await Promise.resolve()

    expect(routerPush).toHaveBeenCalledWith('/eventos')
  })

  it('loads event data in edit view and submits updates', async () => {
    const { eventsStore, wrapper } = mountForm(EventEditView)

    await flushPromises()

    expect(eventsStore.fetchEventDetail).toHaveBeenCalledWith('event-1')
    expect((wrapper.get('#event-name').element as HTMLInputElement).value).toBe('Vue Conf')

    await wrapper.get('#event-name').setValue('Vue Conf Actualizada')
    await wrapper.get('#event-status').setValue('published')
    await wrapper.get('form').trigger('submit')
    await flushPromises()

    expect(eventsStore.updateEvent).toHaveBeenCalledWith(
      'event-1',
      expect.objectContaining({
        name: 'Vue Conf Actualizada',
        status: 'published',
        capacity: 20,
      }),
    )
    expect(routerPush).toHaveBeenCalledWith({
      name: 'event-detail',
      params: { eventId: 'event-1' },
    })
  })

  it('renders edit loading and load error states', async () => {
    const loading = mountForm(EventEditView, {
      eventOverride: null,
      isDetailLoading: true,
    }).wrapper

    expect(loading.text()).toContain('Cargando evento')

    const { eventsStore, wrapper } = mountForm(EventEditView, {
      detailError: 'No existe el evento',
      eventOverride: null,
    })

    expect(wrapper.text()).toContain('No pudimos cargar el evento')
    expect(wrapper.text()).toContain('No existe el evento')

    await wrapper.get('button.btn-secondary').trigger('click')

    expect(eventsStore.fetchEventDetail).toHaveBeenCalledWith('event-1')
  })

  it('validates edit form fields before updating', async () => {
    const { eventsStore, wrapper } = mountForm(EventEditView)

    await flushPromises()
    await wrapper.get('#event-name').setValue('')
    await wrapper.get('#event-capacity').setValue('0')
    await wrapper.get('#event-end-date').setValue('2026-07-09')
    await wrapper.get('form').trigger('submit')

    expect(wrapper.text()).toContain('Escribe el nombre del evento.')
    expect(wrapper.text()).toContain('Define un cupo mayor a cero.')
    expect(wrapper.text()).toContain('La finalización debe ser posterior al inicio.')
    expect(eventsStore.updateEvent).not.toHaveBeenCalled()
  })

  it('shows API errors when edit saving fails', async () => {
    const { eventsStore, wrapper } = mountForm(EventEditView)

    vi.mocked(eventsStore.updateEvent).mockRejectedValueOnce(new Error('No se pudo guardar'))

    await flushPromises()
    await wrapper.get('#event-name').setValue('Vue Conf Fallida')
    await wrapper.get('form').trigger('submit')
    await flushPromises()

    expect(wrapper.text()).toContain('No se pudo guardar')
    expect(routerPush).not.toHaveBeenCalledWith({
      name: 'event-detail',
      params: { eventId: 'event-1' },
    })
  })
})
