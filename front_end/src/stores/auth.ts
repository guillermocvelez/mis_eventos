import { computed, ref } from 'vue'
import { defineStore } from 'pinia'

const TOKEN_STORAGE_KEY = 'mis_eventos.auth.token'
const TOKEN_TYPE_STORAGE_KEY = 'mis_eventos.auth.token_type'
const DEFAULT_API_BASE_URL = 'http://localhost:8000'

export type UserRole = 'admin' | 'organizer' | 'attendee'

type TokenResponse = {
  access_token: string
  token_type: string
}

type LoginCredentials = {
  email: string
  password: string
}

type RegisterCredentials = {
  name: string
  email: string
  password: string
}

type TokenPayload = {
  exp?: number
  role?: string
  sub?: string
}

function getApiBaseUrl() {
  return (import.meta.env.VITE_API_BASE_URL || DEFAULT_API_BASE_URL).replace(/\/$/, '')
}

function getStoredValue(key: string) {
  if (typeof localStorage === 'undefined') return ''
  return localStorage.getItem(key) || ''
}

function setStoredValue(key: string, value: string) {
  if (typeof localStorage === 'undefined') return
  localStorage.setItem(key, value)
}

function removeStoredValue(key: string) {
  if (typeof localStorage === 'undefined') return
  localStorage.removeItem(key)
}

async function readErrorMessage(response: Response) {
  const fallback = 'No pudimos iniciar sesión. Revisa tus datos e inténtalo de nuevo.'

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

function decodeTokenPayload(accessToken: string): TokenPayload {
  if (!accessToken) return {}

  try {
    const payload = accessToken.split('.')[1]
    if (!payload) return {}

    const normalizedPayload = payload.replace(/-/g, '+').replace(/_/g, '/')
    const paddedPayload = normalizedPayload.padEnd(
      normalizedPayload.length + ((4 - (normalizedPayload.length % 4)) % 4),
      '=',
    )
    const decodedPayload = globalThis.atob(paddedPayload)

    return JSON.parse(decodedPayload) as TokenPayload
  } catch {
    return {}
  }
}

function isUserRole(role: string | undefined): role is UserRole {
  return role === 'admin' || role === 'organizer' || role === 'attendee'
}

export const useAuthStore = defineStore('auth', () => {
  const token = ref(getStoredValue(TOKEN_STORAGE_KEY))
  const tokenType = ref(getStoredValue(TOKEN_TYPE_STORAGE_KEY) || 'bearer')
  const isLoading = ref(false)
  const error = ref('')

  const tokenPayload = computed(() => decodeTokenPayload(token.value))
  const isTokenExpired = computed(() => {
    if (!tokenPayload.value.exp) return false
    return tokenPayload.value.exp * 1000 <= Date.now()
  })
  const isAuthenticated = computed(() => Boolean(token.value) && !isTokenExpired.value)
  const userEmail = computed(() => tokenPayload.value.sub || '')
  const userRole = computed<UserRole | null>(() => {
    return isUserRole(tokenPayload.value.role) ? tokenPayload.value.role : null
  })
  const canManageEvents = computed(() => {
    return userRole.value === 'admin' || userRole.value === 'organizer'
  })
  const canAdminister = computed(() => userRole.value === 'admin')
  const authorizationHeader = computed(() => {
    if (!token.value) return ''
    return `${tokenType.value} ${token.value}`
  })

  async function login(credentials: LoginCredentials) {
    isLoading.value = true
    error.value = ''

    const body = new URLSearchParams()
    body.set('username', credentials.email)
    body.set('password', credentials.password)

    try {
      const response = await fetch(`${getApiBaseUrl()}/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body,
      })

      if (!response.ok) {
        throw new Error(await readErrorMessage(response))
      }

      const data = (await response.json()) as TokenResponse

      token.value = data.access_token
      tokenType.value = data.token_type || 'bearer'
      setStoredValue(TOKEN_STORAGE_KEY, token.value)
      setStoredValue(TOKEN_TYPE_STORAGE_KEY, tokenType.value)
    } catch (caughtError) {
      const message = caughtError instanceof Error ? caughtError.message : ''
      error.value = message || 'No pudimos iniciar sesión. Revisa tus datos e inténtalo de nuevo.'
      throw caughtError
    } finally {
      isLoading.value = false
    }
  }

  async function register(credentials: RegisterCredentials) {
    isLoading.value = true
    error.value = ''

    try {
      const response = await fetch(`${getApiBaseUrl()}/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(credentials),
      })

      if (!response.ok) {
        throw new Error(await readErrorMessage(response))
      }

      const data = (await response.json()) as TokenResponse

      token.value = data.access_token
      tokenType.value = data.token_type || 'bearer'
      setStoredValue(TOKEN_STORAGE_KEY, token.value)
      setStoredValue(TOKEN_TYPE_STORAGE_KEY, tokenType.value)
    } catch (caughtError) {
      const message = caughtError instanceof Error ? caughtError.message : ''
      error.value = message || 'No pudimos crear la cuenta. Revisa tus datos e inténtalo de nuevo.'
      throw caughtError
    } finally {
      isLoading.value = false
    }
  }

  function logout() {
    token.value = ''
    tokenType.value = 'bearer'
    error.value = ''
    removeStoredValue(TOKEN_STORAGE_KEY)
    removeStoredValue(TOKEN_TYPE_STORAGE_KEY)
  }

  return {
    authorizationHeader,
    canAdminister,
    canManageEvents,
    error,
    isAuthenticated,
    isTokenExpired,
    isLoading,
    login,
    logout,
    register,
    token,
    userEmail,
    userRole,
    tokenType,
  }
})
