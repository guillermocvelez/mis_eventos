<script setup lang="ts">
import { UiBadge, UiIcon } from '@/components/ui'
import { type EventStatus } from '@/stores/events'

type CapacityTone = 'green' | 'muted' | 'red' | 'yellow'
type BadgeVariant = 'danger' | 'info' | 'neutral' | 'success'

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

defineProps<{
  events: EventCard[]
  statusLabels: Record<EventStatus, string>
  statusVariants: Record<EventStatus, BadgeVariant>
}>()

const emit = defineEmits<{
  'view-detail': [eventId: string]
}>()
</script>

<template>
  <section class="events-grid" aria-label="Listado de eventos">
    <article v-for="event in events" :key="event.id" class="event-card">
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
          <button class="btn btn-outline btn-sm" type="button" @click="emit('view-detail', event.id)">
            Ver detalle
          </button>
        </footer>
      </div>
    </article>
  </section>
</template>
