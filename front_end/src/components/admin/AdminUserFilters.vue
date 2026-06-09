<script setup lang="ts">
import type { UserRole } from '@/types/users'

type UserStatusFilter = 'active' | 'all' | 'inactive'

const searchQuery = defineModel<string>('searchQuery', { default: '' })
const roleFilter = defineModel<UserRole | 'all'>('roleFilter', { default: 'all' })
const statusFilter = defineModel<UserStatusFilter>('statusFilter', { default: 'all' })
</script>

<template>
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
</template>
