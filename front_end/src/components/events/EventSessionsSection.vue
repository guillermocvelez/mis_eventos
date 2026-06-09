<script setup lang="ts">
import { UiButton, UiIcon } from '@/components/ui'
import type { SessionDTO } from '@/stores/events'

const props = defineProps<{
  canManageEvents: boolean
  canRegisterToSessions?: boolean
  checkingSessionRegistrations?: boolean
  deletingSessionId?: string
  registeredSessionIds?: string[]
  registeringSessionId?: string
  sessions: SessionDTO[]
}>()

const emit = defineEmits<{
  'add-session': []
  'delete-session': [session: SessionDTO]
  'edit-session': [session: SessionDTO]
  'register-session': [session: SessionDTO]
}>()

function formatDateTime(date: string) {
  return new Intl.DateTimeFormat('es-CO', {
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    month: 'short',
    year: 'numeric',
  }).format(new Date(date))
}

function getSessionCapacity(session: SessionDTO) {
  if (session.capacity === null) return 'Sin límite'
  return `${session.registered_count} / ${session.capacity} plazas`
}

function isSessionFull(session: SessionDTO) {
  return session.capacity !== null && session.registered_count >= session.capacity
}

function isRegisteredToSession(session: SessionDTO) {
  return props.registeredSessionIds?.includes(session.id) ?? false
}

function getRegisterButtonLabel(session: SessionDTO) {
  if (props.checkingSessionRegistrations) return 'Verificando...'
  if (props.registeringSessionId === session.id) return 'Registrando...'
  if (isSessionFull(session)) return 'Sesión llena'
  return 'Registrarme'
}

function canShowRegisterButton(session: SessionDTO) {
  return props.canRegisterToSessions && !isRegisteredToSession(session)
}
</script>

<template>
  <section class="detail-sessions">
    <div class="detail-section-head">
      <h2 class="section-title">Sesiones · {{ sessions.length }}</h2>
      <UiButton v-if="canManageEvents" size="sm" @click="emit('add-session')">
        <UiIcon name="plus" :size="15" />
        Agregar sesión
      </UiButton>
    </div>

    <div v-if="sessions.length" class="sessions-list">
      <article v-for="session in sessions" :key="session.id" class="session-row">
        <span class="session-avatar">{{ session.title.slice(0, 1).toUpperCase() }}</span>
        <div class="session-main">
          <strong>{{ session.title }}</strong>
          <span>{{ session.speaker?.name || 'Sin ponente asignado' }}</span>
        </div>
        <div class="session-side">
          <span class="time-pill">Inicio {{ formatDateTime(session.start_time) }}</span>
          <span>Fin {{ formatDateTime(session.end_time) }}</span>
          <span>{{ getSessionCapacity(session) }}</span>
          <span v-if="isRegisteredToSession(session)" class="session-status">Inscrito</span>
          <div v-if="canManageEvents" class="detail-actions">
            <UiButton variant="secondary" size="sm" @click="emit('edit-session', session)">
              <UiIcon name="pencil" :size="14" />
              Editar
            </UiButton>
            <UiButton
              variant="danger"
              size="sm"
              :disabled="deletingSessionId === session.id"
              @click="emit('delete-session', session)"
            >
              <UiIcon name="trash" :size="14" />
              {{ deletingSessionId === session.id ? 'Eliminando...' : 'Borrar' }}
            </UiButton>
          </div>
          <UiButton
            v-if="canShowRegisterButton(session)"
            :disabled="
              checkingSessionRegistrations ||
              registeringSessionId === session.id ||
              isSessionFull(session)
            "
            size="sm"
            @click="emit('register-session', session)"
          >
            {{ getRegisterButtonLabel(session) }}
          </UiButton>
        </div>
      </article>
    </div>

    <div v-else class="sessions-empty">Este evento aún no tiene sesiones publicadas.</div>
  </section>
</template>
