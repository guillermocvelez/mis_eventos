import { beforeEach, describe, expect, it, vi } from 'vitest'

import { activatePinia, createAuthToken, jsonResponse } from '@/__tests__/helpers'
import { useAuthStore } from '../auth'

describe('auth store', () => {
  beforeEach(() => {
    activatePinia()
    localStorage.clear()
    vi.restoreAllMocks()
  })

  it('hydrates stored tokens and exposes decoded user claims', () => {
    const token = createAuthToken({
      exp: Math.floor(Date.now() / 1000) + 60,
      role: 'admin',
      sub: 'ana@example.com',
    })

    localStorage.setItem('mis_eventos.auth.token', token)
    localStorage.setItem('mis_eventos.auth.token_type', 'Bearer')

    const store = useAuthStore()

    expect(store.isAuthenticated).toBe(true)
    expect(store.userEmail).toBe('ana@example.com')
    expect(store.userRole).toBe('admin')
    expect(store.canAdminister).toBe(true)
    expect(store.canManageEvents).toBe(true)
    expect(store.authorizationHeader).toBe(`Bearer ${token}`)
  })

  it('treats expired tokens as unauthenticated', () => {
    localStorage.setItem(
      'mis_eventos.auth.token',
      createAuthToken({
        exp: Math.floor(Date.now() / 1000) - 60,
        role: 'attendee',
        sub: 'lu@example.com',
      }),
    )

    const store = useAuthStore()

    expect(store.isTokenExpired).toBe(true)
    expect(store.isAuthenticated).toBe(false)
  })

  it('logs in with form credentials and persists the token', async () => {
    const token = createAuthToken({
      exp: Math.floor(Date.now() / 1000) + 60,
      role: 'organizer',
      sub: 'org@example.com',
    })
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse({ access_token: token, token_type: 'Bearer' }))

    vi.stubGlobal('fetch', fetchMock)

    const store = useAuthStore()

    await store.login({ email: 'org@example.com', password: 'secret' })

    const [, init] = fetchMock.mock.calls[0]!
    const body = init.body as URLSearchParams

    expect(fetchMock).toHaveBeenCalledWith(
      'http://localhost:8000/auth/login',
      expect.objectContaining({
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        method: 'POST',
      }),
    )
    expect(body.get('username')).toBe('org@example.com')
    expect(body.get('password')).toBe('secret')
    expect(store.token).toBe(token)
    expect(store.userRole).toBe('organizer')
    expect(localStorage.getItem('mis_eventos.auth.token')).toBe(token)
  })

  it('registers with JSON credentials', async () => {
    const token = createAuthToken({ role: 'attendee', sub: 'new@example.com' })
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse({ access_token: token, token_type: '' }))

    vi.stubGlobal('fetch', fetchMock)

    const store = useAuthStore()

    await store.register({
      email: 'new@example.com',
      name: 'New User',
      password: 'secret',
    })

    expect(fetchMock).toHaveBeenCalledWith(
      'http://localhost:8000/auth/register',
      expect.objectContaining({
        body: JSON.stringify({
          email: 'new@example.com',
          name: 'New User',
          password: 'secret',
        }),
        headers: { 'Content-Type': 'application/json' },
        method: 'POST',
      }),
    )
    expect(store.tokenType).toBe('bearer')
  })

  it('stores API error messages after failed login', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue(jsonResponse({ detail: 'Credenciales inválidas.' }, { status: 400 })),
    )

    const store = useAuthStore()

    await expect(store.login({ email: 'bad@example.com', password: 'bad' })).rejects.toThrow(
      'Credenciales inválidas.',
    )

    expect(store.error).toBe('Credenciales inválidas.')
    expect(store.isLoading).toBe(false)
  })

  it('logs out and clears persisted auth data', () => {
    localStorage.setItem('mis_eventos.auth.token', 'token')
    localStorage.setItem('mis_eventos.auth.token_type', 'Bearer')

    const store = useAuthStore()

    store.logout()

    expect(store.token).toBe('')
    expect(store.tokenType).toBe('bearer')
    expect(store.authorizationHeader).toBe('')
    expect(localStorage.getItem('mis_eventos.auth.token')).toBeNull()
    expect(localStorage.getItem('mis_eventos.auth.token_type')).toBeNull()
  })
})
