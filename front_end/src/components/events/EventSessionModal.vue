<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue'

import { UiButton, UiField, UiIcon, UiModal, UiTextInput } from '@/components/ui'
import type { EventDTO, SessionCreatePayload, SessionDTO, SpeakerDTO } from '@/stores/events'

const props = defineProps<{
  event: EventDTO
  open: boolean
  saving?: boolean
  session?: SessionDTO | null
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
  startDate: '',
  startTime: '',
  endDate: '',
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
  return Boolean(
    form.title.trim() &&
      form.startDate &&
      form.startTime &&
      form.endDate &&
      form.endTime &&
      !props.saving,
  )
})

const minEndTime = computed(() => {
  if (form.endDate && form.endDate === form.startDate) return form.startTime
  return ''
})

const isEditing = computed(() => Boolean(props.session))
const modalTitle = computed(() => (isEditing.value ? 'Editar sesión' : 'Crear sesión'))
const submitLabel = computed(() => {
  if (props.saving) return 'Guardando...'
  return isEditing.value ? 'Guardar cambios' : 'Guardar sesión'
})

watch(
  () => [props.open, props.session?.id] as const,
  ([isOpen]) => {
    if (isOpen) resetForm()
  },
)

function resetForm() {
  form.title = props.session?.title ?? ''
  form.speakerId = props.session?.speaker?.id ?? ''

  const startDT = toInputDateTime(props.session?.start_time ?? props.event.date)
  form.startDate = startDT.slice(0, 10)
  form.startTime = startDT.slice(11, 16)

  const endDT = props.session?.end_time ? toInputDateTime(props.session.end_time) : ''
  form.endDate = endDT.slice(0, 10)
  form.endTime = endDT.slice(11, 16)

  form.capacity = props.session?.capacity === null ? '' : String(props.session?.capacity ?? '')
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

function startDatetime() {
  return form.startDate && form.startTime ? `${form.startDate}T${form.startTime}` : ''
}

function endDatetime() {
  return form.endDate && form.endTime ? `${form.endDate}T${form.endTime}` : ''
}

function overlapsExistingSession() {
  const nextStart = new Date(startDatetime()).getTime()
  const nextEnd = new Date(endDatetime()).getTime()

  return props.sessions.some((session) => {
    if (session.id === props.session?.id) return false

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

  if (!form.startDate || !form.startTime) {
    fieldErrors.startTime = 'Selecciona la fecha y hora de inicio.'
  }

  if (!form.endDate || !form.endTime) {
    fieldErrors.endTime = 'Selecciona la fecha y hora de finalización.'
  }

  const start = startDatetime()
  const end = endDatetime()
  if (start && end && new Date(end) <= new Date(start)) {
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
    start_time: toApiDate(startDatetime()),
    end_time: toApiDate(endDatetime()),
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

<style scoped>
:deep(.card-body) {
  display: grid;
  gap: var(--space-4);
}
</style>

<template>
  <UiModal :open="open">
    <form @submit.prevent="submitSession">
      <div class="card-header">
        <div>
          <h2 class="card-title">{{ modalTitle }}</h2>
          <p class="card-description">{{ event.name }}</p>
        </div>
        <UiButton variant="ghost" size="sm" @click="emit('close')">Cancelar</UiButton>
      </div>

      <div class="card-body">
        <p v-if="submitError" class="form-alert" role="alert">{{ submitError }}</p>

        <div class="session-form-grid">
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

          <UiField label="Inicio" :error="fieldErrors.startTime" for-id="session-start-date">
            <div class="date-time-pair">
              <UiTextInput
                id="session-start-date"
                v-model="form.startDate"
                :invalid="Boolean(fieldErrors.startTime)"
                type="date"
              />
              <UiTextInput
                v-model="form.startTime"
                :invalid="Boolean(fieldErrors.startTime)"
                type="time"
              />
            </div>
          </UiField>

          <UiField label="Finalización" :error="fieldErrors.endTime" for-id="session-end-date">
            <div class="date-time-pair">
              <UiTextInput
                id="session-end-date"
                v-model="form.endDate"
                :invalid="Boolean(fieldErrors.endTime)"
                :min="form.startDate"
                type="date"
              />
              <UiTextInput
                v-model="form.endTime"
                :invalid="Boolean(fieldErrors.endTime)"
                :min="minEndTime"
                type="time"
              />
            </div>
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
          <UiIcon :name="isEditing ? 'pencil' : 'plus'" :size="16" />
          {{ submitLabel }}
        </UiButton>
      </div>
    </form>
  </UiModal>
</template>
