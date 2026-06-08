<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue'

import { UiButton, UiField, UiIcon, UiModal, UiTextInput } from '@/components/ui'
import type { EventDTO, SessionCreatePayload, SessionDTO, SpeakerDTO } from '@/stores/events'

const props = defineProps<{
  event: EventDTO
  open: boolean
  saving?: boolean
  sessions: SessionDTO[]
  speakers: SpeakerDTO[]
}>()

const emit = defineEmits<{
  close: []
  save: [payload: SessionCreatePayload]
}>()

const form = reactive({
  title: '',
  speakerId: '',
  startTime: '',
  endTime: '',
  capacity: '',
})
const fieldErrors = reactive({
  title: '',
  startTime: '',
  endTime: '',
  capacity: '',
})
const submitError = ref('')

const canSubmit = computed(() => {
  return Boolean(form.title.trim() && form.startTime && form.endTime && !props.saving)
})

watch(
  () => props.open,
  (isOpen) => {
    if (isOpen) resetForm()
  },
)

function resetForm() {
  form.title = ''
  form.speakerId = ''
  form.startTime = toInputDateTime(props.event.date)
  form.endTime = ''
  form.capacity = ''
  clearErrors()
}

function clearErrors() {
  fieldErrors.title = ''
  fieldErrors.startTime = ''
  fieldErrors.endTime = ''
  fieldErrors.capacity = ''
  submitError.value = ''
}

function toInputDateTime(value: string) {
  const date = new Date(value)
  date.setMinutes(date.getMinutes() - date.getTimezoneOffset())
  return date.toISOString().slice(0, 16)
}

function toApiDate(value: string) {
  return new Date(value).toISOString()
}

function overlapsExistingSession() {
  const nextStart = new Date(form.startTime).getTime()
  const nextEnd = new Date(form.endTime).getTime()

  return props.sessions.some((session) => {
    const currentStart = new Date(session.start_time).getTime()
    const currentEnd = new Date(session.end_time).getTime()
    return nextStart < currentEnd && nextEnd > currentStart
  })
}

function validateForm() {
  clearErrors()

  if (!form.title.trim()) {
    fieldErrors.title = 'Escribe el título de la sesión.'
  }

  if (!form.startTime) {
    fieldErrors.startTime = 'Selecciona la hora de inicio.'
  }

  if (!form.endTime) {
    fieldErrors.endTime = 'Selecciona la hora de finalización.'
  }

  if (form.startTime && form.endTime && new Date(form.endTime) <= new Date(form.startTime)) {
    fieldErrors.endTime = 'La finalización debe ser posterior al inicio.'
  }

  if (form.capacity && Number(form.capacity) <= 0) {
    fieldErrors.capacity = 'La capacidad debe ser mayor a cero.'
  }

  if (!fieldErrors.startTime && !fieldErrors.endTime && overlapsExistingSession()) {
    submitError.value = 'Este horario se solapa con otra sesión existente.'
  }

  return (
    !fieldErrors.title &&
    !fieldErrors.startTime &&
    !fieldErrors.endTime &&
    !fieldErrors.capacity &&
    !submitError.value
  )
}

async function submitSession() {
  if (!validateForm()) return

  emit('save', {
    title: form.title.trim(),
    speaker_id: form.speakerId || null,
    start_time: toApiDate(form.startTime),
    end_time: toApiDate(form.endTime),
    capacity: form.capacity ? Number(form.capacity) : null,
  })
}

function setSubmitError(message: string) {
  submitError.value = message
}

defineExpose({
  setSubmitError,
})
</script>

<template>
  <UiModal :open="open">
    <form @submit.prevent="submitSession">
      <div class="card-header">
        <div>
          <h2 class="card-title">Crear sesión</h2>
          <p class="card-description">{{ event.name }}</p>
        </div>
        <UiButton variant="ghost" size="sm" @click="emit('close')">Cancelar</UiButton>
      </div>

      <div class="card-body">
        <p v-if="submitError" class="form-alert" role="alert">{{ submitError }}</p>

        <div class="event-form-grid">
          <UiField label="Título de la sesión" :error="fieldErrors.title" for-id="session-title">
            <UiTextInput
              id="session-title"
              v-model="form.title"
              :invalid="Boolean(fieldErrors.title)"
              placeholder="Ej. Charla de apertura"
            />
          </UiField>

          <UiField label="Ponente" for-id="session-speaker">
            <select id="session-speaker" v-model="form.speakerId" class="input">
              <option value="">Sin ponente asignado</option>
              <option v-for="speaker in speakers" :key="speaker.id" :value="speaker.id">
                {{ speaker.name }}
              </option>
            </select>
          </UiField>

          <UiField label="Inicio" :error="fieldErrors.startTime" for-id="session-start">
            <UiTextInput
              id="session-start"
              v-model="form.startTime"
              :invalid="Boolean(fieldErrors.startTime)"
              type="datetime-local"
            />
          </UiField>

          <UiField label="Finalización" :error="fieldErrors.endTime" for-id="session-end">
            <UiTextInput
              id="session-end"
              v-model="form.endTime"
              :invalid="Boolean(fieldErrors.endTime)"
              :min="form.startTime"
              type="datetime-local"
            />
          </UiField>

          <UiField
            label="Capacidad"
            :error="fieldErrors.capacity"
            for-id="session-capacity"
            hint="Déjalo vacío si no quieres limitar esta sesión."
          >
            <UiTextInput
              id="session-capacity"
              v-model="form.capacity"
              :invalid="Boolean(fieldErrors.capacity)"
              min="1"
              placeholder="Sin límite"
              type="number"
            />
          </UiField>
        </div>
      </div>

      <div class="card-footer form-actions">
        <UiButton variant="ghost" @click="emit('close')">Cancelar</UiButton>
        <UiButton :disabled="!canSubmit" type="submit">
          <UiIcon name="plus" :size="16" />
          {{ saving ? 'Guardando...' : 'Guardar sesión' }}
        </UiButton>
      </div>
    </form>
  </UiModal>
</template>
