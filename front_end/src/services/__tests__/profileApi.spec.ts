import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import { fetchMyProfile } from '../profileApi'
import { useAuthStore } from '@/stores/auth'
import type { UserProfileDTO } from '@/types/profile'

function jsonResponse(body: unknown, init: ResponseInit = {}) {
  return new Response(JSON.stringify(body), {
    headers: { 'Content-Type': 'application/json' },
    status: 200,
    ...init,
  })
}

const profile: UserProfileDTO = {
  id: 'user-1',
  email: 'ana@example.com',
  name: 'Ana Gomez',
  role: 'admin',
  created_at: '2026-01-01T00:00:00Z',
  is_active: true,
  organized_count: 3,
  registered_count: 5,
}

describe('profileApi', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    const authStore = useAuthStore()
    authStore.token = 'token'
    authStore.tokenType = 'Bearer'
    vi.restoreAllMocks()
  })

  it('fetches the current profile with auth headers', async () => {
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse(profile))

    vi.stubGlobal('fetch', fetchMock)

    await expect(fetchMyProfile()).resolves.toEqual(profile)

    expect(fetchMock).toHaveBeenCalledWith(
      'http://localhost:8000/users/me',
      expect.objectContaining({
        headers: expect.objectContaining({
          Authorization: 'Bearer token',
        }),
      }),
    )
  })

  it('logs out and throws detail messages on 401 responses', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue(jsonResponse({ detail: 'Sesión vencida.' }, { status: 401 })),
    )

    const authStore = useAuthStore()

    await expect(fetchMyProfile()).rejects.toThrow('Sesión vencida.')

    expect(authStore.token).toBe('')
  })
})
