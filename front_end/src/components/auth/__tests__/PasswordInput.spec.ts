import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import PasswordInput from '../PasswordInput.vue'

describe('PasswordInput', () => {
  it('emits password changes and toggles visibility', async () => {
    const wrapper = mount(PasswordInput, {
      props: {
        id: 'password',
        modelValue: '',
      },
    })

    expect(wrapper.get('input').attributes('type')).toBe('password')

    await wrapper.get('input').setValue('supersecret')
    await wrapper.get('button').trigger('click')

    expect(wrapper.emitted('update:modelValue')).toEqual([['supersecret']])
    expect(wrapper.get('input').attributes('type')).toBe('text')
    expect(wrapper.get('button').attributes('aria-label')).toBe('Ocultar contraseña')
  })
})

