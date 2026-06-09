import { beforeEach, describe, expect, it, vi } from 'vitest'

import { activatePinia, jsonResponse, makeUser } from '@/__tests__/helpers'
import { createUser, deleteUser, fetchUserById, fetchUsers, updateUser } from '../usersApi'
import { useAuthStore } from '@/stores/auth'

const user = makeUser()

describe('usersApi', () => {
  beforeEach(() => {
    activatePinia()
    const authStore = useAuthStore()
    authStore.token = 'token'
    authStore.tokenType = 'Bearer'
    vi.restoreAllMocks()
  })

  it('fetches users with optional filters', async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      jsonResponse({
        items: [user],
        limit: 10,
        page: 1,
        pages: 1,
        total: 1,
      }),
    )

    vi.stubGlobal('fetch', fetchMock)

    await fetchUsers({
      is_active: false,
      limit: 10,
      page: 1,
      role: 'admin',
      search: ' ana ',
    })

    expect(fetchMock).toHaveBeenCalledWith(
      'http://localhost:8000/users/?limit=10&page=1&search=ana&role=admin&is_active=false',
      expect.objectContaining({
        headers: expect.objectContaining({
          Authorization: 'Bearer token',
        }),
      }),
    )
  })

  it('creates users with JSON payloads', async () => {
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse(user))

    vi.stubGlobal('fetch', fetchMock)

    await createUser({
      email: user.email,
      is_active: true,
      name: user.name,
      password: 'secret',
      role: 'admin',
    })

    expect(fetchMock).toHaveBeenCalledWith(
      'http://localhost:8000/users/',
      expect.objectContaining({
        body: JSON.stringify({
          email: user.email,
          is_active: true,
          name: user.name,
          password: 'secret',
          role: 'admin',
        }),
        headers: expect.objectContaining({
          Authorization: 'Bearer token',
          'Content-Type': 'application/json',
        }),
        method: 'POST',
      }),
    )
  })

  it('fetches a user by id', async () => {
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse(user))

    vi.stubGlobal('fetch', fetchMock)

    await expect(fetchUserById('user-1')).resolves.toEqual(user)

    expect(fetchMock).toHaveBeenCalledWith(
      'http://localhost:8000/users/user-1',
      expect.objectContaining({
        headers: expect.objectContaining({
          Authorization: 'Bearer token',
        }),
      }),
    )
  })

  it('updates and deletes users with the expected endpoints', async () => {
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse(user))

    vi.stubGlobal('fetch', fetchMock)

    await updateUser('user-1', { is_active: false, role: 'attendee' })
    await deleteUser('user-1')

    expect(fetchMock).toHaveBeenNthCalledWith(
      1,
      'http://localhost:8000/users/user-1',
      expect.objectContaining({
        body: JSON.stringify({ is_active: false, role: 'attendee' }),
        method: 'PATCH',
      }),
    )
    expect(fetchMock).toHaveBeenNthCalledWith(
      2,
      'http://localhost:8000/users/user-1',
      expect.objectContaining({
        method: 'DELETE',
      }),
    )
  })

  it('throws fallback messages when error bodies are unreadable', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue(
        new Response('not-json', {
          status: 500,
        }),
      ),
    )

    await expect(fetchUsers({ limit: 10, page: 1 })).rejects.toThrow(
      'No pudimos procesar la solicitud de usuarios. Inténtalo de nuevo.',
    )
  })

  it('throws readable detail messages from API errors', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue(jsonResponse({ detail: 'El correo ya existe.' }, { status: 409 })),
    )

    await expect(createUser({
      email: user.email,
      is_active: true,
      name: user.name,
      password: 'secret',
      role: 'admin',
    })).rejects.toThrow('El correo ya existe.')
  })

  it('logs out on unauthorized responses', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue(jsonResponse({ detail: 'Sesión vencida.' }, { status: 401 })),
    )

    const authStore = useAuthStore()

    await expect(fetchUserById('user-1')).rejects.toThrow('Sesión vencida.')

    expect(authStore.token).toBe('')
    expect(authStore.authorizationHeader).toBe('')
  })
})
