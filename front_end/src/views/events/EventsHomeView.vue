<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'

import { UiBadge, UiButton, UiIcon, UiTextInput } from '@/components/ui'
import { useAuthStore } from '@/stores/auth'
import { type EventDTO, type EventStatus, useEventsStore } from '@/stores/events'

type CapacityTone = 'green' | 'muted' | 'red' | 'yellow'

type EventCard = {
  id: string
  title: string
  date: string
  attendees: number
  capacity: number
  capacityPercent: number
  capacityTone: CapacityTone
  coverClass: string
  icon: string
  location: string
  status: EventStatus
}

const authStore = useAuthStore()
const eventsStore = useEventsStore()
const router = useRouter()
const searchQuery = ref('')
let searchTimeout: ReturnType<typeof setTimeout> | undefined

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

const eventCards = computed(() => eventsStore.items.map(mapEventToCard))

onMounted(() => {
  searchQuery.value = eventsStore.search
  void eventsStore.fetchEvents({ limit: 6, page: 1 })
})

watch(searchQuery, (nextSearch) => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    void eventsStore.fetchEvents({
      limit: eventsStore.limit,
      page: 1,
      search: nextSearch,
    })
  }, 350)
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
    month: 'short',
    year: 'numeric',
  }).format(new Date(date))
}

function getCapacityTone(event: EventDTO): CapacityTone {
  if (event.capacity <= 0) return 'muted'

  const ratio = event.registered_count / event.capacity

  if (ratio >= 1) return 'red'
  if (ratio >= 0.7) return 'yellow'
  if (ratio > 0) return 'green'

  return 'muted'
}

function getCapacityPercent(event: EventDTO) {
  if (event.capacity <= 0) return 0
  return Math.min((event.registered_count / event.capacity) * 100, 100)
}

function getCoverClass(status: EventStatus) {
  if (status === 'draft') return 'cv-draft'
  if (status === 'cancelled') return 'cv-cancelled'
  if (status === 'finished') return 'cv-finished'

  return 'cv-published'
}

function mapEventToCard(event: EventDTO): EventCard {
  return {
    id: event.id,
    title: event.name,
    date: formatEventDate(event.date),
    location: event.location || 'Sin ubicación',
    attendees: event.registered_count,
    capacity: event.capacity,
    capacityPercent: getCapacityPercent(event),
    capacityTone: getCapacityTone(event),
    coverClass: getCoverClass(event.status),
    icon: event.name.slice(0, 2).toUpperCase(),
    status: event.status,
  }
}

async function clearSearch() {
  searchQuery.value = ''
  await eventsStore.clearSearch()
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
      <header class="events-topbar">
        <div>
          <h1 class="page-title">Descubre eventos</h1>
          <p class="page-subtitle">
            Explora próximos eventos y revisa el estado de cada convocatoria.
          </p>
        </div>

        <UiButton v-if="authStore.canManageEvents" size="lg">
          <UiIcon name="plus" />
          Crear evento
        </UiButton>
      </header>

      <section class="events-toolbar" aria-label="Filtros de eventos">
        <div class="searchbar">
          <span class="input-icon lead">
            <UiIcon name="search" />
          </span>
          <UiTextInput
            v-model="searchQuery"
            class="has-lead"
            placeholder="Buscar eventos"
            type="search"
          />
        </div>
      </section>

      <section v-if="eventsStore.isLoading" class="events-empty" aria-live="polite">
        <div class="empty-icon">
          <UiIcon name="ticket" :size="28" />
        </div>
        <h2>Cargando eventos</h2>
        <p>Estamos consultando los eventos disponibles.</p>
      </section>

      <section v-else-if="eventsStore.error" class="events-empty" aria-live="polite">
        <div class="empty-icon danger">
          <UiIcon name="ticket" :size="28" />
        </div>
        <h2>No pudimos cargar los eventos</h2>
        <p>{{ eventsStore.error }}</p>
        <UiButton variant="secondary" @click="eventsStore.fetchEvents({ limit: 6, page: 1 })">
          Reintentar
        </UiButton>
      </section>

      <section v-else-if="eventCards.length" class="events-grid" aria-label="Listado de eventos">
        <article v-for="event in eventCards" :key="event.id" class="event-card">
          <div class="event-cover" :class="event.coverClass">
            <span>{{ event.icon }}</span>
          </div>

          <div class="event-body">
            <div class="event-head">
              <UiBadge :variant="statusVariants[event.status]">
                {{ statusLabels[event.status] }}
              </UiBadge>
            </div>

            <h2>{{ event.title }}</h2>

            <div class="event-meta">
              <span>
                <UiIcon name="calendar" :size="15" />
                {{ event.date }}
              </span>
              <span>
                <UiIcon name="map-pin" :size="15" />
                {{ event.location }}
              </span>
            </div>

            <div class="capacity">
              <div class="cap-head">
                <span>Aforo</span>
                <strong>{{ event.attendees }} / {{ event.capacity }}</strong>
              </div>
              <div class="cap-track">
                <span
                  class="cap-fill"
                  :class="event.capacityTone"
                  :style="{ width: `${event.capacityPercent}%` }"
                />
              </div>
            </div>

            <footer class="event-foot">
              <button
                class="btn btn-outline btn-sm"
                type="button"
                @click="router.push({ name: 'event-detail', params: { eventId: event.id } })"
              >
                Ver detalle
              </button>
            </footer>
          </div>
        </article>
      </section>

      <section v-else class="events-empty" aria-live="polite">
        <div class="empty-icon">
          <UiIcon name="search" :size="28" />
        </div>
        <h2>No encontramos eventos con ese nombre</h2>
        <p>
          Prueba con otras palabras clave o limpia los filtros para ver todos los eventos
          disponibles.
        </p>
        <UiButton variant="secondary" @click="clearSearch">Limpiar búsqueda</UiButton>
      </section>

      <p v-if="eventCards.length && !eventsStore.isLoading" class="events-count">
        Mostrando {{ eventCards.length }} de {{ eventsStore.total }} eventos
      </p>
    </main>
  </div>
</template>
