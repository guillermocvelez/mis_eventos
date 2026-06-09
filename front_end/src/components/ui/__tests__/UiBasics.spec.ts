import { mount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

import UiBadge from '../UiBadge.vue'
import UiButton from '../UiButton.vue'
import UiField from '../UiField.vue'
import UiModal from '../UiModal.vue'
import UiToast from '../UiToast.vue'

describe('basic UI components', () => {
  it('applies button and badge variants', () => {
    const button = mount(UiButton, {
      props: {
        block: true,
        size: 'lg',
        variant: 'danger',
      },
      slots: {
        default: 'Eliminar',
      },
    })
    const badge = mount(UiBadge, {
      props: {
        variant: 'success',
      },
      slots: {
        default: 'Publicado',
      },
    })

    expect(button.classes()).toEqual(expect.arrayContaining(['btn-danger', 'btn-lg', 'btn-block']))
    expect(badge.classes()).toContain('badge-success')
  })

  it('renders field errors before hints', () => {
    const wrapper = mount(UiField, {
      props: {
        error: 'Campo obligatorio',
        forId: 'email',
        hint: 'Usa tu correo',
        label: 'Correo',
      },
      slots: {
        default: '<input id="email" />',
      },
    })

    expect(wrapper.get('label').attributes('for')).toBe('email')
    expect(wrapper.text()).toContain('Campo obligatorio')
    expect(wrapper.text()).not.toContain('Usa tu correo')
  })

  it('renders modal content only when open', () => {
    const closed = mount(UiModal, {
      props: {
        open: false,
      },
      slots: {
        default: 'Contenido',
      },
    })
    const open = mount(UiModal, {
      props: {
        open: true,
      },
      slots: {
        default: 'Contenido',
      },
    })

    expect(closed.text()).toBe('')
    expect(open.get('[role="dialog"]').text()).toBe('Contenido')
  })

  it('emits toast close manually and after the duration', async () => {
    vi.useFakeTimers()

    const wrapper = mount(UiToast, {
      props: {
        duration: 1000,
        message: 'Guardado',
        open: true,
        variant: 'success',
      },
    })

    expect(wrapper.get('[role="status"]').text()).toContain('Guardado')

    await wrapper.get('button').trigger('click')
    expect(wrapper.emitted('close')).toHaveLength(1)

    vi.advanceTimersByTime(1000)
    expect(wrapper.emitted('close')).toHaveLength(2)

    vi.useRealTimers()
  })
})
