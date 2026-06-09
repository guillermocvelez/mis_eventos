import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import UiTextInput from '../UiTextInput.vue'

describe('UiTextInput', () => {
  it('renders input attributes and emits typed values', async () => {
    const wrapper = mount(UiTextInput, {
      props: {
        id: 'email',
        invalid: true,
        min: '2026-01-01',
        modelValue: 'ana@example.com',
        placeholder: 'correo',
        type: 'email',
      },
    })

    const input = wrapper.get('input')

    expect(input.attributes('id')).toBe('email')
    expect(input.attributes('aria-invalid')).toBe('true')
    expect(input.attributes('min')).toBe('2026-01-01')

    await input.setValue('lu@example.com')

    expect(wrapper.emitted('update:modelValue')).toEqual([['lu@example.com']])
  })

  it('passes the disabled state to the input', () => {
    const wrapper = mount(UiTextInput, {
      props: {
        disabled: true,
      },
    })

    expect(wrapper.get('input').attributes('disabled')).toBeDefined()
  })
})
