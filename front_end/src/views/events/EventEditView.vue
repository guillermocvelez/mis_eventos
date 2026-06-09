<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { UiBadge, UiButton, UiField, UiIcon, UiTextInput } from '@/components/ui'
import { useAuthStore } from '@/stores/auth'
import { type EventStatus, useEventsStore } from '@/stores/events'

const authStore = useAuthStore()
const eventsStore = useEventsStore()
const route = useRoute()
const router = useRouter()

const eventId = computed(() => String(route.params.eventId || ''))
const event = computed(() => eventsStore.selectedEvent)
const form = reactive<{
  name: string
  description: string
  startDate: string
  startTime: string
  endDate: string
  endTime: string
  location: string
  capacity: string
  status: EventStatus
}>({
  name: '',
  description: '',
  startDate: '',
  startTime: '',
  endDate: '',
  endTime: '',
  location: '',
  capacity: '',
  status: 'draft',
})
const fieldErrors = reactive({
  name: '',
  date: '',
  endDate: '',
  capacity: '',
})
const submitError = ref('')
const isSubmitting = ref(false)
const populatedEventId = ref('')

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

const canSubmit = computed(() => {
  return Boolean(
    form.name.trim() &&
    form.startDate &&
    form.startTime &&
    Number(form.capacity) > 0 &&
    !isSubmitting.value,
  )
})

const startDatetime = computed(() => {
  if (!form.startDate || !form.startTime) return ''
  return `${form.startDate}T${form.startTime}`
})

const endDatetime = computed(() => {
  if (!form.endDate) return ''
  return `${form.endDate}T${form.endTime || '23:59'}`
})

const startsAtLabel = computed(() => formatPreviewDate(startDatetime.value))
const endsAtLabel = computed(() => formatPreviewDate(endDatetime.value))
const capacityLabel = computed(() => {
  const capacity = Number(form.capacity)
  if (!capacity || capacity <= 0) return 'Sin cupo definido'
  return `${capacity} plazas disponibles`
})

const minEndTime = computed(() => {
  if (form.endDate && form.endDate === form.startDate) return form.startTime
  return ''
})

onMounted(() => {
  void eventsStore.fetchEventDetail(eventId.value)
})

watch(eventId, (nextEventId) => {
  if (nextEventId) {
    populatedEventId.value = ''
    void eventsStore.fetchEventDetail(nextEventId)
  }
})

watch(
  () => authStore.canManageEvents,
  (canManageEvents) => {
    if (!canManageEvents) {
      void router.push('/eventos')
    }
  },
  { immediate: true },
)

watch(
  event,
  (currentEvent) => {
    if (!currentEvent || populatedEventId.value === currentEvent.id) return

    form.name = currentEvent.name
    form.description = currentEvent.description || ''
    const startDT = toInputDateTime(currentEvent.date)
    form.startDate = startDT.slice(0, 10)
    form.startTime = startDT.slice(11, 16)

    const endDT = currentEvent.end_date ? toInputDateTime(currentEvent.end_date) : ''
    form.endDate = endDT.slice(0, 10)
    form.endTime = endDT.slice(11, 16)
    form.location = currentEvent.location || ''
    form.capacity = String(currentEvent.capacity)
    form.status = currentEvent.status
    populatedEventId.value = currentEvent.id
  },
  { immediate: true },
)

function clearFieldErrors() {
  fieldErrors.name = ''
  fieldErrors.date = ''
  fieldErrors.endDate = ''
  fieldErrors.capacity = ''
  submitError.value = ''
}

function toInputDateTime(value: string) {
  const date = new Date(value)
  date.setMinutes(date.getMinutes() - date.getTimezoneOffset())
  return date.toISOString().slice(0, 16)
}

function toApiDate(value: string) {
  if (!value) return null
  return new Date(value).toISOString()
}

function formatPreviewDate(value: string) {
  if (!value) return 'Pendiente'

  return new Intl.DateTimeFormat('es-CO', {
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    month: 'short',
    year: 'numeric',
  }).format(new Date(value))
}

function getCoverClass(status: EventStatus) {
  if (status === 'cancelled') return 'cv-cancelled'
  if (status === 'draft') return 'cv-draft'
  if (status === 'finished') return 'cv-finished'
  return 'cv-published'
}

function validateForm() {
  clearFieldErrors()

  if (!form.name.trim()) {
    fieldErrors.name = 'Escribe el nombre del evento.'
  }

  if (!form.startDate || !form.startTime) {
    fieldErrors.date = 'Selecciona la fecha y hora de inicio.'
  }

  if (form.endDate && startDatetime.value) {
    if (new Date(endDatetime.value).getTime() < new Date(startDatetime.value).getTime()) {
      fieldErrors.endDate = 'La finalización debe ser posterior al inicio.'
    }
  }

  const capacity = Number(form.capacity)
  if (!Number.isFinite(capacity) || capacity <= 0) {
    fieldErrors.capacity = 'Define un cupo mayor a cero.'
  }

  return !fieldErrors.name && !fieldErrors.date && !fieldErrors.endDate && !fieldErrors.capacity
}

async function submitEvent() {
  if (!validateForm()) return

  isSubmitting.value = true

  try {
    const updatedEvent = await eventsStore.updateEvent(eventId.value, {
      name: form.name.trim(),
      description: form.description.trim() || null,
      date: toApiDate(startDatetime.value) || undefined,
      end_date: toApiDate(endDatetime.value),
      location: form.location.trim() || null,
      capacity: Number(form.capacity),
      status: form.status,
    })

    await router.push({ name: 'event-detail', params: { eventId: updatedEvent.id } })
  } catch (caughtError) {
    const message = caughtError instanceof Error ? caughtError.message : ''
    submitError.value = message || 'No pudimos guardar los cambios. Inténtalo de nuevo.'
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <div class="me-root">
    <main class="events-main create-event-page">
      <section v-if="eventsStore.isDetailLoading" class="events-empty" aria-live="polite">
        <div class="empty-icon">
          <UiIcon name="ticket" :size="28" />
        </div>
        <h2>Cargando evento</h2>
        <p>Estamos preparando la información para edición.</p>
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
              <button
                type="button"
                @click="router.push({ name: 'event-detail', params: { eventId } })"
              >
                {{ event.name }}
              </button>
              <span>/</span>
              <span>Editar</span>
            </p>
            <h1 class="page-title">Editar evento</h1>
            <p class="page-subtitle">
              Actualiza la información del evento y conserva el control de estado de publicación.
            </p>
          </div>
        </header>

        <section class="create-event-layout">
          <form class="event-form-panel" @submit.prevent="submitEvent">
            <div class="form-section-head">
              <span class="section-kicker">Edición</span>
              <h2>Datos del evento</h2>
            </div>

            <div class="event-form-grid">
              <UiField label="Nombre del evento" :error="fieldErrors.name" for-id="event-name">
                <UiTextInput
                  id="event-name"
                  v-model="form.name"
                  :invalid="Boolean(fieldErrors.name)"
                  placeholder="Ej. Encuentro de innovación"
                />
              </UiField>

              <UiField label="Estado" for-id="event-status">
                <select id="event-status" v-model="form.status" class="input">
                  <option value="draft">Borrador</option>
                  <option value="published">Publicado</option>
                  <option value="finished">Finalizado</option>
                  <option value="cancelled">Cancelado</option>
                </select>
              </UiField>

              <UiField
                label="Fecha y hora de inicio"
                :error="fieldErrors.date"
                for-id="event-start-date"
              >
                <div class="date-time-pair date-time-stack">
                  <UiTextInput
                    id="event-start-date"
                    v-model="form.startDate"
                    :invalid="Boolean(fieldErrors.date)"
                    type="date"
                  />
                  <UiTextInput
                    v-model="form.startTime"
                    :invalid="Boolean(fieldErrors.date)"
                    type="time"
                  />
                </div>
              </UiField>

              <UiField
                label="Fecha y hora de finalización"
                :error="fieldErrors.endDate"
                for-id="event-end-date"
              >
                <div class="date-time-pair date-time-stack">
                  <UiTextInput
                    id="event-end-date"
                    v-model="form.endDate"
                    :invalid="Boolean(fieldErrors.endDate)"
                    :min="form.startDate"
                    type="date"
                  />
                  <UiTextInput
                    v-model="form.endTime"
                    :invalid="Boolean(fieldErrors.endDate)"
                    :min="minEndTime"
                    type="time"
                  />
                </div>
              </UiField>

              <UiField label="Cupo" :error="fieldErrors.capacity" for-id="event-capacity">
                <UiTextInput
                  id="event-capacity"
                  v-model="form.capacity"
                  :invalid="Boolean(fieldErrors.capacity)"
                  min="1"
                  placeholder="50"
                  type="number"
                />
              </UiField>

              <UiField label="Ubicación" for-id="event-location">
                <UiTextInput
                  id="event-location"
                  v-model="form.location"
                  placeholder="Auditorio principal"
                />
              </UiField>
            </div>

            <UiField label="Descripción" for-id="event-description">
              <textarea
                id="event-description"
                v-model="form.description"
                class="input event-textarea"
                placeholder="Describe el propósito, agenda general o información clave del evento."
                rows="7"
              />
            </UiField>

            <p v-if="submitError" class="form-alert" role="alert">{{ submitError }}</p>

            <div class="form-actions">
              <UiButton
                variant="ghost"
                @click="router.push({ name: 'event-detail', params: { eventId } })"
                >Cancelar</UiButton
              >
              <UiButton :disabled="!canSubmit" type="submit">
                {{ isSubmitting ? 'Guardando...' : 'Guardar cambios' }}
              </UiButton>
            </div>
          </form>

          <aside class="event-preview-panel" aria-label="Resumen del evento">
            <div class="preview-cover" :class="getCoverClass(form.status)">
              <span>{{ form.name ? form.name.slice(0, 2).toUpperCase() : 'EV' }}</span>
            </div>
            <div class="preview-body">
              <UiBadge :variant="statusVariants[form.status]">
                {{ statusLabels[form.status] }}
              </UiBadge>
              <h2>{{ form.name || 'Nombre del evento' }}</h2>
              <p>
                {{
                  form.description ||
                  'La descripción aparecerá aquí para validar cómo se leerá antes de guardar.'
                }}
              </p>

              <div class="preview-meta">
                <span>
                  <UiIcon name="calendar" :size="16" />
                  {{ startsAtLabel }}
                </span>
                <span>
                  <UiIcon name="ticket" :size="16" />
                  {{ capacityLabel }}
                </span>
                <span>
                  <UiIcon name="map-pin" :size="16" />
                  {{ form.location || 'Sin ubicación' }}
                </span>
                <span v-if="form.endDate">
                  <UiIcon name="calendar" :size="16" />
                  Finaliza {{ endsAtLabel }}
                </span>
              </div>
            </div>
          </aside>
        </section>
      </template>
    </main>
  </div>
</template>
