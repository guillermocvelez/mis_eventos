import { createPinia, setActivePinia } from 'pinia'
import { mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import LoginView from '@/views/auth/LoginView.vue'
import RegisterView from '@/views/auth/RegisterView.vue'
import { useAuthStore } from '@/stores/auth'

const routerPush = vi.hoisted(() => vi.fn())
const routeState = vi.hoisted(() => ({
  query: {} as Record<string, string>,
}))

vi.mock('vue-router', () => ({
  RouterLink: { props: ['to'], template: '<a><slot /></a>' },
  useRoute: () => routeState,
  useRouter: () => ({
    push: routerPush,
  }),
}))

function mountWithAuth(component: typeof LoginView | typeof RegisterView) {
  const pinia = createPinia()
  setActivePinia(pinia)
  const authStore = useAuthStore()

  const wrapper = mount(component, {
    global: {
      plugins: [pinia],
      stubs: {
        AuthShell: { template: '<section><slot /><slot name="footer" /></section>' },
      },
    },
  })

  return { authStore, wrapper }
}

describe('auth views', () => {
  beforeEach(() => {
    routeState.query = {}
    routerPush.mockReset()
    localStorage.clear()
  })

  it('validates login before calling the store', async () => {
    const { authStore, wrapper } = mountWithAuth(LoginView)
    const login = vi.spyOn(authStore, 'login').mockResolvedValue(undefined)

    await wrapper.get('form').trigger('submit')

    expect(wrapper.text()).toContain('Introduce un correo electrónico válido.')
    expect(wrapper.text()).toContain('La contraseña debe tener al menos 8 caracteres.')
    expect(login).not.toHaveBeenCalled()
  })

  it('logs in and redirects to the requested page', async () => {
    routeState.query = { redirect: '/perfil' }
    const { authStore, wrapper } = mountWithAuth(LoginView)

    vi.spyOn(authStore, 'login').mockResolvedValue(undefined)

    await wrapper.get('#email').setValue('ana@example.com')
    await wrapper.get('#password').setValue('supersecret')
    await wrapper.get('form').trigger('submit')

    expect(authStore.login).toHaveBeenCalledWith({
      email: 'ana@example.com',
      password: 'supersecret',
    })
    expect(routerPush).toHaveBeenCalledWith('/perfil')
  })

  it('validates register fields before calling the store', async () => {
    const { authStore, wrapper } = mountWithAuth(RegisterView)
    const register = vi.spyOn(authStore, 'register').mockResolvedValue(undefined)

    await wrapper.get('form').trigger('submit')

    expect(wrapper.text()).toContain('Escribe tu nombre completo.')
    expect(wrapper.text()).toContain('Introduce un correo electrónico válido.')
    expect(register).not.toHaveBeenCalled()
  })

  it('registers with trimmed data and navigates to events', async () => {
    const { authStore, wrapper } = mountWithAuth(RegisterView)

    vi.spyOn(authStore, 'register').mockResolvedValue(undefined)

    await wrapper.get('#name').setValue('  Ana Gomez  ')
    await wrapper.get('#email').setValue('  ana@example.com  ')
    await wrapper.get('#password').setValue('supersecret')
    await wrapper.get('form').trigger('submit')

    expect(authStore.register).toHaveBeenCalledWith({
      name: 'Ana Gomez',
      email: 'ana@example.com',
      password: 'supersecret',
    })
    expect(routerPush).toHaveBeenCalledWith('/eventos')
  })
})

