import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import AuthShell from '../AuthShell.vue'

describe('AuthShell', () => {
  it('marks the active auth mode and renders content', () => {
    const wrapper = mount(AuthShell, {
      props: {
        mode: 'register',
      },
      slots: {
        default: '<form>Contenido</form>',
      },
      global: {
        stubs: {
          RouterLink: { props: ['to'], template: '<a :href="to"><slot /></a>' },
        },
      },
    })

    const links = wrapper.findAll('.segment-option')

    expect(wrapper.text()).toContain('Mis Eventos')
    expect(wrapper.text()).toContain('Contenido')
    expect(links[0]!.classes()).not.toContain('on')
    expect(links[1]!.classes()).toContain('on')
  })
})

