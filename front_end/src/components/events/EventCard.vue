<script setup lang="ts">
import { UiBadge, UiIcon } from '@/components/ui'
import type { EventStatus } from '@/stores/events'
import type { EventBadgeVariant, EventCardItem } from './eventCardTypes'

defineProps<{
  event: EventCardItem
  statusLabels: Record<EventStatus, string>
  statusVariants: Record<EventStatus, EventBadgeVariant>
}>()

const emit = defineEmits<{
  'view-detail': [eventId: string]
}>()
</script>

<template>
  <article class="event-card">
    <div class="event-cover" :class="event.coverClass">
      <span>{{ event.icon }}</span>
    </div>

    <div class="event-body">
      <div v-if="event.status" class="event-head">
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
        <span v-if="event.endDate">
          <UiIcon name="calendar" :size="15" />
          {{ event.endDate }}
        </span>
        <span>
          <UiIcon name="clock" :size="15" />
          {{ event.timeRange }}
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
        <button class="btn btn-outline btn-sm" type="button" @click="emit('view-detail', event.id)">
          Ver detalle
        </button>
      </footer>
    </div>
  </article>
</template>
