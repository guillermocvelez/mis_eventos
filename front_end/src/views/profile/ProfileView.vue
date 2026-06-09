<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { UiBadge, UiButton, UiIcon, UiToast } from '@/components/ui'
import { fetchMyRegistrations } from '@/services/eventsApi'
import { fetchMyProfile } from '@/services/profileApi'
import type { EventDTO, EventStatus } from '@/types/events'
import type { UserProfileDTO } from '@/types/profile'
import type { UserRole } from '@/types/users'

type ProfileState = {
  name: string
  email: string
  role: UserRole
  memberSince: string
  organizedCount: number
  registeredCount: number
}

type RegistrationItem = {
  id: string
  title: string
  dateLabel: string
  location: string
  capacityCurrent: number
  capacityTotal: number
  progress: number
  state: EventStatus
  stateLabel: string
}

const route = useRoute()
const router = useRouter()

const isEmptyState = computed(() => route.name === 'profile-empty')

const fallbackProfile: ProfileState = {
  name: 'Laura Giménez',
  email: 'laura.gimenez@empresa.es',
  role: 'organizer',
  memberSince: '2024',
  organizedCount: 12,
  registeredCount: 8,
}

const fallbackRegistrations: RegistrationItem[] = [
  {
    id: 'summit-innovacion-2025',
    title: 'Summit de Innovación 2025',
    dateLabel: '12 mar 2025 · 09:00',
    location: 'IFEMA, Madrid',
    capacityCurrent: 420,
    capacityTotal: 500,
    progress: 84,
    state: 'published',
    stateLabel: 'Publicado',
  },
  {
    id: 'vue-avanzado',
    title: 'Taller de Vue.js Avanzado',
    dateLabel: '18 mar 2025 · 17:00',
    location: 'Online',
    capacityCurrent: 92,
    capacityTotal: 100,
    progress: 92,
    state: 'published',
    stateLabel: 'Publicado',
  },
  {
    id: 'salud-digital',
    title: 'Conferencia de Salud Digital',
    dateLabel: '02 abr 2025 · 10:00',
    location: 'CCIB, Barcelona',
    capacityCurrent: 180,
    capacityTotal: 300,
    progress: 60,
    state: 'published',
    stateLabel: 'Publicado',
  },
]

const profile = ref<ProfileState>(fallbackProfile)
const registrations = ref<RegistrationItem[]>(fallbackRegistrations)

const toast = reactive({
  message: '',
  open: false,
  variant: 'info' as 'danger' | 'info' | 'success',
})

const userRoleLabel = computed(() => roleBadgeLabels[profile.value.role])
const roleLineLabel = computed(() => roleLineLabels[profile.value.role])
const profileSince = computed(() => profile.value.memberSince)
const userName = computed(() => profile.value.name)
const userEmail = computed(() => profile.value.email)
const organizedCount = computed(() => profile.value.organizedCount)
const registeredCount = computed(() => profile.value.registeredCount)
const showEmptyState = computed(() => isEmptyState.value || registrations.value.length === 0)
const registrationsLabel = computed(() =>
  showEmptyState.value ? 'Aún no te has registrado en ningún evento' : `${registrations.value.length} eventos`,
)

const roleBadgeLabels: Record<UserRole, string> = {
  admin: 'Administradora',
  attendee: 'Asistente',
  organizer: 'Organizadora',
}

const roleLineLabels: Record<UserRole, string> = {
  admin: 'Administrador',
  attendee: 'Asistente',
  organizer: 'Organizador',
}

const registrationDateFormatter = new Intl.DateTimeFormat('es-ES', {
  day: '2-digit',
  month: 'short',
  year: 'numeric',
  hour: '2-digit',
  minute: '2-digit',
})

function getInitials(name: string) {
  const parts = name.split(/\s+/).filter(Boolean)

  if (parts.length >= 2) {
    return `${parts[0]?.charAt(0) || ''}${parts[1]?.charAt(0) || ''}`.toUpperCase()
  }

  return name.slice(0, 2).toUpperCase()
}

function mapProfile(dto: UserProfileDTO): ProfileState {
  return {
    name: dto.name,
    email: dto.email,
    role: dto.role,
    memberSince: new Date(dto.created_at).getFullYear().toString(),
    organizedCount: dto.organized_count,
    registeredCount: dto.registered_count,
  }
}

function formatRegistrationDate(dateValue: string) {
  return registrationDateFormatter.format(new Date(dateValue)).replace(',', ' ·')
}

function getStateLabel(state: EventStatus) {
  if (state === 'draft') return 'Borrador'
  if (state === 'finished') return 'Finalizado'
  if (state === 'cancelled') return 'Cancelado'

  return 'Publicado'
}

function getStateVariant(state: EventStatus) {
  if (state === 'published') return 'success'
  if (state === 'finished') return 'info'
  if (state === 'cancelled') return 'danger'

  return 'neutral'
}

function mapRegistration(event: EventDTO): RegistrationItem {
  const capacityTotal = event.capacity || 0
  const progress = capacityTotal > 0 ? Math.round((event.registered_count / capacityTotal) * 100) : 0

  return {
    id: event.id,
    title: event.name,
    dateLabel: formatRegistrationDate(event.date),
    location: event.location || 'Sin ubicación',
    capacityCurrent: event.registered_count,
    capacityTotal,
    progress,
    state: event.status,
    stateLabel: getStateLabel(event.status),
  }
}

function openEditProfile() {
  toast.message = 'La edición de perfil todavía requiere un endpoint backend.'
  toast.variant = 'info'
  toast.open = true
}

function cancelRegistration(title: string) {
  toast.message = `Cancelaremos "${title}" cuando exista el flujo real de backend.`
  toast.variant = 'danger'
  toast.open = true
}

function exploreEvents() {
  void router.push('/eventos')
}

onMounted(async () => {
  const [profileResult, registrationsResult] = await Promise.allSettled([
    fetchMyProfile(),
    fetchMyRegistrations(),
  ])

  if (profileResult.status === 'fulfilled') {
    profile.value = mapProfile(profileResult.value)
  }

  if (registrationsResult.status === 'fulfilled') {
    registrations.value = registrationsResult.value.map(mapRegistration)
  }
})

function getRegistrationKey(item: RegistrationItem) {
  return item.id
}
</script>

<template>
  <div class="me-root profile-app">
    <main class="events-main profile-main">
      <UiToast
        :message="toast.message"
        :open="toast.open"
        :variant="toast.variant"
        @close="toast.open = false"
      />

      <header class="events-topbar profile-topbar">
        <div>
          <p class="section-kicker">Perfil</p>
          <h1 class="page-title">Mi perfil</h1>
          <p class="page-subtitle">
            Revisa tu actividad, tus registros y los eventos que estás siguiendo.
          </p>
        </div>

        <UiButton variant="secondary" size="lg" @click="openEditProfile">
          <UiIcon name="pencil" />
          Editar perfil
        </UiButton>
      </header>

      <section class="profile-hero">
        <div class="profile-identity">
          <span class="profile-avatar">
            {{ getInitials(userName) }}
          </span>

          <div class="profile-identify-text">
            <div class="profile-name-row">
              <h2>{{ userName }}</h2>
              <UiBadge variant="purple">{{ userRoleLabel }}</UiBadge>
            </div>
            <p>{{ userEmail }}</p>
            <span class="profile-role-line">{{ roleLineLabel }}</span>
          </div>
        </div>

        <div class="profile-stats">
          <article class="profile-stat">
            <span>Organizados</span>
            <strong>{{ organizedCount }}</strong>
          </article>
          <article class="profile-stat">
            <span>Registrados</span>
            <strong>{{ registeredCount }}</strong>
          </article>
          <article class="profile-stat">
            <span>Miembro desde</span>
            <strong>{{ profileSince }}</strong>
          </article>
        </div>
      </section>

      <section class="profile-body">
        <div class="profile-panel">
          <div class="profile-panel-head">
            <div>
              <h2>Mis eventos registrados</h2>
              <p>{{ registrationsLabel }}</p>
            </div>
          </div>

          <div v-if="showEmptyState" class="profile-empty">
            <h3>Aún no te has registrado en ningún evento</h3>
            <p>
              Explora el catálogo de eventos y reserva tu plaza. Aparecerán aquí para que los
              tengas siempre a mano.
            </p>
            <UiButton size="lg" @click="exploreEvents">
              <UiIcon name="home" />
              Explorar eventos
            </UiButton>
          </div>

          <div v-else class="profile-list">
            <article v-for="item in registrations" :key="getRegistrationKey(item)" class="profile-item">
              <div class="profile-item-main">
                <div class="profile-item-head">
                  <div>
                    <h3>{{ item.title }}</h3>
                    <p>{{ item.dateLabel }}</p>
                  </div>
                  <UiBadge :variant="getStateVariant(item.state)">{{ item.stateLabel }}</UiBadge>
                </div>

                <p class="profile-location">
                  <UiIcon name="map-pin" :size="16" />
                  {{ item.location }}
                </p>

                <div class="profile-capacity">
                  <div class="profile-capacity-head">
                    <span>Aforo</span>
                    <strong>{{ item.capacityCurrent }}/{{ item.capacityTotal }}</strong>
                  </div>
                  <div class="profile-progress" :aria-label="`Aforo del evento ${item.title}`">
                    <span class="profile-progress-fill" :style="{ width: `${item.progress}%` }" />
                  </div>
                </div>
              </div>

              <div class="profile-item-actions">
                <UiButton variant="danger" size="sm" @click="cancelRegistration(item.title)">
                  <UiIcon name="x" :size="16" />
                  Cancelar registro
                </UiButton>
              </div>
            </article>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>
