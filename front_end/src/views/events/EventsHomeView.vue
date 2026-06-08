<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'

import EventsEmptyState from '@/components/events/EventsEmptyState.vue'
import EventsErrorState from '@/components/events/EventsErrorState.vue'
import EventsGrid from '@/components/events/EventsGrid.vue'
import EventsLoadingState from '@/components/events/EventsLoadingState.vue'
import EventsSidebar from '@/components/events/EventsSidebar.vue'
import EventsToolbar from '@/components/events/EventsToolbar.vue'
import { UiButton, UiIcon } from '@/components/ui'
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
  if (status === 'cancelled') return 'cv-cancelled'
  if (status === 'draft') return 'cv-draft'
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

function goToEventDetail(eventId: string) {
  void router.push({ name: 'event-detail', params: { eventId } })
}
</script>

<template>
  <div class="me-root events-app">
    <EventsSidebar :event-count="eventsStore.total" />

    <main class="events-main">
      <header class="events-topbar">
        <div>
          <h1 class="page-title">Descubre eventos</h1>
          <p class="page-subtitle">
            Explora próximos eventos y revisa el estado de cada convocatoria.
          </p>
        </div>

        <UiButton v-if="authStore.canManageEvents" size="lg" @click="router.push('/eventos/crear')">
          <UiIcon name="plus" />
          Crear evento
        </UiButton>
      </header>

      <EventsToolbar v-model="searchQuery" />

      <EventsLoadingState v-if="eventsStore.isLoading" />

      <EventsErrorState
        v-else-if="eventsStore.error"
        :message="eventsStore.error"
        @retry="eventsStore.fetchEvents({ limit: 6, page: 1 })"
      />

      <EventsGrid
        v-else-if="eventCards.length"
        :events="eventCards"
        :status-labels="statusLabels"
        :status-variants="statusVariants"
        @view-detail="goToEventDetail"
      />

      <EventsEmptyState v-else @clear-search="clearSearch" />

      <p v-if="eventCards.length && !eventsStore.isLoading" class="events-count">
        Mostrando {{ eventCards.length }} de {{ eventsStore.total }} eventos
      </p>
    </main>
  </div>
</template>
