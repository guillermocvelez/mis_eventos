import { useAuthStore } from '@/stores/auth'
import type {
  FetchUsersOptions,
  PaginatedUsersDTO,
  UserCreatePayload,
  UserDTO,
  UserUpdatePayload,
} from '@/types/users'

const DEFAULT_API_BASE_URL = 'http://localhost:8000'

function getApiBaseUrl() {
  return (import.meta.env.VITE_API_BASE_URL || DEFAULT_API_BASE_URL).replace(/\/$/, '')
}

async function readErrorMessage(response: Response) {
  const fallback = 'No pudimos procesar la solicitud de usuarios. Inténtalo de nuevo.'

  try {
    const data: unknown = await response.json()

    if (data && typeof data === 'object' && 'detail' in data) {
      const detail = (data as { detail: unknown }).detail
      if (typeof detail === 'string') return detail
    }
  } catch {
    return fallback
  }

  return fallback
}

async function fetchWithAuth(path: string, init: RequestInit = {}) {
  const authStore = useAuthStore()
  const response = await fetch(`${getApiBaseUrl()}${path}`, {
    ...init,
    headers: {
      Authorization: authStore.authorizationHeader,
      ...init.headers,
    },
  })

  if (response.status === 401) {
    authStore.logout()
  }

  if (!response.ok) {
    throw new Error(await readErrorMessage(response))
  }

  return response
}

export async function fetchUsers(
  options: Required<Pick<FetchUsersOptions, 'limit' | 'page'>> & FetchUsersOptions,
) {
  const params = new URLSearchParams({
    limit: String(options.limit),
    page: String(options.page),
  })

  if (options.search?.trim()) {
    params.set('search', options.search.trim())
  }

  if (options.role) {
    params.set('role', options.role)
  }

  if (options.is_active !== undefined) {
    params.set('is_active', String(options.is_active))
  }

  const response = await fetchWithAuth(`/users/?${params.toString()}`)
  return (await response.json()) as PaginatedUsersDTO
}

export async function fetchUserById(userId: string) {
  const response = await fetchWithAuth(`/users/${userId}`)
  return (await response.json()) as UserDTO
}

export async function createUser(payload: UserCreatePayload) {
  const response = await fetchWithAuth('/users/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  })

  return (await response.json()) as UserDTO
}

export async function updateUser(userId: string, payload: UserUpdatePayload) {
  const response = await fetchWithAuth(`/users/${userId}`, {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  })

  return (await response.json()) as UserDTO
}

export async function deleteUser(userId: string) {
  await fetchWithAuth(`/users/${userId}`, {
    method: 'DELETE',
  })
}
