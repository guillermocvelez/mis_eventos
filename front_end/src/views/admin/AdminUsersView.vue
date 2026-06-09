<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue'

import EventsSidebar from '@/components/events/EventsSidebar.vue'
import { UiButton, UiField, UiIcon, UiModal, UiTextInput, UiToast } from '@/components/ui'
import { createUser, deleteUser, fetchUserById, fetchUsers, updateUser } from '@/services/usersApi'
import type { UserCreatePayload, UserDTO, UserRole, UserUpdatePayload } from '@/types/users'

type UserStatusFilter = 'active' | 'all' | 'inactive'
type UserFormState = {
  email: string
  isActive: 'false' | 'true'
  password: string
  role: UserRole
}

const users = ref<UserDTO[]>([])
const totalUsers = ref(0)
const totalPages = ref(1)
const currentPage = ref(1)
const searchQuery = ref('')
const roleFilter = ref<UserRole | 'all'>('all')
const statusFilter = ref<UserStatusFilter>('all')
const isLoading = ref(false)
const isSaving = ref(false)
const deletingUserId = ref('')
const error = ref('')
const formError = ref('')
const editingUserId = ref('')
const isFormOpen = ref(false)
const toast = reactive({
  message: '',
  open: false,
  variant: 'info' as 'danger' | 'info' | 'success',
})
const form = reactive<UserFormState>({
  email: '',
  isActive: 'true',
  password: '',
  role: 'attendee',
})
const limit = 10
let searchTimeout: ReturnType<typeof setTimeout> | undefined

const roleLabels: Record<UserRole, string> = {
  admin: 'Admin',
  attendee: 'Asistente',
  organizer: 'Organizador',
}

const statusLabels: Record<'active' | 'inactive', string> = {
  active: 'Activo',
  inactive: 'Inactivo',
}

const isEditing = computed(() => Boolean(editingUserId.value))
const formTitle = computed(() => (isEditing.value ? 'Editar usuario' : 'Crear usuario'))
const formActionLabel = computed(() => (isEditing.value ? 'Guardar cambios' : 'Crear usuario'))
const pageButtons = computed(() => {
  const safePages = Math.max(totalPages.value, 1)
  const start = Math.max(Math.min(currentPage.value - 2, safePages - 4), 1)
  const end = Math.min(start + 4, safePages)

  return Array.from({ length: end - start + 1 }, (_, index) => start + index)
})

onMounted(() => {
  void loadUsers()
})

watch([roleFilter, statusFilter], () => {
  resetPaginationAndLoad()
})

watch(currentPage, () => {
  void loadUsers()
})

watch(searchQuery, () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    resetPaginationAndLoad()
  }, 350)
})

function resetPaginationAndLoad() {
  if (currentPage.value === 1) {
    void loadUsers()
    return
  }

  currentPage.value = 1
}

async function loadUsers() {
  isLoading.value = true
  error.value = ''

  try {
    const response = await fetchUsers({
      is_active: getIsActiveFilter(),
      limit,
      page: currentPage.value,
      role: roleFilter.value === 'all' ? undefined : roleFilter.value,
      search: searchQuery.value,
    })

    users.value = response.items
    totalUsers.value = response.total
    totalPages.value = response.pages

    if (currentPage.value > response.pages) {
      currentPage.value = response.pages
    }
  } catch (caughtError) {
    error.value =
      caughtError instanceof Error
        ? caughtError.message
        : 'No pudimos cargar los usuarios. Inténtalo de nuevo.'
  } finally {
    isLoading.value = false
  }
}

function getIsActiveFilter() {
  if (statusFilter.value === 'active') return true
  if (statusFilter.value === 'inactive') return false

  return undefined
}

function getDisplayName(email: string) {
  return (email.split('@')[0] || email)
    .split(/[._-]/)
    .filter(Boolean)
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(' ')
}

function getInitials(email: string) {
  const source = getDisplayName(email) || email
  const parts = source.split(/\s+/).filter(Boolean)

  if (parts.length >= 2) {
    return `${parts[0]?.charAt(0) || ''}${parts[1]?.charAt(0) || ''}`.toUpperCase()
  }

  return source.slice(0, 2).toUpperCase()
}

function getStatus(user: UserDTO) {
  return user.is_active ? 'active' : 'inactive'
}

function formatRegistrationDate(date: string) {
  return new Intl.DateTimeFormat('es-CO', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
  }).format(new Date(date))
}

function openCreateUser() {
  editingUserId.value = ''
  resetForm()
  isFormOpen.value = true
}

async function openEditUser(userId: string) {
  formError.value = ''
  editingUserId.value = userId
  isFormOpen.value = true

  try {
    const user = await fetchUserById(userId)
    form.email = user.email
    form.password = ''
    form.role = user.role
    form.isActive = user.is_active ? 'true' : 'false'
  } catch (caughtError) {
    closeForm()
    showToast(
      caughtError instanceof Error
        ? caughtError.message
        : 'No pudimos cargar el usuario seleccionado.',
      'danger',
    )
  }
}

function closeForm() {
  isFormOpen.value = false
  editingUserId.value = ''
  formError.value = ''
  resetForm()
}

function resetForm() {
  form.email = ''
  form.password = ''
  form.role = 'attendee'
  form.isActive = 'true'
}

async function submitForm() {
  formError.value = ''

  if (!form.email.trim()) {
    formError.value = 'El correo es obligatorio.'
    return
  }

  if (!isEditing.value && !form.password.trim()) {
    formError.value = 'La contraseña es obligatoria para crear usuarios.'
    return
  }

  isSaving.value = true

  try {
    if (isEditing.value) {
      const payload: UserUpdatePayload = {
        email: form.email.trim(),
        is_active: form.isActive === 'true',
        role: form.role,
      }

      if (form.password.trim()) {
        payload.password = form.password
      }

      await updateUser(editingUserId.value, payload)
      showToast('Usuario actualizado correctamente.', 'success')
    } else {
      const payload: UserCreatePayload = {
        email: form.email.trim(),
        is_active: form.isActive === 'true',
        password: form.password,
        role: form.role,
      }

      await createUser(payload)
      showToast('Usuario creado correctamente.', 'success')
    }

    closeForm()
    await loadUsers()
  } catch (caughtError) {
    formError.value =
      caughtError instanceof Error
        ? caughtError.message
        : 'No pudimos guardar el usuario. Inténtalo de nuevo.'
  } finally {
    isSaving.value = false
  }
}

async function removeUser(user: UserDTO) {
  const confirmed = window.confirm(`¿Quieres desactivar a ${user.email}?`)
  if (!confirmed) return

  deletingUserId.value = user.id

  try {
    await deleteUser(user.id)
    showToast('Usuario desactivado correctamente.', 'success')
    await loadUsers()
  } catch (caughtError) {
    showToast(
      caughtError instanceof Error
        ? caughtError.message
        : 'No pudimos desactivar el usuario. Inténtalo de nuevo.',
      'danger',
    )
  } finally {
    deletingUserId.value = ''
  }
}

function goToPage(page: number) {
  if (page < 1 || page > totalPages.value || page === currentPage.value) return

  currentPage.value = page
}

function showToast(message: string, variant: 'danger' | 'info' | 'success') {
  toast.message = message
  toast.variant = variant
  toast.open = true
}
</script>

<template>
  <div class="me-root events-app admin-app">
    <EventsSidebar :event-count="6" />

    <main class="events-main admin-main">
      <UiToast
        :message="toast.message"
        :open="toast.open"
        :variant="toast.variant"
        @close="toast.open = false"
      />

      <header class="events-topbar admin-topbar">
        <div>
          <p class="section-kicker">Administración</p>
          <h1 class="page-title">Gestión de usuarios</h1>
          <p class="page-subtitle">
            Administra roles, estados y permisos de los miembros de la plataforma.
          </p>
        </div>

        <UiButton size="lg" @click="openCreateUser">
          <UiIcon name="plus" />
          Crear usuario
        </UiButton>
      </header>

      <section class="admin-panel" aria-labelledby="admin-users-title">
        <div class="admin-panel-head">
          <div>
            <h2 id="admin-users-title">Usuarios</h2>
            <p>Vista operativa para revisar perfiles y preparar cambios de rol.</p>
          </div>

          <div class="admin-filters">
            <label class="admin-filter">
              <span>Buscar</span>
              <input
                v-model="searchQuery"
                aria-label="Buscar usuarios por correo"
                class="input"
                placeholder="correo@empresa.com"
                type="search"
              />
            </label>

            <label class="admin-filter">
              <span>Rol</span>
              <select v-model="roleFilter" aria-label="Filtrar usuarios por rol">
                <option value="all">Todos los roles</option>
                <option value="organizer">Organizador</option>
                <option value="admin">Admin</option>
                <option value="attendee">Asistente</option>
              </select>
            </label>

            <label class="admin-filter">
              <span>Estado</span>
              <select v-model="statusFilter" aria-label="Filtrar usuarios por estado">
                <option value="all">Todos</option>
                <option value="active">Activos</option>
                <option value="inactive">Inactivos</option>
              </select>
            </label>
          </div>
        </div>

        <div v-if="error" class="admin-state danger">
          <p>{{ error }}</p>
          <UiButton size="sm" variant="secondary" @click="loadUsers">Reintentar</UiButton>
        </div>

        <div v-else-if="isLoading" class="admin-state">
          <p>Cargando usuarios...</p>
        </div>

        <div v-else-if="!users.length" class="admin-state">
          <p>No hay usuarios para los filtros seleccionados.</p>
        </div>

        <div v-else class="admin-table-wrap">
          <table class="admin-users-table">
            <thead>
              <tr>
                <th scope="col">Usuario</th>
                <th scope="col">Correo</th>
                <th scope="col">Rol</th>
                <th scope="col">Estado</th>
                <th scope="col">Registro</th>
                <th scope="col">Acciones</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="user in users" :key="user.id">
                <td>
                  <div class="admin-user-cell">
                    <span class="admin-user-avatar" :class="`role-${user.role}`">
                      {{ getInitials(user.email) }}
                    </span>
                    <strong>{{ getDisplayName(user.email) }}</strong>
                  </div>
                </td>
                <td>
                  <span class="admin-email">{{ user.email }}</span>
                </td>
                <td>
                  <span class="admin-role-pill" :class="`role-${user.role}`">
                    {{ roleLabels[user.role] }}
                  </span>
                </td>
                <td>
                  <span class="admin-status-pill" :class="`status-${getStatus(user)}`">
                    {{ statusLabels[getStatus(user)] }}
                  </span>
                </td>
                <td>
                  <span class="admin-date">{{ formatRegistrationDate(user.created_at) }}</span>
                </td>
                <td>
                  <div class="admin-row-actions">
                    <UiButton size="sm" variant="ghost" @click="openEditUser(user.id)">
                      <UiIcon name="pencil" :size="16" />
                      Editar
                    </UiButton>
                    <UiButton
                      :disabled="deletingUserId === user.id || !user.is_active"
                      size="sm"
                      variant="danger"
                      @click="removeUser(user)"
                    >
                      <UiIcon name="trash" :size="16" />
                      Desactivar
                    </UiButton>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <footer class="admin-pagination">
          <p>Mostrando {{ users.length }} de {{ totalUsers }} usuarios</p>

          <nav aria-label="Paginación de usuarios" class="admin-page-list">
            <button type="button" :disabled="currentPage === 1" @click="goToPage(currentPage - 1)">
              ‹
            </button>
            <button
              v-for="page in pageButtons"
              :key="page"
              :class="{ active: page === currentPage }"
              type="button"
              @click="goToPage(page)"
            >
              {{ page }}
            </button>
            <button
              type="button"
              :disabled="currentPage === totalPages"
              @click="goToPage(currentPage + 1)"
            >
              ›
            </button>
          </nav>
        </footer>
      </section>

      <UiModal :open="isFormOpen">
        <form class="admin-user-form" @submit.prevent="submitForm">
          <div class="card-header">
            <div>
              <h2 class="card-title">{{ formTitle }}</h2>
              <p class="card-description">
                {{
                  isEditing ? 'Actualiza los datos del usuario.' : 'Crea una cuenta administrada.'
                }}
              </p>
            </div>
            <button class="icon-btn light" type="button" aria-label="Cerrar" @click="closeForm">
              <UiIcon name="x" :size="18" />
            </button>
          </div>

          <div class="admin-user-form-body">
            <p v-if="formError" class="form-alert">{{ formError }}</p>

            <UiField for-id="admin-user-email" label="Correo">
              <UiTextInput
                id="admin-user-email"
                v-model="form.email"
                placeholder="usuario@empresa.com"
                type="email"
              />
            </UiField>

            <UiField
              for-id="admin-user-password"
              label="Contraseña"
              :hint="isEditing ? 'Déjala vacía si no quieres cambiarla.' : ''"
            >
              <UiTextInput
                id="admin-user-password"
                v-model="form.password"
                :placeholder="isEditing ? 'Sin cambios' : 'Contraseña inicial'"
                type="password"
              />
            </UiField>

            <div class="admin-form-grid">
              <UiField for-id="admin-user-role" label="Rol">
                <select id="admin-user-role" v-model="form.role" class="input">
                  <option value="attendee">Asistente</option>
                  <option value="organizer">Organizador</option>
                  <option value="admin">Admin</option>
                </select>
              </UiField>

              <UiField for-id="admin-user-status" label="Estado">
                <select id="admin-user-status" v-model="form.isActive" class="input">
                  <option value="true">Activo</option>
                  <option value="false">Inactivo</option>
                </select>
              </UiField>
            </div>
          </div>

          <div class="card-footer form-actions">
            <UiButton :disabled="isSaving" type="button" variant="ghost" @click="closeForm">
              Cancelar
            </UiButton>
            <UiButton :disabled="isSaving" type="submit">
              {{ isSaving ? 'Guardando...' : formActionLabel }}
            </UiButton>
          </div>
        </form>
      </UiModal>
    </main>
  </div>
</template>
