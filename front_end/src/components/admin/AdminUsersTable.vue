<script setup lang="ts">
import { UiButton, UiIcon } from '@/components/ui'
import type { UserDTO, UserRole } from '@/types/users'

defineProps<{
  users: UserDTO[]
  deletingUserId: string
}>()

const emit = defineEmits<{
  edit: [userId: string]
  delete: [user: UserDTO]
}>()

const roleLabels: Record<UserRole, string> = {
  admin: 'Admin',
  attendee: 'Asistente',
  organizer: 'Organizador',
}

const statusLabels: Record<'active' | 'inactive', string> = {
  active: 'Activo',
  inactive: 'Inactivo',
}

function getStatus(user: UserDTO) {
  return user.is_active ? 'active' : 'inactive'
}

function getInitials(name: string) {
  const parts = name.split(/\s+/).filter(Boolean)

  if (parts.length >= 2) {
    return `${parts[0]?.charAt(0) || ''}${parts[1]?.charAt(0) || ''}`.toUpperCase()
  }

  return name.slice(0, 2).toUpperCase()
}

function formatRegistrationDate(date: string) {
  return new Intl.DateTimeFormat('es-CO', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
  }).format(new Date(date))
}
</script>

<template>
  <div class="admin-table-wrap">
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
                {{ getInitials(user.name) }}
              </span>
              <strong>{{ user.name }}</strong>
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
              <UiButton size="sm" variant="ghost" @click="emit('edit', user.id)">
                <UiIcon name="pencil" :size="16" />
                Editar
              </UiButton>
              <UiButton
                :disabled="deletingUserId === user.id || !user.is_active"
                size="sm"
                variant="danger"
                @click="emit('delete', user)"
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
</template>
