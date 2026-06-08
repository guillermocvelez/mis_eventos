<script setup lang="ts">
import { computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { UiBadge, UiButton, UiIcon } from '@/components/ui'
import { useAuthStore } from '@/stores/auth'
import { type EventDTO, type EventStatus, type SessionDTO, useEventsStore } from '@/stores/events'

const authStore = useAuthStore()
const eventsStore = useEventsStore()
const route = useRoute()
const router = useRouter()

const eventId = computed(() => String(route.params.eventId || ''))
const event = computed(() => eventsStore.selectedEvent)
const sessions = computed(() => {
  return [...eventsStore.sessions].sort(
    (left, right) => new Date(left.start_time).getTime() - new Date(right.start_time).getTime(),
  )
})

const roleLabel = computed(() => {
  if (authStore.userRole === 'admin') return 'Administrador'
  if (authStore.userRole === 'organizer') return 'Organizador'
  return 'Visitante'
})

const statusLabels: Record<EventStatus, string> = {
  cancelled: 'Cancelado',
  draft: 'Borrador',
  finished: 'Finalizado',
  published: 'Publicado',
}

const statusVariants: Record<EventStatus, 'danger' | 'info' | 'neutral' | 'success'> = {
  cancelled: 'danger',
  draft: 'info',
  finished: 'neutral',
  published: 'success',
}

const registeredPercent = computed(() => {
  if (!event.value || event.value.capacity <= 0) return 0
  return Math.min((event.value.registered_count / event.value.capacity) * 100, 100)
})

const availableSeats = computed(() => {
  if (!event.value) return 0
  return Math.max(event.value.capacity - event.value.registered_count, 0)
})

const isEventFull = computed(() =>
  Boolean(event.value && event.value.registered_count >= event.value.capacity),
)

onMounted(() => {
  void eventsStore.fetchEventDetail(eventId.value)
})

watch(eventId, (nextEventId) => {
  if (nextEventId) {
    void eventsStore.fetchEventDetail(nextEventId)
  }
})

watch(
  () => authStore.isAuthenticated,
  (isAuthenticated) => {
    if (!isAuthenticated) {
      void router.push('/login')
    }
  },
)

function formatEventDate(date: string) {
  return new Intl.DateTimeFormat('es-CO', {
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    month: 'short',
    year: 'numeric',
  }).format(new Date(date))
}

function formatTimeRange(session: SessionDTO) {
  const formatter = new Intl.DateTimeFormat('es-CO', {
    hour: '2-digit',
    minute: '2-digit',
  })

  return `${formatter.format(new Date(session.start_time))} - ${formatter.format(new Date(session.end_time))}`
}

function getSessionCapacity(session: SessionDTO) {
  if (session.capacity === null) return 'Sin límite'
  return `${session.registered_count} / ${session.capacity} plazas`
}

function getOrganizerLabel(currentEvent: EventDTO) {
  return `Organiza ${currentEvent.created_by.slice(0, 8)}`
}

async function logout() {
  authStore.logout()
  await router.push('/login')
}
</script>

<template>
  <div class="me-root events-app">
    <aside class="events-sidebar">
      <div class="events-brand">
        <span class="brand-mark">ME</span>
        <div>
          <strong>Mis Eventos</strong>
          <span>Gestión inteligente</span>
        </div>
      </div>

      <nav class="events-nav" aria-label="Principal">
        <a class="active" href="/eventos">
          <UiIcon name="ticket" />
          Principal
        </a>
      </nav>

      <div class="events-user-card">
        <span class="events-avatar">{{
          authStore.userEmail.slice(0, 1).toUpperCase() || 'U'
        }}</span>
        <div>
          <strong>{{ authStore.userEmail || 'Usuario autenticado' }}</strong>
          <span>{{ roleLabel }}</span>
        </div>
        <button aria-label="Cerrar sesión" class="icon-btn" type="button" @click="logout">
          <UiIcon name="log-out" />
        </button>
      </div>
    </aside>

    <main class="events-main">
      <section v-if="eventsStore.isDetailLoading" class="events-empty" aria-live="polite">
        <div class="empty-icon">
          <UiIcon name="ticket" :size="28" />
        </div>
        <h2>Cargando evento</h2>
        <p>Estamos consultando el detalle y sus sesiones.</p>
      </section>

      <section v-else-if="eventsStore.detailError" class="events-empty" aria-live="polite">
        <div class="empty-icon danger">
          <UiIcon name="ticket" :size="28" />
        </div>
        <h2>No pudimos cargar el evento</h2>
        <p>{{ eventsStore.detailError }}</p>
        <UiButton variant="secondary" @click="eventsStore.fetchEventDetail(eventId)"
          >Reintentar</UiButton
        >
      </section>

      <template v-else-if="event">
        <header class="detail-topbar">
          <div>
            <p class="detail-crumb">
              <button type="button" @click="router.push('/eventos')">Eventos</button>
              <span>/</span>
              <span>{{ event.name }}</span>
            </p>
            <h1 class="page-title">{{ event.name }}</h1>
          </div>

          <div v-if="authStore.canManageEvents" class="detail-actions">
            <UiButton variant="secondary">Editar evento</UiButton>
            <UiButton variant="danger">Eliminar</UiButton>
          </div>
        </header>

        <section class="detail-layout">
          <article class="detail-main-card">
            <div class="detail-hero">
              <UiBadge :variant="statusVariants[event.status]">
                {{ statusLabels[event.status] }}
              </UiBadge>
              <span>{{ event.name.slice(0, 2).toUpperCase() }}</span>
            </div>

            <div class="detail-content">
              <div class="detail-meta">
                <span>
                  <UiIcon name="calendar" :size="16" />
                  {{ formatEventDate(event.date) }}
                </span>
                <span>
                  <UiIcon name="map-pin" :size="16" />
                  {{ event.location || 'Sin ubicación' }}
                </span>
                <span>
                  <UiIcon name="users" :size="16" />
                  {{ getOrganizerLabel(event) }}
                </span>
              </div>

              <section>
                <h2 class="section-title">Sobre el evento</h2>
                <p class="detail-description">
                  {{ event.description || 'Este evento aún no tiene una descripción publicada.' }}
                </p>
              </section>

              <section class="detail-sessions">
                <div class="detail-section-head">
                  <h2 class="section-title">Sesiones · {{ sessions.length }}</h2>
                  <UiButton v-if="authStore.canManageEvents" size="sm">
                    <UiIcon name="plus" :size="15" />
                    Agregar sesión
                  </UiButton>
                </div>

                <div v-if="sessions.length" class="sessions-list">
                  <article v-for="session in sessions" :key="session.id" class="session-row">
                    <span class="session-avatar">{{
                      session.title.slice(0, 1).toUpperCase()
                    }}</span>
                    <div class="session-main">
                      <strong>{{ session.title }}</strong>
                      <span>{{ session.speaker?.name || 'Sin ponente asignado' }}</span>
                    </div>
                    <div class="session-side">
                      <span class="time-pill">{{ formatTimeRange(session) }}</span>
                      <span>{{ getSessionCapacity(session) }}</span>
                    </div>
                  </article>
                </div>

                <div v-else class="sessions-empty">
                  Este evento aún no tiene sesiones publicadas.
                </div>
              </section>
            </div>
          </article>

          <aside class="registration-panel">
            <div class="donut" :style="{ '--progress': `${registeredPercent}%` }">
              <span>{{ availableSeats }}</span>
            </div>
            <div>
              <p class="d-lbl">Disponibles</p>
              <p class="d-num">{{ availableSeats }} plazas</p>
            </div>

            <div class="cap-grid">
              <div>
                <span>Registrados</span>
                <strong>{{ event.registered_count }}</strong>
              </div>
              <div>
                <span>Capacidad</span>
                <strong>{{ event.capacity }}</strong>
              </div>
            </div>

            <UiButton block :disabled="isEventFull" size="lg">
              {{ isEventFull ? 'Evento lleno' : 'Registrarme' }}
            </UiButton>
          </aside>
        </section>
      </template>
    </main>
  </div>
</template>
