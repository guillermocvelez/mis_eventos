<script setup lang="ts">
import { type EventStatus } from '@/stores/events'
import EventCard from './EventCard.vue'
import type { EventBadgeVariant, EventCardItem } from './eventCardTypes'

defineProps<{
  events: EventCardItem[]
  statusLabels: Record<EventStatus, string>
  statusVariants: Record<EventStatus, EventBadgeVariant>
}>()

const emit = defineEmits<{
  'view-detail': [eventId: string]
}>()
</script>

<template>
  <section class="events-grid" aria-label="Listado de eventos">
    <EventCard
      v-for="event in events"
      :key="event.id"
      :event="event"
      :status-labels="statusLabels"
      :status-variants="statusVariants"
      @view-detail="emit('view-detail', $event)"
    />
  </section>
</template>
