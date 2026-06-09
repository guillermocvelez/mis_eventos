import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import { makeEvent, makeSession, makeSpeaker } from '@/__tests__/helpers'
import EventSessionModal from '../EventSessionModal.vue'

const event = makeEvent({
  date: '2026-07-10T14:00:00.000Z',
  capacity: 20,
  registered_count: 4,
})
const speaker = makeSpeaker()
const existingSession = makeSession({
  title: 'Keynote',
  speaker,
  start_time: '2026-07-10T15:00:00.000Z',
  end_time: '2026-07-10T16:00:00.000Z',
  capacity: 10,
  registered_count: 2,
})

function mountModal(props: Partial<InstanceType<typeof EventSessionModal>['$props']> = {}) {
  return mount(EventSessionModal, {
    props: {
      event,
      open: false,
      sessions: [],
      speakers: [speaker],
      ...props,
    },
  })
}

async function fillSessionForm(wrapper: ReturnType<typeof mountModal>) {
  await wrapper.get('#session-title').setValue('  Taller de pruebas  ')
  await wrapper.get('#session-speaker').setValue('speaker-1')
  await wrapper.get('#session-start-date').setValue('2099-01-01')
  await wrapper.findAll('input[type="time"]')[0]!.setValue('09:00')
  await wrapper.get('#session-end-date').setValue('2099-01-01')
  await wrapper.findAll('input[type="time"]')[1]!.setValue('10:00')
  await wrapper.get('#session-capacity').setValue('30')
}

describe('EventSessionModal', () => {
  it('validates required fields before saving', async () => {
    const wrapper = mountModal()

    await wrapper.setProps({ open: true })
    await wrapper.get('form').trigger('submit')

    expect(wrapper.text()).toContain('Escribe el título de la sesión.')
    expect(wrapper.text()).toContain('Selecciona la fecha y hora de finalización.')
    expect(wrapper.emitted('save')).toBeUndefined()
  })

  it('emits a normalized session payload', async () => {
    const wrapper = mountModal()

    await wrapper.setProps({ open: true })
    await fillSessionForm(wrapper)
    await wrapper.get('form').trigger('submit')

    expect(wrapper.emitted('save')?.[0]?.[0]).toEqual(
      expect.objectContaining({
        title: 'Taller de pruebas',
        speaker_id: 'speaker-1',
        capacity: 30,
      }),
    )
  })

  it('blocks sessions that overlap existing sessions', async () => {
    const wrapper = mountModal({
      sessions: [existingSession],
    })

    await wrapper.setProps({ open: true })
    await wrapper.get('#session-title').setValue('Solapada')
    await wrapper.get('#session-start-date').setValue('2026-07-10')
    await wrapper.findAll('input[type="time"]')[0]!.setValue('10:30')
    await wrapper.get('#session-end-date').setValue('2026-07-10')
    await wrapper.findAll('input[type="time"]')[1]!.setValue('11:30')
    await wrapper.get('form').trigger('submit')

    expect(wrapper.text()).toContain('Este horario se solapa con otra sesión existente.')
    expect(wrapper.emitted('save')).toBeUndefined()
  })

  it('loads edit values and exposes submit errors', async () => {
    const wrapper = mountModal({
      session: existingSession,
    })

    await wrapper.setProps({ open: true })

    expect((wrapper.get('#session-title').element as HTMLInputElement).value).toBe('Keynote')
    expect((wrapper.get('#session-speaker').element as HTMLSelectElement).value).toBe('speaker-1')

    wrapper.vm.setSubmitError('No pudimos guardar.')
    await wrapper.vm.$nextTick()

    expect(wrapper.text()).toContain('No pudimos guardar.')
  })
})
