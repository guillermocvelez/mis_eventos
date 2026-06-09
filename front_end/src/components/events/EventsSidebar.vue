<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'

import { UiIcon } from '@/components/ui'
import { useAuthStore, type UserRole } from '@/stores/auth'

withDefaults(
  defineProps<{
    eventCount?: number
  }>(),
  {
    eventCount: 0,
  },
)

const authStore = useAuthStore()
const route = useRoute()
const router = useRouter()

const roleLabels: Record<UserRole, string> = {
  admin: 'Administradora',
  attendee: 'Asistente',
  organizer: 'Organizadora',
}

const userRole = computed(() => authStore.userRole || 'attendee')
const roleLabel = computed(() => roleLabels[userRole.value])
const canCreateEvents = computed(() => userRole.value === 'admin' || userRole.value === 'organizer')
const isAdmin = computed(() => userRole.value === 'admin')
const isEventsActive = computed(() => route.name === 'events-home' || route.name === 'event-detail')
const isAdminActive = computed(() => route.name === 'admin-users')
const avatarTone = computed(() => {
  if (userRole.value === 'admin') return 'purple'
  if (userRole.value === 'organizer') return 'blue'

  return 'navy'
})
const displayName = computed(() => {
  if (!authStore.userEmail) return 'Usuario autenticado'

  return (authStore.userEmail.split('@')[0] || authStore.userEmail)
    .split(/[._-]/)
    .filter(Boolean)
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(' ')
})
const initials = computed(() => {
  const source = displayName.value || authStore.userEmail || 'Usuario'
  const parts = source.split(/\s+/).filter(Boolean)

  if (parts.length >= 2) {
    return `${parts[0]?.charAt(0) || ''}${parts[1]?.charAt(0) || ''}`.toUpperCase()
  }

  return source.slice(0, 2).toUpperCase()
})

async function logout() {
  authStore.logout()
  await router.push('/login')
}
</script>

<template>
  <aside class="events-sidebar" :class="`role-${userRole}`">
    <div class="events-brand">
      <span class="brand-mark">
        <UiIcon name="ticket" :size="20" />
      </span>
      <div>
        <strong>Mis Eventos</strong>
        <span>Gestión inteligente</span>
      </div>
    </div>

    <div class="events-nav-group">
      <p class="events-nav-label">Principal</p>
      <nav class="events-nav" aria-label="Principal">
        <RouterLink :class="{ active: isEventsActive }" to="/eventos">
          <UiIcon name="home" />
          <span>Eventos</span>
          <span v-if="eventCount > 0" class="events-nav-badge">{{ eventCount }}</span>
        </RouterLink>

        <button v-if="canCreateEvents" aria-disabled="true" class="events-nav-item" type="button">
          <UiIcon name="circle-plus" />
          <span>Crear evento</span>
        </button>

        <button aria-disabled="true" class="events-nav-item" type="button">
          <UiIcon name="user" />
          <span>Mi perfil</span>
        </button>
      </nav>
    </div>

    <div v-if="isAdmin" class="events-nav-group">
      <p class="events-nav-label">Administración</p>
      <nav class="events-nav" aria-label="Administración">
        <RouterLink :class="{ active: isAdminActive }" class="admin" to="/admin">
          <UiIcon name="shield" />
          <span>Admin</span>
        </RouterLink>
      </nav>
    </div>

    <div class="events-user-card">
      <span class="events-avatar" :class="`avatar-${avatarTone}`">{{ initials }}</span>
      <div>
        <strong>{{ displayName }}</strong>
        <span>{{ roleLabel }}</span>
      </div>
      <button aria-label="Cerrar sesión" class="icon-btn" type="button" @click="logout">
        <UiIcon name="log-out" />
      </button>
    </div>
  </aside>
</template>
