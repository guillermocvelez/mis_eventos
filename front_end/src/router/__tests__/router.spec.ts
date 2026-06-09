import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it } from 'vitest'

import router from '@/router'
import { useAuthStore } from '@/stores/auth'

function createToken(payload: Record<string, unknown>) {
  return `header.${btoa(JSON.stringify(payload)).replace(/=+$/, '')}.signature`
}

async function navigate(path: string) {
  await router.push(path)
  await router.isReady()
  return router.currentRoute.value
}

describe('router guards', () => {
  beforeEach(async () => {
    setActivePinia(createPinia())
    localStorage.clear()
    await navigate('/login')
  })

  it('redirects unauthenticated users to login with redirect query', async () => {
    const route = await navigate('/eventos/crear')

    expect(route.path).toBe('/login')
    expect(route.query.redirect).toBe('/eventos/crear')
  })

  it('prevents authenticated guests from opening auth pages', async () => {
    const authStore = useAuthStore()

    authStore.token = createToken({
      role: 'attendee',
      sub: 'ana@example.com',
    })

    const route = await navigate('/registro')

    expect(route.path).toBe('/eventos')
  })

  it('blocks event management routes for attendees', async () => {
    const authStore = useAuthStore()

    authStore.token = createToken({
      role: 'attendee',
      sub: 'ana@example.com',
    })

    const route = await navigate('/eventos/crear')

    expect(route.path).toBe('/eventos')
  })

  it('allows organizers to access event management routes', async () => {
    const authStore = useAuthStore()

    authStore.token = createToken({
      role: 'organizer',
      sub: 'org@example.com',
    })

    const route = await navigate('/eventos/crear')

    expect(route.name).toBe('event-create')
  })

  it('blocks admin routes for organizers', async () => {
    const authStore = useAuthStore()

    authStore.token = createToken({
      role: 'organizer',
      sub: 'org@example.com',
    })

    const route = await navigate('/admin')

    expect(route.path).toBe('/eventos')
  })

  it('logs out expired tokens before navigating', async () => {
    const authStore = useAuthStore()

    authStore.token = createToken({
      exp: Math.floor(Date.now() / 1000) - 60,
      role: 'admin',
      sub: 'admin@example.com',
    })

    const route = await navigate('/admin')

    expect(route.path).toBe('/login')
    expect(authStore.token).toBe('')
  })
})
