<script setup lang="ts">
import { onMounted, reactive, ref, watch } from 'vue'

import { AdminUserFilters, AdminUserFormModal, AdminUsersTable } from '@/components/admin'
import { UiButton, UiIcon, UiPagination, UiToast } from '@/components/ui'
import { deleteUser, fetchUsers } from '@/services/usersApi'
import type { UserDTO, UserRole } from '@/types/users'
import { useEventsStore } from '@/stores/events'

const eventsStore = useEventsStore()

type UserStatusFilter = 'active' | 'all' | 'inactive'

const users = ref<UserDTO[]>([])
const totalUsers = ref(0)
const totalPages = ref(1)
const currentPage = ref(1)
const searchQuery = ref('')
const roleFilter = ref<UserRole | 'all'>('all')
const statusFilter = ref<UserStatusFilter>('all')
const isLoading = ref(false)
const deletingUserId = ref('')
const error = ref('')
const editingUserId = ref('')
const isFormOpen = ref(false)
const toast = reactive({
  message: '',
  open: false,
  variant: 'info' as 'danger' | 'info' | 'success',
})

const limit = 10
let searchTimeout: ReturnType<typeof setTimeout> | undefined

onMounted(() => {
  void loadUsers()
})

watch([roleFilter, statusFilter], () => {
  currentPage.value = 1
  void loadUsers()
})

watch(currentPage, () => {
  void loadUsers()
})

watch(searchQuery, () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    currentPage.value = 1
    void loadUsers()
  }, 350)
})

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

function openCreateUser() {
  editingUserId.value = ''
  isFormOpen.value = true
}

function openEditUser(userId: string) {
  editingUserId.value = userId
  isFormOpen.value = true
}

function closeForm() {
  isFormOpen.value = false
  editingUserId.value = ''
}

async function handleFormSaved() {
  showToast(
    editingUserId.value ? 'Usuario actualizado correctamente.' : 'Usuario creado correctamente.',
    'success',
  )
  await loadUsers()
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

function showToast(message: string, variant: 'danger' | 'info' | 'success') {
  toast.message = message
  toast.variant = variant
  toast.open = true
}
</script>

<template>
  <div class="me-root admin-app">
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

          <AdminUserFilters
            v-model:searchQuery="searchQuery"
            v-model:roleFilter="roleFilter"
            v-model:statusFilter="statusFilter"
          />
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

        <AdminUsersTable
          v-else
          :users="users"
          :deleting-user-id="deletingUserId"
          @edit="openEditUser"
          @delete="removeUser"
        />

        <UiPagination
          :current-page="currentPage"
          :total-pages="totalPages"
          :total-items="totalUsers"
          :items-shown="users.length"
          @page-change="currentPage = $event"
        />
      </section>

      <AdminUserFormModal
        :is-open="isFormOpen"
        :user-id="editingUserId"
        @close="closeForm"
        @saved="handleFormSaved"
      />
    </main>
  </div>
</template>
