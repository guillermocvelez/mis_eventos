import { mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import { activatePinia, authenticate } from '@/__tests__/helpers'
import EventsSidebar from '../EventsSidebar.vue'
import type { UserRole } from '@/stores/auth'

const routerPush = vi.hoisted(() => vi.fn())
const routeState = vi.hoisted(() => ({
  name: 'events-home' as string,
}))

vi.mock('vue-router', () => ({
  RouterLink: {
    props: ['to'],
    template: '<a :href="typeof to === \'string\' ? to : to.path"><slot /></a>',
  },
  useRoute: () => routeState,
  useRouter: () => ({
    push: routerPush,
  }),
}))

function mountSidebar(role: UserRole = 'attendee') {
  const pinia = activatePinia()
  const authStore = authenticate(role, 'ana.gomez@example.com')

  const wrapper = mount(EventsSidebar, {
    props: {
      eventCount: 4,
    },
    global: {
      plugins: [pinia],
    },
  })

  return { authStore, wrapper }
}

describe('EventsSidebar', () => {
  beforeEach(() => {
    routerPush.mockReset()
    routeState.name = 'events-home'
  })

  it('renders user identity, role and event count', () => {
    const { wrapper } = mountSidebar('organizer')

    expect(wrapper.text()).toContain('Ana Gomez')
    expect(wrapper.text()).toContain('Organizadora')
    expect(wrapper.text()).toContain('4')
    expect(wrapper.find('a[href="/eventos"]').classes()).toContain('active')
  })

  it('shows admin navigation only for admins', () => {
    const attendee = mountSidebar('attendee').wrapper
    const admin = mountSidebar('admin').wrapper

    expect(attendee.text()).not.toContain('Admin')
    expect(admin.text()).toContain('Admin')
  })

  it('logs out and redirects to login', async () => {
    const { authStore, wrapper } = mountSidebar('admin')

    await wrapper.get('button[aria-label="Cerrar sesión"]').trigger('click')

    expect(authStore.token).toBe('')
    expect(routerPush).toHaveBeenCalledWith('/login')
  })
})
