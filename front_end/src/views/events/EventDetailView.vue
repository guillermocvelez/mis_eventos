<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import EventRegistrationPanel from '@/components/events/EventRegistrationPanel.vue'
import EventSessionModal from '@/components/events/EventSessionModal.vue'
import EventSessionsSection from '@/components/events/EventSessionsSection.vue'
import { UiBadge, UiButton, UiIcon, UiModal, UiToast } from '@/components/ui'
import { useAuthStore } from '@/stores/auth'
import {
  type EventDTO,
  type EventStatus,
  type SessionCreatePayload,
  type SessionDTO,
  useEventsStore,
} from '@/stores/events'

const authStore = useAuthStore()
const eventsStore = useEventsStore()
const route = useRoute()
const router = useRouter()
const sessionModalRef = ref<InstanceType<typeof EventSessionModal> | null>(null)
const isSessionModalOpen = ref(false)
const isSessionSaving = ref(false)
const deletingSessionId = ref('')
const selectedSession = ref<SessionDTO | null>(null)
const sessionPendingDeletion = ref<SessionDTO | null>(null)
const deleteSessionError = ref('')
const isRegisteringToEvent = ref(false)
const isCancellingEventRegistration = ref(false)
const registeringSessionId = ref('')
const registrationError = ref('')
const sessionRegistrationError = ref('')
const toastMessage = ref('')

const eventId = computed(() => String(route.params.eventId || ''))
const event = computed(() => eventsStore.selectedEvent)
const isRegistrantsRoute = computed(() => route.name === 'event-registrants')
const isRegisteredToEvent = computed(() => eventsStore.isRegisteredToEvent(eventId.value))
const registrationPanelError = computed(
  () => registrationError.value || eventsStore.myRegistrationsError,
)
const canRegisterToSessions = computed(() => isRegisteredToEvent.value)
const sessions = computed(() => {
  return [...eventsStore.sessions].sort(
    (left, right) => new Date(left.start_time).getTime() - new Date(right.start_time).getTime(),
  )
})

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

const roleLabels: Record<string, string> = {
  admin: 'Administrador',
  attendee: 'Asistente',
  organizer: 'Organizador',
}

onMounted(() => {
  void loadEventDetail(eventId.value)
})

watch(
  () => [eventId.value, route.name] as const,
  ([nextEventId]) => {
    if (nextEventId) {
      void loadEventDetail(nextEventId)
    }
  },
)

watch(
  () => authStore.isAuthenticated,
  (isAuthenticated) => {
    if (!isAuthenticated) {
      void router.push('/login')
    }
  },
)

function getCoverClass(status: EventStatus) {
  if (status === 'cancelled') return 'cv-cancelled'
  if (status === 'draft') return 'cv-draft'
  if (status === 'finished') return 'cv-finished'

  return 'cv-published'
}

function formatEventDate(date: string) {
  return new Intl.DateTimeFormat('es-CO', {
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    month: 'short',
    year: 'numeric',
  }).format(new Date(date))
}

function getEventEndDateLabel(currentEvent: EventDTO) {
  if (!currentEvent.end_date) return 'Sin fecha de finalización'
  return formatEventDate(currentEvent.end_date)
}

function getOrganizerLabel(currentEvent: EventDTO) {
  return `Organiza ${currentEvent.created_by.slice(0, 8)}`
}

function getRoleLabel(role: string) {
  return roleLabels[role] || role
}

async function loadEventDetail(nextEventId: string) {
  registrationError.value = ''
  sessionRegistrationError.value = ''
  toastMessage.value = ''

  await Promise.all([
    eventsStore.fetchEventDetail(nextEventId),
    eventsStore.fetchMyRegistrations(),
    eventsStore.fetchMySessionRegistrations(),
  ])

  if (isRegistrantsRoute.value) {
    await eventsStore.fetchEventRegistrants(nextEventId)
  }
}

async function loadSpeakersIfNeeded() {
  if (!eventsStore.speakers.length && !eventsStore.speakersError) {
    await eventsStore.fetchSpeakers()
  }
}

async function openCreateSessionModal() {
  selectedSession.value = null
  isSessionModalOpen.value = true

  await loadSpeakersIfNeeded()
}

async function openEditSessionModal(session: SessionDTO) {
  selectedSession.value = session
  isSessionModalOpen.value = true

  await loadSpeakersIfNeeded()
}

function closeSessionModal() {
  isSessionModalOpen.value = false
  selectedSession.value = null
}

async function saveSession(payload: SessionCreatePayload) {
  isSessionSaving.value = true

  try {
    if (selectedSession.value) {
      await eventsStore.updateSession(eventId.value, selectedSession.value.id, payload)
    } else {
      await eventsStore.createSession(eventId.value, payload)
    }

    closeSessionModal()
  } catch (caughtError) {
    const message = caughtError instanceof Error ? caughtError.message : ''
    sessionModalRef.value?.setSubmitError(
      message || 'No pudimos guardar la sesión. Inténtalo de nuevo.',
    )
  } finally {
    isSessionSaving.value = false
  }
}

function requestDeleteSession(session: SessionDTO) {
  sessionPendingDeletion.value = session
  deleteSessionError.value = ''
}

function closeDeleteSessionModal() {
  if (deletingSessionId.value) return

  sessionPendingDeletion.value = null
  deleteSessionError.value = ''
}

async function confirmDeleteSession() {
  if (!sessionPendingDeletion.value) return

  deletingSessionId.value = sessionPendingDeletion.value.id
  deleteSessionError.value = ''

  try {
    await eventsStore.deleteSession(eventId.value, sessionPendingDeletion.value.id)
    sessionPendingDeletion.value = null
  } catch (caughtError) {
    const message = caughtError instanceof Error ? caughtError.message : ''
    deleteSessionError.value = message || 'No pudimos eliminar la sesión. Inténtalo de nuevo.'
  } finally {
    deletingSessionId.value = ''
  }
}

async function registerToEvent() {
  registrationError.value = ''
  toastMessage.value = ''
  isRegisteringToEvent.value = true

  try {
    await eventsStore.registerToEvent(eventId.value)
    toastMessage.value = 'Te registraste correctamente.'
  } catch (caughtError) {
    const message = caughtError instanceof Error ? caughtError.message : ''
    if (message.toLowerCase().includes('ya está registrado')) {
      await eventsStore.fetchMyRegistrations()
      return
    }

    registrationError.value = message || 'No pudimos completar tu registro. Inténtalo de nuevo.'
  } finally {
    isRegisteringToEvent.value = false
  }
}

async function registerToSession(session: SessionDTO) {
  sessionRegistrationError.value = ''
  toastMessage.value = ''
  registeringSessionId.value = session.id

  try {
    await eventsStore.registerToSession(session.id)
    toastMessage.value = `Te registraste en ${session.title}.`
  } catch (caughtError) {
    const message = caughtError instanceof Error ? caughtError.message : ''
    if (message.toLowerCase().includes('ya está registrado')) {
      await eventsStore.fetchMySessionRegistrations()
      return
    }

    sessionRegistrationError.value =
      message || 'No pudimos completar tu registro a la sesión. Inténtalo de nuevo.'
  } finally {
    registeringSessionId.value = ''
  }
}

async function cancelEventRegistration() {
  registrationError.value = ''
  toastMessage.value = ''
  isCancellingEventRegistration.value = true

  try {
    await eventsStore.cancelEventRegistration(eventId.value)
    toastMessage.value = 'Tu registro fue cancelado.'
  } catch (caughtError) {
    const message = caughtError instanceof Error ? caughtError.message : ''
    registrationError.value = message || 'No pudimos cancelar tu registro. Inténtalo de nuevo.'
  } finally {
    isCancellingEventRegistration.value = false
  }
}
</script>

<template>
  <div class="me-root">
    <UiToast
      :duration="4000"
      :message="toastMessage"
      :open="Boolean(toastMessage)"
      variant="success"
      @close="toastMessage = ''"
    />

    <main class="events-main">
      <section v-if="eventsStore.isDetailLoading" class="events-empty" aria-live="polite">
        <div class="empty-icon">
          <UiIcon name="ticket" :size="28" />
        </div>
        <h2>Cargando evento</h2>
        <p>Estamos consultando el detalle y sus sesiones.</p>
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
              <span>{{ event.name }}</span>
            </p>
            <h1 class="page-title">{{ event.name }}</h1>
          </div>

          <div v-if="authStore.canManageEvents" class="detail-actions">
            <UiButton
              v-if="!isRegistrantsRoute"
              variant="secondary"
              @click="router.push({ name: 'event-registrants', params: { eventId } })"
            >
              Ver registrados
            </UiButton>
            <UiButton
              v-else
              variant="secondary"
              @click="router.push({ name: 'event-detail', params: { eventId } })"
            >
              Ver detalle
            </UiButton>
            <UiButton
              variant="secondary"
              @click="router.push({ name: 'event-edit', params: { eventId } })"
              >Editar evento</UiButton
            >
            <UiButton variant="danger">Eliminar</UiButton>
          </div>
        </header>

        <section class="detail-layout">
          <article class="detail-main-card">
            <div class="detail-hero" :class="getCoverClass(event.status)">
              <UiBadge v-if="event.status" :variant="statusVariants[event.status]">
                {{ statusLabels[event.status] }}
              </UiBadge>
            </div>

            <div class="detail-content">
              <div class="detail-meta">
                <span>
                  <UiIcon name="calendar" :size="16" />
                  Inicio {{ formatEventDate(event.date) }}
                </span>
                <span>
                  <UiIcon name="calendar" :size="16" />
                  Fin {{ getEventEndDateLabel(event) }}
                </span>
                <span>
                  <UiIcon name="map-pin" :size="16" />
                  {{ event.location || 'Sin ubicación' }}
                </span>
                <span>
                  <UiIcon name="users" :size="16" />
                  {{ getOrganizerLabel(event) }}
                </span>
              </div>

              <section>
                <h2 class="section-title">Sobre el evento</h2>
                <p class="detail-description">
                  {{ event.description || 'Este evento aún no tiene una descripción publicada.' }}
                </p>
              </section>

              <section v-if="isRegistrantsRoute" class="registrants-section">
                <div class="detail-section-head">
                  <h2 class="section-title">
                    Registrados · {{ eventsStore.eventRegistrants.length }}
                  </h2>
                </div>

                <div v-if="eventsStore.isEventRegistrantsLoading" class="sessions-empty">
                  Cargando usuarios registrados.
                </div>
                <p v-else-if="eventsStore.eventRegistrantsError" class="form-alert" role="alert">
                  {{ eventsStore.eventRegistrantsError }}
                </p>
                <div v-else-if="eventsStore.eventRegistrants.length" class="registrants-list">
                  <article
                    v-for="registrant in eventsStore.eventRegistrants"
                    :key="registrant.user_id"
                    class="registrant-row"
                  >
                    <span class="session-avatar">
                      {{ registrant.email.slice(0, 1).toUpperCase() }}
                    </span>
                    <div class="session-main">
                      <strong>{{ registrant.email }}</strong>
                      <span>{{ getRoleLabel(registrant.role) }}</span>
                    </div>
                    <div class="session-side">
                      <span class="time-pill">
                        Registro {{ formatEventDate(registrant.registered_at) }}
                      </span>
                    </div>
                  </article>
                </div>
                <div v-else class="sessions-empty">
                  Este evento aún no tiene usuarios registrados.
                </div>
              </section>

              <template v-else>
                <EventSessionsSection
                  :can-manage-events="authStore.canManageEvents"
                  :can-register-to-sessions="canRegisterToSessions"
                  :checking-session-registrations="eventsStore.isMySessionRegistrationsLoading"
                  :deleting-session-id="deletingSessionId"
                  :registered-session-ids="eventsStore.registeredSessionIds"
                  :registering-session-id="registeringSessionId"
                  :sessions="sessions"
                  @add-session="openCreateSessionModal"
                  @delete-session="requestDeleteSession"
                  @edit-session="openEditSessionModal"
                  @register-session="registerToSession"
                />
                <p
                  v-if="sessionRegistrationError || eventsStore.mySessionRegistrationsError"
                  class="form-alert"
                  role="alert"
                >
                  {{ sessionRegistrationError || eventsStore.mySessionRegistrationsError }}
                </p>
              </template>
            </div>
          </article>

          <EventRegistrationPanel
            :cancelling="isCancellingEventRegistration"
            :checking-registration="eventsStore.isMyRegistrationsLoading"
            :error="registrationPanelError"
            :event="event"
            :is-registered="isRegisteredToEvent"
            :registering="isRegisteringToEvent"
            @cancel-registration="cancelEventRegistration"
            @register="registerToEvent"
          />
        </section>

        <EventSessionModal
          ref="sessionModalRef"
          :event="event"
          :open="isSessionModalOpen"
          :saving="isSessionSaving"
          :session="selectedSession"
          :sessions="sessions"
          :speakers="eventsStore.speakers"
          @close="closeSessionModal"
          @save="saveSession"
        />

        <UiModal :open="Boolean(sessionPendingDeletion)">
          <div class="card-header">
            <div>
              <h2 class="card-title">Eliminar sesión</h2>
              <p class="card-description">{{ sessionPendingDeletion?.title }}</p>
            </div>
            <UiButton variant="ghost" size="sm" @click="closeDeleteSessionModal">
              Cancelar
            </UiButton>
          </div>

          <div class="card-body">
            <p v-if="deleteSessionError" class="form-alert" role="alert">
              {{ deleteSessionError }}
            </p>
            <p class="card-description">
              Esta acción eliminará la sesión del evento. No se puede deshacer.
            </p>
          </div>

          <div class="card-footer form-actions">
            <UiButton
              variant="ghost"
              :disabled="Boolean(deletingSessionId)"
              @click="closeDeleteSessionModal"
            >
              Cancelar
            </UiButton>
            <UiButton
              variant="danger"
              :disabled="Boolean(deletingSessionId)"
              @click="confirmDeleteSession"
            >
              <UiIcon name="trash" :size="16" />
              {{ deletingSessionId ? 'Eliminando...' : 'Eliminar sesión' }}
            </UiButton>
          </div>
        </UiModal>
      </template>
    </main>
  </div>
</template>
