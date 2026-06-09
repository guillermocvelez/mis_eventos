<script setup lang="ts">
import { computed } from 'vue'

import { UiButton } from '@/components/ui'
import type { EventDTO } from '@/stores/events'

const props = defineProps<{
  cancelling?: boolean
  checkingRegistration?: boolean
  event: EventDTO
  error?: string
  isRegistered?: boolean
  registering?: boolean
  success?: string
}>()

const emit = defineEmits<{
  'cancel-registration': []
  register: []
}>()

const registeredPercent = computed(() => {
  if (props.event.capacity <= 0) return 0
  return Math.min((props.event.registered_count / props.event.capacity) * 100, 100)
})

const availableSeats = computed(() => {
  return Math.max(props.event.capacity - props.event.registered_count, 0)
})

const isEventFull = computed(() => props.event.registered_count >= props.event.capacity)
const showRegisterButton = computed(() => {
  return props.event.status === 'published' && !props.isRegistered
})
const statusMessage = computed(() => {
  if (props.isRegistered) return 'Ya estás registrado en este evento.'
  return props.success
})
const isDisabled = computed(
  () => props.registering || props.cancelling || props.checkingRegistration || isEventFull.value,
)
const buttonLabel = computed(() => {
  if (props.checkingRegistration) return 'Verificando...'
  if (props.registering) return 'Registrando...'
  if (isEventFull.value) return 'Evento lleno'
  return 'Registrarme'
})
const cancelButtonLabel = computed(() => {
  return props.cancelling ? 'Cancelando...' : 'Cancelar registro'
})
</script>

<template>
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

    <p v-if="error" class="form-alert" role="alert">{{ error }}</p>
    <p v-else-if="statusMessage" class="form-alert success" role="status">{{ statusMessage }}</p>

    <UiButton
      v-if="showRegisterButton"
      block
      :disabled="isDisabled"
      size="lg"
      @click="emit('register')"
    >
      {{ buttonLabel }}
    </UiButton>

    <UiButton
      v-else-if="isRegistered"
      block
      :disabled="cancelling || checkingRegistration"
      size="lg"
      variant="danger"
      @click="emit('cancel-registration')"
    >
      {{ cancelButtonLabel }}
    </UiButton>
  </aside>
</template>
