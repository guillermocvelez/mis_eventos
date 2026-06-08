<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue'
import { useRouter } from 'vue-router'

import EventsSidebar from '@/components/events/EventsSidebar.vue'
import { UiButton, UiField, UiIcon, UiTextInput } from '@/components/ui'
import { useAuthStore } from '@/stores/auth'
import { useEventsStore } from '@/stores/events'

const authStore = useAuthStore()
const eventsStore = useEventsStore()
const router = useRouter()

const form = reactive({
  name: '',
  description: '',
  date: '',
  endDate: '',
  location: '',
  capacity: '50',
})
const fieldErrors = reactive({
  name: '',
  date: '',
  endDate: '',
  capacity: '',
})
const submitError = ref('')
const isSubmitting = ref(false)

const canSubmit = computed(() => {
  return Boolean(form.name.trim() && form.date && Number(form.capacity) > 0 && !isSubmitting.value)
})

const startsAtLabel = computed(() => formatPreviewDate(form.date))
const endsAtLabel = computed(() => formatPreviewDate(form.endDate))
const capacityLabel = computed(() => {
  const capacity = Number(form.capacity)
  if (!capacity || capacity <= 0) return 'Sin cupo definido'
  return `${capacity} plazas disponibles`
})

const minDateTime = computed(() => {
  const now = new Date()
  now.setMinutes(now.getMinutes() - now.getTimezoneOffset() + 5)
  return now.toISOString().slice(0, 16)
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

function clearFieldErrors() {
  fieldErrors.name = ''
  fieldErrors.date = ''
  fieldErrors.endDate = ''
  fieldErrors.capacity = ''
  submitError.value = ''
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

function toApiDate(value: string) {
  if (!value) return null
  return new Date(value).toISOString()
}

function validateForm() {
  clearFieldErrors()

  if (!form.name.trim()) {
    fieldErrors.name = 'Escribe el nombre del evento.'
  }

  if (!form.date) {
    fieldErrors.date = 'Selecciona la fecha y hora de inicio.'
  } else if (new Date(form.date).getTime() <= Date.now()) {
    fieldErrors.date = 'La fecha de inicio debe ser futura.'
  }

  if (
    form.endDate &&
    form.date &&
    new Date(form.endDate).getTime() < new Date(form.date).getTime()
  ) {
    fieldErrors.endDate = 'La finalización debe ser posterior al inicio.'
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
    const createdEvent = await eventsStore.createEvent({
      name: form.name.trim(),
      description: form.description.trim() || null,
      date: toApiDate(form.date) || '',
      end_date: toApiDate(form.endDate),
      location: form.location.trim() || null,
      capacity: Number(form.capacity),
    })

    await router.push({ name: 'event-detail', params: { eventId: createdEvent.id } })
  } catch (caughtError) {
    const message = caughtError instanceof Error ? caughtError.message : ''
    submitError.value = message || 'No pudimos crear el evento. Inténtalo de nuevo.'
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <div class="me-root events-app">
    <EventsSidebar :event-count="eventsStore.total" />

    <main class="events-main create-event-page">
      <header class="detail-topbar">
        <div>
          <p class="detail-crumb">
            <button type="button" @click="router.push('/eventos')">Eventos</button>
            <span>/</span>
            <span>Crear evento</span>
          </p>
          <h1 class="page-title">Crear evento</h1>
          <p class="page-subtitle">
            Publica una nueva convocatoria con fecha, cupo y ubicación listos para gestión.
          </p>
        </div>
      </header>

      <section class="create-event-layout">
        <form class="event-form-panel" @submit.prevent="submitEvent">
          <div class="form-section-head">
            <span class="section-kicker">Información principal</span>
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

            <UiField label="Fecha y hora de inicio" :error="fieldErrors.date" for-id="event-date">
              <UiTextInput
                id="event-date"
                v-model="form.date"
                :invalid="Boolean(fieldErrors.date)"
                :min="minDateTime"
                type="datetime-local"
              />
            </UiField>

            <UiField
              label="Fecha y hora de finalización"
              :error="fieldErrors.endDate"
              for-id="event-end-date"
              hint="Opcional si el evento termina el mismo día."
            >
              <UiTextInput
                id="event-end-date"
                v-model="form.endDate"
                :invalid="Boolean(fieldErrors.endDate)"
                :min="form.date || minDateTime"
                type="datetime-local"
              />
            </UiField>

            <UiField label="Ubicación" for-id="event-location">
              <UiTextInput
                id="event-location"
                v-model="form.location"
                placeholder="Auditorio principal"
              />
            </UiField>

            <UiField label="Descripción" for-id="event-description">
              <textarea
                id="event-description"
                v-model="form.description"
                class="input event-textarea"
                placeholder="Describe el propósito, agenda general o información clave del evento."
                rows="7"
              />
            </UiField>
          </div>

          <p v-if="submitError" class="form-alert" role="alert">{{ submitError }}</p>

          <div class="form-actions">
            <UiButton variant="ghost" @click="router.push('/eventos')">Cancelar</UiButton>
            <UiButton :disabled="!canSubmit" type="submit">
              <UiIcon name="plus" />
              {{ isSubmitting ? 'Creando...' : 'Crear evento' }}
            </UiButton>
          </div>
        </form>

        <aside class="event-preview-panel" aria-label="Resumen del evento">
          <div class="preview-cover cv-draft">
            <span>{{ form.name ? form.name.slice(0, 2).toUpperCase() : 'EV' }}</span>
          </div>
          <div class="preview-body">
            <span class="section-kicker">Borrador</span>
            <h2>{{ form.name || 'Nombre del evento' }}</h2>
            <p>
              {{
                form.description ||
                'La descripción aparecerá aquí para validar cómo se leerá antes de crearlo.'
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
    </main>
  </div>
</template>
